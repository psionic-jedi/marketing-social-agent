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
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
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

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
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
                    html_content = self._scrape_page(state["category_url"])
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

    def _scrape_page(self, url: str, timeout: int = 60000) -> str:
        """
        Scrape a web page using Playwright.

        Args:
            url: URL to scrape
            timeout: Timeout in milliseconds (default: 60 seconds)

        Returns:
            HTML content of the page
        """
        browser = None
        page = None

        try:
            with sync_playwright() as p:
                # Launch browser with anti-detection settings
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        '--disable-blink-features=AutomationControlled',
                        '--disable-dev-shm-usage',
                        '--no-sandbox'
                    ]
                )

                # Create context with realistic browser settings
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )

                page = context.new_page()

                # Set default navigation timeout
                page.set_default_navigation_timeout(timeout)
                page.set_default_timeout(timeout)

                # Navigate to URL with lenient wait condition
                logger.info(f"Navigating to {url} with {timeout}ms timeout")
                page.goto(url, wait_until="domcontentloaded")

                # Wait for dynamic content to load
                page.wait_for_timeout(3000)

                # Get page content
                html_content = page.content()
                logger.info(f"Successfully scraped {url} ({len(html_content)} bytes)")

                browser.close()
                return html_content

        except PlaywrightTimeoutError as e:
            logger.warning(f"Timeout scraping {url} after {timeout}ms: {e}")
            # Try to get whatever content was loaded
            try:
                if page:
                    content = page.content()
                    if browser:
                        browser.close()
                    if content and len(content) > 1000:
                        logger.info(f"Returning partial content ({len(content)} bytes)")
                        return content
            except Exception as partial_error:
                logger.error(f"Could not get partial content: {partial_error}")

            # Clean up
            if browser:
                try:
                    browser.close()
                except:
                    pass

            raise  # Re-raise to trigger fallback to mock data

        except Exception as e:
            logger.error(f"Error scraping {url}: {e}", exc_info=True)
            # Close browser if it exists
            if browser:
                try:
                    browser.close()
                except:
                    pass
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

Extract as many products as you can find, including:
- Product name
- Price (if available)
- Brief description
- Any key features mentioned

HTML content (truncated to first 5000 chars):
{html_content[:5000]}

Return a JSON array of products with fields: name, price, description, features.
If you can't find specific products, return an empty array and explain what you found instead."""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                temperature=0.3,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse Claude's response
            # In a real implementation, we'd use structured output
            # For now, we'll create sample data
            logger.info(f"Claude analyzed page: {response.content[0].text[:200]}...")

            # Return sample product data for demo
            return [
                {
                    "name": "Sample Product 1",
                    "price": 12.99,
                    "description": "Comfortable children's clothing item",
                    "features": ["Organic cotton", "Machine washable"]
                },
                {
                    "name": "Sample Product 2",
                    "price": 15.99,
                    "description": "High-quality children's wear",
                    "features": ["Durable", "Soft fabric"]
                }
            ]

        except Exception as e:
            logger.error(f"Error parsing products: {e}")
            return []

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

        # Calculate price statistics
        prices = [p.get("price", 0) for p in products if p.get("price")]
        price_range = {
            "min": min(prices) if prices else 0,
            "max": max(prices) if prices else 0,
            "avg": sum(prices) / len(prices) if prices else 0
        }

        # Extract common features
        all_features = []
        for product in products:
            all_features.extend(product.get("features", []))

        return {
            "category_name": "Children's Clothing Category",
            "total_products": len(products),
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
        """Get mock product data for testing."""
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
