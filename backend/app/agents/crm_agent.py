"""
CRM Agent - Creates email marketing campaigns using MJML.

Responsibilities:
1. Design welcome email series
2. Create promotional email campaigns
3. Generate cart abandonment emails
4. Build customer segmentation strategy
5. Create email automation workflows
6. Generate MJML templates with HTML preview
"""
import logging
from typing import Dict, List
from anthropic import Anthropic
from mjml import mjml_to_html

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


def convert_mjml_to_html(mjml_content: str) -> str:
    """
    Convert MJML template to HTML.

    Args:
        mjml_content: MJML template string

    Returns:
        HTML string or None on error
    """
    try:
        result = mjml_to_html(mjml_content)
        if result.html:
            return result.html
        else:
            logger.warning(f"MJML conversion returned no HTML: {result.errors}")
            return None
    except Exception as e:
        logger.error(f"Failed to convert MJML to HTML: {e}")
        return None


class CRMAgent:
    """CRM agent for creating email marketing campaigns and automation."""

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the CRM agent workflow.

        Args:
            state: Current campaign state

        Returns:
            Updated state with crm_plan
        """
        logger.info(f"CRM Agent starting for campaign {state['campaign_id']}")

        state["current_step"] = "crm"
        state["progress_percentage"] = 85

        try:
            research_data = state.get("research_data")
            content_outputs = state.get("content_outputs")

            if not research_data or not content_outputs:
                raise ValueError("Missing research data or content outputs")

            category_name = research_data.get("category_insights", {}).get("category_name", "Products")

            # Generate email campaigns
            logger.info("Generating welcome email series")
            welcome_series = self._generate_welcome_series(research_data, content_outputs)

            logger.info("Creating promotional campaigns")
            promotional_campaigns = self._generate_promotional_campaigns(research_data, content_outputs)

            logger.info("Generating cart abandonment email")
            cart_abandonment = self._generate_cart_abandonment(category_name, content_outputs)

            logger.info("Creating customer segmentation")
            segmentation_strategy = self._create_segmentation_strategy(research_data)

            logger.info("Building automation workflows")
            automation_workflows = self._create_automation_workflows()

            # Compile CRM plan
            crm_plan = {
                "welcome_series": welcome_series,
                "promotional_campaigns": promotional_campaigns,
                "cart_abandonment": cart_abandonment,
                "segmentation_strategy": segmentation_strategy,
                "automation_workflows": automation_workflows,
                "email_frequency": self._generate_frequency_recommendations(),
                "best_practices": self._generate_best_practices()
            }

            state["crm_plan"] = crm_plan
            state["progress_percentage"] = 90
            logger.info("CRM Agent completed successfully")

            return state

        except Exception as e:
            error_msg = f"CRM Agent failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["progress_percentage"] = 90
            return state

    def _generate_welcome_series(self, research_data: Dict, content_outputs: Dict) -> List[Dict]:
        """Generate 3-email welcome series with MJML templates featuring specific brands and products."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        hero_section = content_outputs.get("hero_section", {})
        features = content_outputs.get("features", [])
        products = research_data.get("products", [])

        # Extract specific brands and featured products
        brands = self._extract_brands(products)
        top_brands = brands[:3] if brands else ["Designer"]
        featured_products = self._get_featured_products(products, 3)

        welcome_emails = []

        # Email 1: Welcome + Featured Brands & Products
        mjml_welcome = self._generate_mjml_welcome_email_with_products(
            category_name, hero_section, top_brands, featured_products, features[:3]
        )
        welcome_emails.append({
            "email_number": 1,
            "send_timing": "Immediately after signup",
            "subject_line": f"Welcome! Discover {', '.join(top_brands[:2])} & More {category_name}",
            "preheader": f"Shop {top_brands[0]} and other designer {category_name.lower()} ✨",
            "content_blocks": [
                {
                    "type": "hero",
                    "headline": f"Welcome to Our Family!",
                    "subheadline": hero_section.get("subheadline", ""),
                    "image": "welcome-hero.jpg",
                    "cta": "Start Shopping",
                    "cta_url": "/shop"
                },
                {
                    "type": "featured_brands",
                    "brands": top_brands
                },
                {
                    "type": "featured_products",
                    "products": featured_products
                },
                {
                    "type": "features",
                    "features": features[:3]
                }
            ],
            "mjml_template": mjml_welcome,
            "html_template": convert_mjml_to_html(mjml_welcome)
        })

        # Email 2: Feature Spotlight with Specific Products
        feature_highlights = features[:3] if features else []
        mjml_educational = self._generate_mjml_feature_spotlight_email(
            category_name, feature_highlights, featured_products, research_data
        )
        welcome_emails.append({
            "email_number": 2,
            "send_timing": "2 days after signup",
            "subject_line": f"Why Parents Love Our {category_name}: {feature_highlights[0]['title'] if feature_highlights else 'Quality & Style'}",
            "preheader": f"Discover what makes our {category_name.lower()} special",
            "content_blocks": [
                {
                    "type": "header",
                    "headline": f"Why Our {category_name} Stand Out",
                    "image": "features-header.jpg"
                },
                {
                    "type": "feature_spotlight",
                    "features": feature_highlights
                },
                {
                    "type": "featured_products",
                    "products": featured_products
                },
                {
                    "type": "cta",
                    "text": "Shop The Collection",
                    "url": "/shop"
                }
            ],
            "mjml_template": mjml_educational,
            "html_template": convert_mjml_to_html(mjml_educational)
        })

        # Email 3: Brand Spotlight with Discount
        spotlight_brand = top_brands[0] if top_brands else "Designer"
        brand_products = [p for p in products if p.get('brand', '').lower() == spotlight_brand.lower()][:3]
        if not brand_products:
            brand_products = featured_products

        mjml_offer = self._generate_mjml_brand_spotlight_offer(
            spotlight_brand, brand_products, category_name, "WELCOME15"
        )
        welcome_emails.append({
            "email_number": 3,
            "send_timing": "5 days after signup",
            "subject_line": f"🎁 15% Off {spotlight_brand} {category_name} - Your Welcome Gift",
            "preheader": f"Exclusive: Save on {spotlight_brand} and designer {category_name.lower()}",
            "content_blocks": [
                {
                    "type": "brand_spotlight",
                    "brand": spotlight_brand,
                    "products": brand_products
                },
                {
                    "type": "offer",
                    "headline": "Welcome Gift: 15% Off",
                    "code": "WELCOME15",
                    "cta": "Shop Now",
                    "cta_url": "/shop?discount=WELCOME15"
                }
            ],
            "mjml_template": mjml_offer,
            "html_template": convert_mjml_to_html(mjml_offer)
        })

        return welcome_emails

    def _get_featured_products(self, products: List[Dict], count: int = 3) -> List[Dict]:
        """Get featured products with clean data for email display."""
        featured = []
        for product in products[:count * 2]:  # Look at more products to filter
            if product.get('name') and product.get('price'):
                brand = product.get('brand') or 'Designer'
                # Handle empty image URLs with branded placeholder
                image_url = product.get('image_url')
                if not image_url or str(image_url).strip() == '':
                    brand_initial = brand[0].upper() if brand else 'C'
                    image_url = f"https://via.placeholder.com/200x250/f5f0eb/C5A572?text={brand_initial}"

                featured.append({
                    "name": product.get('name', 'Product')[:50],  # Truncate long names
                    "brand": brand,
                    "price": product.get('price', 0),
                    "image_url": image_url,
                    "url": product.get('url') or '/shop'
                })
            if len(featured) >= count:
                break
        return featured

    def _generate_promotional_campaigns(self, research_data: Dict, content_outputs: Dict) -> List[Dict]:
        """Generate promotional email campaigns with specific brands and features."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        products = research_data.get("products", [])
        features = content_outputs.get("features", [])

        # Extract specific data for campaigns
        brands = self._extract_brands(products)
        top_brands = brands[:4] if brands else ["Designer"]
        featured_products = self._get_featured_products(products, 4)

        # Get price range for sale messaging
        price_range = research_data.get("category_insights", {}).get("price_range", {})
        min_price = price_range.get("min", 20)
        max_price = price_range.get("max", 200)

        # Extract key features for campaign messaging
        feature_titles = [f.get("title", "") for f in features[:3]] if features else ["Quality", "Comfort", "Style"]

        campaigns = []

        # Campaign 1: Brand Spotlight - New Arrivals from Top Brand
        spotlight_brand = top_brands[0] if top_brands else "Designer"
        brand_products = [p for p in products if p.get('brand', '').lower() == spotlight_brand.lower()][:4]
        if not brand_products:
            brand_products = featured_products[:4]

        mjml_brand = self._generate_mjml_brand_campaign(spotlight_brand, brand_products, category_name)
        campaigns.append({
            "campaign_name": f"{spotlight_brand} New Arrivals",
            "send_date": "Monthly - 1st week",
            "subject_line": f"Just In: New {spotlight_brand} {category_name} You'll Love",
            "preheader": f"Discover the latest {spotlight_brand} pieces for your little one",
            "target_segment": f"{spotlight_brand} Brand Fans + {category_name} Browsers",
            "goal": f"Drive sales of {spotlight_brand} products",
            "featured_products": brand_products,
            "mjml_template": mjml_brand,
            "html_template": convert_mjml_to_html(mjml_brand)
        })

        # Campaign 2: Feature-Focused Campaign
        key_feature = features[0] if features else {"title": "Premium Quality", "description": "Crafted with care"}
        mjml_feature = self._generate_mjml_feature_campaign(key_feature, featured_products, category_name)
        campaigns.append({
            "campaign_name": f"{key_feature.get('title', 'Quality')} Collection",
            "send_date": "Monthly - 2nd week",
            "subject_line": f"{key_feature.get('title', 'Premium Quality')}: {category_name} That Last",
            "preheader": key_feature.get('description', 'Discover our collection')[:60],
            "target_segment": "Quality-focused shoppers + Previous buyers",
            "goal": f"Highlight {key_feature.get('title', 'quality')} as key differentiator",
            "featured_feature": key_feature,
            "featured_products": featured_products,
            "mjml_template": mjml_feature,
            "html_template": convert_mjml_to_html(mjml_feature)
        })

        # Campaign 3: Multi-Brand Showcase
        if len(top_brands) >= 2:
            multi_brand_products = []
            for brand in top_brands[:3]:
                brand_p = [p for p in products if p.get('brand', '').lower() == brand.lower()]
                if brand_p:
                    multi_brand_products.append(brand_p[0])
            if not multi_brand_products:
                multi_brand_products = featured_products[:3]

            mjml_multi = self._generate_mjml_multi_brand_campaign(top_brands[:3], multi_brand_products, category_name)
            campaigns.append({
                "campaign_name": "Designer Brands Showcase",
                "send_date": "Monthly - 3rd week",
                "subject_line": f"Shop {', '.join(top_brands[:2])} & More {category_name}",
                "preheader": f"Exclusive designer {category_name.lower()} from top brands",
                "target_segment": "Luxury Buyers + Brand-conscious shoppers",
                "goal": "Showcase brand variety and drive high-value sales",
                "featured_brands": top_brands[:3],
                "featured_products": multi_brand_products,
                "mjml_template": mjml_multi,
                "html_template": convert_mjml_to_html(mjml_multi)
            })

        # Campaign 4: Price-Point Campaign (Gift Guide style)
        mid_price = (min_price + max_price) / 2
        price_products = sorted(products, key=lambda x: x.get('price', 0))
        under_price_products = [p for p in price_products if p.get('price', 0) < mid_price][:3]
        if not under_price_products:
            under_price_products = featured_products[:3]

        mjml_price = self._generate_mjml_price_campaign(mid_price, under_price_products, category_name)
        campaigns.append({
            "campaign_name": f"{category_name} Under £{mid_price:.0f}",
            "send_date": "Monthly - 4th week",
            "subject_line": f"Beautiful {category_name} Under £{mid_price:.0f} 🎁",
            "preheader": f"Designer quality doesn't have to break the bank",
            "target_segment": "Value Seekers + Gift shoppers",
            "goal": "Drive conversions at accessible price points",
            "price_threshold": mid_price,
            "featured_products": under_price_products,
            "mjml_template": mjml_price,
            "html_template": convert_mjml_to_html(mjml_price)
        })

        # Campaign 5: Seasonal Sale with specific products
        sale_products = featured_products[:4]
        mjml_sale = self._generate_mjml_sale_campaign(sale_products, category_name)
        campaigns.append({
            "campaign_name": "Seasonal Sale Event",
            "send_date": "Quarterly",
            "subject_line": f"Up to 30% Off {spotlight_brand}, {top_brands[1] if len(top_brands) > 1 else 'Designer'} & More {category_name}",
            "preheader": f"Limited time: Designer {category_name.lower()} at exceptional prices",
            "target_segment": "All active subscribers + Previous buyers",
            "goal": "Drive volume sales and clear seasonal inventory",
            "featured_brands": top_brands[:3],
            "featured_products": sale_products,
            "mjml_template": mjml_sale,
            "html_template": convert_mjml_to_html(mjml_sale)
        })

        return campaigns

    def _generate_cart_abandonment(self, category_name: str, content_outputs: Dict) -> Dict:
        """Generate cart abandonment email series."""
        return {
            "series_name": "Cart Abandonment Recovery",
            "emails": [
                {
                    "email_number": 1,
                    "send_timing": "1 hour after abandonment",
                    "subject_line": "You left something behind! 🛒",
                    "preheader": "Your items are waiting for you",
                    "discount_offered": False,
                    "conversion_rate_expected": "8-12%"
                },
                {
                    "email_number": 2,
                    "send_timing": "24 hours after abandonment",
                    "subject_line": f"Still thinking about these {category_name}?",
                    "preheader": "We saved them for you + here's 10% off!",
                    "discount_offered": True,
                    "discount_code": "CART10",
                    "conversion_rate_expected": "5-8%"
                },
                {
                    "email_number": 3,
                    "send_timing": "72 hours after abandonment",
                    "subject_line": "Last chance! Your cart expires soon",
                    "preheader": "Items selling fast - complete your order now",
                    "discount_offered": True,
                    "discount_code": "LASTCHANCE15",
                    "conversion_rate_expected": "3-5%"
                }
            ],
            "total_expected_recovery_rate": "16-25%",
            "mjml_template": self._generate_mjml_cart_abandonment(),
            "html_template": convert_mjml_to_html(self._generate_mjml_cart_abandonment())
        }

    def _create_segmentation_strategy(self, research_data: Dict) -> Dict:
        """Create intelligent customer segmentation strategy based on category data."""
        category_insights = research_data.get("category_insights", {})
        products = research_data.get("products", [])

        category_name = category_insights.get("category_name", "Products")
        price_range = category_insights.get("price_range", {})
        min_price = price_range.get("min", 0)
        max_price = price_range.get("max", 500)

        # Detect gender from category name
        gender = self._detect_gender(category_name)

        # Detect age group from category name and products
        age_group = self._detect_age_group(category_name, products)

        # Detect product type
        product_type = self._detect_product_type(category_name)

        # Extract top brands from products
        brands = self._extract_brands(products)
        top_brands = brands[:3] if brands else ["Designer"]

        # Calculate price tiers
        luxury_threshold = min_price + (max_price - min_price) * 0.7
        mid_threshold = min_price + (max_price - min_price) * 0.4

        segments = []

        # 1. Category-specific purchase history segment
        segments.append({
            "segment_name": f"Previous {category_name} Buyers",
            "criteria": f"Purchased from {category_name} category in last 12 months",
            "klaviyo_definition": f"Has placed order where Item Category = '{category_name}' at least 1 time in the last 365 days",
            "email_frequency": "2 times per week",
            "content_strategy": f"New {category_name} arrivals, restocks of previously viewed items, complementary products",
            "priority": "High"
        })

        # 2. Gender-specific segment (if applicable)
        if gender:
            segments.append({
                "segment_name": f"{gender} Clothing Shoppers",
                "criteria": f"Purchased any {gender.lower()} items in last 12 months",
                "klaviyo_definition": f"Has placed order where Item Gender = '{gender}' at least 1 time in the last 365 days",
                "email_frequency": "2 times per week",
                "content_strategy": f"All new {gender.lower()} arrivals across categories, gender-specific promotions",
                "priority": "High"
            })

        # 3. Age group segment (if applicable)
        if age_group:
            segments.append({
                "segment_name": f"{age_group} Age Group Parents",
                "criteria": f"Purchased items in {age_group.lower()} age range",
                "klaviyo_definition": f"Has placed order where Item Age Group = '{age_group}' at least 1 time in the last 365 days",
                "email_frequency": "1-2 times per week",
                "content_strategy": f"Age-appropriate products, size-up reminders, developmental milestone content",
                "priority": "Medium"
            })

        # 4. Luxury buyers segment
        segments.append({
            "segment_name": "Luxury Buyers",
            "criteria": f"Average order value > £{luxury_threshold:.0f} OR purchased premium brands",
            "klaviyo_definition": f"Average Order Value >= {luxury_threshold:.0f} OR Has placed order where Brand in ['{top_brands[0]}'] at least 1 time",
            "email_frequency": "2-3 times per week",
            "content_strategy": "Exclusive previews, VIP early access, premium brand launches, white-glove service messaging",
            "priority": "High"
        })

        # 5. Brand affinity segments (top 2 brands)
        for brand in top_brands[:2]:
            segments.append({
                "segment_name": f"{brand} Brand Fans",
                "criteria": f"Purchased {brand} products 2+ times OR browsed {brand} 5+ times",
                "klaviyo_definition": f"Has placed order where Brand = '{brand}' at least 2 times OR Has viewed product where Brand = '{brand}' at least 5 times in the last 90 days",
                "email_frequency": "When brand has new arrivals/restocks",
                "content_strategy": f"New {brand} releases, {brand} restocks, brand-specific promotions",
                "priority": "Medium"
            })

        # 6. Price-sensitive segment
        segments.append({
            "segment_name": "Value Seekers",
            "criteria": f"Average order value < £{mid_threshold:.0f} OR primarily purchases sale items",
            "klaviyo_definition": f"Average Order Value < {mid_threshold:.0f} OR Has placed order where Item On Sale = true at least 2 times",
            "email_frequency": "1-2 times per week",
            "content_strategy": "Sale alerts, clearance events, outlet items, discount codes",
            "priority": "Medium"
        })

        # 7. Cross-sell opportunity segment
        complementary = self._get_complementary_categories(product_type)
        if complementary:
            segments.append({
                "segment_name": f"{category_name} Cross-Sell Opportunity",
                "criteria": f"Purchased {category_name} but NOT {complementary} in last 6 months",
                "klaviyo_definition": f"Has placed order where Category = '{category_name}' at least 1 time AND Has NOT placed order where Category = '{complementary}' in the last 180 days",
                "email_frequency": "1 time per week",
                "content_strategy": f"Introduce {complementary.lower()} to complete the look, bundle offers",
                "priority": "Medium"
            })

        # 8. Lapsed category buyers
        segments.append({
            "segment_name": f"Lapsed {category_name} Buyers",
            "criteria": f"Purchased {category_name} 6-12 months ago, no recent purchase",
            "klaviyo_definition": f"Has placed order where Category = '{category_name}' at least 1 time between 180 and 365 days ago AND Has NOT placed order in the last 180 days",
            "email_frequency": "1 time per week",
            "content_strategy": f"'We miss you' campaigns, what's new in {category_name}, comeback discount",
            "priority": "Low"
        })

        return {
            "segments": segments,
            "category_context": {
                "category": category_name,
                "detected_gender": gender,
                "detected_age_group": age_group,
                "product_type": product_type,
                "top_brands": top_brands,
                "price_tiers": {
                    "luxury": f"£{luxury_threshold:.0f}+",
                    "mid_range": f"£{mid_threshold:.0f}-£{luxury_threshold:.0f}",
                    "value": f"Under £{mid_threshold:.0f}"
                }
            },
            "personalization_tactics": [
                f"Product recommendations based on {category_name} browse history",
                f"Similar {product_type.lower()} from other brands they may like",
                "Size predictions based on previous purchases",
                f"'{gender} new arrivals' personalized sections" if gender else "Gender-specific sections",
                "Price-appropriate recommendations based on purchase history",
                "Brand affinity-based product suggestions"
            ]
        }

    def _detect_gender(self, category_name: str) -> str:
        """Detect gender from category name."""
        name_lower = category_name.lower()
        if any(word in name_lower for word in ['boy', 'boys', 'male']):
            return "Boys"
        elif any(word in name_lower for word in ['girl', 'girls', 'female']):
            return "Girls"
        elif any(word in name_lower for word in ['baby', 'infant', 'newborn']):
            return "Baby"
        elif any(word in name_lower for word in ['unisex', 'neutral']):
            return "Unisex"
        return None

    def _detect_age_group(self, category_name: str, products: List[Dict]) -> str:
        """Detect age group from category and product data."""
        name_lower = category_name.lower()

        # Check category name first
        if any(word in name_lower for word in ['baby', 'infant', 'newborn', '0-12', '0-24']):
            return "Baby (0-2 years)"
        elif any(word in name_lower for word in ['toddler', '1-3', '2-4']):
            return "Toddler (1-4 years)"
        elif any(word in name_lower for word in ['kid', 'kids', 'child', 'children', '4-12']):
            return "Kids (4-12 years)"
        elif any(word in name_lower for word in ['teen', 'teenager', 'junior', '12-16']):
            return "Teen (12-16 years)"

        # Check product names/descriptions for age hints
        for product in products[:10]:
            name = product.get('name', '').lower()
            if any(word in name for word in ['baby', 'infant']):
                return "Baby (0-2 years)"
            elif any(word in name for word in ['toddler']):
                return "Toddler (1-4 years)"

        return None

    def _detect_product_type(self, category_name: str) -> str:
        """Detect product type from category name."""
        name_lower = category_name.lower()

        product_types = {
            "Bags": ['bag', 'bags', 'backpack', 'rucksack'],
            "Clothing": ['clothing', 'clothes', 'wear', 'outfit', 'dress', 'shirt', 'trouser', 'jean'],
            "Shoes": ['shoe', 'shoes', 'boot', 'boots', 'trainer', 'sneaker', 'sandal'],
            "Accessories": ['accessory', 'accessories', 'hat', 'scarf', 'glove', 'belt'],
            "Outerwear": ['coat', 'jacket', 'outerwear', 'parka', 'puffer'],
            "Sleepwear": ['sleep', 'pyjama', 'pajama', 'nightwear', 'sleepsuit'],
            "Swimwear": ['swim', 'swimwear', 'beach', 'pool']
        }

        for ptype, keywords in product_types.items():
            if any(kw in name_lower for kw in keywords):
                return ptype

        return "Products"

    def _extract_brands(self, products: List[Dict]) -> List[str]:
        """Extract unique brands from products."""
        brands = []
        seen = set()

        for product in products:
            brand = product.get('brand', '')
            if brand and brand.lower() not in seen:
                seen.add(brand.lower())
                brands.append(brand)

        return brands[:10]

    def _get_complementary_categories(self, product_type: str) -> str:
        """Get complementary category for cross-sell."""
        complements = {
            "Bags": "Accessories",
            "Clothing": "Shoes",
            "Shoes": "Clothing",
            "Accessories": "Bags",
            "Outerwear": "Accessories",
            "Sleepwear": "Clothing",
            "Swimwear": "Accessories"
        }
        return complements.get(product_type)

    def _create_automation_workflows(self) -> List[Dict]:
        """Create email automation workflows."""
        return [
            {
                "workflow_name": "Welcome Series",
                "trigger": "New subscriber",
                "email_count": 3,
                "duration": "7 days",
                "goal": "Onboard new subscribers and drive first purchase"
            },
            {
                "workflow_name": "Post-Purchase",
                "trigger": "Order completed",
                "email_count": 4,
                "duration": "30 days",
                "emails": [
                    {"day": 1, "type": "Order confirmation with care instructions"},
                    {"day": 7, "type": "Product review request"},
                    {"day": 14, "type": "Cross-sell recommendations"},
                    {"day": 30, "type": "Replenishment reminder"}
                ]
            },
            {
                "workflow_name": "Browse Abandonment",
                "trigger": "Viewed product but didn't add to cart",
                "email_count": 1,
                "duration": "24 hours",
                "goal": "Remind and encourage add to cart"
            },
            {
                "workflow_name": "Birthday Campaign",
                "trigger": "Customer birthday (if captured)",
                "email_count": 1,
                "timing": "7 days before birthday",
                "content": "Birthday discount code (20% off)"
            },
            {
                "workflow_name": "Winback Campaign",
                "trigger": "180 days since last purchase",
                "email_count": 3,
                "duration": "14 days",
                "goal": "Re-engage lapsed customers"
            }
        ]

    def _generate_frequency_recommendations(self) -> Dict:
        """Generate email frequency recommendations."""
        return {
            "promotional_emails": "1-2 per week maximum",
            "transactional_emails": "As needed (immediate)",
            "newsletter": "1 per week or bi-weekly",
            "best_send_times": {
                "weekdays": "10 AM - 11 AM or 7 PM - 8 PM",
                "weekends": "9 AM - 10 AM",
                "avoid": "Mondays before 10 AM, Friday evenings"
            },
            "testing_recommendations": "A/B test send times for your specific audience"
        }

    def _generate_best_practices(self) -> List[str]:
        """Generate email marketing best practices."""
        return [
            "Always include a clear, single call-to-action",
            "Keep subject lines under 50 characters for mobile",
            "Use preheader text to complement subject line",
            "Ensure mobile responsiveness (60%+ of opens are mobile)",
            "Include alt text for all images",
            "Maintain consistent sender name and email address",
            "Test emails across major email clients",
            "Include easy unsubscribe option in footer",
            "Personalize with subscriber's first name when appropriate",
            "Monitor deliverability and sender reputation",
            "Clean email list quarterly (remove hard bounces)",
            "Implement double opt-in for quality subscribers",
            "Use MJML for responsive email design",
            "Track opens, clicks, conversions for optimisation"
        ]

    def _get_mjml_header(self) -> str:
        """Generate consistent MJML header with branding."""
        return """
    <!-- Header -->
    <mj-section background-color="#ffffff" padding="20px 20px 10px">
      <mj-column>
        <mj-image src="https://via.placeholder.com/180x60/ffffff/C5A572?text=LOGO" width="180px" alt="Logo" />
      </mj-column>
    </mj-section>

    <!-- Navigation -->
    <mj-section background-color="#ffffff" padding="0 20px 20px">
      <mj-column>
        <mj-navbar base-url="/" hamburger="hamburger" ico-color="#333333">
          <mj-navbar-link href="/christmas" color="#333333" font-size="12px" font-weight="400" letter-spacing="1px" text-transform="uppercase">Christmas</mj-navbar-link>
          <mj-navbar-link href="/baby" color="#333333" font-size="12px" font-weight="400" letter-spacing="1px" text-transform="uppercase">Baby</mj-navbar-link>
          <mj-navbar-link href="/girls" color="#333333" font-size="12px" font-weight="400" letter-spacing="1px" text-transform="uppercase">Girls</mj-navbar-link>
          <mj-navbar-link href="/boys" color="#333333" font-size="12px" font-weight="400" letter-spacing="1px" text-transform="uppercase">Boys</mj-navbar-link>
        </mj-navbar>
      </mj-column>
    </mj-section>

    <mj-section padding="0">
      <mj-column>
        <mj-divider border-color="#e5e5e5" border-width="1px" />
      </mj-column>
    </mj-section>
