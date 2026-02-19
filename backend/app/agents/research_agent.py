"""
Research Agent - Gathers product intelligence and parent insights.

Responsibilities:
1. Scrape and analyze category page
2. Extract product details
3. Search for parent questions
4. Competitor analysis
5. SEO research
"""
import logging
from typing import Dict, List
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from bs4 import BeautifulSoup
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Research agent for gathering product and market intelligence."""

    def __init__(self, use_mock_data: bool = None, progress_callback=None):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.progress_callback = progress_callback
        # Use config setting if not explicitly provided
        if use_mock_data is None:
            self.use_mock_data = not settings.use_real_scraping
        else:
            self.use_mock_data = use_mock_data

    def _update_progress(self, campaign_id: str, step: str, percentage: float):
        """Update progress via callback if available."""
        if self.progress_callback:
            try:
                self.progress_callback(campaign_id, step, percentage)
            except Exception as e:
                logger.warning(f"Failed to update progress: {e}")

    async def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the research agent workflow.

        Args:
            state: Current campaign state

        Returns:
            Updated state with research_data populated
        """
        logger.info(f"Research Agent starting for campaign {state['campaign_id']}")

        state["current_step"] = "research"
        state["progress_percentage"] = 10
        campaign_id = state['campaign_id']

        try:
            # Use mock data in development or if scraping fails
            if self.use_mock_data:
                logger.info("Using mock data for research (development mode)")
                products = self._get_mock_products()
                category_insights = self._get_mock_insights()
            else:
                # Step 1: Scrape category page(s) with pagination support
                logger.info(f"Scraping category page: {state['category_url']}")
                self._update_progress(campaign_id, 'research:scraping_page', 5)
                all_products = []
                all_html_content = ""
                target_min_products = 60

                try:
                    # Scrape first page
                    html_content = await self._scrape_page(state["category_url"])
                    all_html_content = html_content

                    # Parse products from first page
                    logger.info("Parsing product data from listing page")
                    self._update_progress(campaign_id, 'research:parsing_products', 8)
                    products = self._parse_products(html_content, state["category_url"])
                    all_products.extend(products)
                    logger.info(f"Found {len(products)} products on page 1")

                    # If we don't have enough products, try pagination
                    if len(all_products) < target_min_products:
                        logger.info(f"Only found {len(all_products)} products, attempting pagination...")
                        self._update_progress(campaign_id, f'research:pagination ({len(all_products)} products found)', 10)
                        paginated_products = await self._scrape_paginated_products(
                            state["category_url"],
                            existing_products=all_products,
                            target_count=target_min_products,
                            max_pages=5
                        )
                        if paginated_products:
                            # Deduplicate by URL
                            existing_urls = {p.get('url') for p in all_products if p.get('url')}
                            for prod in paginated_products:
                                if prod.get('url') and prod.get('url') not in existing_urls:
                                    all_products.append(prod)
                                    existing_urls.add(prod.get('url'))
                            logger.info(f"After pagination: {len(all_products)} total products")

                    products = all_products

                except Exception as scrape_error:
                    logger.warning(f"Scraping failed, falling back to mock data: {scrape_error}")
                    products = self._get_mock_products()
                    category_insights = self._get_mock_insights()
                else:
                    # Step 3: Deep scrape product detail pages for full descriptions
                    product_urls = [p.get('url') for p in products if p.get('url')]
                    if product_urls:
                        logger.info(f"Found {len(product_urls)} product URLs, starting deep scrape...")

                        # Update state to show deep scraping phase
                        state["current_step"] = "deep_scraping"
                        state["progress_percentage"] = 12
                        self._update_progress(campaign_id, f'research:deep_scraping (0/{len(product_urls)})', 12)

                        detailed_products = await self._scrape_product_details(
                            product_urls,
                            state["category_url"],
                            max_products=120,
                            min_products=60,
                            state=state,  # Pass state for progress updates
                            campaign_id=campaign_id  # Pass campaign_id for progress callback
                        )

                        # Merge detailed data with listing data
                        if detailed_products:
                            logger.info(f"Merging {len(detailed_products)} detailed products with listing data")
                            products = self._merge_product_data(products, detailed_products)

                        # Return to research step after deep scraping
                        state["current_step"] = "research"
                    else:
                        logger.warning("No product URLs found, skipping deep scrape")

                    # Step 4: Analyse with Claude to extract insights
                    logger.info("Analysing products with Claude")
                    self._update_progress(campaign_id, 'research:analysing_products', 22)
                    category_insights = self._analyze_category(products, all_html_content if all_html_content else html_content)

            # Step 4: Research parent questions
            logger.info("Researching parent questions")
            self._update_progress(campaign_id, 'research:parent_questions', 25)
            parent_questions = self._research_parent_questions(
                category_insights.get("category_name", "children's products")
            )

            # Step 5: SEO keyword research
            logger.info("Conducting SEO research")
            self._update_progress(campaign_id, 'research:seo_research', 27)
            seo_keywords = self._research_seo_keywords(
                category_insights.get("category_name", "")
            )

            # Step 6: Generate content/article ideas
            logger.info("Generating content ideas")
            self._update_progress(campaign_id, 'research:content_ideas', 28)
            content_ideas = self._generate_content_ideas(
                products=products,
                category_insights=category_insights,
                parent_questions=parent_questions
            )

            # Compile research data
            research_data = {
                "products": products,
                "category_insights": category_insights,
                "parent_questions": parent_questions,
                "seo_keywords": seo_keywords,
                "content_ideas": content_ideas,
                "competitor_insights": {
                    "effective_messaging": [],
                    "content_gaps": []
                }
            }

            state["research_data"] = research_data
            state["progress_percentage"] = 30
            logger.info("Research Agent completed successfully")

            return state

        except Exception as e:
            error_msg = f"Research Agent failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["progress_percentage"] = 30  # Still advance progress
            return state

    async def _scrape_page(self, url: str, timeout: int = 60000) -> str:
        """
        Scrape a web page using Playwright (async).

        Args:
            url: URL to scrape
            timeout: Timeout in milliseconds (default: 60 seconds)

        Returns:
            HTML content of the page
        """
        browser = None
        page = None

        try:
            logger.info(f"[SCRAPER] Starting Playwright for {url}")
            async with async_playwright() as p:
                logger.info(f"[SCRAPER] Playwright context created")
                # Launch browser with anti-detection settings
                logger.info(f"[SCRAPER] Launching Chromium browser...")
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )
                logger.info(f"[SCRAPER] Browser launched successfully")

                # Create context with realistic browser settings
                logger.info(f"[SCRAPER] Creating browser context...")
                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = await context.new_page()
                logger.info(f"[SCRAPER] New page created")

                # Set default navigation timeout
                page.set_default_navigation_timeout(timeout)
                page.set_default_timeout(timeout)
                logger.info(f"[SCRAPER] Timeouts set to {timeout}ms")

                # Navigate to URL with lenient wait condition
                logger.info(f"[SCRAPER] Navigating to {url} with {timeout}ms timeout")
                await page.goto(url, wait_until="domcontentloaded")
                logger.info(f"[SCRAPER] Page loaded (domcontentloaded)")

                # Wait for dynamic content to load
                logger.info(f"[SCRAPER] Waiting 3s for dynamic content...")
                await page.wait_for_timeout(3000)
                logger.info(f"[SCRAPER] Dynamic content wait complete")

                # Scroll the page multiple times to load more products (many sites lazy-load)
                logger.info(f"[SCRAPER] Scrolling page to load more products (15 scrolls)...")
                for i in range(15):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(800)

                    # Every 5 scrolls, try clicking "Load More" or "Show More" buttons
                    if i % 5 == 4:
                        try:
                            load_more_selectors = [
                                'button:has-text("Load More")',
                                'button:has-text("Show More")',
                                'button:has-text("View More")',
                                'a:has-text("Load More")',
                                'a:has-text("Show More")',
                                '[class*="load-more"]',
                                '[class*="show-more"]',
                                '[class*="loadmore"]',
                                '[data-action="load-more"]',
                            ]
                            for selector in load_more_selectors:
                                try:
                                    btn = page.locator(selector).first
                                    if await btn.is_visible(timeout=500):
                                        await btn.click()
                                        logger.info(f"[SCRAPER] Clicked load more button: {selector}")
                                        await page.wait_for_timeout(2000)
                                        break
                                except:
                                    continue
                        except Exception as e:
                            pass  # No load more button found, continue scrolling

                logger.info(f"[SCRAPER] Page scrolling complete")

                # Try to click any remaining "Load More" buttons
                for _ in range(3):
                    try:
                        load_more_clicked = False
                        load_more_selectors = [
                            'button:has-text("Load More")',
                            'button:has-text("Show More")',
                            'button:has-text("View More")',
                            '[class*="load-more"]',
                            '[class*="loadmore"]',
                        ]
                        for selector in load_more_selectors:
                            try:
                                btn = page.locator(selector).first
                                if await btn.is_visible(timeout=500):
                                    await btn.click()
                                    logger.info(f"[SCRAPER] Clicked additional load more: {selector}")
                                    await page.wait_for_timeout(2000)
                                    load_more_clicked = True
                                    break
                            except:
                                continue
                        if not load_more_clicked:
                            break
                    except:
                        break

                # Get page content
                logger.info(f"[SCRAPER] Extracting page content...")
                html_content = await page.content()
                logger.info(f"[SCRAPER] Successfully scraped {url} ({len(html_content)} bytes)")

                await browser.close()
                logger.info(f"[SCRAPER] Browser closed")
                return html_content

        except PlaywrightTimeoutError as e:
            logger.error(f"[SCRAPER] TIMEOUT scraping {url} after {timeout}ms: {e}", exc_info=True)
            # Try to get whatever content was loaded
            try:
                if page:
                    logger.info(f"[SCRAPER] Attempting to get partial content...")
                    content = await page.content()
                    if browser:
                        await browser.close()
                        logger.info(f"[SCRAPER] Browser closed after timeout")
                    if content and len(content) > 1000:
                        logger.info(f"[SCRAPER] Returning partial content ({len(content)} bytes)")
                        return content
                    else:
                        logger.warning(f"[SCRAPER] Partial content too small: {len(content) if content else 0} bytes")
            except Exception as partial_error:
                logger.error(f"[SCRAPER] Could not get partial content: {partial_error}", exc_info=True)

            # Clean up
            if browser:
                try:
                    await browser.close()
                    logger.info(f"[SCRAPER] Browser cleanup complete")
                except Exception as cleanup_error:
                    logger.error(f"[SCRAPER] Cleanup failed: {cleanup_error}")

            raise  # Re-raise to trigger fallback to mock data

        except Exception as e:
            logger.error(f"[SCRAPER] FATAL ERROR scraping {url}: {type(e).__name__}: {e}", exc_info=True)
            # Close browser if it exists
            if browser:
                try:
                    await browser.close()
                    logger.info(f"[SCRAPER] Browser closed after error")
                except Exception as cleanup_error:
                    logger.error(f"[SCRAPER] Cleanup failed: {cleanup_error}")
            raise  # Re-raise to trigger fallback to mock data

    async def _scrape_paginated_products(self, base_url: str, existing_products: List[Dict], target_count: int = 60, max_pages: int = 5) -> List[Dict]:
        """
        Scrape additional pages to get more products via pagination.

        Args:
            base_url: The original category URL
            existing_products: Products already scraped from page 1
            target_count: Target number of products to reach
            max_pages: Maximum number of additional pages to scrape

        Returns:
            List of additional products from paginated pages
        """
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        all_new_products = []
        current_count = len(existing_products)

        logger.info(f"[PAGINATION] Starting pagination scrape. Current: {current_count}, Target: {target_count}")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )

                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = await context.new_page()
                page.set_default_navigation_timeout(45000)
                page.set_default_timeout(45000)

                for page_num in range(2, max_pages + 2):  # Start from page 2
                    if current_count + len(all_new_products) >= target_count:
                        logger.info(f"[PAGINATION] Reached target count, stopping pagination")
                        break

                    # Try different pagination URL patterns
                    pagination_urls = self._generate_pagination_urls(base_url, page_num)

                    page_scraped = False
                    for pag_url in pagination_urls:
                        try:
                            logger.info(f"[PAGINATION] Trying page {page_num}: {pag_url[:80]}...")
                            await page.goto(pag_url, wait_until="domcontentloaded")
                            await page.wait_for_timeout(2000)

                            # Scroll to load lazy content
                            for _ in range(5):
                                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                                await page.wait_for_timeout(500)

                            html_content = await page.content()

                            # Parse products from this page
                            page_products = self._parse_products(html_content, pag_url)

                            if page_products and len(page_products) > 0:
                                logger.info(f"[PAGINATION] Found {len(page_products)} products on page {page_num}")
                                all_new_products.extend(page_products)
                                page_scraped = True
                                break
                            else:
                                logger.info(f"[PAGINATION] No products found at {pag_url[:50]}, trying next pattern")

                        except Exception as e:
                            logger.warning(f"[PAGINATION] Failed to scrape {pag_url[:50]}: {e}")
                            continue

                    if not page_scraped:
                        logger.info(f"[PAGINATION] Could not find page {page_num}, stopping pagination")
                        break

                    await page.wait_for_timeout(1000)  # Brief delay between pages

                await browser.close()

        except Exception as e:
            logger.error(f"[PAGINATION] Error during pagination: {e}", exc_info=True)

        logger.info(f"[PAGINATION] Pagination complete. Found {len(all_new_products)} additional products")
        return all_new_products

    def _generate_pagination_urls(self, base_url: str, page_num: int) -> List[str]:
        """
        Generate possible pagination URL patterns for a given page number.

        Args:
            base_url: The original URL
            page_num: The page number to generate URLs for

        Returns:
            List of possible pagination URLs to try
        """
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

        urls = []
        parsed = urlparse(base_url)

        # Pattern 1: ?page=N or &page=N
        query_params = parse_qs(parsed.query)
        query_params['page'] = [str(page_num)]
        new_query = urlencode(query_params, doseq=True)
        urls.append(urlunparse(parsed._replace(query=new_query)))

        # Pattern 2: ?p=N
        query_params2 = parse_qs(parsed.query)
        query_params2['p'] = [str(page_num)]
        new_query2 = urlencode(query_params2, doseq=True)
        urls.append(urlunparse(parsed._replace(query=new_query2)))

        # Pattern 3: /page/N/ in path
        path = parsed.path.rstrip('/')
        if '/page/' not in path:
            new_path = f"{path}/page/{page_num}/"
            urls.append(urlunparse(parsed._replace(path=new_path)))

        # Pattern 4: ?start=N (offset-based, assuming ~24 products per page)
        query_params4 = parse_qs(parsed.query)
        query_params4['start'] = [str((page_num - 1) * 24)]
        new_query4 = urlencode(query_params4, doseq=True)
        urls.append(urlunparse(parsed._replace(query=new_query4)))

        # Pattern 5: ?offset=N
        query_params5 = parse_qs(parsed.query)
        query_params5['offset'] = [str((page_num - 1) * 24)]
        new_query5 = urlencode(query_params5, doseq=True)
        urls.append(urlunparse(parsed._replace(query=new_query5)))

        # Pattern 6: #page=N (hash-based, less common but worth trying)
        urls.append(f"{base_url}#page={page_num}")

        return urls

    async def _scrape_product_details(self, product_urls: List[str], base_url: str, max_products: int = 120, min_products: int = 60, state: Dict = None, campaign_id: str = None) -> List[Dict]:
        """
        Scrape individual product detail pages to get full descriptions.

        Args:
            product_urls: List of product URLs to scrape
            base_url: Base URL for resolving relative URLs
            max_products: Maximum number of products to scrape (default: 120)
            min_products: Minimum number of products to aim for (default: 60)
            state: Campaign state for progress updates

        Returns:
            List of product detail dictionaries
        """
        from urllib.parse import urljoin

        product_details = []
        # Ensure we scrape at least min_products if available, up to max_products
        available_urls = len(product_urls)
        target_products = min(max_products, max(min_products, available_urls))
        urls_to_scrape = product_urls[:target_products]
        total_products = len(urls_to_scrape)

        logger.info(f"[DEEP SCRAPER] Starting deep scrape of {total_products} product pages")

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )

                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = await context.new_page()
                page.set_default_navigation_timeout(30000)  # 30s timeout per page
                page.set_default_timeout(30000)

                for i, url in enumerate(urls_to_scrape):
                    try:
                        # Update progress (deep scraping runs from 12% to 22% of total)
                        progress = 12 + (10 * (i / total_products))  # 12% to 22%
                        if state:
                            state["progress_percentage"] = round(progress, 1)
                            state["current_step"] = f"deep_scraping ({i+1}/{total_products})"
                        if campaign_id:
                            self._update_progress(campaign_id, f'research:deep_scraping ({i+1}/{total_products})', round(progress, 1))

                        # Resolve relative URLs
                        full_url = urljoin(base_url, url)
                        logger.info(f"[DEEP SCRAPER] Scraping product {i+1}/{total_products}: {full_url[:80]}...")

                        await page.goto(full_url, wait_until="domcontentloaded")
                        await page.wait_for_timeout(1500)  # Wait for dynamic content

                        # Get page content
                        html = await page.content()

                        # Use Claude to extract product details
                        detail = await self._extract_product_detail(html, full_url)
                        if detail:
                            detail['url'] = full_url
                            product_details.append(detail)
                            logger.info(f"[DEEP SCRAPER] Extracted details for: {detail.get('name', 'Unknown')[:50]}")

                        # Small delay to avoid rate limiting
                        await page.wait_for_timeout(500)

                    except Exception as e:
                        logger.warning(f"[DEEP SCRAPER] Failed to scrape {url}: {e}")
                        continue

                await browser.close()
                logger.info(f"[DEEP SCRAPER] Completed deep scrape. Got details for {len(product_details)} products")

        except Exception as e:
            logger.error(f"[DEEP SCRAPER] Error during deep scrape: {e}", exc_info=True)

        return product_details

    async def _extract_product_detail(self, html_content: str, url: str) -> Dict:
        """
        Extract detailed product information from a product detail page.

        Args:
            html_content: HTML content of the product page
            url: URL of the product page

        Returns:
            Dictionary with product details
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Remove scripts and styles for cleaner content
        for tag in soup.find_all(['script', 'style', 'nav', 'header', 'footer']):
            tag.decompose()

        # Get the main content area
        main_content = str(soup.find('main') or soup.find('body') or soup)[:40000]

        prompt = f"""Extract detailed product information from this product detail page.

