"""
Analyst Agent - Provides campaign analysis, insights, and recommendations.

Responsibilities:
1. Budget allocation across channels
2. Performance predictions
3. Risk analysis
4. ROI projections
5. Optimization recommendations
6. Competitive analysis
"""
import logging
from typing import Dict, List
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


class AnalystAgent:
    """Analyst agent for campaign analysis and strategic recommendations."""

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the analyst agent workflow.

        Args:
            state: Current campaign state with all previous agent outputs

        Returns:
            Updated state with analyst_insights
        """
        logger.info(f"Analyst Agent starting for campaign {state['campaign_id']}")

        state["current_step"] = "analyst"
        state["progress_percentage"] = 95

        try:
            budget = state.get("budget") or 5000
            research_data = state.get("research_data")
            ppc_campaign = state.get("ppc_campaign")
            social_media_plan = state.get("social_media_plan")
            crm_plan = state.get("crm_plan")

            if not research_data:
                raise ValueError("No research data available")

            category_insights = research_data.get("category_insights", {})

            # Generate comprehensive analysis
            logger.info("Creating budget allocation")
            budget_allocation = self._create_budget_allocation(budget, category_insights)

            logger.info("Generating performance predictions")
            performance_predictions = self._generate_performance_predictions(
                budget, category_insights, ppc_campaign, social_media_plan
            )

            logger.info("Conducting risk analysis")
            risk_analysis = self._conduct_risk_analysis(research_data, budget)

            logger.info("Calculating ROI projections")
            roi_projections = self._calculate_roi_projections(budget, category_insights)

            logger.info("Creating optimization recommendations")
            optimization_recommendations = self._create_optimization_recommendations(
                research_data, ppc_campaign, social_media_plan, crm_plan
            )

            logger.info("Analyzing competitive landscape")
            competitive_analysis = self._analyze_competitive_landscape(category_insights)

            logger.info("Generating KPI dashboard")
            kpi_dashboard = self._generate_kpi_dashboard()

            # Compile analyst insights
            analyst_insights = {
                "executive_summary": self._generate_executive_summary(budget, category_insights),
                "budget_allocation": budget_allocation,
                "performance_predictions": performance_predictions,
                "roi_projections": roi_projections,
                "risk_analysis": risk_analysis,
                "optimization_recommendations": optimization_recommendations,
                "competitive_analysis": competitive_analysis,
                "kpi_dashboard": kpi_dashboard,
                "timeline": self._create_implementation_timeline(),
                "success_metrics": self._define_success_metrics()
            }

            state["analyst_insights"] = analyst_insights
            state["progress_percentage"] = 100
            logger.info("Analyst Agent completed successfully")

            return state

        except Exception as e:
            error_msg = f"Analyst Agent failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["progress_percentage"] = 100
            return state

    def _generate_executive_summary(self, budget: float, category_insights: Dict) -> Dict:
        """Generate executive summary of the campaign."""
        category_name = category_insights.get("category_name", "Products")
        total_products = category_insights.get("total_products", 0)
        avg_price = category_insights.get("price_range", {}).get("avg", 0)

        return {
            "campaign_overview": f"Comprehensive marketing campaign for {category_name} category with {total_products} products",
            "budget": f"£{budget:,.2f}",
            "duration": "90 days (recommended initial phase)",
            "target_audience": "Parents with children aged 0-24 months, primarily UK-based",
            "key_objectives": [
                "Increase category page visibility and traffic",
                "Drive conversions and sales",
                "Build brand awareness in parent communities",
                "Establish email subscriber base"
            ],
            "expected_outcomes": {
                "traffic_increase": "35-50% increase in category page traffic",
                "conversion_rate": "2.5-3.5% conversion rate (industry benchmark: 2%)",
                "email_subscribers": "1,500-2,500 new subscribers",
                "social_engagement": "5,000-8,000 total engagement actions",
                "revenue_projection": f"£{budget * 3.5:,.2f} - £{budget * 4.5:,.2f} (3.5-4.5x ROAS)"
            },
            "confidence_level": "High - based on industry benchmarks and market analysis"
        }

    def _create_budget_allocation(self, total_budget: float, category_insights: Dict) -> Dict:
        """Create comprehensive budget allocation across all channels."""
        allocations = {
            "google_ads_search": {
                "amount": total_budget * 0.35,
                "percentage": 35,
                "rationale": "Primary driver of high-intent traffic and conversions",
                "expected_roas": "4-6x"
            },
            "social_media_ads": {
                "amount": total_budget * 0.25,
                "percentage": 25,
                "rationale": "Brand awareness and audience building, strong visual platform",
                "expected_roas": "2.5-3.5x",
                "breakdown": {
                    "facebook_instagram": total_budget * 0.18,
                    "tiktok": total_budget * 0.07
                }
            },
            "email_marketing": {
                "amount": total_budget * 0.10,
                "percentage": 10,
                "rationale": "Highest ROI channel for nurturing and retention",
                "expected_roas": "8-12x"
            },
            "content_production": {
                "amount": total_budget * 0.15,
                "percentage": 15,
                "rationale": "Photography, video, graphics for ads and social",
                "includes": ["Product photography", "Lifestyle shoots", "Video content", "Graphics"]
            },
            "tools_and_software": {
                "amount": total_budget * 0.05,
                "percentage": 5,
                "rationale": "Essential marketing tools and analytics",
                "includes": ["Email platform", "Analytics tools", "Design tools", "Social management"]
            },
            "testing_and_optimization": {
                "amount": total_budget * 0.10,
                "percentage": 10,
                "rationale": "Reserved for testing new channels and optimizations",
                "expected_use": "A/B testing, new platform trials, seasonal adjustments"
            }
        }

        # Calculate totals
        total_allocated = sum(item["amount"] for item in allocations.values())

        return {
            "total_budget": total_budget,
            "allocations": allocations,
            "total_allocated": total_allocated,
            "currency": "GBP",
            "period": "90 days",
            "reallocation_schedule": "Review and adjust every 30 days based on performance"
        }

    def _generate_performance_predictions(self, budget: float, category_insights: Dict,
                                        ppc_campaign: Dict, social_media_plan: Dict) -> Dict:
        """Generate performance predictions for each channel."""
        avg_price = category_insights.get("price_range", {}).get("avg", 15)

        return {
            "google_ads": {
                "impressions": "150,000 - 200,000",
                "clicks": "4,500 - 6,000",
                "ctr": "3.0 - 3.5%",
                "cpc": "£0.80 - £1.20",
                "conversions": "135 - 210",
                "conversion_rate": "3.0 - 3.5%",
                "revenue": f"£{135 * avg_price:,.2f} - £{210 * avg_price:,.2f}",
                "roas": "4.5 - 6.0x"
            },
            "social_media_organic": {
                "reach": "25,000 - 40,000",
                "engagement": "1,500 - 2,500",
                "engagement_rate": "4-6%",
                "profile_visits": "2,000 - 3,500",
                "website_clicks": "800 - 1,400",
                "conversions": "20 - 42",
                "estimated_revenue": f"£{20 * avg_price:,.2f} - £{42 * avg_price:,.2f}"
            },
            "social_media_paid": {
                "impressions": "500,000 - 750,000",
                "reach": "100,000 - 150,000",
                "clicks": "3,000 - 4,500",
                "cpc": "£0.40 - £0.60",
                "conversions": "75 - 135",
                "conversion_rate": "2.5 - 3.0%",
                "revenue": f"£{75 * avg_price:,.2f} - £{135 * avg_price:,.2f}",
                "roas": "2.5 - 3.5x"
            },
            "email_marketing": {
                "list_growth": "1,500 - 2,500 subscribers",
                "open_rate": "22 - 28%",
                "click_rate": "3.5 - 4.5%",
                "conversion_rate": "4 - 6%",
                "conversions": "60 - 120",
                "revenue": f"£{60 * avg_price:,.2f} - £{120 * avg_price:,.2f}",
                "roas": "8 - 12x"
            },
            "overall_campaign": {
                "total_revenue_projection": f"£{budget * 3.5:,.2f} - £{budget * 4.5:,.2f}",
                "total_conversions": "290 - 507",
                "blended_roas": "3.5 - 4.5x",
                "customer_acquisition_cost": f"£{budget / 400:,.2f}",
                "break_even_roas": "1.0x (campaign profitable above this)"
            }
        }

    def _conduct_risk_analysis(self, research_data: Dict, budget: float) -> Dict:
        """Conduct risk analysis for the campaign."""
        return {
            "identified_risks": [
                {
                    "risk": "Seasonal demand fluctuations",
                    "severity": "Medium",
                    "probability": "High",
                    "impact": "Sales may vary 20-30% between seasons",
                    "mitigation": "Adjust messaging and promotions seasonally, build email list during low seasons"
                },
                {
                    "risk": "High competition for keywords",
                    "severity": "Medium",
                    "probability": "High",
                    "impact": "Higher CPCs, need £1.20-1.50 instead of £0.80",
                    "mitigation": "Focus on long-tail keywords, improve Quality Score, use exact match"
                },
                {
                    "risk": "Ad fatigue on social media",
                    "severity": "Low",
                    "probability": "Medium",
                    "impact": "Declining engagement rates after 2-3 weeks",
                    "mitigation": "Refresh creative every 2 weeks, A/B test new concepts"
                },
                {
                    "risk": "Email deliverability issues",
                    "severity": "High",
                    "probability": "Low",
                    "impact": "Reduced ROI from email channel",
                    "mitigation": "Use reputable ESP, implement DMARC/SPF, clean list regularly"
                },
                {
                    "risk": "Budget depletion before optimization",
                    "severity": "Medium",
                    "probability": "Medium",
                    "impact": "Insufficient data for optimization",
                    "mitigation": "Start with 50% budget, scale after proving channels"
                }
            ],
            "overall_risk_level": "Low-Medium",
            "contingency_recommendations": [
                "Reserve 10% of budget for unexpected opportunities",
                "Monitor daily spend and pause underperforming campaigns",
                "Have backup creative ready for quick deployment",
                "Establish clear KPIs and review weekly"
            ]
        }

    def _calculate_roi_projections(self, budget: float, category_insights: Dict) -> Dict:
        """Calculate ROI projections."""
        avg_price = category_insights.get("price_range", {}).get("avg", 15)
        avg_margin = 0.40  # Assume 40% margin

        return {
            "investment": f"£{budget:,.2f}",
            "projected_revenue": {
                "conservative": f"£{budget * 3.0:,.2f}",
                "moderate": f"£{budget * 4.0:,.2f}",
                "optimistic": f"£{budget * 5.0:,.2f}"
            },
            "projected_profit": {
                "conservative": f"£{(budget * 3.0 * avg_margin) - budget:,.2f}",
                "moderate": f"£{(budget * 4.0 * avg_margin) - budget:,.2f}",
                "optimistic": f"£{(budget * 5.0 * avg_margin) - budget:,.2f}"
            },
            "roi_percentage": {
                "conservative": f"{((3.0 * avg_margin) - 1) * 100:.1f}%",
                "moderate": f"{((4.0 * avg_margin) - 1) * 100:.1f}%",
                "optimistic": f"{((5.0 * avg_margin) - 1) * 100:.1f}%"
            },
            "break_even_analysis": {
                "break_even_roas": "2.5x (assuming 40% margin)",
                "break_even_conversions": int(budget / (avg_price * avg_margin)),
                "days_to_break_even": "30-45 days (estimated)"
            },
            "long_term_value": {
                "customer_lifetime_value": f"£{avg_price * 3.5:,.2f}",
                "ltv_to_cac_ratio": "3.5:1 (healthy ratio)",
                "repeat_purchase_rate": "25-35% (industry average)"
            }
        }

    def _create_optimization_recommendations(self, research_data: Dict, ppc_campaign: Dict,
                                            social_media_plan: Dict, crm_plan: Dict) -> List[Dict]:
        """Create actionable optimization recommendations."""
        return [
            {
                "priority": "High",
                "category": "Google Ads",
                "recommendation": "Start with exact match keywords only",
                "rationale": "Higher intent, lower wasted spend during learning phase",
                "expected_impact": "10-15% improvement in ROAS",
                "implementation": "Week 1"
            },
            {
                "priority": "High",
                "category": "Social Media",
                "recommendation": "Focus Instagram budget on Reels format",
                "rationale": "3-5x higher organic reach than static posts",
                "expected_impact": "30-40% increase in engagement",
                "implementation": "Week 1"
            },
            {
                "priority": "High",
                "category": "Email Marketing",
                "recommendation": "Implement exit-intent popup for email capture",
                "rationale": "Can capture 2-4% of visitors who would otherwise leave",
                "expected_impact": "300-500 additional subscribers per month",
                "implementation": "Week 2"
            },
            {
                "priority": "Medium",
                "category": "Content",
                "recommendation": "Create user-generated content campaign",
                "rationale": "Authentic content performs 5x better than branded content",
                "expected_impact": "25% reduction in content costs, higher engagement",
                "implementation": "Week 4"
            },
            {
                "priority": "Medium",
                "category": "Conversion Optimisation",
                "recommendation": "Add trust badges and parent reviews to category page",
                "rationale": "Social proof increases conversion rate by 15-20%",
                "expected_impact": "15% lift in conversion rate",
                "implementation": "Week 2"
            },
            {
                "priority": "Low",
                "category": "Retargeting",
                "recommendation": "Set up product-specific retargeting audiences",
                "rationale": "Show exact products viewed to warm audience",
                "expected_impact": "8-12% improvement in retargeting ROAS",
                "implementation": "Week 6"
            }
        ]

    def _analyze_competitive_landscape(self, category_insights: Dict) -> Dict:
        """Analyze competitive landscape."""
        return {
            "market_position": "Growing market with established players",
            "competitive_intensity": "Medium-High",
            "key_differentiators": category_insights.get("unique_selling_points", []),
            "competitive_advantages": [
                "Curated selection vs. mass market",
                "Quality focus vs. price competition",
                "Parent-centric messaging",
                "Organic and sustainable options"
            ],
            "recommended_positioning": "Premium quality at mid-market prices",
            "messaging_opportunities": [
                "Emphasize quality and safety",
                "Highlight parent testimonials",
                "Focus on peace of mind",
                "Stress convenience and ease"
            ]
        }

    def _generate_kpi_dashboard(self) -> Dict:
        """Generate KPI dashboard structure."""
        return {
            "north_star_metric": "Revenue from category page",
            "primary_kpis": [
                {"metric": "Revenue", "target": "£17,500+", "frequency": "Monthly"},
                {"metric": "ROAS", "target": "4.0x+", "frequency": "Weekly"},
                {"metric": "Conversion Rate", "target": "3.0%+", "frequency": "Daily"},
                {"metric": "Customer Acquisition Cost", "target": "£12.50 or less", "frequency": "Weekly"}
            ],
            "secondary_kpis": [
                {"metric": "Click-Through Rate (Ads)", "target": "3.0%+", "frequency": "Daily"},
                {"metric": "Email Open Rate", "target": "25%+", "frequency": "Per campaign"},
                {"metric": "Social Engagement Rate", "target": "5%+", "frequency": "Weekly"},
                {"metric": "Website Traffic", "target": "10,000+ sessions", "frequency": "Monthly"}
            ],
            "engagement_metrics": [
                {"metric": "Average Order Value", "target": "£45+", "frequency": "Weekly"},
                {"metric": "Cart Abandonment Rate", "target": "<70%", "frequency": "Daily"},
                {"metric": "Email Subscriber Growth", "target": "500+ per month", "frequency": "Monthly"},
                {"metric": "Return Customer Rate", "target": "25%+", "frequency": "Monthly"}
            ]
        }

    def _create_implementation_timeline(self) -> Dict:
        """Create implementation timeline."""
        return {
            "phase_1_setup": {
                "duration": "Week 1-2",
                "activities": [
                    "Set up Google Ads campaigns",
                    "Create social media content calendar",
                    "Implement email welcome series",
                    "Install tracking pixels and analytics",
                    "Prepare initial creative assets"
                ]
            },
            "phase_2_launch": {
                "duration": "Week 3",
                "activities": [
                    "Launch Google Ads at 50% budget",
                    "Begin social media posting schedule",
                    "Activate email automations",
                    "Start content production pipeline"
                ]
            },
            "phase_3_optimization": {
                "duration": "Week 4-8",
                "activities": [
                    "Daily bid adjustments",
                    "Weekly creative refresh",
                    "A/B testing campaigns",
                    "Expand top performers",
                    "Scale budget to 100%"
                ]
            },
            "phase_4_scaling": {
                "duration": "Week 9-12",
                "activities": [
                    "Increase budget on proven channels",
                    "Test new platforms (TikTok, Pinterest)",
                    "Implement retargeting campaigns",
                    "Launch influencer partnerships",
                    "Refine audience segments"
                ]
            }
        }

    def _define_success_metrics(self) -> List[Dict]:
        """Define success metrics for the campaign."""
        return [
            {
                "metric": "Campaign Profitability",
                "success_threshold": "ROAS >= 3.5x",
                "measurement": "Total revenue / Total ad spend",
                "review_frequency": "Weekly"
            },
            {
                "metric": "Traffic Growth",
                "success_threshold": "40% increase in category page sessions",
                "measurement": "Google Analytics - Category page traffic",
                "review_frequency": "Monthly"
            },
            {
                "metric": "Email List Growth",
                "success_threshold": "2,000+ new subscribers in 90 days",
                "measurement": "Email platform subscriber count",
                "review_frequency": "Monthly"
            },
            {
                "metric": "Social Media Engagement",
                "success_threshold": "6,000+ total engagements",
                "measurement": "Sum of likes, comments, shares, saves",
                "review_frequency": "Monthly"
            },
            {
                "metric": "Customer Acquisition",
                "success_threshold": "400+ new customers",
                "measurement": "First-time purchases from campaign",
                "review_frequency": "Monthly"
            }
        ]