"""

    def _get_mjml_footer(self) -> str:
        """Generate consistent MJML footer with social links."""
        return """
    <!-- Footer -->
    <mj-section background-color="#ffffff" padding="30px 20px 10px">
      <mj-column>
        <mj-divider border-color="#e5e5e5" border-width="1px" padding-bottom="20px" />
        <mj-text align="center" color="#666666" font-size="12px" line-height="18px">
          Download our App
        </mj-text>
        <mj-social font-size="12px" icon-size="30px" mode="horizontal" padding="10px 0">
          <mj-social-element name="facebook" href="https://facebook.com/" background-color="#ffffff" color="#333333" />
          <mj-social-element name="instagram" href="https://instagram.com/" background-color="#ffffff" color="#333333" />
          <mj-social-element name="pinterest" href="https://pinterest.com/" background-color="#ffffff" color="#333333" />
        </mj-social>
      </mj-column>
    </mj-section>

    <mj-section background-color="#ffffff" padding="10px 20px 30px">
      <mj-column>
        <mj-text align="center" color="#999999" font-size="11px" line-height="16px">
          <a href="/downloads" style="color: #999999; text-decoration: none;">Downloads</a> &nbsp;|&nbsp;
          <a href="/privacy" style="color: #999999; text-decoration: none;">Privacy Policy</a> &nbsp;|&nbsp;
          <a href="/unsubscribe" style="color: #999999; text-decoration: none;">Unsubscribe</a>
        </mj-text>
        <mj-text align="center" color="#999999" font-size="10px" line-height="14px" padding-top="15px">
          © 2025 Your Company. All rights reserved.
        </mj-text>
      </mj-column>
    </mj-section>
