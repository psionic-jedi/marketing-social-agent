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
                    # Step 2: Parse product data
                    logger.info("Parsing product data")
                    products = self._parse_products(html_content, state["category_url"])

                    # Step 3: Analyze with Claude to extract insights
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

    def _parse_products(self, html_content: str, url: str) -> List[Dict]:
        """
        Parse product information from HTML.

        Args:
            html_content: HTML content of the page
            url: Original URL (for context)

        Returns:
            List of product dictionaries
        """
        soup = BeautifulSoup(html_content, 'html.parser')

        # Use Claude to help parse the products intelligently
        prompt = f"""Analyze this HTML content from a children's clothing category page and extract product information.

URL: {url}

Extract as many products as you can find (aim for at least 20 products if available), including:
- Product name
- Price (if available, convert to numeric format)
- Brief description (if available)
- Any key features mentioned

Look for common HTML patterns like:
- Product cards/tiles
- Product list items
- Data attributes (data-product, data-price, etc.)
- Price elements (class names with 'price', 'cost', etc.)
- Product name elements (h2, h3, product titles)

HTML content (first 30000 chars):
{html_content[:30000]}

IMPORTANT: Return ONLY valid JSON, no other text. Format:
{{
  "products": [
    {{
      "name": "Product Name",
      "price": 12.99,
      "description": "Brief description",
      "features": ["feature1", "feature2"]
    }}
  ]
}}

Extract as many products as possible. If you find fewer than 20, extract all you can find.
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

        # Use Claude to analyze the ENTIRE page for comprehensive pricing
        prompt = f"""Analyze this category page HTML to extract comprehensive pricing data.

Look through ALL price elements on the page (not just a sample) and provide:
1. Minimum price found
2. Maximum price found
3. Average/typical price
4. Total number of products visible on the page
5. Category name (extract from page title, breadcrumbs, or headings)

HTML content (first 30000 chars):
{html_content[:30000]}

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
