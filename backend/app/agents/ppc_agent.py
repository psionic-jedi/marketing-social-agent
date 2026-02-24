"""
PPC Agent - Creates Google Ads campaign structure and ad copy.

Responsibilities:
1. Generate keyword research and grouping based on scraped product data
2. Create ad groups with targeted keywords (by brand, product type, price tier)
3. Write compelling ad copy (headlines, descriptions)
4. Set bid recommendations
5. Create negative keyword lists
6. Define campaign structure
"""
import logging
import re
from typing import Dict, List, Set
from collections import Counter
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


class PPCAgent:
    """PPC agent for creating Google Ads campaigns."""

    # Common designer brands for children's products
    KNOWN_BRANDS = {
        'gucci', 'moncler', 'ralph lauren', 'burberry', 'dolce & gabbana', 'dolce and gabbana',
        'fendi', 'versace', 'armani', 'boss', 'hugo boss', 'kenzo', 'givenchy', 'stella mccartney',
        'moschino', 'dsquared2', 'balmain', 'off-white', 'palm angels', 'stone island',
        'canada goose', 'the north face', 'tommy hilfiger', 'calvin klein', 'michael kors',
        'coach', 'marc jacobs', 'chloe', 'bonpoint', 'tartine et chocolat', 'petit bateau',
        'jacadi', 'absorba', 'mayoral', 'il gufo', 'molo', 'mini rodini', 'bobo choses'
    }

    # Product type keywords to look for
    PRODUCT_TYPES = {
        'backpack': ['backpack', 'rucksack', 'school bag'],
        'messenger bag': ['messenger', 'crossbody', 'cross body', 'shoulder bag'],
        'travel bag': ['travel', 'weekend', 'duffle', 'duffel', 'holdall'],
        'sports bag': ['sports', 'gym', 'kit bag'],
        'wallet': ['wallet', 'purse', 'card holder'],
        'pouch': ['pouch', 'clutch', 'wash bag', 'toiletry']
    }

    def __init__(self, cost_tracker=None):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.cost_tracker = cost_tracker

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the PPC agent workflow.

        Args:
            state: Current campaign state with research_data

        Returns:
            Updated state with ppc_campaign
        """
        logger.info(f"PPC Agent starting for campaign {state['campaign_id']}")

        state["current_step"] = "ppc"
        state["progress_percentage"] = 75

        try:
            research_data = state.get("research_data")
            if not research_data:
                raise ValueError("No research data available")

            budget = state.get("budget") or 5000
            category_insights = research_data.get("category_insights", {})
            seo_keywords = research_data.get("seo_keywords", {})
            products = research_data.get("products", [])

            # Extract product intelligence from scraped data
            logger.info("Extracting product intelligence from scraped data")
            extracted_brands = self._extract_brands_from_products(products)
            extracted_types = self._extract_product_types(products)
            long_tail_keywords = self._extract_long_tail_keywords(products, category_insights)

            logger.info(f"Found {len(extracted_brands)} brands, {len(extracted_types)} product types")

            # Generate PPC campaign structure using extracted data
            logger.info("Generating keyword strategy")
            keyword_strategy = self._generate_keyword_strategy(
                seo_keywords, category_insights, extracted_brands, extracted_types, long_tail_keywords
            )

            logger.info("Creating ad groups")
            ad_groups = self._create_ad_groups(
                keyword_strategy, category_insights, extracted_brands, extracted_types, products
            )

            logger.info("Generating ad copy")
            ads = self._generate_ad_copy(ad_groups, research_data, extracted_brands)

            logger.info("Creating budget allocation")
            budget_allocation = self._create_budget_allocation(budget, ad_groups)

            logger.info("Generating negative keywords")
            negative_keywords = self._generate_negative_keywords(category_insights)

            # Generate campaign type recommendations
            logger.info("Generating campaign type recommendations")
            campaign_types = self._generate_campaign_types(budget, category_insights, products)

            # Generate KPI targets
            logger.info("Calculating KPI targets")
            kpi_targets = self._generate_kpi_targets(budget, category_insights, products)

            # Generate strategic budget allocation across campaign types
            logger.info("Creating strategic budget allocation")
            strategic_allocation = self._generate_strategic_allocation(budget, campaign_types, kpi_targets)

            # Compile PPC campaign
            ppc_campaign = {
                "campaign_name": f"{category_insights.get('category_name', 'Product')} - Search Campaign",
                "campaign_types": campaign_types,
                "recommended_campaign_mix": strategic_allocation["campaign_mix"],
                "budget_daily": budget_allocation["daily_budget"],
                "budget_monthly": budget,
                "bidding_strategy": "Maximize Conversions",
                "keyword_strategy": keyword_strategy,
                "ad_groups": ad_groups,
                "ads": ads,
                "negative_keywords": negative_keywords,
                "budget_allocation": budget_allocation,
                "strategic_allocation": strategic_allocation,
                "kpi_targets": kpi_targets,
                "targeting": self._generate_targeting_settings(research_data),
                "tracking": self._generate_tracking_setup(),
                "product_intelligence": {
                    "brands_found": list(extracted_brands.keys())[:10],
                    "product_types_found": list(extracted_types.keys()),
                    "long_tail_keywords_generated": len(long_tail_keywords)
                }
            }

            state["ppc_campaign"] = ppc_campaign
            state["progress_percentage"] = 80
            logger.info("PPC Agent completed successfully")

            return state

        except Exception as e:
            error_msg = f"PPC Agent failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["progress_percentage"] = 80
            return state

    def _extract_brands_from_products(self, products: List[Dict]) -> Dict[str, int]:
        """Extract brand names from product data with frequency counts."""
        brand_counts = Counter()

        for product in products:
            # Check product name, brand field, and description
            name = (product.get('name') or '').lower()
            brand = (product.get('brand') or '').lower()
            description = (product.get('description') or '').lower()

            combined_text = f"{name} {brand} {description}"

            # Look for known brands
            for known_brand in self.KNOWN_BRANDS:
                if known_brand in combined_text:
                    # Capitalize properly for display
                    display_brand = known_brand.title()
                    brand_counts[display_brand] += 1

        # Return brands sorted by frequency
        return dict(brand_counts.most_common())

    def _extract_product_types(self, products: List[Dict]) -> Dict[str, List[str]]:
        """Extract product types from product data."""
        type_products = {ptype: [] for ptype in self.PRODUCT_TYPES}

        for product in products:
            name = (product.get('name') or '').lower()
            description = (product.get('description') or '').lower()
            combined_text = f"{name} {description}"

            for product_type, keywords in self.PRODUCT_TYPES.items():
                for keyword in keywords:
                    if keyword in combined_text:
                        type_products[product_type].append(product.get('name', ''))
                        break

        # Remove empty types
        return {k: v for k, v in type_products.items() if v}

    def _extract_long_tail_keywords(self, products: List[Dict], category_insights: Dict) -> List[str]:
        """Generate long-tail keywords from actual product data."""
        category_name = category_insights.get("category_name", "Products")
        long_tail = set()

        # Extract unique descriptors from product names
        for product in products:
            name = product.get('name') or ''
            brand = product.get('brand') or ''

            # Brand + category combinations
            if brand:
                long_tail.add(f"{brand} {category_name}".lower())
                long_tail.add(f"{brand} kids {category_name}".lower())
                long_tail.add(f"{brand} boys {category_name}".lower())
                long_tail.add(f"{brand} girls {category_name}".lower())

            # Extract color/pattern keywords
            colors = ['black', 'white', 'blue', 'pink', 'red', 'navy', 'grey', 'gray', 'beige', 'brown']
            for color in colors:
                if color in name.lower():
                    long_tail.add(f"{color} {category_name}".lower())

            # Extract material keywords
            materials = ['leather', 'canvas', 'nylon', 'cotton', 'wool']
            for material in materials:
                if material in name.lower():
                    long_tail.add(f"{material} {category_name}".lower())
                    long_tail.add(f"kids {material} {category_name}".lower())

        # Add use-case keywords
        use_cases = [
            f"school {category_name}",
            f"kids {category_name}",
            f"children's {category_name}",
            f"designer {category_name}",
            f"luxury {category_name}",
            f"premium {category_name}",
            f"best {category_name} for kids",
            f"boys {category_name} uk",
            f"girls {category_name} uk"
        ]
        long_tail.update(use_cases)

        return list(long_tail)

    def _generate_keyword_strategy(
        self,
        seo_keywords: Dict,
        category_insights: Dict,
        extracted_brands: Dict[str, int],
        extracted_types: Dict[str, List[str]],
        long_tail_keywords: List[str]
    ) -> Dict:
        """Generate comprehensive keyword strategy using scraped product data."""
        category_name = category_insights.get("category_name", "Products")

        # Extract keywords from research
        primary_keywords = seo_keywords.get("primary", [])
        secondary_keywords = seo_keywords.get("secondary", [])

        # Generate brand-specific keywords from scraped data
        brand_keywords = []
        for brand in list(extracted_brands.keys())[:5]:  # Top 5 brands
            brand_keywords.extend([
                f"{brand} {category_name}",
                f"{brand} kids {category_name}",
                f"buy {brand} {category_name}",
            ])

        # Generate product type keywords from scraped data
        type_keywords = []
        for product_type in extracted_types.keys():
            type_keywords.extend([
                f"boys {product_type}",
                f"kids {product_type}",
                f"designer {product_type}",
                f"children's {product_type}",
            ])

        # Core category keywords
        category_keywords = [
            f"{category_name}",
            f"buy {category_name}",
            f"{category_name} online",
            f"{category_name} uk"
        ]

        # Commercial intent keywords
        commercial_keywords = [
            f"{category_name} sale",
            f"best {category_name}",
            f"designer {category_name}",
            f"luxury {category_name}",
            f"premium {category_name}"
        ]

        return {
            "brand_keywords": {
                "keywords": brand_keywords,
                "match_type": "Phrase",
                "bid_modifier": 1.3,
                "priority": "High",
                "rationale": "High-intent brand searchers convert well"
            },
            "product_type_keywords": {
                "keywords": type_keywords,
                "match_type": "Phrase",
                "bid_modifier": 1.1,
                "priority": "High",
                "rationale": "Specific product type searches indicate purchase intent"
            },
            "category_keywords": {
                "keywords": category_keywords,
                "match_type": "Exact",
                "bid_modifier": 1.0,
                "priority": "High",
                "rationale": "Core category terms for broad visibility"
            },
            "commercial_keywords": {
                "keywords": commercial_keywords,
                "match_type": "Phrase",
                "bid_modifier": 1.2,
                "priority": "High",
                "rationale": "Commercial intent signals readiness to buy"
            },
            "long_tail_keywords": {
                "keywords": long_tail_keywords[:30],
                "match_type": "Broad Match Modified",
                "bid_modifier": 0.8,
                "priority": "Medium",
                "rationale": "Lower competition, higher relevance"
            },
            "primary_seo_keywords": {
                "keywords": primary_keywords[:10],
                "match_type": "Phrase",
                "bid_modifier": 0.9,
                "priority": "Medium",
                "rationale": "SEO-derived keywords for additional coverage"
            }
        }

    def _create_ad_groups(
        self,
        keyword_strategy: Dict,
        category_insights: Dict,
        extracted_brands: Dict[str, int],
        extracted_types: Dict[str, List[str]],
        products: List[Dict]
    ) -> List[Dict]:
        """Create ad groups with targeted keywords based on scraped data."""
        category_name = category_insights.get("category_name", "Products")
        price_range = category_insights.get("price_range", {})

        ad_groups = []

        # 1. Brand-specific ad groups (top 3 brands)
        top_brands = list(extracted_brands.keys())[:3]
        for brand in top_brands:
            brand_keywords = [
                f"{brand} {category_name}",
                f"{brand} kids {category_name}",
                f"buy {brand} {category_name}",
                f"{brand} boys {category_name}",
                f"{brand} children's {category_name}"
            ]
            ad_groups.append({
                "ad_group_name": f"{brand} {category_name}",
                "keywords": brand_keywords,
                "match_types": ["Phrase", "Exact"],
                "max_cpc": 1.80,
                "priority": "High",
                "recommended_daily_budget": 40,
                "theme": "brand",
                "brand": brand
            })

        # 2. Product type ad groups
        for product_type, type_products in extracted_types.items():
            if len(type_products) >= 2:  # Only create if we have products
                type_keywords = [
                    f"boys {product_type}",
                    f"kids {product_type}",
                    f"designer {product_type}",
                    f"children's {product_type}",
                    f"luxury {product_type}",
                    f"best {product_type} for kids"
                ]
                ad_groups.append({
                    "ad_group_name": f"Kids {product_type.title()}",
                    "keywords": type_keywords,
                    "match_types": ["Phrase", "Broad Match Modified"],
                    "max_cpc": 1.40,
                    "priority": "High",
                    "recommended_daily_budget": 35,
                    "theme": "product_type",
                    "product_type": product_type
                })

        # 3. Price tier ad groups
        min_price = price_range.get('min', 0)
        max_price = price_range.get('max', 500)

        # Luxury tier (top 30% of price range)
        luxury_threshold = min_price + (max_price - min_price) * 0.7
        ad_groups.append({
            "ad_group_name": f"Luxury Designer {category_name}",
            "keywords": [
                f"luxury {category_name}",
                f"designer {category_name}",
                f"premium {category_name}",
                f"high end {category_name}",
                f"best designer {category_name}"
            ],
            "match_types": ["Phrase"],
            "max_cpc": 2.00,
            "priority": "High",
            "recommended_daily_budget": 50,
            "theme": "price_tier",
            "price_tier": f"£{luxury_threshold:.0f}+"
        })

        # 4. Commercial intent ad group
        ad_groups.append({
            "ad_group_name": f"{category_name} - Sale & Deals",
            "keywords": keyword_strategy["commercial_keywords"]["keywords"],
            "match_types": ["Phrase"],
            "max_cpc": 1.50,
            "priority": "High",
            "recommended_daily_budget": 45,
            "theme": "commercial"
        })

        # 5. Long-tail ad groups - create specific groups based on keyword themes
        long_tail_kws = keyword_strategy["long_tail_keywords"]["keywords"]

        # Group long-tail keywords by theme
        material_keywords = [kw for kw in long_tail_kws if any(m in kw for m in ['leather', 'canvas', 'nylon', 'cotton'])]
        use_case_keywords = [kw for kw in long_tail_kws if any(u in kw for u in ['school', 'travel', 'sports', 'gym'])]
        style_keywords = [kw for kw in long_tail_kws if any(s in kw for s in ['designer', 'luxury', 'premium'])]

        # Create material-focused ad group if we have relevant keywords
        if material_keywords:
            ad_groups.append({
                "ad_group_name": f"Quality Materials - {category_name}",
                "keywords": material_keywords[:10],
                "match_types": ["Phrase", "Broad Match Modified"],
                "max_cpc": 1.10,
                "priority": "Medium",
                "recommended_daily_budget": 25,
                "theme": "material",
                "focus": "materials"
            })

        # Create use-case focused ad group if we have relevant keywords
        if use_case_keywords:
            ad_groups.append({
                "ad_group_name": f"School & Travel - {category_name}",
                "keywords": use_case_keywords[:10],
                "match_types": ["Phrase", "Broad Match Modified"],
                "max_cpc": 1.20,
                "priority": "High",
                "recommended_daily_budget": 30,
                "theme": "use_case",
                "focus": "practical use"
            })

        # 6. Core category catchall
        ad_groups.append({
            "ad_group_name": f"{category_name} - General",
            "keywords": keyword_strategy["category_keywords"]["keywords"],
            "match_types": ["Exact", "Phrase"],
            "max_cpc": 1.20,
            "priority": "Medium",
            "recommended_daily_budget": 35,
            "theme": "category"
        })

        # 7. Ensure minimum 5 ad groups by adding additional groups if needed
        additional_groups = [
            {
                "ad_group_name": f"Gift Ideas - {category_name}",
                "keywords": [
                    f"{category_name} gift",
                    f"gift {category_name}",
                    f"best {category_name} gift",
                    f"{category_name} present",
                    f"birthday {category_name}"
                ],
                "match_types": ["Phrase", "Broad Match Modified"],
                "max_cpc": 1.30,
                "priority": "Medium",
                "recommended_daily_budget": 30,
                "theme": "gift"
            },
            {
                "ad_group_name": f"New Arrivals - {category_name}",
                "keywords": [
                    f"new {category_name}",
                    f"latest {category_name}",
                    f"{category_name} new collection",
                    f"new season {category_name}",
                    f"{category_name} 2024"
                ],
                "match_types": ["Phrase"],
                "max_cpc": 1.25,
                "priority": "Medium",
                "recommended_daily_budget": 28,
                "theme": "new_arrivals"
            },
            {
                "ad_group_name": f"UK Delivery - {category_name}",
                "keywords": [
                    f"{category_name} uk",
                    f"buy {category_name} uk",
                    f"{category_name} free delivery",
                    f"{category_name} next day delivery",
                    f"{category_name} uk online"
                ],
                "match_types": ["Phrase"],
                "max_cpc": 1.15,
                "priority": "Medium",
                "recommended_daily_budget": 25,
                "theme": "delivery"
            },
            {
                "ad_group_name": f"Reviews & Best - {category_name}",
                "keywords": [
                    f"best {category_name}",
                    f"top {category_name}",
                    f"{category_name} reviews",
                    f"recommended {category_name}",
                    f"quality {category_name}"
                ],
                "match_types": ["Phrase", "Broad Match Modified"],
                "max_cpc": 1.35,
                "priority": "Medium",
                "recommended_daily_budget": 32,
                "theme": "reviews"
            }
        ]

        # Add additional groups until we have at least 5
        for additional in additional_groups:
            if len(ad_groups) >= 5:
                break
            ad_groups.append(additional)

        # Cap at maximum 10 ad groups
        if len(ad_groups) > 10:
            # Prioritize: keep High priority first, then Medium
            high_priority = [ag for ag in ad_groups if ag.get("priority") == "High"]
            medium_priority = [ag for ag in ad_groups if ag.get("priority") == "Medium"]
            ad_groups = high_priority[:7] + medium_priority[:3]

        logger.info(f"Created {len(ad_groups)} ad groups (min 5, max 10)")
        return ad_groups

    def _generate_ad_copy(self, ad_groups: List[Dict], research_data: Dict, extracted_brands: Dict[str, int]) -> List[Dict]:
        """Generate ad copy for each ad group using Claude."""
        category_insights = research_data.get("category_insights", {})
        category_name = category_insights.get("category_name", "Products")
        usps = category_insights.get("unique_selling_points", [])
        price_range = category_insights.get("price_range", {})

        ads = []

        # Generate tailored ads for each ad group based on its theme
        for ad_group in ad_groups:
            theme = ad_group.get("theme", "general")
            ad_group_name = ad_group["ad_group_name"]

            # Build theme-specific context
            theme_context = self._get_theme_context(ad_group, category_name, price_range)

            prompt = f"""Create 2 unique Google Ads text ad variations for: {ad_group_name}