"""

    def _generate_mjml_welcome_email(self, category_name: str, hero_section: Dict) -> str:
        """Generate MJML template for welcome email."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()
        headline = hero_section.get("headline", f"Welcome to Our {category_name} Collection")

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
    <mj-style>
      .headline {{ font-family: Georgia, 'Times New Roman', serif; }}
      .body-text {{ font-family: Arial, Helvetica, sans-serif; }}
    </mj-style>
  </mj-head>
  <mj-body background-color="#ffffff">
    {header}

    <!-- Hero Image Section -->
    <mj-section background-url="https://via.placeholder.com/600x400/e8e4df/333333?text=Welcome+Hero+Image" background-size="cover" background-repeat="no-repeat" padding="100px 20px" text-align="center">
      <mj-column>
        <mj-text align="center" color="#ffffff" font-size="42px" font-weight="400" line-height="48px" font-family="Georgia, 'Times New Roman', serif">
          <em>Welcome</em><br/>To Our Family
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Welcome Message -->
    <mj-section background-color="#ffffff" padding="40px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          We're thrilled to have you join us! Discover our carefully curated {category_name} collection, featuring the finest designer pieces for your little ones.
        </mj-text>
        <mj-button href="/shop" padding-top="25px">
          Start Shopping
        </mj-button>
      </mj-column>
    </mj-section>

    <!-- Features Section -->
    <mj-section background-color="#ffffff" padding="30px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Why Shop With Us
        </mj-text>
      </mj-column>
    </mj-section>

    <mj-section background-color="#ffffff" padding="0 20px 40px">
      <mj-column>
        <mj-text align="center" font-size="13px" color="#666666" line-height="22px" font-family="Arial, Helvetica, sans-serif">
          <strong>Free Delivery</strong> on orders over £100<br/>
          <strong>Easy Returns</strong> within 28 days<br/>
          <strong>Luxury Gift Wrapping</strong> available
        </mj-text>
      </mj-column>
    </mj-section>

    {footer}
  </mj-body>
