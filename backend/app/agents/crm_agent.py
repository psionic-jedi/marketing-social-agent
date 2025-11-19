"""
CRM Agent - Creates email marketing campaigns using MJML.

Responsibilities:
1. Design welcome email series
2. Create promotional email campaigns
3. Generate cart abandonment emails
4. Build customer segmentation strategy
5. Create email automation workflows
6. Generate MJML templates
"""
import logging
from typing import Dict, List
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


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
            segmentation_strategy = self._create_segmentation_strategy()

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
        """Generate 3-email welcome series with MJML templates."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        hero_section = content_outputs.get("hero_section", {})

        welcome_emails = []

        # Email 1: Welcome + Brand Introduction
        welcome_emails.append({
            "email_number": 1,
            "send_timing": "Immediately after signup",
            "subject_line": f"Welcome! Discover Our {category_name} Collection",
            "preheader": f"Your journey to quality {category_name} starts here ✨",
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
                    "type": "text",
                    "content": f"We're thrilled to have you! Discover our carefully curated {category_name} collection, designed with parents in mind."
                },
                {
                    "type": "features",
                    "features": content_outputs.get("features", [])[:3]
                }
            ],
            "mjml_template": self._generate_mjml_welcome_email(category_name, hero_section)
        })

        # Email 2: Educational Content
        welcome_emails.append({
            "email_number": 2,
            "send_timing": "2 days after signup",
            "subject_line": f"Your Guide to Choosing the Perfect {category_name}",
            "preheader": "Everything you need to know",
            "content_blocks": [
                {
                    "type": "header",
                    "headline": f"Choosing the Best {category_name}",
                    "image": "guide-header.jpg"
                },
                {
                    "type": "tips",
                    "tips": research_data.get("parent_questions", [])[:3]
                },
                {
                    "type": "cta",
                    "text": "Browse Our Collection",
                    "url": "/shop"
                }
            ],
            "mjml_template": self._generate_mjml_educational_email(category_name, research_data)
        })

        # Email 3: Special Offer
        welcome_emails.append({
            "email_number": 3,
            "send_timing": "5 days after signup",
            "subject_line": "🎁 Here's 15% Off Your First Order",
            "preheader": "A special welcome gift just for you",
            "content_blocks": [
                {
                    "type": "hero",
                    "headline": "Welcome Gift: 15% Off",
                    "subheadline": "Use code WELCOME15 at checkout",
                    "image": "discount-banner.jpg",
                    "cta": "Claim Your Discount",
                    "cta_url": "/shop?discount=WELCOME15"
                },
                {
                    "type": "social_proof",
                    "heading": "Join thousands of happy parents",
                    "testimonials": 2
                }
            ],
            "mjml_template": self._generate_mjml_offer_email("WELCOME15")
        })

        return welcome_emails

    def _generate_promotional_campaigns(self, research_data: Dict, content_outputs: Dict) -> List[Dict]:
        """Generate promotional email campaigns."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")

        campaigns = [
            {
                "campaign_name": "New Arrivals Announcement",
                "send_date": "Monthly - 1st week",
                "subject_line": f"New {category_name} Just Arrived! 🎉",
                "target_segment": "All subscribers",
                "goal": "Drive traffic to new products",
                "mjml_template_type": "Product showcase"
            },
            {
                "campaign_name": "Seasonal Sale",
                "send_date": "Quarterly",
                "subject_line": f"Seasonal Sale: Up to 30% Off {category_name}",
                "target_segment": "Active customers + engaged subscribers",
                "goal": "Increase sales",
                "mjml_template_type": "Sale announcement"
            },
            {
                "campaign_name": "Customer Appreciation",
                "send_date": "Bi-annually",
                "subject_line": "Thank You! Here's Something Special",
                "target_segment": "Past customers",
                "goal": "Re-engagement and loyalty",
                "mjml_template_type": "Loyalty reward"
            }
        ]

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
            "mjml_template": self._generate_mjml_cart_abandonment()
        }

    def _create_segmentation_strategy(self) -> Dict:
        """Create customer segmentation strategy."""
        return {
            "segments": [
                {
                    "segment_name": "VIP Customers",
                    "criteria": "Lifetime value > £500 OR 5+ purchases",
                    "size_estimate": "5-10% of list",
                    "email_frequency": "2-3 times per week",
                    "content_strategy": "Exclusive early access, VIP sales, personalized recommendations"
                },
                {
                    "segment_name": "Active Shoppers",
                    "criteria": "Purchase in last 90 days",
                    "size_estimate": "15-20% of list",
                    "email_frequency": "2 times per week",
                    "content_strategy": "New arrivals, trending products, limited-time offers"
                },
                {
                    "segment_name": "Engaged Browsers",
                    "criteria": "Opened 3+ emails in last 30 days, no purchase yet",
                    "size_estimate": "25-30% of list",
                    "email_frequency": "1-2 times per week",
                    "content_strategy": "Educational content, social proof, first-time buyer discounts"
                },
                {
                    "segment_name": "At-Risk Customers",
                    "criteria": "No purchase in 180+ days, previously active",
                    "size_estimate": "20-25% of list",
                    "email_frequency": "1 time per week",
                    "content_strategy": "Re-engagement campaigns, special offers, feedback requests"
                },
                {
                    "segment_name": "Inactive Subscribers",
                    "criteria": "No open in 90+ days",
                    "size_estimate": "20-30% of list",
                    "email_frequency": "1 time per month",
                    "content_strategy": "Win-back campaigns, preference center, unsubscribe option"
                }
            ],
            "personalization_tactics": [
                "Product recommendations based on browse history",
                "Location-based content",
                "Child age-based segmentation",
                "Seasonal relevance"
            ]
        }

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
            "Track opens, clicks, conversions for optimization"
        ]

    def _generate_mjml_welcome_email(self, category_name: str, hero_section: Dict) -> str:
        """Generate MJML template for welcome email."""
        return f"""
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, sans-serif" />
      <mj-text font-size="14px" color="#333333" line-height="20px" />
      <mj-button background-color="#4CAF50" color="white" font-size="16px" border-radius="5px" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#f4f4f4">
    <!-- Header -->
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-image src="logo.png" width="150px" alt="Logo" />
      </mj-column>
    </mj-section>

    <!-- Hero Section -->
    <mj-section background-color="#4CAF50" padding="40px 20px">
      <mj-column>
        <mj-text color="#ffffff" font-size="32px" font-weight="bold" align="center">
          Welcome to Our Family!
        </mj-text>
        <mj-text color="#ffffff" font-size="18px" align="center">
          {hero_section.get("subheadline", "Quality products for your little ones")}
        </mj-text>
        <mj-button href="/shop" padding-top="20px">
          Start Shopping
        </mj-button>
      </mj-column>
    </mj-section>

    <!-- Content Section -->
    <mj-section background-color="#ffffff" padding="40px 20px">
      <mj-column>
        <mj-text>
          <h2>We're Thrilled to Have You!</h2>
          <p>Discover our carefully curated {category_name} collection, designed with parents in mind.</p>
        </mj-text>
      </mj-column>
    </mj-section>

    <!-- Footer -->
    <mj-section background-color="#333333" padding="20px">
      <mj-column>
        <mj-text color="#ffffff" align="center" font-size="12px">
          © 2025 Your Company. All rights reserved.
        </mj-text>
        <mj-text color="#ffffff" align="center" font-size="12px">
          <a href="/unsubscribe" style="color: #ffffff;">Unsubscribe</a>
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""

    def _generate_mjml_educational_email(self, category_name: str, research_data: Dict) -> str:
        """Generate MJML template for educational email."""
        return f"""