URL: {url}

Extract:
1. Product name (full name)
2. Price (current price, numeric)
3. Original price if on sale (numeric, or null)
4. Full description (complete product description, can be multiple paragraphs)
5. Key features (bullet points or specifications)
6. Material/fabric information
7. Size information available
8. Brand name
9. Any care instructions

HTML content:
{main_content}

IMPORTANT: Return ONLY valid JSON:
{{
  "name": "Full Product Name",
  "price": 29.99,
  "original_price": null,
  "description": "Full detailed description...",
  "features": ["feature 1", "feature 2"],
  "material": "Cotton, Polyester, etc.",
  "sizes": ["S", "M", "L"] or "One Size",
  "brand": "Brand Name",
  "care_instructions": "Machine wash at 30°C..."
}}

If you cannot find certain fields, use null for that field."""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.2,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            return json.loads(response_text)

        except Exception as e:
            logger.warning(f"[DEEP SCRAPER] Failed to extract details from {url}: {e}")
            return None

    def _merge_product_data(self, listing_products: List[Dict], detailed_products: List[Dict]) -> List[Dict]:
        """
        Merge detailed product data with listing page data.

        Args:
            listing_products: Products from listing page (basic info)
            detailed_products: Products from detail pages (full descriptions)

        Returns:
            Merged list of products with full details
        """
        # Create a lookup by URL for detailed products
        detailed_by_url = {}
        for dp in detailed_products:
            if dp.get('url'):
                detailed_by_url[dp['url']] = dp

        merged = []
        for lp in listing_products:
            product_url = lp.get('url', '')

            # Try to find matching detailed product
            detailed = None
            for url_key, dp in detailed_by_url.items():
                # Match by URL (handle relative vs absolute)
                if url_key in product_url or product_url in url_key or \
                   url_key.split('/')[-1] == product_url.split('/')[-1]:
                    detailed = dp
                    break

            if detailed:
                # Merge: detailed data takes priority, but keep listing data as fallback
                merged_product = {
                    'name': detailed.get('name') or lp.get('name', ''),
                    'price': detailed.get('price') or lp.get('price'),
                    'original_price': detailed.get('original_price'),
                    'description': detailed.get('description') or lp.get('description', ''),
                    'features': detailed.get('features') or lp.get('features', []),
                    'material': detailed.get('material'),
                    'sizes': detailed.get('sizes') or lp.get('sizes'),
                    'brand': detailed.get('brand'),
                    'care_instructions': detailed.get('care_instructions'),
                    'url': detailed.get('url') or lp.get('url')
                }
                merged.append(merged_product)
                logger.debug(f"Merged detailed data for: {merged_product['name'][:40]}")
            else:
                # No detailed data found, use listing data as-is
                merged.append(lp)

        logger.info(f"Merged {len([m for m in merged if m.get('description') and len(str(m.get('description', ''))) > 50])} products with full descriptions")
        return merged

    def _parse_products(self, html_content: str, url: str) -> List[Dict]:
        """
        Parse product information from HTML.

        Args:
            html_content: HTML content of the page
            url: Original URL (for context)

        Returns:
            List of product dictionaries
        """
        import re
        import json as json_module
        from urllib.parse import urljoin

        soup = BeautifulSoup(html_content, 'html.parser')

        # Strategy 0: Direct product link extraction (most reliable)
        # Find all product links by common patterns
        product_links = set()

        # Pattern 1: Links with product-related classes or data attributes
        product_link_selectors = [
            'a[class*="product"]',
            'a[class*="Product"]',
            'a[data-product]',
            'a[data-item]',
            '[class*="product-card"] a',
            '[class*="product-tile"] a',
            '[class*="product-item"] a',
            '[class*="ProductCard"] a',
            'article a[href*="/p/"]',
            'article a[href*="/product"]',
            '.products-grid a',
            '.product-list a',
        ]

        for selector in product_link_selectors:
            try:
                for link in soup.select(selector):
                    href = link.get('href', '')
                    if href and not href.startswith('#') and not href.startswith('javascript'):
                        # Filter for likely product URLs
                        if any(pattern in href.lower() for pattern in ['/p/', '/product', '/item', '-p-', '/products/']):
                            product_links.add(urljoin(url, href))
                        elif re.search(r'/[a-z0-9-]+-p\d+', href, re.I):  # Pattern like /product-name-p12345
                            product_links.add(urljoin(url, href))
            except:
                continue

        # Pattern 2: Links within product grid/list containers
        grid_containers = soup.find_all(['div', 'ul', 'section'], class_=re.compile(r'product|grid|listing|results', re.I))
        for container in grid_containers:
            for link in container.find_all('a', href=True):
                href = link.get('href', '')
                if href and len(href) > 10 and not href.startswith('#'):
                    # Check if it looks like a product URL (not category/filter)
                    if not any(skip in href.lower() for skip in ['filter', 'sort', 'page=', 'category', '#', 'javascript', 'login', 'cart', 'wishlist']):
                        full_url = urljoin(url, href)
                        if full_url != url and full_url.startswith('http'):
                            product_links.add(full_url)

        if product_links:
            logger.info(f"[DIRECT EXTRACTION] Found {len(product_links)} potential product links directly from HTML")

        # Strategy 1: Look for embedded JSON product data (common in modern e-commerce)
        # Many sites embed product data in script tags for SEO or client-side rendering
        embedded_products = []

        # Look for JSON-LD structured data
        for script in soup.find_all('script', type='application/ld+json'):
            try:
                data = json_module.loads(script.string)
                if isinstance(data, dict) and data.get('@type') in ['Product', 'ItemList', 'ProductCollection']:
                    logger.info(f"Found JSON-LD product data")
                    embedded_products.append(data)
                elif isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and item.get('@type') in ['Product', 'ItemList']:
                            embedded_products.append(item)
            except (json_module.JSONDecodeError, TypeError):
                pass

        # Look for product data in script tags (common patterns)
        for script in soup.find_all('script'):
            if script.string:
                # Look for common product data patterns
                patterns = [
                    r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
                    r'window\.products\s*=\s*(\[.*?\]);',
                    r'"products"\s*:\s*(\[.*?\])',
                    r'productData\s*=\s*({.*?});',
                ]
                for pattern in patterns:
                    match = re.search(pattern, script.string, re.DOTALL)
                    if match:
                        try:
                            data = json_module.loads(match.group(1))
                            logger.info(f"Found embedded product data via pattern: {pattern[:30]}")
                            if isinstance(data, list) and len(data) > 0:
                                embedded_products.extend(data)
                            elif isinstance(data, dict):
                                embedded_products.append(data)
                        except json_module.JSONDecodeError:
                            pass

        if embedded_products:
            logger.info(f"Found {len(embedded_products)} embedded product entries, parsing...")
            # Try to extract product info from embedded data
            products = self._extract_from_embedded_data(embedded_products)
            if products:
                return products

        # Strategy 2: Extract just the main content area (skip header/nav/footer)
        main_content = ""

        # Try to find main product area - get ALL product containers
        product_containers = soup.find_all(['main', 'div', 'ul', 'section'], class_=re.compile(r'product|catalog|listing|grid|items|results', re.I))
        if product_containers:
            for container in product_containers:  # Get ALL matching containers
                main_content += str(container)
            logger.info(f"Extracted {len(main_content)} chars from {len(product_containers)} product containers")

        # If no product containers found, try to get body content minus scripts/styles
        if len(main_content) < 5000:
            body = soup.find('body')
            if body:
                # Remove script and style tags
                for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
                    tag.decompose()
                main_content = str(body)
                logger.info(f"Using cleaned body content: {len(main_content)} chars")

        # Strategy 3: Send more content to Claude (increased to 150k chars for 60-120 products)
        # Take content from multiple positions to catch products
        content_for_claude = ""

        if main_content and len(main_content) > 1000:
            # Use the extracted main content - increased limit for more products
            content_for_claude = main_content[:150000]
        else:
            # Fallback: take beginning, middle and end of HTML
            total_len = len(html_content)
            content_for_claude = html_content[:60000]  # First 60k
            if total_len > 120000:
                # Add middle section
                mid_start = (total_len // 2) - 30000
                content_for_claude += "\n... [MIDDLE SECTION] ...\n" + html_content[mid_start:mid_start + 60000]

        logger.info(f"Sending {len(content_for_claude)} chars to Claude for product parsing")

        # Use Claude to help parse the products intelligently
        prompt = f"""Analyze this HTML content from a children's clothing category page and extract product information.