</mjml>
"""

    def _generate_mjml_educational_email(self, category_name: str, research_data: Dict) -> str:
        """Generate MJML template for educational email."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {header}

    <!-- Hero Section -->
    <mj-section background-color="#ffffff" padding="40px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="32px" font-weight="400" line-height="40px" color="#333333" font-family="Georgia, 'Times New Roman', serif">
          <em>Your Guide to</em><br/>Choosing the Perfect {category_name}
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <!-- Intro Text -->
    <mj-section background-color="#ffffff" padding="0 40px 30px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          Making the right choice for your child is important. Here's everything you need to know to find the perfect pieces for your little one.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Tips Section -->
    <mj-section background-color="#f9f7f5" padding="40px 40px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif" padding-bottom="20px">
          Expert Tips
        </mj-text>
        <mj-text font-size="14px" line-height="28px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          <strong>1. Quality Materials</strong><br/>
          Look for natural, breathable fabrics that are gentle on delicate skin.<br/><br/>
          <strong>2. Perfect Fit</strong><br/>
          Allow room for growth while ensuring comfort and ease of movement.<br/><br/>
          <strong>3. Easy Care</strong><br/>
          Choose pieces that are machine washable for everyday convenience.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- CTA Section -->
    <mj-section background-color="#ffffff" padding="40px 40px">
      <mj-column>
        <mj-text align="center" font-size="18px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-bottom="20px">
          Ready to explore our collection?
        </mj-text>
        <mj-button href="/shop">
          Browse Our Collection
        </mj-button>
      </mj-column>
    </mj-section>

    {footer}
  </mj-body>