Category: {category_name}
Ad Group Theme: {theme}
{theme_context}
Price range: £{price_range.get('min', 0):.0f} - £{price_range.get('max', 0):.0f}
USPs: {', '.join(usps[:3]) if usps else 'Quality, designer brands, free delivery'}

For each ad variation, create:
- 4 headlines (30 chars each max) - compelling, keyword-rich, actionable
- 2 descriptions (90 chars each max) - benefit-focused, include USPs

IMPORTANT RULES:
- Do NOT include specific product counts (no "50+", "35+", etc.)
- Do NOT repeat the same phrase across headlines
- Each headline should be unique and offer different value
- Include at least one headline with a call-to-action
- Make headlines specific to the ad group theme

Return ONLY valid JSON:
{{
  "ads": [
    {{
      "variation": 1,
      "headlines": ["headline1", "headline2", "headline3", "headline4"],
      "descriptions": ["description1", "description2"]
    }}
  ]
}}"""

            try:
                response = self.anthropic.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=1500,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )

                if self.cost_tracker:
                    self.cost_tracker.record(response, "ppc", f"ad_copy_{ad_group_name[:50]}")

                import json
                response_text = response.content[0].text.strip()
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                    response_text = response_text.strip()

                ad_data = json.loads(response_text)

                for ad_variation in ad_data.get("ads", []):
                    # Generate appropriate URL paths based on theme
                    path1, path2 = self._get_url_paths(ad_group, category_name)

                    ads.append({
                        "ad_group": ad_group_name,
                        "ad_variation": ad_variation.get("variation", 1),
                        "headlines": ad_variation.get("headlines", [])[:4],
                        "descriptions": ad_variation.get("descriptions", [])[:2],
                        "path1": path1,
                        "path2": path2,
                        "final_url": "/category",
                        "display_url": f"www.example.com/{path1.lower()}/{path2.lower()}"
                    })

                logger.info(f"Generated {len(ad_data.get('ads', []))} ads for {ad_group_name}")

            except Exception as e:
                logger.error(f"Error generating ads for {ad_group_name}: {e}", exc_info=True)
                # Fallback to theme-appropriate template
                fallback_ad = self._get_fallback_ad(ad_group, category_name)
                ads.append(fallback_ad)

        return ads

    def _get_theme_context(self, ad_group: Dict, category_name: str, price_range: Dict) -> str:
        """Get theme-specific context for ad generation."""
        theme = ad_group.get("theme", "general")

        if theme == "brand":
            brand = ad_group.get("brand", "Designer")
            return f"Focus: {brand} brand products\nHighlight: Brand prestige, authenticity, quality"

        elif theme == "product_type":
            product_type = ad_group.get("product_type", "products")
            return f"Focus: {product_type.title()} specifically\nHighlight: Style, functionality, variety"

        elif theme == "price_tier":
            return f"Focus: Luxury/premium segment\nHighlight: Exclusivity, quality materials, designer labels"

        elif theme == "commercial":
            return f"Focus: Deals and value\nHighlight: Sale items, best prices, limited offers"

        elif theme == "material":
            return f"Focus: Quality materials (leather, canvas, etc.)\nHighlight: Durability, craftsmanship, premium fabrics"

        elif theme == "use_case":
            return f"Focus: Practical uses (school, travel, sports)\nHighlight: Functionality, durability, perfect for purpose"

        elif theme == "long_tail":
            return f"Focus: Specific customer needs\nHighlight: Selection, expertise, perfect match"

        else:
            return f"Focus: General category awareness\nHighlight: Range, quality, service"

    def _get_url_paths(self, ad_group: Dict, category_name: str) -> tuple:
        """Generate appropriate URL paths based on ad group theme."""
        theme = ad_group.get("theme", "general")
        cat_slug = ((category_name or '')[:15]).replace(" ", "-").lower()

        if theme == "brand":
            brand = ad_group.get("brand", "designer")
            return (brand[:15].replace(" ", "-").lower(), cat_slug)

        elif theme == "product_type":
            product_type = ad_group.get("product_type", "products")
            return (cat_slug, product_type[:15].replace(" ", "-").lower())

        elif theme == "price_tier":
            return ("luxury", cat_slug)

        elif theme == "commercial":
            return (cat_slug, "sale")

        elif theme == "material":
            return (cat_slug, "quality")

        elif theme == "use_case":
            return (cat_slug, "functional")

        else:
            return (cat_slug, "shop")

    def _get_fallback_ad(self, ad_group: Dict, category_name: str) -> Dict:
        """Generate fallback ad based on theme."""
        theme = ad_group.get("theme", "general")
        path1, path2 = self._get_url_paths(ad_group, category_name)

        if theme == "brand":
            brand = ad_group.get("brand", "Designer")
            headlines = [
                f"Shop {brand} {category_name}"[:30],
                f"Authentic {brand} Collection"[:30],
                f"Official {brand} Stockist"[:30],
                "Free UK Delivery"
            ]
            descriptions = [
                f"Discover our {brand} {category_name} range. Authentic designer pieces."[:90],
                "Fast delivery. Easy returns. Shop with confidence."[:90]
            ]
        elif theme == "product_type":
            ptype = ad_group.get("product_type", "Products").title()
            headlines = [
                f"Designer Kids {ptype}"[:30],
                f"Shop Boys {ptype} Online"[:30],
                f"Premium {ptype} Collection"[:30],
                "Free Delivery Available"
            ]
            descriptions = [
                f"Browse our curated {ptype.lower()} collection. Top designer brands."[:90],
                "Quality guaranteed. Fast shipping. Easy returns."[:90]
            ]
        elif theme == "price_tier":
            headlines = [
                f"Luxury {category_name}"[:30],
                "Premium Designer Brands"[:30],
                "Exclusive Collections"[:30],
                "Shop Luxury Kids Fashion"[:30]
            ]
            descriptions = [
                f"Discover luxury {category_name}. Gucci, Moncler, Burberry & more."[:90],
                "Exceptional quality. Free delivery on orders over £100."[:90]
            ]
        elif theme == "material":
            headlines = [
                f"Quality Leather {category_name}"[:30],
                "Premium Materials Only"[:30],
                "Crafted To Last"[:30],
                "Durable & Stylish"[:30]
            ]
            descriptions = [
                f"Premium quality {category_name} in leather, canvas & more. Built to last."[:90],
                "Exceptional craftsmanship. Designer brands. Free delivery available."[:90]
            ]
        elif theme == "use_case":
            headlines = [
                f"School {category_name} For Kids"[:30],
                "Perfect For School"[:30],
                "Durable & Practical"[:30],
                "Kids Will Love These"[:30]
            ]
            descriptions = [
                f"Functional {category_name} perfect for school, travel & sports. Designer quality."[:90],
                "Built for active kids. Stylish & practical. Free returns."[:90]
            ]
        else:
            headlines = [
                f"Shop {category_name} Online"[:30],
                f"Designer {category_name}"[:30],
                "Top Brands Available"[:30],
                "Free UK Delivery"
            ]
            descriptions = [
                f"Browse our {category_name} collection. Designer brands, great prices."[:90],
                "Fast delivery. Free returns. Trusted by parents."[:90]
            ]

        return {
            "ad_group": ad_group["ad_group_name"],
            "ad_variation": 1,
            "headlines": headlines,
            "descriptions": descriptions,
            "path1": path1,
            "path2": path2,
            "final_url": "/category",
            "display_url": f"www.example.com/{path1}/{path2}"
        }

    def _create_budget_allocation(self, total_budget: float, ad_groups: List[Dict]) -> Dict:
        """Create budget allocation across ad groups."""
        daily_budget = total_budget / 30  # Assume 30-day month

        # Calculate recommended budget per ad group
        total_recommended = sum(ag.get("recommended_daily_budget", 50) for ag in ad_groups)

        allocation = []
        for ad_group in ad_groups:
            recommended = ad_group.get("recommended_daily_budget", 50)
            percentage = (recommended / total_recommended) * 100
            allocated_daily = (recommended / total_recommended) * daily_budget
            allocated_monthly = allocated_daily * 30

            allocation.append({
                "ad_group": ad_group["ad_group_name"],
                "theme": ad_group.get("theme", "general"),
                "daily_budget": round(allocated_daily, 2),
                "monthly_budget": round(allocated_monthly, 2),
                "percentage": round(percentage, 1),
                "priority": ad_group["priority"]
            })

        return {
            "daily_budget": round(daily_budget, 2),
            "monthly_budget": total_budget,
            "allocation_by_ad_group": allocation,
            "reserve_budget": round(daily_budget * 0.1, 2),
            "testing_budget": round(daily_budget * 0.15, 2)
        }

    def _generate_negative_keywords(self, category_insights: Dict) -> Dict:
        """Generate negative keyword lists."""
        category_name = category_insights.get("category_name", "Products")

        return {
            "account_level": [
                "free",
                "diy",
                "pattern",
                "template",
                "job",
                "career",
                "salary",
                "wholesale"
            ],
            "campaign_level": [
                "second hand",
                "used",
                "vintage",
                "handmade",
                "knitting",
                "sewing"
            ],
            "competitor_brands": [
                # Would list actual competitor brands
                "competitor1",
                "competitor2"
            ]
        }

    def _generate_targeting_settings(self, research_data: Dict) -> Dict:
        """Generate targeting and audience settings."""
        return {
            "locations": {
                "included": ["United Kingdom"],
                "excluded": []
            },
            "languages": ["English"],
            "audiences": {
                "in_market": ["Parents", "Baby & Children's Products"],
                "affinity": ["Parenting Enthusiasts", "Family Focused"],
                "remarketing": "All website visitors - last 30 days"
            },
            "demographics": {
                "age_ranges": ["25-34", "35-44", "45-54"],
                "parental_status": ["Parent"],
                "household_income": ["Top 10%", "11-20%", "21-30%", "31-40%", "41-50%"]
            },
            "devices": {
                "mobile": {
                    "bid_adjustment": 0,
                    "percentage_of_traffic": "60%"
                },
                "desktop": {
                    "bid_adjustment": 10,
                    "percentage_of_traffic": "30%"
                },
                "tablet": {
                    "bid_adjustment": -10,
                    "percentage_of_traffic": "10%"
                }
            },
            "ad_schedule": {
                "days": "Monday-Sunday",
                "hours": "6 AM - 11 PM",
                "bid_adjustments": {
                    "weekday_mornings": 15,
                    "weekday_evenings": 20,
                    "weekend_all_day": 10
                }
            }
        }

    def _generate_tracking_setup(self) -> Dict:
        """Generate conversion tracking setup."""
        return {
            "conversion_actions": [
                {
                    "name": "Purchase",
                    "value": 50,
                    "count": "One per click"
                },
                {
                    "name": "Add to Cart",
                    "value": 5,
                    "count": "Every"
                },
                {
                    "name": "Newsletter Signup",
                    "value": 10,
                    "count": "One per click"
                }
            ],
            "tracking_template": "{lpurl}?utm_source=google&utm_medium=cpc&utm_campaign={campaignid}&utm_content={adgroupid}",
            "gtm_setup": "Required: Set up Google Tag Manager with Google Ads conversion tracking",
            "enhanced_conversions": "Recommended: Enable for better attribution"
        }

    def _generate_campaign_types(self, budget: float, category_insights: Dict, products: List[Dict]) -> Dict:
        """
        Generate recommendations for different Google Ads campaign types.

        Args:
            budget: Monthly budget
            category_insights: Category analysis data
            products: List of products

        Returns:
            Dict with campaign type recommendations
        """
        category_name = category_insights.get("category_name", "Products")
        price_range = category_insights.get("price_range", {})
        avg_price = price_range.get("avg", 50)
        product_count = len(products)

        # Determine if Shopping campaigns are viable (need product feed)
        has_sufficient_products = product_count >= 20
        is_high_aov = avg_price >= 30  # High average order value

        campaign_types = {
            "search": {
                "name": "Search Campaigns",
                "recommended": True,
                "priority": "High",
                "description": "Text ads shown on Google Search results",
                "best_for": "Capturing high-intent buyers actively searching",
                "expected_roas": "3.0x - 5.0x",
                "recommended_budget_percentage": 40,
                "setup_complexity": "Medium",
                "time_to_results": "1-2 weeks",
                "subtypes": [
                    {
                        "name": "Brand Search",
                        "description": "Protect brand terms and competitor conquesting",
                        "budget_percentage": 10,
                        "expected_roas": "8.0x - 12.0x"
                    },
                    {
                        "name": "Non-Brand Search",
                        "description": "Generic category and product keywords",
                        "budget_percentage": 30,
                        "expected_roas": "2.5x - 4.0x"
                    }
                ]
            },
            "performance_max": {
                "name": "Performance Max",
                "recommended": has_sufficient_products,
                "priority": "High" if has_sufficient_products else "Medium",
                "description": "AI-driven campaigns across all Google channels",
                "best_for": "Maximising conversions with automated optimisation",
                "expected_roas": "2.5x - 4.5x",
                "recommended_budget_percentage": 35 if has_sufficient_products else 20,
                "setup_complexity": "Low",
                "time_to_results": "2-4 weeks (learning period)",
                "requirements": [
                    "Product feed in Google Merchant Center",
                    "High-quality images and videos",
                    "Conversion tracking set up",
                    "Audience signals configured"
                ],
                "asset_groups": [
                    {
                        "name": f"Premium {category_name}",
                        "theme": "Luxury/Designer products",
                        "audience_signals": ["In-market: Luxury Shoppers", "Affinity: Fashion Enthusiasts"]
                    },
                    {
                        "name": f"Value {category_name}",
                        "theme": "Best value products",
                        "audience_signals": ["In-market: Bargain Hunters", "Affinity: Budget Conscious Parents"]
                    }
                ]
            },
            "shopping": {
                "name": "Standard Shopping",
                "recommended": has_sufficient_products,
                "priority": "High" if has_sufficient_products else "Low",
                "description": "Product listing ads with images and prices",
                "best_for": "Visual product discovery with price comparison",
                "expected_roas": "4.0x - 6.0x",
                "recommended_budget_percentage": 25 if has_sufficient_products else 0,
                "setup_complexity": "Medium",
                "time_to_results": "1-2 weeks",
                "requirements": [
                    "Google Merchant Center account",
                    "Product feed with accurate data",
                    "Competitive pricing"
                ],
                "campaign_structure": {
                    "priority_high": {
                        "name": "Shopping - High Priority (Brands)",
                        "products": "Top designer brands only",
                        "bid_strategy": "Target ROAS 400%"
                    },
                    "priority_medium": {
                        "name": "Shopping - Medium Priority (Category)",
                        "products": "All category products",
                        "bid_strategy": "Maximize Conversion Value"
                    },
                    "priority_low": {
                        "name": "Shopping - Low Priority (Catchall)",
                        "products": "Everything else",
                        "bid_strategy": "Manual CPC (conservative)"
                    }
                }
            },
            "display": {
                "name": "Display Campaigns",
                "recommended": budget >= 3000,
                "priority": "Medium",
                "description": "Visual banner ads across Google Display Network",
                "best_for": "Brand awareness and remarketing",
                "expected_roas": "1.5x - 3.0x",
                "recommended_budget_percentage": 10,
                "setup_complexity": "Medium",
                "time_to_results": "2-4 weeks",
                "subtypes": [
                    {
                        "name": "Remarketing",
                        "description": "Re-engage past visitors",
                        "budget_percentage": 7,
                        "expected_roas": "4.0x - 8.0x",
                        "audiences": ["All visitors - 30 days", "Cart abandoners - 14 days", "Past purchasers - 90 days"]
                    },
                    {
                        "name": "Prospecting",
                        "description": "Find new customers with similar audiences",
                        "budget_percentage": 3,
                        "expected_roas": "1.0x - 2.0x",
                        "audiences": ["Similar to purchasers", "In-market: Children's Products"]
                    }
                ]
            },
            "youtube": {
                "name": "YouTube Video Campaigns",
                "recommended": budget >= 5000 and is_high_aov,
                "priority": "Low" if budget < 5000 else "Medium",
                "description": "Video ads on YouTube",
                "best_for": "Brand storytelling and product demonstrations",
                "expected_roas": "1.0x - 2.5x",
                "recommended_budget_percentage": 5 if budget >= 5000 else 0,
                "setup_complexity": "High",
                "time_to_results": "4-8 weeks",
                "requirements": [
                    "High-quality video content",
                    "Budget for video production",
                    "Clear brand message"
                ],
                "ad_formats": [
                    {"name": "Skippable In-Stream", "best_for": "Brand awareness", "min_budget": "£50/day"},
                    {"name": "Non-Skippable In-Stream", "best_for": "Key messages", "min_budget": "£75/day"},
                    {"name": "Video Discovery", "best_for": "Engagement", "min_budget": "£30/day"}
                ]
            },
            "demand_gen": {
                "name": "Demand Gen Campaigns",
                "recommended": budget >= 4000,
                "priority": "Medium",
                "description": "Visual campaigns across YouTube, Gmail, and Discover",
                "best_for": "Mid-funnel engagement with visual storytelling",
                "expected_roas": "2.0x - 3.5x",
                "recommended_budget_percentage": 10 if budget >= 4000 else 0,
                "setup_complexity": "Medium",
                "time_to_results": "3-6 weeks",
                "requirements": [
                    "High-quality images (multiple aspect ratios)",
                    "Compelling headlines and descriptions",
                    "Strong audience signals"
                ]
            }
        }

        return campaign_types

    def _generate_kpi_targets(self, budget: float, category_insights: Dict, products: List[Dict]) -> Dict:
        """
        Generate KPI targets including ROAS, profitability, and other metrics.

        Args:
            budget: Monthly budget
            category_insights: Category analysis data
            products: List of products

        Returns:
            Dict with KPI targets and benchmarks
        """
        price_range = category_insights.get("price_range", {})
        avg_price = price_range.get("avg", 50)
        min_price = price_range.get("min", 20)
        max_price = price_range.get("max", 200)

        # Estimate margins based on price tier (luxury = higher margin)
        if avg_price >= 100:
            estimated_margin = 0.45  # 45% margin for luxury
            margin_tier = "Premium/Luxury"
        elif avg_price >= 50:
            estimated_margin = 0.35  # 35% margin for mid-range
            margin_tier = "Mid-Range"
        else:
            estimated_margin = 0.25  # 25% margin for value
            margin_tier = "Value"

        # Calculate break-even ROAS
        break_even_roas = 1 / estimated_margin

        # Target ROAS should be above break-even for profitability
        target_roas = break_even_roas * 1.5  # 50% above break-even
        stretch_roas = break_even_roas * 2.0  # 100% above break-even

        # Calculate estimated metrics based on budget
        estimated_cpc = 0.80 if avg_price < 50 else (1.20 if avg_price < 100 else 1.80)
        estimated_ctr = 0.035  # 3.5% CTR
        estimated_cvr = 0.025  # 2.5% conversion rate

        estimated_clicks = budget / estimated_cpc
        estimated_conversions = estimated_clicks * estimated_cvr
        estimated_revenue = estimated_conversions * avg_price
        estimated_profit = (estimated_revenue * estimated_margin) - budget

        kpi_targets = {
            "profitability_analysis": {
                "margin_tier": margin_tier,
                "estimated_gross_margin": f"{estimated_margin * 100:.0f}%",
                "break_even_roas": round(break_even_roas, 2),
                "target_roas_for_profit": round(target_roas, 2),
                "explanation": f"With an estimated {estimated_margin*100:.0f}% gross margin, you need at least {break_even_roas:.1f}x ROAS to break even. Target {target_roas:.1f}x for healthy profitability."
            },
            "roas_targets": {
                "minimum_roas": round(break_even_roas, 2),
                "target_roas": round(target_roas, 2),
                "stretch_roas": round(stretch_roas, 2),
                "by_campaign_type": {
                    "brand_search": {"target": 8.0, "minimum": 5.0},
                    "non_brand_search": {"target": round(target_roas, 2), "minimum": round(break_even_roas, 2)},
                    "shopping": {"target": round(target_roas * 1.2, 2), "minimum": round(break_even_roas, 2)},
                    "performance_max": {"target": round(target_roas, 2), "minimum": round(break_even_roas * 0.9, 2)},
                    "display_remarketing": {"target": 5.0, "minimum": 3.0},
                    "display_prospecting": {"target": 2.0, "minimum": 1.0}
                }
            },
            "efficiency_targets": {
                "target_cpa": round(avg_price * estimated_margin * 0.4, 2),  # 40% of margin
                "maximum_cpa": round(avg_price * estimated_margin * 0.6, 2),  # 60% of margin
                "target_cpc": round(estimated_cpc, 2),
                "target_ctr": "3.0% - 5.0%",
                "target_cvr": "2.0% - 4.0%",
                "target_impression_share": "60% - 80%"
            },
            "revenue_targets": {
                "monthly_budget": budget,
                "target_revenue": round(budget * target_roas, 2),
                "stretch_revenue": round(budget * stretch_roas, 2),
                "target_orders": round(budget * target_roas / avg_price, 0),
                "target_aov": round(avg_price * 1.1, 2),  # 10% above current avg
                "target_profit": round((budget * target_roas * estimated_margin) - budget, 2)
            },
            "estimated_performance": {
                "monthly_clicks": round(estimated_clicks, 0),
                "monthly_conversions": round(estimated_conversions, 0),
                "estimated_revenue": round(estimated_revenue, 2),
                "estimated_roas": round(estimated_revenue / budget, 2),
                "estimated_profit": round(estimated_profit, 2),
                "profit_margin_on_adspend": f"{(estimated_profit / budget) * 100:.1f}%" if budget > 0 else "N/A"
            },
            "optimization_thresholds": {
                "pause_threshold": {
                    "roas_below": round(break_even_roas * 0.7, 2),
                    "cpa_above": round(avg_price * estimated_margin * 0.8, 2),
                    "action": "Pause underperforming keywords/ad groups"
                },
                "scale_threshold": {
                    "roas_above": round(target_roas * 1.3, 2),
                    "cpa_below": round(avg_price * estimated_margin * 0.3, 2),
                    "action": "Increase budget by 20-30%"
                },
                "test_threshold": {
                    "min_clicks": 100,
                    "min_spend": round(budget * 0.05, 2),
                    "action": "Minimum data before optimization decisions"
                }
            },
            "benchmarks": {
                "industry": "Children's Fashion/Retail",
                "typical_cpc": "£0.60 - £1.50",
                "typical_ctr": "2.5% - 4.5%",
                "typical_cvr": "1.5% - 3.5%",
                "typical_roas": "2.5x - 5.0x",
                "source": "Industry averages - actual results vary"
            }
        }

        return kpi_targets

    def _generate_strategic_allocation(self, budget: float, campaign_types: Dict, kpi_targets: Dict) -> Dict:
        """
        Generate strategic budget allocation across campaign types.

        Args:
            budget: Monthly budget
            campaign_types: Campaign type recommendations
            kpi_targets: KPI targets

        Returns:
            Dict with strategic budget allocation
        """
        daily_budget = budget / 30

        # Calculate allocation based on recommendations
        campaign_mix = []
        total_percentage = 0

        # Priority order for budget allocation
        priority_order = ["search", "performance_max", "shopping", "display", "demand_gen", "youtube"]

        for campaign_key in priority_order:
            campaign = campaign_types.get(campaign_key, {})
            if campaign.get("recommended", False):
                percentage = campaign.get("recommended_budget_percentage", 0)
                if total_percentage + percentage <= 100:
                    monthly_allocation = budget * (percentage / 100)
                    daily_allocation = monthly_allocation / 30

                    campaign_mix.append({
                        "campaign_type": campaign.get("name", campaign_key),
                        "percentage": percentage,
                        "monthly_budget": round(monthly_allocation, 2),
                        "daily_budget": round(daily_allocation, 2),
                        "priority": campaign.get("priority", "Medium"),
                        "expected_roas": campaign.get("expected_roas", "N/A"),
                        "time_to_results": campaign.get("time_to_results", "2-4 weeks")
                    })
                    total_percentage += percentage

        # If budget remains, allocate to testing
        remaining_percentage = 100 - total_percentage
        if remaining_percentage > 0:
            campaign_mix.append({
                "campaign_type": "Testing & Experiments",
                "percentage": remaining_percentage,
                "monthly_budget": round(budget * (remaining_percentage / 100), 2),
                "daily_budget": round((budget * (remaining_percentage / 100)) / 30, 2),
                "priority": "Low",
                "expected_roas": "Variable",
                "time_to_results": "Ongoing"
            })

        # Phase recommendations based on budget
        if budget < 2000:
            phase_recommendation = {
                "phase": "Foundation",
                "focus": "Search campaigns only",
                "rationale": "Build conversion data before expanding",
                "next_step": "Add Shopping/PMax at £3,000+ monthly"
            }
        elif budget < 5000:
            phase_recommendation = {
                "phase": "Growth",
                "focus": "Search + Shopping/Performance Max",
                "rationale": "Balanced approach for scaling",
                "next_step": "Add Display remarketing at £5,000+ monthly"
            }
        else:
            phase_recommendation = {
                "phase": "Scale",
                "focus": "Full-funnel campaigns",
                "rationale": "Budget supports multi-channel approach",
                "next_step": "Test YouTube/Demand Gen for brand building"
            }

        return {
            "campaign_mix": campaign_mix,
            "total_monthly_budget": budget,
            "total_daily_budget": round(daily_budget, 2),
            "phase_recommendation": phase_recommendation,
            "allocation_strategy": {
                "high_intent": {
                    "campaigns": ["Search (Brand)", "Shopping"],
                    "budget_percentage": "40-50%",
                    "goal": "Capture ready-to-buy customers"
                },
                "mid_funnel": {
                    "campaigns": ["Search (Non-Brand)", "Performance Max"],
                    "budget_percentage": "35-45%",
                    "goal": "Convert interested shoppers"
                },
                "awareness": {
                    "campaigns": ["Display", "YouTube", "Demand Gen"],
                    "budget_percentage": "10-20%",
                    "goal": "Build brand and drive new traffic"
                }
            },
            "scaling_rules": [
                {
                    "trigger": f"ROAS consistently above {kpi_targets['roas_targets']['stretch_roas']}x for 2 weeks",
                    "action": "Increase budget by 20%",
                    "focus": "Scale winning campaigns first"
                },
                {
                    "trigger": f"ROAS below {kpi_targets['roas_targets']['minimum_roas']}x for 2 weeks",
                    "action": "Reduce budget by 20% or pause",
                    "focus": "Reallocate to better performers"
                },
                {
                    "trigger": "Campaign limited by budget with strong ROAS",
                    "action": "Prioritize budget increase",
                    "focus": "Don't leave money on the table"
                }
            ],
            "monthly_review_checklist": [
                "Compare actual ROAS vs targets by campaign type",
                "Review search term reports for negative keyword opportunities",
                "Check impression share - increase budget if limited",
                "Analyze device and time-of-day performance",
                "Review audience performance in PMax/Display",
                "Test new ad copy variations",
                "Update product feed if using Shopping/PMax"
            ]
        }
