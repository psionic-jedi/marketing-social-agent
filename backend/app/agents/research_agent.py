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

    def __init__(self, use_mock_data: bool = None):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        # Use config setting if not explicitly provided
        if use_mock_data is None:
            self.use_mock_data = not settings.use_real_scraping
        else:
            self.use_mock_data = use_mock_data

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

        try:
            # Use mock data in development or if scraping fails
            if self.use_mock_data:
                logger.info("Using mock data for research (development mode)")
                products = self._get_mock_products()
                category_insights = self._get_mock_insights()
            else:
                # Step 1: Scrape category page (with 60s timeout)
                logger.info(f"Scraping category page: {state['category_url']}")
                try:
                    html_content = await self._scrape_page(state["category_url"])
                except Exception as scrape_error:
                    logger.warning(f"Scraping failed, falling back to mock data: {scrape_error}")
                    products = self._get_mock_products()
                    category_insights = self._get_mock_insights()
                else:
                    # Step 2: Parse product data from listing page
                    logger.info("Parsing product data from listing page")
                    products = self._parse_products(html_content, state["category_url"])

                    # Step 3: Deep scrape product detail pages for full descriptions
                    product_urls = [p.get('url') for p in products if p.get('url')]
                    if product_urls:
                        logger.info(f"Found {len(product_urls)} product URLs, starting deep scrape...")

                        # Update state to show deep scraping phase
                        state["current_step"] = "deep_scraping"
                        state["progress_percentage"] = 12

                        detailed_products = await self._scrape_product_details(
                            product_urls,
                            state["category_url"],
                            max_products=35,
                            state=state  # Pass state for progress updates
                        )

                        # Merge detailed data with listing data
                        if detailed_products:
                            logger.info(f"Merging {len(detailed_products)} detailed products with listing data")
                            products = self._merge_product_data(products, detailed_products)

                        # Return to research step after deep scraping
                        state["current_step"] = "research"
                    else:
                        logger.warning("No product URLs found, skipping deep scrape")

                    # Step 4: Analyze with Claude to extract insights
                    logger.info("Analyzing products with Claude")
                    category_insights = self._analyze_category(products, html_content)

            # Step 4: Research parent questions
            logger.info("Researching parent questions")
            parent_questions = self._research_parent_questions(
                category_insights.get("category_name", "children's products")
            )

            # Step 5: SEO keyword research
            logger.info("Conducting SEO research")
            seo_keywords = self._research_seo_keywords(
                category_insights.get("category_name", "")
            )

            # Compile research data
            research_data = {
                "products": products,
                "category_insights": category_insights,
                "parent_questions": parent_questions,
                "seo_keywords": seo_keywords,
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

                # Scroll the page to load more products (many sites lazy-load)
                logger.info(f"[SCRAPER] Scrolling page to load more products...")
                for i in range(3):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await page.wait_for_timeout(1000)
                logger.info(f"[SCRAPER] Page scrolling complete")

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

    async def _scrape_product_details(self, product_urls: List[str], base_url: str, max_products: int = 35, state: Dict = None) -> List[Dict]:
        """
        Scrape individual product detail pages to get full descriptions.

        Args:
            product_urls: List of product URLs to scrape
            base_url: Base URL for resolving relative URLs
            max_products: Maximum number of products to scrape (default: 35)
            state: Campaign state for progress updates

        Returns:
            List of product detail dictionaries
        """
        from urllib.parse import urljoin

        product_details = []
        urls_to_scrape = product_urls[:max_products]
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
                        # Update progress (deep scraping runs from 12% to 25% of total)
                        if state:
                            progress = 12 + (13 * (i / total_products))  # 12% to 25%
                            state["progress_percentage"] = round(progress, 1)
                            state["current_step"] = f"deep_scraping ({i+1}/{total_products})"

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

        soup = BeautifulSoup(html_content, 'html.parser')

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

        # Try to find main product area
        product_containers = soup.find_all(['main', 'div'], class_=re.compile(r'product|catalog|listing|grid|items', re.I))
        if product_containers:
            for container in product_containers[:3]:  # Take first few matching containers
                main_content += str(container)
            logger.info(f"Extracted {len(main_content)} chars from product containers")

        # If no product containers found, try to get body content minus scripts/styles
        if len(main_content) < 5000:
            body = soup.find('body')
            if body:
                # Remove script and style tags
                for tag in body.find_all(['script', 'style', 'nav', 'header', 'footer', 'noscript']):
                    tag.decompose()
                main_content = str(body)
                logger.info(f"Using cleaned body content: {len(main_content)} chars")

        # Strategy 3: Send more content to Claude (increased from 30k to 80k chars)
        # Take content from multiple positions to catch products
        content_for_claude = ""

        if main_content and len(main_content) > 1000:
            # Use the extracted main content
            content_for_claude = main_content[:80000]
        else:
            # Fallback: take beginning, middle and end of HTML
            total_len = len(html_content)
            content_for_claude = html_content[:40000]  # First 40k
            if total_len > 80000:
                # Add middle section
                mid_start = (total_len // 2) - 20000
                content_for_claude += "\n... [MIDDLE SECTION] ...\n" + html_content[mid_start:mid_start + 40000]

        logger.info(f"Sending {len(content_for_claude)} chars to Claude for product parsing")

        # Use Claude to help parse the products intelligently
        prompt = f"""Analyze this HTML content from a children's clothing category page and extract product information.

URL: {url}

Extract as many products as you can find (aim for at least 20-35 products if available), including:
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
Extract as many products as possible (up to 35). If you find fewer, extract all you can find.
If you can't find specific products, return {{"products": [], "explanation": "reason"}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
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
                return products
            else:
                explanation = data.get("explanation", "No explanation provided")
                logger.warning(f"No products found: {explanation}")
                # Fall back to mock data if no products found
                return self._get_mock_products()

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from Claude response: {e}")
            logger.debug(f"Response was: {response_text[:500]}")
            return self._get_mock_products()
        except Exception as e:
            logger.error(f"Error parsing products: {e}", exc_info=True)
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