</mjml>
"""

    def _generate_mjml_offer_email(self, discount_code: str) -> str:
        """Generate MJML template for offer email."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {header}

    <!-- Gift Box Icon -->
    <mj-section background-color="#ffffff" padding="40px 40px 10px">
      <mj-column>
        <mj-text align="center" font-size="48px">
          🎁
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Offer Headline -->
    <mj-section background-color="#ffffff" padding="10px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="36px" font-weight="400" line-height="44px" color="#333333" font-family="Georgia, 'Times New Roman', serif">
          <em>A Special Gift</em><br/>Just For You
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <!-- Discount Box -->
    <mj-section background-color="#f9f7f5" padding="40px">
      <mj-column>
        <mj-text align="center" font-size="18px" color="#333333" font-family="Georgia, 'Times New Roman', serif">
          Enjoy
        </mj-text>
        <mj-text align="center" font-size="56px" font-weight="400" color="#C5A572" font-family="Georgia, 'Times New Roman', serif" padding="10px 0">
          15% OFF
        </mj-text>
        <mj-text align="center" font-size="14px" color="#666666" font-family="Arial, Helvetica, sans-serif">
          your first order
        </mj-text>
        <mj-text align="center" font-size="13px" color="#333333" font-family="Arial, Helvetica, sans-serif" padding-top="20px">
          Use code at checkout:
        </mj-text>
        <mj-text align="center" font-size="24px" font-weight="600" color="#333333" letter-spacing="3px" font-family="Arial, Helvetica, sans-serif" padding="10px 0">
          {discount_code}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- CTA -->
    <mj-section background-color="#ffffff" padding="40px 40px">
      <mj-column>
        <mj-button href="/shop?discount={discount_code}">
          Claim Your Discount
        </mj-button>
        <mj-text align="center" font-size="12px" color="#999999" font-family="Arial, Helvetica, sans-serif" padding-top="20px">
          *Valid for 30 days. Cannot be combined with other offers.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Social Proof -->
    <mj-section background-color="#ffffff" padding="20px 40px 40px">
      <mj-column>
        <mj-text align="center" font-size="14px" color="#333333" font-family="Georgia, 'Times New Roman', serif" font-style="italic">
          "Absolutely beautiful quality. My daughter looks adorable!"
        </mj-text>
        <mj-text align="center" font-size="12px" color="#C5A572" font-family="Arial, Helvetica, sans-serif" padding-top="10px">
          ★★★★★
        </mj-text>
      </mj-column>
    </mj-section>

    {footer}
  </mj-body>