URL: {url}

Extract as many products as you can find (aim for at least 60-120 products if available), including:
- Product name
- Price (if available, convert to numeric format)
- Brief description (if available)
- Any key features mentioned
- Product URL/link (the href to the product detail page - VERY IMPORTANT)

Look for common HTML patterns like:
- Product cards/tiles with <a> links
- Product list items
- Data attributes (data-product, data-price, data-url, etc.)
- Price elements (class names with 'price', 'cost', etc.)
- Product name elements (h2, h3, product titles)
- Links to product detail pages (usually wrapping the product card or image)

HTML content:
{content_for_claude}

IMPORTANT: Return ONLY valid JSON, no other text. Format:
{{
  "products": [
    {{
      "name": "Product Name",
      "price": 12.99,
      "description": "Brief description",
      "features": ["feature1", "feature2"],
      "url": "/product/123" or "https://example.com/product/123"
    }}
  ]
}}

The URL field is critical - extract the href link to each product's detail page.
Extract as many products as possible (up to 120). If you find fewer, extract all you can find.
If you can't find specific products, return {{"products": [], "explanation": "reason"}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=16000,  # Increased for 60-120 products
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse Claude's JSON response
            import json
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            data = json.loads(response_text)
            products = data.get("products", [])

            if products:
                logger.info(f"Successfully parsed {len(products)} products from {url}")

                # If we didn't get enough products, supplement with directly extracted links
                if len(products) < 60 and product_links:
                    existing_urls = {p.get('url', '').rstrip('/') for p in products if p.get('url')}
                    for link in product_links:
                        if link.rstrip('/') not in existing_urls and len(products) < 120:
                            products.append({
                                'name': '',  # Will be filled by deep scraper
                                'price': None,
                                'url': link,
                                'description': '',
                                'features': []
                            })
                            existing_urls.add(link.rstrip('/'))
                    logger.info(f"Supplemented with direct links: now {len(products)} products")

                return products
            else:
                explanation = data.get("explanation", "No explanation provided")
                logger.warning(f"No products found via Claude: {explanation}")

                # Use directly extracted links as fallback
                if product_links:
                    logger.info(f"Using {len(product_links)} directly extracted links as fallback")
                    return [{'name': '', 'price': None, 'url': link, 'description': '', 'features': []} for link in list(product_links)[:120]]

                # Fall back to mock data if no products found
                return self._get_mock_products()

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Claude response: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            # Use directly extracted links as fallback
            if product_links:
                logger.info(f"Using {len(product_links)} directly extracted links after JSON error")
                return [{'name': '', 'price': None, 'url': link, 'description': '', 'features': []} for link in list(product_links)[:120]]
            return self._get_mock_products()
        except Exception as e:
            logger.error(f"Error parsing products: {e}", exc_info=True)
            # Use directly extracted links as fallback
            if product_links:
                logger.info(f"Using {len(product_links)} directly extracted links after error")
                return [{'name': '', 'price': None, 'url': link, 'description': '', 'features': []} for link in list(product_links)[:120]]
            return self._get_mock_products()

    def _extract_from_embedded_data(self, data_list: List) -> List[Dict]:
        """
        Extract product information from embedded JSON data (JSON-LD, __INITIAL_STATE__, etc.)

        Args:
            data_list: List of parsed JSON objects

        Returns:
            List of product dictionaries
        """
        products = []

        for data in data_list:
            try:
                # Handle JSON-LD Product type
                if isinstance(data, dict):
                    if data.get('@type') == 'Product':
                        product = {
                            'name': data.get('name', ''),
                            'price': None,
                            'description': data.get('description', ''),
                            'features': []
                        }
                        # Extract price from offers
                        offers = data.get('offers', {})
                        if isinstance(offers, dict):
                            product['price'] = offers.get('price') or offers.get('lowPrice')
                        elif isinstance(offers, list) and offers:
                            product['price'] = offers[0].get('price')

                        if product['name']:
                            products.append(product)

                    # Handle ItemList (list of products)
                    elif data.get('@type') == 'ItemList':
                        items = data.get('itemListElement', [])
                        for item in items:
                            if isinstance(item, dict):
                                item_data = item.get('item', item)
                                product = {
                                    'name': item_data.get('name', ''),
                                    'price': None,
                                    'description': item_data.get('description', ''),
                                    'features': []
                                }
                                offers = item_data.get('offers', {})
                                if isinstance(offers, dict):
                                    product['price'] = offers.get('price') or offers.get('lowPrice')
                                if product['name']:
                                    products.append(product)

                    # Handle generic product objects (from __INITIAL_STATE__ etc.)
                    elif 'name' in data or 'title' in data or 'productName' in data:
                        product = {
                            'name': data.get('name') or data.get('title') or data.get('productName', ''),
                            'price': data.get('price') or data.get('salePrice') or data.get('finalPrice'),
                            'description': data.get('description') or data.get('shortDescription', ''),
                            'features': data.get('features', [])
                        }
                        if product['name']:
                            products.append(product)

                    # Handle nested products array
                    if 'products' in data and isinstance(data['products'], list):
                        for item in data['products']:
                            if isinstance(item, dict):
                                product = {
                                    'name': item.get('name') or item.get('title', ''),
                                    'price': item.get('price') or item.get('salePrice'),
                                    'description': item.get('description', ''),
                                    'features': item.get('features', [])
                                }
                                if product['name']:
                                    products.append(product)

            except Exception as e:
                logger.debug(f"Error extracting from embedded data: {e}")
                continue

        if products:
            logger.info(f"Extracted {len(products)} products from embedded JSON data")

        return products

    def _analyze_category(self, products: List[Dict], html_content: str) -> Dict:
        """
        Analyze category and products to extract insights.

        Args:
            products: List of parsed products
            html_content: Original HTML content

        Returns:
            Dictionary of category insights
        """
        if not products:
            return {
                "category_name": "Unknown Category",
                "total_products": 0,
                "price_range": {"min": 0, "max": 0, "avg": 0},
                "common_features": [],
                "unique_selling_points": []
            }

        # Extract cleaner content for analysis
        import re
        soup = BeautifulSoup(html_content, 'html.parser')

        # Try to get just the main content for better analysis
        main_content = ""
        product_containers = soup.find_all(['main', 'div'], class_=re.compile(r'product|catalog|listing|grid|items', re.I))
        if product_containers:
            for container in product_containers[:3]:
                main_content += str(container)

        if len(main_content) < 5000:
            main_content = html_content

        # Use Claude to analyze the ENTIRE page for comprehensive pricing
        prompt = f"""Analyze this category page HTML to extract comprehensive pricing data.

Look through ALL price elements on the page (not just a sample) and provide:
1. Minimum price found
2. Maximum price found
3. Average/typical price
4. Total number of products visible on the page
5. Category name (extract from page title, breadcrumbs, or headings)

HTML content:
{main_content[:60000]}

IMPORTANT: Return ONLY valid JSON:
{{
  "category_name": "extracted category name",
  "total_products_on_page": 50,
  "min_price": 9.99,
  "max_price": 99.99,
  "avg_price": 34.99
}}

If you can't find prices, use the sample products data as fallback."""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            page_data = json.loads(response_text)

            price_range = {
                "min": page_data.get("min_price") or 0,
                "max": page_data.get("max_price") or 0,
                "avg": page_data.get("avg_price") or 0
            }

            total_products = page_data.get("total_products_on_page", len(products))
            category_name = page_data.get("category_name", "Children's Clothing Category")

            # If Claude couldn't find prices, fall back to sample product prices
            if price_range['min'] == 0 and price_range['max'] == 0:
                prices = [p.get("price", 0) for p in products if p.get("price")]
                if prices:
                    price_range = {
                        "min": min(prices),
                        "max": max(prices),
                        "avg": sum(prices) / len(prices)
                    }
                    logger.info(f"Using sample product prices: £{price_range['min']}-£{price_range['max']}")

            logger.info(f"Page analysis: {total_products} products, £{price_range['min']:.2f}-£{price_range['max']:.2f}")

        except Exception as e:
            logger.error(f"Error analyzing full page, using sample data: {e}", exc_info=True)
            # Fallback to sample product prices
            prices = [p.get("price", 0) for p in products if p.get("price")]
            price_range = {
                "min": min(prices) if prices else 0,
                "max": max(prices) if prices else 0,
                "avg": sum(prices) / len(prices) if prices else 0
            }
            total_products = len(products)
            category_name = "Children's Clothing Category"

        # Extract common features from sample products
        all_features = []
        for product in products:
            all_features.extend(product.get("features", []))

        return {
            "category_name": category_name,
            "total_products": total_products,
            "price_range": price_range,
            "common_features": list(set(all_features))[:5],
            "unique_selling_points": [
                "Quality materials",
                "Comfortable designs",
                "Durable construction"
            ]
        }

    def _research_parent_questions(self, category_name: str) -> List[Dict]:
        """
        Research common parent questions about the product category.

        Args:
            category_name: Name of the product category

        Returns:
            List of parent questions with frequency
        """
        prompt = f"""What are the most common questions parents ask when shopping for {category_name}?

List 5-7 of the most frequently asked questions that parents have when considering purchasing {category_name}.

For each question, indicate:
1. The question itself
2. How common it is (very common, common, or occasional)
3. A brief note on where parents typically ask this (forums, reviews, etc.)

Format as a clear list."""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1000,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )

            # For demo, return sample questions
            return [
                {
                    "question": "What size should I buy for my child?",
                    "frequency": "very common",
                    "source": "product reviews, forums"
                },
                {
                    "question": "Is this product safe for sensitive skin?",
                    "frequency": "common",
                    "source": "product Q&A, parenting forums"
                },
                {
                    "question": "How durable is this product?",
                    "frequency": "common",
                    "source": "reviews, social media"
                }
            ]

        except Exception as e:
            logger.error(f"Error researching parent questions: {e}")
            return []

    def _research_seo_keywords(self, category_name: str) -> Dict:
        """
        Research SEO keywords for the category.

        Args:
            category_name: Name of the category

        Returns:
            Dictionary with primary, secondary, and long-tail keywords
        """
        return {
            "primary": [category_name.lower(), f"{category_name} online"],
            "secondary": [
                f"best {category_name}",
                f"buy {category_name}",
                f"quality {category_name}"
            ],
            "long_tail": [
                f"where to buy {category_name}",
                f"affordable {category_name}",
                f"{category_name} for kids"
            ]
        }

    def _generate_content_ideas(self, products: List[Dict], category_insights: Dict, parent_questions: List[str]) -> List[Dict]:
        """
        Generate contextual content/article ideas based on products and category.

        Uses Claude to brainstorm practical, helpful content ideas that would
        resonate with parents shopping for these products.

        Args:
            products: List of product data
            category_insights: Category analysis
            parent_questions: Common parent questions

        Returns:
            List of content idea dictionaries with title, intro, type, and metadata
        """
        category_name = category_insights.get("category_name", "children's products")
        price_range = category_insights.get("price_range", {})
        common_features = category_insights.get("common_features", [])

        # Extract age ranges from products
        age_indicators = []
        for product in products[:30]:
            name = product.get("name", "").lower()
            desc = product.get("description", "").lower()
            combined = f"{name} {desc}"

            if any(term in combined for term in ["newborn", "0-3m", "0-3 month"]):
                age_indicators.append("newborn")
            if any(term in combined for term in ["baby", "infant", "3-6m", "6-9m", "9-12m"]):
                age_indicators.append("baby")
            if any(term in combined for term in ["toddler", "12-18m", "18-24m", "2-3y"]):
                age_indicators.append("toddler")
            if any(term in combined for term in ["kids", "child", "3-4y", "4-5y", "5-6y"]):
                age_indicators.append("kids")

        # Determine primary age group
        from collections import Counter
        age_counts = Counter(age_indicators)
        primary_age = age_counts.most_common(1)[0][0] if age_counts else "baby"

        # Extract product types/themes
        product_names = [p.get("name", "") for p in products[:20]]
        product_features = []
        for p in products[:20]:
            product_features.extend(p.get("features", []))

        prompt = f"""You are a content strategist for a premium children's clothing retailer.

Based on this product category, generate 3 highly practical and helpful article/content ideas that would genuinely help parents.

CATEGORY: {category_name}
PRIMARY AGE GROUP: {primary_age}
PRICE RANGE: £{price_range.get('min', 0):.0f} - £{price_range.get('max', 0):.0f}
SAMPLE PRODUCTS: {', '.join(product_names[:10])}
COMMON FEATURES: {', '.join([str(f) for f in common_features[:8]])}
PARENT QUESTIONS: {', '.join([q.get('question', str(q)) if isinstance(q, dict) else str(q) for q in parent_questions[:5]]) if parent_questions else 'General buying advice'}

IMPORTANT GUIDELINES:
1. Focus on PRACTICAL, REAL-WORLD USEFUL content that helps parents make decisions
2. Consider safety, comfort, age-appropriateness, and seasonal factors
3. Include specific, actionable advice (e.g., temperature guidelines, sizing tips, care instructions)
4. Mix content types: buying guides, how-to guides, educational content
5. Make titles compelling and SEO-friendly
6. The intro should hook readers and preview the value they'll get

EXAMPLES of good content angles:
- For nightwear: "What temperature should my baby's room be? Sleep layering guide by age"
- For swimwear: "UV protection guide: How to keep babies safe in the sun"
- For coats: "How to layer children's clothing for cold weather without overheating"
- For shoes: "When should babies start wearing shoes? A podiatrist's guide"

Return ONLY valid JSON:
{{
  "content_ideas": [
    {{
      "id": "idea_1",
      "title": "Compelling SEO-friendly title",
      "intro": "2-3 sentence introduction that hooks the reader and previews the article's value (60-100 words)",
      "type": "buying_guide" | "how_to" | "educational" | "seasonal",
      "target_audience": "e.g., First-time parents, Parents of newborns",
      "key_topics": ["topic1", "topic2", "topic3"],
      "seo_keywords": ["keyword1", "keyword2"],
      "estimated_word_count": 1200,
      "why_this_matters": "Brief explanation of why this content would resonate with parents"
    }}
  ]
}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            response_text = response.content[0].text.strip()

            # Clean markdown if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            data = json.loads(response_text)
            content_ideas = data.get("content_ideas", [])

            logger.info(f"Generated {len(content_ideas)} content ideas for {category_name}")
            return content_ideas

        except Exception as e:
            logger.error(f"Error generating content ideas: {e}", exc_info=True)
            # Return fallback ideas
            return [
                {
                    "id": "idea_1",
                    "title": f"The Complete Guide to Choosing {category_name}",
                    "intro": f"Shopping for {category_name} can be overwhelming with so many options available. In this comprehensive guide, we'll help you understand what to look for, from materials and sizing to safety features and value for money.",
                    "type": "buying_guide",
                    "target_audience": "Parents shopping for " + primary_age + "s",
                    "key_topics": ["Materials", "Sizing", "Safety", "Value"],
                    "seo_keywords": [category_name.lower(), f"best {category_name}"],
                    "estimated_word_count": 1200,
                    "why_this_matters": "Parents need practical guidance to make informed purchasing decisions"
                },
                {
                    "id": "idea_2",
                    "title": f"How to Care for Your Child's {category_name}: Tips from the Experts",
                    "intro": f"Proper care extends the life of your child's {category_name} and keeps them looking their best. Learn the washing, drying, and storage techniques that professionals recommend.",
                    "type": "how_to",
                    "target_audience": "All parents",
                    "key_topics": ["Washing", "Drying", "Storage", "Stain removal"],
                    "seo_keywords": [f"how to wash {category_name}", f"{category_name} care"],
                    "estimated_word_count": 800,
                    "why_this_matters": "Helps parents get more value from their purchases"
                },
                {
                    "id": "idea_3",
                    "title": f"Seasonal {category_name} Essentials: What Your Child Needs",
                    "intro": f"As the seasons change, so do your child's {category_name} needs. Discover what essentials to have ready for each season and how to transition your child's wardrobe smoothly.",
                    "type": "seasonal",
                    "target_audience": "Parents planning ahead",
                    "key_topics": ["Seasonal needs", "Layering", "Planning", "Essentials"],
                    "seo_keywords": [f"seasonal {category_name}", f"{category_name} essentials"],
                    "estimated_word_count": 1000,
                    "why_this_matters": "Helps parents plan and budget for their children's needs"
                }
            ]

    def _get_mock_products(self) -> List[Dict]:
        """Get mock product data for testing (expanded to 20+ products)."""
        return [
            {
                "name": "Organic Cotton Baby Sleepsuit",
                "price": 12.99,
                "sizes": ["0-3m", "3-6m", "6-9m", "9-12m"],
                "description": "Super soft organic cotton sleepsuit with easy poppers",
                "features": ["100% organic cotton", "Temperature regulating", "Easy poppers for nappy changes", "Machine washable"]
            },
            {
                "name": "Zip-Up Baby Sleepsuit Pack of 3",
                "price": 18.99,
                "sizes": ["Newborn", "0-3m", "3-6m"],
                "description": "Convenient 3-pack with zip closure for quick changes",
                "features": ["Soft cotton blend", "Zip closure", "Value pack", "Non-slip feet"]
            },
            {
                "name": "Premium Bamboo Sleepsuit",
                "price": 15.99,
                "sizes": ["0-3m", "3-6m", "6-9m"],
                "description": "Luxurious bamboo fabric for sensitive skin",
                "features": ["Bamboo fabric", "Hypoallergenic", "Temperature control", "Soft seams"]
            },
            {
                "name": "Printed Character Sleepsuit",
                "price": 10.99,
                "sizes": ["3-6m", "6-9m", "9-12m", "12-18m"],
                "description": "Fun printed designs with popular characters",
                "features": ["Fun prints", "Cotton rich", "Easy care", "Affordable"]
            },
            {
                "name": "All-Season Sleepsuit",
                "price": 14.99,
                "sizes": ["0-3m", "3-6m", "6-9m", "9-12m", "12-18m"],
                "description": "Versatile sleepsuit suitable for all seasons",
                "features": ["Adaptive fabric", "Year-round comfort", "Durable construction", "Wide size range"]
            },
            {
                "name": "Velour Baby Sleepsuit",
                "price": 16.99,
                "description": "Soft velour fabric for ultimate comfort",
                "features": ["Plush velour", "Front zip", "Fold-over mitts", "Luxury feel"]
            },
            {
                "name": "Striped Cotton Sleepsuit",
                "price": 9.99,
                "description": "Classic striped design in soft cotton",
                "features": ["100% cotton", "Envelope neck", "Nickel-free poppers", "Easy care"]
            },
            {
                "name": "Footed Sleepsuit with Hood",
                "price": 13.99,
                "description": "Cozy hooded sleepsuit with integrated feet",
                "features": ["Hooded design", "Non-slip feet", "Two-way zip", "Extra warmth"]
            },
            {
                "name": "Sleeveless Sleep Sack",
                "price": 19.99,
                "description": "Safe sleeping bag alternative to blankets",
                "features": ["TOG rated", "Sleeveless design", "Zip closure", "Safe sleep"]
            },
            {
                "name": "Ribbed Knit Sleepsuit",
                "price": 17.99,
                "description": "Stretchy ribbed knit for growing babies",
                "features": ["Ribbed texture", "Stretchy fit", "Organic cotton", "Grows with baby"]
            },
            {
                "name": "Animal Print Sleepsuit",
                "price": 11.99,
                "description": "Adorable animal-themed sleepsuit",
                "features": ["Fun animal prints", "Soft cotton", "Easy poppers", "Machine washable"]
            },
            {
                "name": "Thermal Sleepsuit",
                "price": 14.99,
                "description": "Extra warm sleepsuit for cold nights",
                "features": ["Thermal fabric", "Heat retention", "Cozy lining", "Winter essential"]
            },
            {
                "name": "Kimono Style Sleepsuit",
                "price": 13.99,
                "description": "Easy-dress kimono wrap design",
                "features": ["No overhead dressing", "Newborn friendly", "Soft ties", "Gentle on skin"]
            },
            {
                "name": "Two-Way Zip Sleepsuit",
                "price": 12.99,
                "description": "Convenient two-way zipper for easy changes",
                "features": ["Dual zip", "Quick changes", "Soft cotton", "Practical design"]
            },
            {
                "name": "Patterned Twin Pack",
                "price": 22.99,
                "description": "Value pack with two coordinating sleepsuits",
                "features": ["2-pack value", "Mix and match", "Coordinating prints", "Great value"]
            },
            {
                "name": "Sleepsuit with Mitts",
                "price": 11.99,
                "description": "Integrated scratch mitts for newborns",
                "features": ["Fold-over mitts", "Scratch protection", "Soft seams", "Newborn essential"]
            },
            {
                "name": "Embroidered Sleepsuit",
                "price": 18.99,
                "description": "Delicate embroidered details",
                "features": ["Embroidered design", "Premium quality", "Gift-worthy", "Special occasions"]
            },
            {
                "name": "Sleepsuit with Ears",
                "price": 13.99,
                "description": "Cute hooded design with animal ears",
                "features": ["Animal ears", "Hood included", "Adorable design", "Photo-ready"]
            },
            {
                "name": "Waffle Knit Sleepsuit",
                "price": 15.99,
                "description": "Textured waffle weave fabric",
                "features": ["Waffle texture", "Breathable", "Soft cotton", "Modern design"]
            },
            {
                "name": "Sleepsuit Gift Set",
                "price": 29.99,
                "description": "Boxed set of 3 sleepsuits with accessories",
                "features": ["3-piece set", "Gift box", "Coordinated items", "Perfect gift"]
            }
        ]

    def _get_mock_insights(self) -> Dict:
        """Get mock category insights for testing."""
        return {
            "category_name": "Baby Sleepsuits",
            "total_products": 45,
            "price_range": {
                "min": 8.99,
                "max": 24.99,
                "avg": 14.50
            },
            "common_features": [
                "Temperature regulation (67% of products)",
                "Easy nappy change design (54% of products)",
                "Soft seam construction (89% of products)",
                "Machine washable (100% of products)",
                "Organic/natural fabrics (34% of products)"
            ],
            "unique_selling_points": [
                "Wide range of organic cotton options",
                "Size range from premature to 24 months",
                "Award-winning comfort designs",
                "Hypoallergenic options for sensitive skin",
                "Value multi-packs available"
            ],
            "price_segments": {
                "budget": "£8.99-£11.99 (basic cotton sleepsuits)",
                "mid_range": "£12.99-£16.99 (organic/premium cotton)",
                "premium": "£17.99-£24.99 (bamboo/luxury fabrics)"
            }
        }