<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding="40px 20px">
      <mj-column>
        <mj-text font-size="28px" font-weight="bold">
          Your Guide to Choosing the Perfect {category_name}
        </mj-text>
        <mj-divider border-color="#4CAF50" border-width="2px" />
        <mj-text>
          Making the right choice for your child is important. Here's what you need to know.
        </mj-text>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""

    def _generate_mjml_offer_email(self, discount_code: str) -> str:
        """Generate MJML template for offer email."""
        return f"""
<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#FFD700" padding="60px 20px">
      <mj-column>
        <mj-text color="#333333" font-size="36px" font-weight="bold" align="center">
          Welcome Gift: 15% Off
        </mj-text>
        <mj-text color="#333333" font-size="24px" align="center">
          Use code: {discount_code}
        </mj-text>
        <mj-button href="/shop?discount={discount_code}">
          Claim Your Discount
        </mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""

    def _generate_mjml_cart_abandonment(self) -> str:
        """Generate MJML template for cart abandonment."""
        return """
<mjml>
  <mj-body background-color="#f4f4f4">
    <mj-section background-color="#ffffff" padding="40px 20px">
      <mj-column>
        <mj-text font-size="28px" font-weight="bold">
          You left something behind! 🛒
        </mj-text>
        <mj-text>
          Your items are still waiting in your cart. Complete your purchase today!
        </mj-text>
        <mj-button href="/cart">
          Return to Cart
        </mj-button>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
"""