</mjml>
"""

    def _generate_mjml_cart_abandonment(self) -> str:
        """Generate MJML template for cart abandonment."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {header}

    <!-- Headline -->
    <mj-section background-color="#ffffff" padding="40px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="32px" font-weight="400" line-height="40px" color="#333333" font-family="Georgia, 'Times New Roman', serif">
          <em>Did You Forget</em><br/>Something Special?
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <!-- Message -->
    <mj-section background-color="#ffffff" padding="0 40px 30px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          We noticed you left some beautiful items in your shopping bag. Don't worry, we've saved them for you!
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Cart Items Placeholder -->
    <mj-section background-color="#f9f7f5" padding="30px 40px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif" padding-bottom="15px">
          Your Saved Items
        </mj-text>
        <mj-text align="center" font-size="14px" color="#666666" font-family="Arial, Helvetica, sans-serif">
          [Your cart items will appear here]
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- CTA -->
    <mj-section background-color="#ffffff" padding="40px 40px">
      <mj-column>
        <mj-button href="/cart">
          Complete Your Order
        </mj-button>
      </mj-column>
    </mj-section>

    <!-- Urgency Message -->
    <mj-section background-color="#ffffff" padding="0 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="13px" color="#666666" font-family="Arial, Helvetica, sans-serif">
          Items in your cart are subject to availability. Complete your purchase soon to avoid disappointment.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Help Section -->
    <mj-section background-color="#ffffff" padding="20px 40px 40px">
      <mj-column>
        <mj-text align="center" font-size="14px" color="#333333" font-family="Georgia, 'Times New Roman', serif">
          Need help? Our customer service team is here for you.
        </mj-text>
        <mj-text align="center" font-size="13px" color="#C5A572" font-family="Arial, Helvetica, sans-serif" padding-top="10px">
          <a href="/contact" style="color: #C5A572; text-decoration: none;">Contact Us</a>
        </mj-text>
      </mj-column>
    </mj-section>

    {footer}
  </mj-body>
