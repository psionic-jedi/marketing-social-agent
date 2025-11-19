"""
PPC Agent - Creates Google Ads campaign structure and ad copy.

Responsibilities:
1. Generate keyword research and grouping
2. Create ad groups with targeted keywords
3. Write compelling ad copy (headlines, descriptions)
4. Set bid recommendations
5. Create negative keyword lists
6. Define campaign structure
"""
import logging
from typing import Dict, List
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


class PPCAgent:
    """PPC agent for creating Google Ads campaigns."""

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)

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

            budget = state.get("budget", 5000)
            category_insights = research_data.get("category_insights", {})
            seo_keywords = research_data.get("seo_keywords", {})

            # Generate PPC campaign structure
            logger.info("Generating keyword strategy")
            keyword_strategy = self._generate_keyword_strategy(seo_keywords, category_insights)

            logger.info("Creating ad groups")
            ad_groups = self._create_ad_groups(keyword_strategy, category_insights)

            logger.info("Generating ad copy")
            ads = self._generate_ad_copy(ad_groups, research_data)

            logger.info("Creating budget allocation")
            budget_allocation = self._create_budget_allocation(budget, ad_groups)

            logger.info("Generating negative keywords")
            negative_keywords = self._generate_negative_keywords(category_insights)

            # Compile PPC campaign
            ppc_campaign = {
                "campaign_name": f"{category_insights.get('category_name', 'Product')} - Search Campaign",
                "campaign_type": "Search",
                "budget_daily": budget_allocation["daily_budget"],
                "budget_monthly": budget,
                "bidding_strategy": "Maximize Conversions",
                "keyword_strategy": keyword_strategy,
                "ad_groups": ad_groups,
                "ads": ads,
                "negative_keywords": negative_keywords,
                "budget_allocation": budget_allocation,
                "targeting": self._generate_targeting_settings(research_data),
                "tracking": self._generate_tracking_setup()
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

    def _generate_keyword_strategy(self, seo_keywords: Dict, category_insights: Dict) -> Dict:
        """Generate comprehensive keyword strategy."""
        category_name = category_insights.get("category_name", "Products")

        # Extract keywords from research
        primary_keywords = seo_keywords.get("primary", [])
        secondary_keywords = seo_keywords.get("secondary", [])
        long_tail_keywords = seo_keywords.get("long_tail", [])

        # Add product-specific keywords
        branded_keywords = [
            f"{category_name}",
            f"buy {category_name}",
            f"{category_name} online"
        ]

        commercial_keywords = [
            f"{category_name} sale",
            f"best {category_name}",
            f"cheap {category_name}",
            f"quality {category_name}"
        ]

        return {
            "branded_keywords": {
                "keywords": branded_keywords,
                "match_type": "Exact",
                "bid_modifier": 1.2,
                "priority": "High"
            },
            "primary_keywords": {
                "keywords": primary_keywords[:10],
                "match_type": "Phrase",
                "bid_modifier": 1.0,
                "priority": "High"
            },
            "secondary_keywords": {
                "keywords": secondary_keywords[:15],
                "match_type": "Phrase",
                "bid_modifier": 0.8,
                "priority": "Medium"
            },
            "long_tail_keywords": {
                "keywords": long_tail_keywords[:20],
                "match_type": "Broad Match Modified",
                "bid_modifier": 0.6,
                "priority": "Medium"
            },
            "commercial_keywords": {
                "keywords": commercial_keywords,
                "match_type": "Phrase",
                "bid_modifier": 1.1,
                "priority": "High"
            }
        }

    def _create_ad_groups(self, keyword_strategy: Dict, category_insights: Dict) -> List[Dict]:
        """Create ad groups with targeted keywords."""
        category_name = category_insights.get("category_name", "Products")

        ad_groups = []

        # Branded ad group
        ad_groups.append({
            "ad_group_name": f"{category_name} - Branded",
            "keywords": keyword_strategy["branded_keywords"]["keywords"],
            "match_types": ["Exact", "Phrase"],
            "max_cpc": 1.50,
            "priority": "High",
            "recommended_daily_budget": 50
        })

        # Category ad group
        ad_groups.append({
            "ad_group_name": f"{category_name} - Category",
            "keywords": keyword_strategy["primary_keywords"]["keywords"],
            "match_types": ["Phrase", "Broad Match Modified"],
            "max_cpc": 1.20,
            "priority": "High",
            "recommended_daily_budget": 80
        })

        # Commercial intent ad group
        ad_groups.append({
            "ad_group_name": f"{category_name} - Commercial",
            "keywords": keyword_strategy["commercial_keywords"]["keywords"],
            "match_types": ["Phrase"],
            "max_cpc": 1.40,
            "priority": "High",
            "recommended_daily_budget": 60
        })

        # Long-tail ad group
        ad_groups.append({
            "ad_group_name": f"{category_name} - Long Tail",
            "keywords": keyword_strategy["long_tail_keywords"]["keywords"][:10],
            "match_types": ["Broad Match Modified", "Phrase"],
            "max_cpc": 0.90,
            "priority": "Medium",
            "recommended_daily_budget": 40
        })

        return ad_groups

    def _generate_ad_copy(self, ad_groups: List[Dict], research_data: Dict) -> List[Dict]:
        """Generate ad copy for each ad group using Claude."""
        category_insights = research_data.get("category_insights", {})
        category_name = category_insights.get("category_name", "Products")
        products = research_data.get("products", [])
        usps = category_insights.get("unique_selling_points", [])
        price_range = category_insights.get("price_range", {})

        # Generate unique ads for first 2 ad groups using Claude
        ads = []

        for i, ad_group in enumerate(ad_groups[:2]):  # Focus on main ad groups
            prompt = f"""Create 3 unique Google Ads text ad variations for the ad group: {ad_group['ad_group_name']}

Category: {category_name}
Keywords: {', '.join(ad_group.get('keywords', [])[:5])}
Products: {len(products)} items available
Price range: £{price_range.get('min', 0):.2f} - £{price_range.get('max', 0):.2f}
USPs: {', '.join(usps[:3]) if usps else 'Quality, comfort, value'}

For each ad variation, create:
- 4 headlines (30 chars each max) - compelling, keyword-rich, actionable
- 2 descriptions (90 chars each max) - benefit-focused, include USPs

Google Ads best practices:
- Include keywords in headlines
- Highlight unique benefits
- Add clear call-to-action
- Use numbers/percentages when relevant

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
                    max_tokens=2000,
                    temperature=0.7,
                    messages=[{"role": "user", "content": prompt}]
                )

                import json
                response_text = response.content[0].text.strip()
                if response_text.startswith("```"):
                    response_text = response_text.split("```")[1]
                    if response_text.startswith("json"):
                        response_text = response_text[4:]
                    response_text = response_text.strip()

                ad_data = json.loads(response_text)

                for ad_variation in ad_data.get("ads", []):
                    ads.append({
                        "ad_group": ad_group["ad_group_name"],
                        "ad_variation": ad_variation.get("variation", 1),
                        "headlines": ad_variation.get("headlines", [])[:4],
                        "descriptions": ad_variation.get("descriptions", [])[:2],
                        "path1": category_name[:15].replace(" ", "-"),
                        "path2": "shop" if i % 2 == 0 else "sale",
                        "final_url": "/category",
                        "display_url": f"www.example.com/{category_name.lower().replace(' ', '-')}"
                    })

                logger.info(f"Generated {len(ad_data.get('ads', []))} unique ads for {ad_group['ad_group_name']}")

            except Exception as e:
                logger.error(f"Error generating ads for {ad_group['ad_group_name']}: {e}", exc_info=True)
                # Fallback to template
                ads.append({
                    "ad_group": ad_group["ad_group_name"],
                    "ad_variation": 1,
                    "headlines": [
                        f"Quality {category_name} | Shop Now",
                        f"Best {category_name} Online",
                        f"Premium {category_name}",
                        f"Free Delivery Available"
                    ],
                    "descriptions": [
                        f"Shop our premium {category_name} collection. Quality guaranteed.",
                        f"Trusted by thousands of parents. Fast delivery."
                    ],
                    "path1": category_name[:15].replace(" ", "-"),
                    "path2": "shop",
                    "final_url": "/category",
                    "display_url": f"www.example.com/{category_name.lower().replace(' ', '-')}"
                })

        # Add template ads for remaining ad groups
        for ad_group in ad_groups[2:]:
            ads.append({
                "ad_group": ad_group["ad_group_name"],
                "ad_variation": 1,
                "headlines": [
                    f"{category_name} Deals",
                    f"Shop {category_name} Now",
                    f"Quality {category_name}",
                    f"Fast & Free Delivery"
                ],
                "descriptions": [
                    f"Browse our {category_name} collection. Great value.",
                    "Free returns. Excellent customer service."
                ],
                "path1": category_name[:15].replace(" ", "-"),
                "path2": "deals",
                "final_url": "/category",
                "display_url": f"www.example.com/{category_name.lower().replace(' ', '-')}"
            })

        return ads

    def _create_budget_allocation(self, total_budget: float, ad_groups: List[Dict]) -> Dict:
        """Create budget allocation across ad groups."""
        daily_budget = total_budget / 30  # Assume 30-day month

        # Calculate recommended budget per ad group
        total_recommended = sum(ag.get("recommended_daily_budget", 50) for ag in ad_groups)

        allocation = []
        for ad_group in ad_groups:
            recommended = ad_group.get("recommended_daily_budget", 50)
            percentage = (recommended / total_recommended) * 100
            allocated = (recommended / total_recommended) * daily_budget

            allocation.append({
                "ad_group": ad_group["ad_group_name"],
                "daily_budget": round(allocated, 2),
                "monthly_budget": round(allocated * 30, 2),
                "percentage": round(percentage, 1),
                "priority": ad_group["priority"]
            })

        return {
            "daily_budget": round(daily_budget, 2),
            "monthly_budget": total_budget,
            "allocation_by_ad_group": allocation,
            "reserve_budget": round(daily_budget * 0.1, 2),  # 10% reserve
            "testing_budget": round(daily_budget * 0.15, 2)  # 15% for testing
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
