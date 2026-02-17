"""
Meta Ads Agent - Creates Facebook and Instagram advertising campaigns.

Responsibilities:
1. Generate audience targeting (interests, behaviors, custom, lookalike)
2. Create ad sets with proper targeting and placements
3. Generate ad creatives (single image, carousel, collection)
4. Write compelling ad copy (primary text, headlines, descriptions)
5. Recommend placements (Feed, Stories, Reels)
6. Define campaign objectives and structure
"""
import logging
import json
from typing import Dict, List
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


class MetaAdsAgent:
    """Meta Ads agent for creating Facebook and Instagram campaigns."""

    # Interest categories for children's fashion
    INTEREST_CATEGORIES = {
        'parenting': [
            'Parenting', 'Motherhood', 'Fatherhood', 'New parents',
            'Pregnancy', 'Baby products', 'Parenting magazines'
        ],
        'luxury': [
            'Luxury goods', 'Designer brands', 'High-end fashion',
            'Premium products', 'Luxury lifestyle'
        ],
        'fashion': [
            'Children\'s clothing', 'Kids fashion', 'Baby fashion',
            'Fashion accessories', 'Online shopping'
        ],
        'lifestyle': [
            'Family', 'Family vacations', 'Private schools',
            'Premium lifestyle', 'Organic products'
        ]
    }

    # Behavior categories
    BEHAVIOR_CATEGORIES = {
        'shopping': [
            'Engaged shoppers', 'Online buyers', 'Fashion purchasers'
        ],
        'parents': [
            'Parents (all)', 'Parents with toddlers (1-2 years)',
            'Parents with preschoolers (3-5 years)',
            'Parents with early school age children (6-8 years)'
        ],
        'income': [
            'High household income', 'Frequent travelers'
        ]
    }

    # Campaign objectives mapping
    CAMPAIGN_OBJECTIVES = {
        'awareness': 'Brand awareness and reach',
        'traffic': 'Drive website traffic',
        'engagement': 'Post engagement and interactions',
        'conversions': 'Website conversions and purchases',
        'catalog_sales': 'Dynamic product ads from catalog'
    }

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the Meta Ads agent workflow.

        Args:
            state: Current campaign state with research_data

        Returns:
            Updated state with meta_ads_campaign
        """
        logger.info(f"Meta Ads Agent starting for campaign {state['campaign_id']}")

        state["current_step"] = "meta_ads"
        state["progress_percentage"] = 78

        try:
            research_data = state.get("research_data")
            content_outputs = state.get("content_outputs")
            if not research_data:
                raise ValueError("No research data available")

            budget = state.get("budget") or 5000
            category_insights = research_data.get("category_insights", {})
            products = research_data.get("products", [])

            # Extract product intelligence
            logger.info("Extracting product intelligence for Meta targeting")
            brands = self._extract_brands(products)
            price_insights = self._analyze_price_points(products, category_insights)

            # Detect demographics from category
            demographics = self._detect_demographics(category_insights.get("category_name", ""))

            # Generate campaign structure
            logger.info("Generating campaign objectives")
            campaign_structure = self._create_campaign_structure(
                category_insights, budget, demographics
            )

            logger.info("Creating audience targeting")
            audiences = self._create_audience_targeting(
                category_insights, demographics, brands, price_insights
            )

            logger.info("Generating ad sets")
            ad_sets = self._create_ad_sets(
                audiences, category_insights, budget
            )

            logger.info("Creating ad creatives")
            ad_creatives = self._create_ad_creatives(
                research_data, content_outputs, products, brands, demographics
            )

            logger.info("Generating ad copy")
            ad_copy = self._generate_ad_copy(
                research_data, content_outputs, brands, demographics
            )

            # Compile Meta Ads campaign
            meta_ads_campaign = {
                "campaign_structure": campaign_structure,
                "audiences": audiences,
                "ad_sets": ad_sets,
                "ad_creatives": ad_creatives,
                "ad_copy": ad_copy,
                "budget_allocation": self._create_budget_allocation(budget, ad_sets),
                "placement_recommendations": self._get_placement_recommendations(demographics),
                "best_practices": self._get_meta_best_practices()
            }

            state["meta_ads_campaign"] = meta_ads_campaign
            state["progress_percentage"] = 80
            logger.info("Meta Ads Agent completed successfully")

            return state

        except Exception as e:
            error_msg = f"Meta Ads Agent failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["progress_percentage"] = 80
            return state

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

    def _analyze_price_points(self, products: List[Dict], category_insights: Dict) -> Dict:
        """Analyze price points for targeting."""
        prices = [p.get('price', 0) for p in products if p.get('price')]
        if not prices:
            price_range = category_insights.get("price_range", {})
            return {
                "min": price_range.get("min", 20),
                "max": price_range.get("max", 200),
                "avg": (price_range.get("min", 20) + price_range.get("max", 200)) / 2,
                "tier": "mid"
            }

        avg_price = sum(prices) / len(prices)
        tier = "luxury" if avg_price > 150 else "mid" if avg_price > 50 else "value"

        return {
            "min": min(prices),
            "max": max(prices),
            "avg": avg_price,
            "tier": tier
        }

    def _detect_demographics(self, category_name: str) -> Dict:
        """Detect target demographics from category name."""
        name_lower = category_name.lower()

        # Detect gender
        gender = None
        if any(word in name_lower for word in ['boy', 'boys']):
            gender = "boys"
        elif any(word in name_lower for word in ['girl', 'girls']):
            gender = "girls"
        elif any(word in name_lower for word in ['baby', 'infant', 'newborn']):
            gender = "baby"

        # Detect age group
        age_group = "all"
        if any(word in name_lower for word in ['baby', 'infant', 'newborn', '0-12', '0-24']):
            age_group = "baby"
        elif any(word in name_lower for word in ['toddler', '1-3', '2-4']):
            age_group = "toddler"
        elif any(word in name_lower for word in ['teen', 'teenager', 'junior']):
            age_group = "teen"

        # Detect product type
        product_type = "clothing"
        if any(word in name_lower for word in ['bag', 'bags', 'backpack']):
            product_type = "bags"
        elif any(word in name_lower for word in ['shoe', 'shoes', 'boot', 'trainer']):
            product_type = "shoes"
        elif any(word in name_lower for word in ['coat', 'jacket', 'outerwear']):
            product_type = "outerwear"

        return {
            "gender": gender,
            "age_group": age_group,
            "product_type": product_type,
            "category_name": category_name
        }

    def _create_campaign_structure(self, category_insights: Dict, budget: float, demographics: Dict) -> Dict:
        """Create the overall campaign structure."""
        category_name = category_insights.get("category_name", "Products")

        # Determine primary objective based on budget
        if budget >= 5000:
            primary_objective = "conversions"
        elif budget >= 2000:
            primary_objective = "traffic"
        else:
            primary_objective = "awareness"

        return {
            "campaign_name": f"Childrensalon - {category_name}",
            "primary_objective": primary_objective,
            "objective_description": self.CAMPAIGN_OBJECTIVES.get(primary_objective),
            "recommended_campaign_types": [
                {
                    "type": "Conversions Campaign",
                    "objective": "conversions",
                    "description": "Drive purchases with optimized delivery to likely buyers",
                    "recommended_budget_split": "60%"
                },
                {
                    "type": "Retargeting Campaign",
                    "objective": "conversions",
                    "description": "Re-engage website visitors and cart abandoners",
                    "recommended_budget_split": "25%"
                },
                {
                    "type": "Prospecting Campaign",
                    "objective": "traffic",
                    "description": "Reach new audiences similar to existing customers",
                    "recommended_budget_split": "15%"
                }
            ],
            "optimization_goal": "Purchase" if primary_objective == "conversions" else "Link Clicks",
            "attribution_window": "7-day click, 1-day view"
        }

    def _create_audience_targeting(
        self, category_insights: Dict, demographics: Dict,
        brands: List[str], price_insights: Dict
    ) -> Dict:
        """Create detailed audience targeting."""
        category_name = category_insights.get("category_name", "Products")
        gender = demographics.get("gender")
        age_group = demographics.get("age_group")
        price_tier = price_insights.get("tier", "mid")

        audiences = {
            "core_audiences": [],
            "custom_audiences": [],
            "lookalike_audiences": []
        }

        # Core Audience 1: Interest-based parents
        parent_interests = self.INTEREST_CATEGORIES['parenting'].copy()
        if price_tier == "luxury":
            parent_interests.extend(self.INTEREST_CATEGORIES['luxury'])

        audiences["core_audiences"].append({
            "name": f"Parents interested in {category_name}",
            "targeting": {
                "age_range": "25-45",
                "genders": "All",
                "interests": parent_interests[:8],
                "behaviors": self.BEHAVIOR_CATEGORIES['parents'][:3],
                "exclude": ["Budget shopping", "Discount seekers"] if price_tier == "luxury" else []
            },
            "estimated_reach": "500K - 1M",
            "priority": "High"
        })

        # Core Audience 2: Luxury/Fashion focused
        if price_tier in ["luxury", "mid"]:
            audiences["core_audiences"].append({
                "name": "Luxury Children's Fashion Enthusiasts",
                "targeting": {
                    "age_range": "28-50",
                    "genders": "All",
                    "interests": self.INTEREST_CATEGORIES['luxury'] + self.INTEREST_CATEGORIES['fashion'][:4],
                    "behaviors": self.BEHAVIOR_CATEGORIES['income'] + ["Frequent online buyers"],
                    "exclude": []
                },
                "estimated_reach": "200K - 500K",
                "priority": "High"
            })

        # Core Audience 3: Gender-specific if detected
        if gender:
            gender_display = gender.title()
            audiences["core_audiences"].append({
                "name": f"Parents of {gender_display}",
                "targeting": {
                    "age_range": "25-45",
                    "genders": "All",
                    "interests": [f"{gender_display} clothing", f"{gender_display} fashion", "Children's fashion"],
                    "behaviors": [f"Parents with children ({self._get_age_behavior(age_group)})"],
                    "detailed_targeting": f"Parents shopping for {gender}"
                },
                "estimated_reach": "300K - 700K",
                "priority": "Medium"
            })

        # Core Audience 4: Brand-aware (if brands found)
        if brands:
            brand_list = ', '.join(brands[:3])
            audiences["core_audiences"].append({
                "name": f"Designer Brand Shoppers ({brand_list})",
                "targeting": {
                    "age_range": "25-50",
                    "genders": "All",
                    "interests": brands[:5] + ["Designer fashion", "Luxury brands"],
                    "behaviors": ["Engaged shoppers", "High-end retail shoppers"],
                    "exclude": []
                },
                "estimated_reach": "100K - 300K",
                "priority": "Medium"
            })

        # Custom Audiences
        audiences["custom_audiences"] = [
            {
                "name": "Website Visitors - All",
                "source": "Website traffic (Pixel)",
                "retention": "180 days",
                "description": "All website visitors in the last 6 months"
            },
            {
                "name": f"{category_name} Page Viewers",
                "source": "Website traffic (Pixel)",
                "retention": "30 days",
                "description": f"Visitors who viewed {category_name} category pages"
            },
            {
                "name": "Add to Cart - No Purchase",
                "source": "Website traffic (Pixel)",
                "retention": "14 days",
                "description": "Users who added items to cart but didn't purchase"
            },
            {
                "name": "Past Purchasers",
                "source": "Customer list / Pixel",
                "retention": "365 days",
                "description": "Customers who have purchased in the last year"
            },
            {
                "name": "Email Subscribers",
                "source": "Customer list (Klaviyo export)",
                "retention": "N/A",
                "description": "Newsletter subscribers for exclusion or targeting"
            }
        ]

        # Lookalike Audiences
        audiences["lookalike_audiences"] = [
            {
                "name": "Lookalike - Purchasers (1%)",
                "source": "Past Purchasers",
                "percentage": "1%",
                "country": "United Kingdom",
                "description": "Top 1% most similar to existing customers - highest quality"
            },
            {
                "name": "Lookalike - Purchasers (3%)",
                "source": "Past Purchasers",
                "percentage": "3%",
                "country": "United Kingdom",
                "description": "Broader reach while maintaining quality"
            },
            {
                "name": "Lookalike - High Value Customers",
                "source": "Top 25% customers by LTV",
                "percentage": "1%",
                "country": "United Kingdom",
                "description": "Similar to highest spending customers"
            },
            {
                "name": f"Lookalike - {category_name} Buyers",
                "source": f"Customers who purchased {category_name}",
                "percentage": "2%",
                "country": "United Kingdom",
                "description": f"Similar to customers who bought {category_name}"
            }
        ]

        return audiences

    def _get_age_behavior(self, age_group: str) -> str:
        """Get Meta's parent behavior targeting based on age group."""
        mapping = {
            "baby": "0-12 months",
            "toddler": "1-2 years",
            "all": "all ages"
        }
        return mapping.get(age_group, "all ages")

    def _create_ad_sets(self, audiences: Dict, category_insights: Dict, budget: float) -> List[Dict]:
        """Create ad sets from audiences."""
        ad_sets = []
        category_name = category_insights.get("category_name", "Products")

        # Ad Set 1: Prospecting - Core Interest Audiences
        ad_sets.append({
            "name": f"Prospecting - {category_name} Interest",
            "campaign_type": "Conversions",
            "audience": audiences["core_audiences"][0] if audiences["core_audiences"] else None,
            "placements": {
                "type": "Advantage+ Placements (Recommended)",
                "platforms": ["Facebook", "Instagram"],
                "positions": ["Feed", "Stories", "Reels", "Explore"]
            },
            "budget_type": "Daily budget",
            "recommended_daily_budget": f"£{(budget * 0.3 / 30):.2f}",
            "optimization": "Conversions - Purchase",
            "bid_strategy": "Lowest cost",
            "schedule": "Run continuously"
        })

        # Ad Set 2: Lookalike Audiences
        ad_sets.append({
            "name": f"Lookalike - {category_name} Purchasers",
            "campaign_type": "Conversions",
            "audience": audiences["lookalike_audiences"][0] if audiences["lookalike_audiences"] else None,
            "placements": {
                "type": "Advantage+ Placements (Recommended)",
                "platforms": ["Facebook", "Instagram"],
                "positions": ["Feed", "Stories", "Reels"]
            },
            "budget_type": "Daily budget",
            "recommended_daily_budget": f"£{(budget * 0.25 / 30):.2f}",
            "optimization": "Conversions - Purchase",
            "bid_strategy": "Lowest cost",
            "schedule": "Run continuously"
        })

        # Ad Set 3: Retargeting - Website Visitors
        ad_sets.append({
            "name": "Retargeting - Website Visitors",
            "campaign_type": "Conversions",
            "audience": {
                "name": "Website Visitors (30 days)",
                "exclude": "Past Purchasers (14 days)"
            },
            "placements": {
                "type": "Manual placements",
                "platforms": ["Facebook", "Instagram"],
                "positions": ["Feed", "Stories", "Right Column"]
            },
            "budget_type": "Daily budget",
            "recommended_daily_budget": f"£{(budget * 0.2 / 30):.2f}",
            "optimization": "Conversions - Purchase",
            "bid_strategy": "Lowest cost",
            "schedule": "Run continuously"
        })

        # Ad Set 4: Retargeting - Cart Abandoners
        ad_sets.append({
            "name": "Retargeting - Cart Abandoners",
            "campaign_type": "Conversions",
            "audience": {
                "name": "Add to Cart - No Purchase (14 days)",
                "exclude": "Past Purchasers (7 days)"
            },
            "placements": {
                "type": "Manual placements",
                "platforms": ["Facebook", "Instagram"],
                "positions": ["Feed", "Stories"]
            },
            "budget_type": "Daily budget",
            "recommended_daily_budget": f"£{(budget * 0.15 / 30):.2f}",
            "optimization": "Conversions - Purchase",
            "bid_strategy": "Cost cap",
            "schedule": "Run continuously",
            "notes": "High intent audience - can afford higher CPA"
        })

        # Ad Set 5: Brand Awareness (if budget allows)
        if budget >= 3000:
            ad_sets.append({
                "name": f"Awareness - {category_name} Launch",
                "campaign_type": "Awareness",
                "audience": audiences["core_audiences"][1] if len(audiences["core_audiences"]) > 1 else audiences["core_audiences"][0],
                "placements": {
                    "type": "Advantage+ Placements",
                    "platforms": ["Facebook", "Instagram"],
                    "positions": ["Feed", "Stories", "Reels", "In-stream"]
                },
                "budget_type": "Daily budget",
                "recommended_daily_budget": f"£{(budget * 0.1 / 30):.2f}",
                "optimization": "Reach",
                "bid_strategy": "Lowest cost",
                "schedule": "Run continuously"
            })

        return ad_sets

    def _create_ad_creatives(
        self, research_data: Dict, content_outputs: Dict,
        products: List[Dict], brands: List[str], demographics: Dict
    ) -> List[Dict]:
        """Create ad creative recommendations."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        features = content_outputs.get("features", []) if content_outputs else []

        creatives = []

        # Creative 1: Single Image - Hero
        creatives.append({
            "name": f"{category_name} - Hero Image",
            "format": "Single Image",
            "placement_optimized": ["Feed", "Explore"],
            "specs": {
                "aspect_ratio": "1:1 (recommended) or 4:5",
                "resolution": "1080x1080 or 1080x1350",
                "file_type": "JPG or PNG",
                "max_file_size": "30MB"
            },
            "creative_direction": {
                "style": "Lifestyle imagery showing child wearing/using product",
                "mood": "Aspirational, warm, family-focused",
                "key_elements": [
                    "Happy child as hero",
                    "Product clearly visible",
                    "Minimal text on image (< 20%)",
                    "Brand logo subtle in corner"
                ],
                "avoid": ["Cluttered backgrounds", "Multiple products", "Heavy text overlays"]
            },
            "recommended_for": "Prospecting campaigns"
        })

        # Creative 2: Carousel - Product Range
        carousel_products = products[:5] if products else []
        creatives.append({
            "name": f"{category_name} - Product Carousel",
            "format": "Carousel",
            "placement_optimized": ["Feed"],
            "specs": {
                "cards": "3-10 cards",
                "aspect_ratio": "1:1",
                "resolution": "1080x1080 per card",
                "file_type": "JPG or PNG"
            },
            "creative_direction": {
                "card_strategy": [
                    "Card 1: Hero lifestyle shot",
                    "Cards 2-4: Individual product shots",
                    "Final card: CTA or brand message"
                ],
                "products_to_feature": [p.get('name', 'Product')[:30] for p in carousel_products[:4]],
                "brands_to_highlight": brands[:3] if brands else ["Designer"],
                "style": "Clean product photography on neutral background"
            },
            "recommended_for": "Retargeting campaigns"
        })

        # Creative 3: Stories/Reels - Vertical Video
        creatives.append({
            "name": f"{category_name} - Stories/Reels",
            "format": "Vertical Video or Static",
            "placement_optimized": ["Stories", "Reels"],
            "specs": {
                "aspect_ratio": "9:16",
                "resolution": "1080x1920",
                "duration": "5-15 seconds (video)",
                "file_type": "MP4 (video) or JPG/PNG (static)"
            },
            "creative_direction": {
                "style": "Fast-paced, engaging, native feel",
                "key_elements": [
                    "Hook in first 2 seconds",
                    "Full-screen immersive design",
                    "Clear CTA button area at bottom",
                    "Sound-on design (music/voiceover)"
                ],
                "video_ideas": [
                    "Unboxing moment",
                    "Child trying on outfit",
                    "Before/after styling",
                    "Quick product showcase"
                ]
            },
            "recommended_for": "Awareness and prospecting"
        })

        # Creative 4: Collection Ad
        creatives.append({
            "name": f"{category_name} - Collection Ad",
            "format": "Collection",
            "placement_optimized": ["Feed"],
            "specs": {
                "cover": "Image or video (1:1 or 16:9)",
                "product_images": "4+ products from catalog",
                "instant_experience": "Required"
            },
            "creative_direction": {
                "cover_strategy": "Lifestyle hero image featuring multiple products",
                "product_selection": "Best sellers or new arrivals",
                "instant_experience_template": "Storefront",
                "benefits": [
                    "Immersive browsing experience",
                    "Direct product links",
                    "Seamless shopping journey"
                ]
            },
            "recommended_for": "High-intent audiences, retargeting"
        })

        # Creative 5: Dynamic Product Ad (DPA)
        creatives.append({
            "name": f"{category_name} - Dynamic Product Ad",
            "format": "Dynamic (Catalog)",
            "placement_optimized": ["Feed", "Right Column"],
            "specs": {
                "catalog_required": True,
                "template": "Single image or carousel",
                "auto_generated": True
            },
            "creative_direction": {
                "template_customization": [
                    "Add brand frame/border",
                    "Include price overlay",
                    "Add 'New In' or 'Sale' badges"
                ],
                "product_feed_requirements": [
                    "High-quality images",
                    "Accurate pricing",
                    "Stock availability",
                    "Product categories"
                ]
            },
            "recommended_for": "Retargeting cart abandoners, cross-sell"
        })

        return creatives

    def _generate_ad_copy(
        self, research_data: Dict, content_outputs: Dict,
        brands: List[str], demographics: Dict
    ) -> Dict:
        """Generate Meta ad copy variations using Claude."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        features = content_outputs.get("features", []) if content_outputs else []
        gender = demographics.get("gender", "children")

        # Get feature highlights for copy
        feature_highlights = [f.get("title", "") for f in features[:3]] if features else ["Quality", "Style", "Comfort"]
        brand_mentions = ", ".join(brands[:2]) if brands else "designer brands"

        try:
            prompt = f"""Generate Meta (Facebook/Instagram) ad copy for a luxury children's fashion retailer.

Category: {category_name}
Target: Parents shopping for {gender if gender else 'children'}
Featured Brands: {brand_mentions}
Key Features: {', '.join(feature_highlights)}

Generate 4 ad copy variations. For each variation, provide:
1. Primary Text (125 chars optimal, max 500 - the main body copy)
2. Headline (27 chars optimal, max 40 - appears below image)
3. Description (27 chars optimal, max 30 - appears below headline)
4. Call to Action button recommendation

The copy should:
- Be emotional and aspirational (not search-focused like Google Ads)
- Speak to parents' desires for their children
- Highlight the luxury/quality aspect
- Include a sense of exclusivity or urgency where appropriate
- NOT include specific product counts or percentages unless it's a sale

Respond in this exact JSON format:
{{
    "variations": [
        {{
            "name": "Variation name",
            "tone": "emotional/aspirational/urgency/social-proof",
            "primary_text": "Main ad copy here",
            "headline": "Short headline",
            "description": "Brief description",
            "cta_button": "Shop Now"
        }}
    ]
}}"""

            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text

            # Parse JSON response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response_text)
            if json_match:
                ad_copy_data = json.loads(json_match.group())
                variations = ad_copy_data.get("variations", [])
            else:
                variations = []

        except Exception as e:
            logger.warning(f"Failed to generate ad copy with Claude: {e}")
            variations = []

        # Add default variations if needed
        if len(variations) < 4:
            default_variations = self._get_default_ad_copy(category_name, brand_mentions, gender)
            variations.extend(default_variations[len(variations):4])

        return {
            "variations": variations[:4],
            "best_practices": {
                "primary_text": "Front-load the most important message. Use emojis sparingly. Include clear value proposition.",
                "headline": "Keep it short and action-oriented. Test questions vs statements.",
                "description": "Reinforce the headline or add urgency/social proof.",
                "cta_buttons": ["Shop Now", "Learn More", "Get Offer", "See More"]
            },
            "character_limits": {
                "primary_text": {"optimal": 125, "max": 500},
                "headline": {"optimal": 27, "max": 40},
                "description": {"optimal": 27, "max": 30}
            }
        }

    def _get_default_ad_copy(self, category_name: str, brands: str, gender: str) -> List[Dict]:
        """Get default ad copy variations."""
        return [
            {
                "name": "Aspirational",
                "tone": "aspirational",
                "primary_text": f"Give them the best. Our {category_name.lower()} collection features {brands} - designed for the moments that matter most. ✨",
                "headline": f"Designer {category_name}",
                "description": "Luxury for little ones",
                "cta_button": "Shop Now"
            },
            {
                "name": "Quality Focus",
                "tone": "emotional",
                "primary_text": f"Because they deserve exceptional quality. Discover our handpicked {category_name.lower()} from the world's finest brands.",
                "headline": "Quality That Lasts",
                "description": "Free delivery over £100",
                "cta_button": "Shop Now"
            },
            {
                "name": "New Arrivals",
                "tone": "urgency",
                "primary_text": f"Just landed ✈️ New {category_name.lower()} from {brands}. Be the first to shop the latest styles before they're gone.",
                "headline": "New Arrivals",
                "description": "Shop the latest",
                "cta_button": "See More"
            },
            {
                "name": "Social Proof",
                "tone": "social-proof",
                "primary_text": f"Join thousands of parents who choose Childrensalon for designer {category_name.lower()}. Trusted for quality, loved for style. 💝",
                "headline": "Parents' Top Choice",
                "description": "5-star rated service",
                "cta_button": "Shop Now"
            }
        ]

    def _create_budget_allocation(self, total_budget: float, ad_sets: List[Dict]) -> Dict:
        """Create budget allocation across campaigns."""
        return {
            "total_monthly_budget": f"£{total_budget:.2f}",
            "recommended_split": {
                "prospecting": {
                    "percentage": "45%",
                    "amount": f"£{total_budget * 0.45:.2f}",
                    "focus": "New customer acquisition"
                },
                "retargeting": {
                    "percentage": "40%",
                    "amount": f"£{total_budget * 0.40:.2f}",
                    "focus": "Website visitors and cart abandoners"
                },
                "awareness": {
                    "percentage": "15%",
                    "amount": f"£{total_budget * 0.15:.2f}",
                    "focus": "Brand building and reach"
                }
            },
            "daily_budget_recommendation": f"£{total_budget / 30:.2f}",
            "minimum_viable_budget": "£500/month for meaningful results",
            "scaling_advice": "Increase budget by 20% every 3-4 days if ROAS target is met"
        }

    def _get_placement_recommendations(self, demographics: Dict) -> Dict:
        """Get placement recommendations based on demographics."""
        return {
            "recommended_approach": "Advantage+ Placements (let Meta optimise)",
            "manual_placement_notes": {
                "Facebook Feed": {
                    "priority": "High",
                    "best_for": "Detailed product information, longer copy",
                    "audience": "Slightly older demographics (30-50)"
                },
                "Instagram Feed": {
                    "priority": "High",
                    "best_for": "Visual products, lifestyle imagery",
                    "audience": "Fashion-conscious parents (25-40)"
                },
                "Instagram Stories": {
                    "priority": "High",
                    "best_for": "Quick engagement, swipe-up actions",
                    "audience": "Engaged, mobile-first users"
                },
                "Instagram Reels": {
                    "priority": "Medium-High",
                    "best_for": "Discovery, brand awareness, younger parents",
                    "audience": "Trend-aware, video consumers"
                },
                "Facebook Marketplace": {
                    "priority": "Low",
                    "best_for": "Consider excluding - typically lower intent for luxury",
                    "audience": "Bargain hunters"
                },
                "Audience Network": {
                    "priority": "Low",
                    "best_for": "Extended reach at lower CPM",
                    "audience": "Consider excluding for luxury positioning"
                }
            }
        }

    def _get_meta_best_practices(self) -> List[str]:
        """Get Meta Ads best practices."""
        return [
            "Use Advantage+ placements for optimal delivery across all Meta platforms",
            "Set up Meta Pixel with all standard events (ViewContent, AddToCart, Purchase)",
            "Create a product catalog for dynamic retargeting ads",
            "Test 3-5 ad creatives per ad set before scaling",
            "Use Campaign Budget Optimisation (CBO) for efficient spend allocation",
            "Set up custom conversions for category-specific tracking",
            "Implement the Conversions API (CAPI) for improved tracking accuracy",
            "Use broad targeting and let Meta's algorithm find the right audience",
            "Refresh creative every 2-4 weeks to combat ad fatigue",
            "Exclude past purchasers from prospecting campaigns (7-14 day window)",
            "Use cost cap bidding for retargeting to control CPA",
            "Monitor frequency - aim for <3 for prospecting, <5 for retargeting",
            "A/B test ad copy, not just images - small copy changes can significantly impact CTR",
            "Schedule campaigns for UK peak hours (7-9am, 12-2pm, 7-10pm)"
        ]