</mjml>
"""

    def _generate_mjml_welcome_email_with_products(
        self, category_name: str, hero_section: Dict, brands: List[str],
        products: List[Dict], features: List[Dict]
    ) -> str:
        """Generate MJML welcome email with featured brands and products."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        # Build product grid HTML
        product_html = self._build_product_grid_mjml(products)

        # Build brand badges
        brand_list = ', '.join(brands[:3]) if brands else "Designer Brands"

        # Build feature highlights
        feature_html = ""
        for feature in features[:3]:
            feature_html += f"""
            <mj-text font-size="13px" color="#666666" line-height="20px" font-family="Arial, Helvetica, sans-serif" padding="5px 0">
              <strong style="color: #C5A572;">✓</strong> {feature.get('title', '')}: {feature.get('description', '')[:60]}
            </mj-text>"""

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Hero Section -->
    <mj-section background-url="https://via.placeholder.com/600x300/e8e4df/333333?text=Welcome" background-size="cover" padding="80px 20px" text-align="center">
      <mj-column>
        <mj-text align="center" color="#ffffff" font-size="38px" font-weight="400" line-height="44px" font-family="Georgia, 'Times New Roman', serif">
          <em>Welcome</em><br/>To Our Family
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Welcome Message -->
    <mj-section background-color="#ffffff" padding="40px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          We're thrilled to have you! Discover our carefully curated {category_name} collection featuring {{brand_list}} and more.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Featured Brands Badge -->
    <mj-section background-color="#ffffff" padding="10px 40px 30px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Featuring: {{brand_list}}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Featured Products Section -->
    <mj-section background-color="#f9f7f5" padding="30px 20px 10px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Just For You
        </mj-text>
        <mj-text align="center" font-size="24px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="10px">
          Featured {category_name}
        </mj-text>
      </mj-column>
    </mj-section>

    {{product_html}}

    <mj-section background-color="#f9f7f5" padding="20px 40px 40px">
      <mj-column>
        <mj-button href="/shop">
          Shop All {category_name}
        </mj-button>
      </mj-column>
    </mj-section>

    <!-- Why Shop With Us -->
    <mj-section background-color="#ffffff" padding="40px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Why Shop With Us
        </mj-text>
        {{feature_html}}
      </mj-column>
    </mj-section>

    <!-- Service Badges -->
    <mj-section background-color="#ffffff" padding="20px 20px 40px">
      <mj-column>
        <mj-text align="center" font-size="13px" color="#666666" line-height="22px" font-family="Arial, Helvetica, sans-serif">
          <strong>Free Delivery</strong> on orders over £100 &nbsp;|&nbsp;
          <strong>Easy Returns</strong> within 28 days &nbsp;|&nbsp;
          <strong>Luxury Gift Wrapping</strong>
        </mj-text>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _generate_mjml_feature_spotlight_email(
        self, category_name: str, features: List[Dict],
        products: List[Dict], research_data: Dict
    ) -> str:
        """Generate MJML email highlighting specific features with products."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        product_html = self._build_product_grid_mjml(products[:3])

        # Build feature sections
        feature_sections = ""
        for i, feature in enumerate(features[:3]):
            bg_color = "#ffffff" if i % 2 == 0 else "#f9f7f5"
            feature_sections += f"""
    <mj-section background-color="{bg_color}" padding="30px 40px">
      <mj-column>
        <mj-text align="center" font-size="20px" color="#333333" font-family="Georgia, 'Times New Roman', serif">
          {feature.get('title', 'Quality Feature')}
        </mj-text>
        <mj-text align="center" font-size="14px" color="#666666" line-height="24px" font-family="Arial, Helvetica, sans-serif" padding-top="10px">
          {feature.get('description', '')}
        </mj-text>
      </mj-column>
    </mj-section>"""

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Hero Section -->
    <mj-section background-color="#ffffff" padding="40px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Why Parents Choose Us
        </mj-text>
        <mj-text align="center" font-size="32px" font-weight="400" line-height="40px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="15px">
          <em>The Quality</em><br/>You Can Trust
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <mj-section background-color="#ffffff" padding="0 40px 30px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          Discover what makes our {category_name} the choice of discerning parents who want only the best for their little ones.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Feature Sections -->
    {{feature_sections}}

    <!-- Products Section -->
    <mj-section background-color="#ffffff" padding="40px 20px 10px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Shop The Quality
        </mj-text>
        <mj-text align="center" font-size="24px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="10px">
          Featured Picks
        </mj-text>
      </mj-column>
    </mj-section>

    {{product_html}}

    <mj-section background-color="#ffffff" padding="20px 40px 40px">
      <mj-column>
        <mj-button href="/shop">
          Shop The Collection
        </mj-button>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _generate_mjml_brand_spotlight_offer(
        self, brand: str, products: List[Dict], category_name: str, discount_code: str
    ) -> str:
        """Generate MJML email spotlighting a specific brand with discount."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        product_html = self._build_product_grid_mjml(products[:3])

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Brand Spotlight Hero -->
    <mj-section background-color="#f9f7f5" padding="40px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Brand Spotlight
        </mj-text>
        <mj-text align="center" font-size="36px" font-weight="400" line-height="44px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="15px">
          <em>{brand}</em>
        </mj-text>
        <mj-text align="center" font-size="16px" color="#666666" font-family="Arial, Helvetica, sans-serif" padding-top="10px">
          {category_name}
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <!-- Discount Offer -->
    <mj-section background-color="#f9f7f5" padding="0 40px 30px">
      <mj-column>
        <mj-text align="center" font-size="48px" font-weight="400" color="#C5A572" font-family="Georgia, 'Times New Roman', serif">
          15% OFF
        </mj-text>
        <mj-text align="center" font-size="14px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          Your Welcome Gift
        </mj-text>
        <mj-text align="center" font-size="18px" font-weight="600" color="#333333" letter-spacing="2px" font-family="Arial, Helvetica, sans-serif" padding-top="15px">
          Code: {discount_code}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Featured Products -->
    <mj-section background-color="#ffffff" padding="40px 20px 10px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Featured From {brand}
        </mj-text>
      </mj-column>
    </mj-section>

    {{product_html}}

    <mj-section background-color="#ffffff" padding="20px 40px 40px">
      <mj-column>
        <mj-button href="/shop?brand={brand}&discount={discount_code}">
          Shop {brand} Now
        </mj-button>
        <mj-text align="center" font-size="12px" color="#999999" font-family="Arial, Helvetica, sans-serif" padding-top="20px">
          *Valid for 30 days. Cannot be combined with other offers.
        </mj-text>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _generate_mjml_brand_campaign(self, brand: str, products: List[Dict], category_name: str) -> str:
        """Generate MJML promotional campaign for a specific brand."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        product_html = self._build_product_grid_mjml(products[:4])

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Hero -->
    <mj-section background-url="https://via.placeholder.com/600x300/e8e4df/333333?text={brand}" background-size="cover" padding="80px 20px" text-align="center">
      <mj-column>
        <mj-text align="center" color="#ffffff" font-size="14px" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          New Arrivals
        </mj-text>
        <mj-text align="center" color="#ffffff" font-size="42px" font-weight="400" line-height="48px" font-family="Georgia, 'Times New Roman', serif" padding-top="10px">
          <em>{brand}</em>
        </mj-text>
        <mj-text align="center" color="#ffffff" font-size="16px" font-family="Arial, Helvetica, sans-serif" padding-top="10px">
          {category_name}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Intro -->
    <mj-section background-color="#ffffff" padding="40px 40px 30px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          Discover the latest {brand} {category_name.lower()} - exquisite design meets exceptional quality in every piece.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Products -->
    <mj-section background-color="#f9f7f5" padding="30px 20px 10px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          New In
        </mj-text>
        <mj-text align="center" font-size="24px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="10px">
          {brand} {category_name}
        </mj-text>
      </mj-column>
    </mj-section>

    {{product_html}}

    <mj-section background-color="#f9f7f5" padding="20px 40px 40px">
      <mj-column>
        <mj-button href="/shop?brand={brand}">
          Shop {brand}
        </mj-button>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _generate_mjml_feature_campaign(self, feature: Dict, products: List[Dict], category_name: str) -> str:
        """Generate MJML promotional campaign highlighting a specific feature."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        feature_title = feature.get('title', 'Premium Quality')
        feature_desc = feature.get('description', 'Crafted with exceptional care and attention to detail.')

        product_html = self._build_product_grid_mjml(products[:4])

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Hero -->
    <mj-section background-color="#ffffff" padding="50px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          What Sets Us Apart
        </mj-text>
        <mj-text align="center" font-size="36px" font-weight="400" line-height="44px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="15px">
          <em>{feature_title}</em>
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <!-- Feature Description -->
    <mj-section background-color="#ffffff" padding="0 40px 40px">
      <mj-column>
        <mj-text align="center" font-size="16px" line-height="28px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          {feature_desc}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Highlight Box -->
    <mj-section background-color="#f9f7f5" padding="30px 40px">
      <mj-column>
        <mj-text align="center" font-size="18px" color="#333333" font-family="Georgia, 'Times New Roman', serif">
          "{feature_title}" Collection
        </mj-text>
        <mj-text align="center" font-size="14px" color="#666666" font-family="Arial, Helvetica, sans-serif" padding-top="10px">
          {category_name} that embody our commitment to excellence
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Products -->
    {{product_html}}

    <mj-section background-color="#ffffff" padding="30px 40px 40px">
      <mj-column>
        <mj-button href="/shop">
          Shop The Collection
        </mj-button>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _generate_mjml_multi_brand_campaign(self, brands: List[str], products: List[Dict], category_name: str) -> str:
        """Generate MJML promotional campaign showcasing multiple brands."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        brand_list = ', '.join(brands[:2]) + ' & More' if len(brands) > 2 else ' & '.join(brands)
        product_html = self._build_product_grid_mjml(products[:3])

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Hero -->
    <mj-section background-color="#f9f7f5" padding="50px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Designer {category_name}
        </mj-text>
        <mj-text align="center" font-size="32px" font-weight="400" line-height="40px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="15px">
          <em>Shop</em><br/>{brand_list}
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 80px" />
      </mj-column>
    </mj-section>

    <!-- Intro -->
    <mj-section background-color="#f9f7f5" padding="0 40px 40px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          Discover our curated collection of designer {category_name.lower()} from the world's most prestigious brands.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Brand Badges -->
    <mj-section background-color="#ffffff" padding="30px 40px">
      <mj-column>
        <mj-text align="center" font-size="14px" color="#C5A572" letter-spacing="1px" font-family="Arial, Helvetica, sans-serif">
          {' · '.join(brands[:4])}
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Products -->
    {{product_html}}

    <mj-section background-color="#ffffff" padding="30px 40px 40px">
      <mj-column>
        <mj-button href="/shop">
          Shop All Brands
        </mj-button>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _generate_mjml_price_campaign(self, price_threshold: float, products: List[Dict], category_name: str) -> str:
        """Generate MJML campaign for price-point focused promotion."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        product_html = self._build_product_grid_mjml(products[:3])

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Hero -->
    <mj-section background-color="#f9f7f5" padding="50px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Gift Guide
        </mj-text>
        <mj-text align="center" font-size="36px" font-weight="400" line-height="44px" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="15px">
          <em>{category_name}</em><br/>Under £{price_threshold:.0f}
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <!-- Intro -->
    <mj-section background-color="#f9f7f5" padding="0 40px 40px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          Designer quality doesn't have to break the bank. Discover beautiful {category_name.lower()} at accessible price points.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Products -->
    <mj-section background-color="#ffffff" padding="30px 20px 10px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Top Picks Under £{price_threshold:.0f}
        </mj-text>
      </mj-column>
    </mj-section>

    {{product_html}}

    <mj-section background-color="#ffffff" padding="30px 40px 40px">
      <mj-column>
        <mj-button href="/shop?max_price={price_threshold:.0f}">
          Shop Under £{price_threshold:.0f}
        </mj-button>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _generate_mjml_sale_campaign(self, products: List[Dict], category_name: str) -> str:
        """Generate MJML campaign for seasonal sale."""
        header = self._get_mjml_header()
        footer = self._get_mjml_footer()

        product_html = self._build_product_grid_mjml(products[:4])

        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Georgia, 'Times New Roman', serif" />
      <mj-text font-size="14px" color="#333333" line-height="24px" />
      <mj-button background-color="#C5A572" color="#ffffff" font-size="13px" font-weight="400" letter-spacing="1px" border-radius="0" text-transform="uppercase" inner-padding="15px 30px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#ffffff">
    {{header}}

    <!-- Hero -->
    <mj-section background-color="#f9f7f5" padding="50px 40px 20px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Limited Time
        </mj-text>
        <mj-text align="center" font-size="48px" font-weight="400" color="#333333" font-family="Georgia, 'Times New Roman', serif" padding-top="10px">
          <em>Seasonal Sale</em>
        </mj-text>
        <mj-text align="center" font-size="42px" font-weight="400" color="#C5A572" font-family="Georgia, 'Times New Roman', serif" padding-top="10px">
          Up to 30% Off
        </mj-text>
        <mj-divider border-color="#C5A572" border-width="1px" padding="20px 100px" />
      </mj-column>
    </mj-section>

    <!-- Intro -->
    <mj-section background-color="#f9f7f5" padding="0 40px 40px">
      <mj-column>
        <mj-text align="center" font-size="15px" line-height="26px" color="#333333" font-family="Arial, Helvetica, sans-serif">
          Designer {category_name.lower()} at exceptional prices. Don't miss out on these limited-time savings.
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Products -->
    <mj-section background-color="#ffffff" padding="30px 20px 10px">
      <mj-column>
        <mj-text align="center" font-size="11px" color="#C5A572" letter-spacing="2px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          Sale Highlights
        </mj-text>
      </mj-column>
    </mj-section>

    {{product_html}}

    <mj-section background-color="#ffffff" padding="30px 40px 20px">
      <mj-column>
        <mj-button href="/sale">
          Shop The Sale
        </mj-button>
      </mj-column>
    </mj-section>

    <!-- Urgency -->
    <mj-section background-color="#ffffff" padding="0 40px 40px">
      <mj-column>
        <mj-text align="center" font-size="12px" color="#999999" font-family="Arial, Helvetica, sans-serif">
          *While stocks last. Sale ends soon.
        </mj-text>
      </mj-column>
    </mj-section>

    {{footer}}
  </mj-body>
</mjml>
"""

    def _build_product_grid_mjml(self, products: List[Dict]) -> str:
        """Build MJML product grid section."""
        if not products:
            return ""

        product_sections = []
        for product in products[:4]:
            name = product.get('name', 'Product')[:40]
            brand = product.get('brand') or 'Designer'
            price = product.get('price', 0)
            url = product.get('url') or '/shop'

            # Use actual image or create a nice placeholder
            image = product.get('image_url')
            if not image or image.strip() == '':
                # Create placeholder with brand initial
                brand_initial = brand[0].upper() if brand else 'C'
                # Use Childrensalon-style placeholder (warm beige with gold accent)
                image = f"https://via.placeholder.com/200x250/f5f0eb/C5A572?text={brand_initial}"

            product_sections.append(f"""
    <mj-section background-color="#f9f7f5" padding="15px 20px">
      <mj-column width="40%">
        <mj-image src="{image}" alt="{name}" width="150px" />
      </mj-column>
      <mj-column width="60%">
        <mj-text font-size="11px" color="#C5A572" letter-spacing="1px" text-transform="uppercase" font-family="Arial, Helvetica, sans-serif">
          {brand}
        </mj-text>
        <mj-text font-size="14px" color="#333333" font-family="Arial, Helvetica, sans-serif" padding-top="5px">
          {name}
        </mj-text>
        <mj-text font-size="16px" font-weight="600" color="#333333" font-family="Arial, Helvetica, sans-serif" padding-top="8px">
          £{price:.2f}
        </mj-text>
        <mj-button href="{url}" font-size="11px" inner-padding="10px 20px" padding-top="10px">
          View
        </mj-button>
      </mj-column>
    </mj-section>""")

        return "\n".join(product_sections)
