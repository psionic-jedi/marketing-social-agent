import React, { useState } from 'react';
import { CampaignResults as CampaignResultsType } from '../services/api';
import './CampaignResults.css';

interface CampaignResultsProps {
  results: CampaignResultsType;
  onDelete?: () => void;
}

interface EmailPreview {
  subject: string;
  html: string;
}

const CampaignResults: React.FC<CampaignResultsProps> = ({ results, onDelete }) => {
  const [emailPreview, setEmailPreview] = useState<EmailPreview | null>(null);
  if (!results.results) {
    return (
      <div className="results-empty">
        <div className="status-badge status-running">
          <span className="status-pulse"></span>
          {results.status}
        </div>
        <p>Campaign is still processing. Results will appear here when complete.</p>
      </div>
    );
  }

  const { research_data, content_outputs, social_media_plan, ppc_campaign, meta_ads_campaign, crm_plan, analyst_insights } = results.results;

  return (
    <div className="campaign-results">
      <div className="results-header">
        <div>
          <h2>Campaign Results</h2>
          <p className="campaign-id">ID: {results.campaign_id}</p>
          {results.category_url && (
            <p className="campaign-url" style={{fontSize: '14px', color: '#666', marginTop: '5px'}}>
              <strong>Analyzed URL:</strong> <a href={results.category_url} target="_blank" rel="noopener noreferrer" style={{color: '#4CAF50'}}>{results.category_url}</a>
            </p>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div className={`status-badge status-${results.status}`}>
            {results.status === 'completed' && '✓ '}
            {results.status}
          </div>
          {onDelete && (
            <button
              className="delete-btn delete-btn-detail"
              onClick={onDelete}
              title="Delete campaign"
            >
              🗑️ Delete
            </button>
          )}
        </div>
      </div>

      {/* Research Data Section */}
      {research_data && (
        <section className="results-section">
          <h3 className="section-title">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M9 2C13.4183 2 17 5.58172 17 10C17 11.8487 16.3729 13.551 15.3199 14.9056L18.7071 18.2929L17.2929 19.7071L13.9056 16.3199C12.551 17.3729 10.8487 18 9 18C4.58172 18 1 14.4183 1 10C1 5.58172 4.58172 2 9 2ZM9 4C5.68629 4 3 6.68629 3 10C3 13.3137 5.68629 16 9 16C12.3137 16 15 13.3137 15 10C15 6.68629 12.3137 4 9 4Z" fill="currentColor"/>
            </svg>
            Research & Analysis
          </h3>

          {research_data.category_insights && (
            <div className="insight-card">
              <h4>{research_data.category_insights.category_name}</h4>
              <div className="stat-grid">
                <div className="stat-item">
                  <span className="stat-label">Products Found</span>
                  <span className="stat-value">{research_data.category_insights.total_products}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Price Range</span>
                  <span className="stat-value">
                    £{research_data.category_insights.price_range?.min} - £{research_data.category_insights.price_range?.max}
                  </span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Average Price</span>
                  <span className="stat-value">£{research_data.category_insights.price_range?.avg.toFixed(2)}</span>
                </div>
              </div>

              {research_data.category_insights.common_features && (
                <div className="features-list">
                  <h5>Common Features</h5>
                  {research_data.category_insights.common_features.map((feature: string, idx: number) => (
                    <div key={idx} className="feature-tag">{feature}</div>
                  ))}
                </div>
              )}
            </div>
          )}

          {research_data.products && research_data.products.length > 0 && (
            <div className="products-grid">
              <h5>Sample Products Analyzed ({research_data.products.length})</h5>
              {research_data.products.slice(0, 3).map((product: any, idx: number) => (
                <div key={idx} className="product-card">
                  <div className="product-header">
                    <h6>{product.name}</h6>
                    <span className="product-price">£{product.price}</span>
                  </div>
                  {product.description && (
                    <p className="product-description">{product.description}</p>
                  )}
                  {product.features && (
                    <div className="product-features">
                      {product.features.slice(0, 3).map((feature: string, fIdx: number) => (
                        <span key={fIdx} className="feature-badge">{feature}</span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Content Outputs Section */}
      {content_outputs && (
        <section className="results-section">
          <h3 className="section-title">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 4H16C17.1046 4 18 4.89543 18 6V14C18 15.1046 17.1046 16 16 16H4C2.89543 16 2 15.1046 2 14V6C2 4.89543 2.89543 4 4 4Z" stroke="currentColor" strokeWidth="2"/>
              <path d="M6 8H14M6 12H10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Generated Content
          </h3>

          {content_outputs.hero_section && (
            <div className="content-card hero-card">
              <div className="hero-badge">Hero Section</div>
              <h4 className="hero-headline">{content_outputs.hero_section.headline}</h4>
              <p className="hero-subheadline">{content_outputs.hero_section.subheadline}</p>
              <button className="hero-cta">{content_outputs.hero_section.cta_text}</button>
            </div>
          )}

          {content_outputs.features && content_outputs.features.length > 0 && (
            <div className="features-grid">
              <h5>Feature Callouts</h5>
              {content_outputs.features.map((feature: any, idx: number) => (
                <div key={idx} className="feature-card">
                  <div className="feature-icon">{feature.icon === 'quality' ? '✨' : feature.icon === 'comfort' ? '💎' : '🛡️'}</div>
                  <h6>{feature.title}</h6>
                  <p>{feature.description}</p>
                </div>
              ))}
            </div>
          )}

          {content_outputs.meta_tags && (
            <div className="seo-card">
              <h5>SEO Meta Tags</h5>
              <div className="meta-item">
                <span className="meta-label">Title:</span>
                <code>{content_outputs.meta_tags.meta_title}</code>
              </div>
              <div className="meta-item">
                <span className="meta-label">Description:</span>
                <code>{content_outputs.meta_tags.meta_description}</code>
              </div>
            </div>
          )}

          {content_outputs.image_prompts && content_outputs.image_prompts.length > 0 && (
            <div className="image-prompts-card">
              <h5>Image Generation Prompts ({content_outputs.image_prompts.length})</h5>
              {content_outputs.image_prompts.slice(0, 3).map((prompt: any, idx: number) => (
                <div key={idx} className="meta-item">
                  <span className="meta-label">{prompt.type}:</span>
                  <code>{prompt.prompt}</code>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Social Media Section */}
      {social_media_plan && (
        <section className="results-section">
          <h3 className="section-title">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M18 2H2V18H18V2Z" stroke="currentColor" strokeWidth="2"/>
              <path d="M6 7H14M6 10H14M6 13H10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Social Media Strategy
          </h3>

          {social_media_plan.tiktok && social_media_plan.tiktok.concepts && (
            <div className="social-platform">
              <h5>TikTok Content Ideas</h5>
              {social_media_plan.tiktok.concepts.slice(0, 3).map((concept: any, idx: number) => (
                <div key={idx} className="content-card">
                  <div className="concept-number">Concept {concept.concept_number || idx + 1}</div>
                  <h6>{concept.hook}</h6>
                  <p>{concept.content_idea}</p>
                  <div className="hashtags">
                    {concept.hashtags?.map((tag: string, tagIdx: number) => (
                      <span key={tagIdx} className="feature-badge">{tag}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {social_media_plan.instagram && social_media_plan.instagram.posts && (
            <div className="social-platform">
              <h5>Instagram Posts</h5>
              {social_media_plan.instagram.posts.slice(0, 3).map((post: any, idx: number) => (
                <div key={idx} className="content-card">
                  <p className="post-caption">{post.caption?.substring(0, 150)}...</p>
                  <div className="hashtags">
                    {post.hashtags?.slice(0, 5).map((tag: string, tagIdx: number) => (
                      <span key={tagIdx} className="feature-badge">{tag}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* PPC Campaign Section */}
      {ppc_campaign && ppc_campaign.ads && (
        <section className="results-section">
          <h3 className="section-title">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M4 6H16M4 10H16M4 14H10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            Google Ads Campaign
          </h3>

          <div className="ads-list">
            {ppc_campaign.ads.slice(0, 3).map((ad: any, idx: number) => (
              <div key={idx} className="content-card">
                <div className="ad-group-badge">{ad.ad_group}</div>
                <div className="ad-headlines">
                  {ad.headlines?.slice(0, 2).map((headline: string, hIdx: number) => (
                    <h6 key={hIdx} className="ad-headline">{headline}</h6>
                  ))}
                </div>
                <p className="ad-description">{ad.descriptions?.[0]}</p>
                <div className="ad-url">
                  <span className="meta-label">Display URL:</span>
                  <code>{ad.display_url}</code>
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Meta Ads Section */}
      {meta_ads_campaign && (
        <section className="results-section">
          <h3 className="section-title">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M18 2H2V18H18V2Z" stroke="currentColor" strokeWidth="2"/>
              <circle cx="7" cy="7" r="2" fill="currentColor"/>
              <path d="M10 13L13 8L17 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Meta Ads (Facebook & Instagram)
          </h3>

          {/* Campaign Structure */}
          {meta_ads_campaign.campaign_structure && (
            <div className="insight-card">
              <h4>{meta_ads_campaign.campaign_structure.campaign_name}</h4>
              <div className="stat-grid">
                <div className="stat-item">
                  <span className="stat-label">Primary Objective</span>
                  <span className="stat-value" style={{textTransform: 'capitalize'}}>{meta_ads_campaign.campaign_structure.primary_objective}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Optimization</span>
                  <span className="stat-value">{meta_ads_campaign.campaign_structure.optimization_goal}</span>
                </div>
              </div>
              {meta_ads_campaign.campaign_structure.recommended_campaign_types && (
                <div className="campaign-types">
                  <h5 style={{marginTop: '1rem', marginBottom: '0.5rem'}}>Recommended Campaign Types</h5>
                  {meta_ads_campaign.campaign_structure.recommended_campaign_types.map((campaign: any, idx: number) => (
                    <div key={idx} className="meta-item">
                      <span className="meta-label">{campaign.type} ({campaign.recommended_budget_split}):</span>
                      <code>{campaign.description}</code>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Audiences */}
          {meta_ads_campaign.audiences && (
            <div className="audiences-section">
              <h5>Target Audiences</h5>

              {meta_ads_campaign.audiences.core_audiences && meta_ads_campaign.audiences.core_audiences.length > 0 && (
                <div className="audience-group">
                  <h6 style={{color: '#4CAF50', marginBottom: '0.5rem'}}>Core Audiences</h6>
                  {meta_ads_campaign.audiences.core_audiences.slice(0, 3).map((audience: any, idx: number) => (
                    <div key={idx} className="content-card">
                      <div className="ad-group-badge">{audience.priority} Priority</div>
                      <h6>{audience.name}</h6>
                      <div className="audience-details">
                        <span className="stat-label">Age Range:</span> {audience.targeting?.age_range || 'All'}<br/>
                        <span className="stat-label">Interests:</span> {audience.targeting?.interests?.slice(0, 4).join(', ')}
                      </div>
                      <div className="stat-item" style={{marginTop: '0.5rem'}}>
                        <span className="stat-label">Est. Reach:</span>
                        <span className="stat-value">{audience.estimated_reach}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {meta_ads_campaign.audiences.lookalike_audiences && meta_ads_campaign.audiences.lookalike_audiences.length > 0 && (
                <div className="audience-group" style={{marginTop: '1rem'}}>
                  <h6 style={{color: '#2196F3', marginBottom: '0.5rem'}}>Lookalike Audiences</h6>
                  {meta_ads_campaign.audiences.lookalike_audiences.slice(0, 2).map((audience: any, idx: number) => (
                    <div key={idx} className="content-card">
                      <h6>{audience.name}</h6>
                      <p className="email-preview">{audience.description}</p>
                      <div className="hashtags">
                        <span className="feature-badge">{audience.percentage} - {audience.country}</span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Ad Sets */}
          {meta_ads_campaign.ad_sets && meta_ads_campaign.ad_sets.length > 0 && (
            <div className="ad-sets-section">
              <h5>Ad Sets ({meta_ads_campaign.ad_sets.length})</h5>
              {meta_ads_campaign.ad_sets.slice(0, 4).map((adSet: any, idx: number) => (
                <div key={idx} className="content-card">
                  <div className="ad-group-badge">{adSet.campaign_type}</div>
                  <h6>{adSet.name}</h6>
                  <div className="stat-grid" style={{marginTop: '0.5rem'}}>
                    <div className="stat-item">
                      <span className="stat-label">Daily Budget</span>
                      <span className="stat-value">{adSet.recommended_daily_budget}</span>
                    </div>
                    <div className="stat-item">
                      <span className="stat-label">Optimization</span>
                      <span className="stat-value">{adSet.optimization}</span>
                    </div>
                  </div>
                  <div className="hashtags" style={{marginTop: '0.5rem'}}>
                    {adSet.placements?.positions?.map((placement: string, pIdx: number) => (
                      <span key={pIdx} className="feature-badge">{placement}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Ad Copy */}
          {meta_ads_campaign.ad_copy && meta_ads_campaign.ad_copy.variations && (
            <div className="ad-copy-section">
              <h5>Ad Copy Variations</h5>
              {meta_ads_campaign.ad_copy.variations.map((variation: any, idx: number) => (
                <div key={idx} className="content-card">
                  <div className="ad-group-badge" style={{textTransform: 'capitalize'}}>{variation.tone}</div>
                  <h6 style={{color: '#1877F2'}}>{variation.headline}</h6>
                  <p className="post-caption">{variation.primary_text}</p>
                  <div className="ad-url">
                    <span className="meta-label">Description:</span>
                    <code>{variation.description}</code>
                  </div>
                  <div className="hashtags">
                    <span className="feature-badge">CTA: {variation.cta_button}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Creative Recommendations */}
          {meta_ads_campaign.ad_creatives && meta_ads_campaign.ad_creatives.length > 0 && (
            <div className="creatives-section">
              <h5>Creative Formats</h5>
              <div className="creatives-grid">
                {meta_ads_campaign.ad_creatives.map((creative: any, idx: number) => (
                  <div key={idx} className="content-card">
                    <div className="ad-group-badge">{creative.format}</div>
                    <h6>{creative.name}</h6>
                    <div className="meta-item">
                      <span className="meta-label">Specs:</span>
                      <code>{creative.specs?.aspect_ratio || creative.specs?.resolution}</code>
                    </div>
                    <div className="hashtags">
                      {creative.placement_optimized?.map((placement: string, pIdx: number) => (
                        <span key={pIdx} className="feature-badge">{placement}</span>
                      ))}
                    </div>
                    <p className="email-preview" style={{marginTop: '0.5rem'}}>{creative.recommended_for}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Budget Allocation */}
          {meta_ads_campaign.budget_allocation && (
            <div className="strategy-card">
              <h5>Budget Allocation</h5>
              <div className="stat-grid">
                <div className="stat-item">
                  <span className="stat-label">Total Monthly</span>
                  <span className="stat-value">{meta_ads_campaign.budget_allocation.total_monthly_budget}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">Daily Budget</span>
                  <span className="stat-value">{meta_ads_campaign.budget_allocation.daily_budget_recommendation}</span>
                </div>
              </div>
              {meta_ads_campaign.budget_allocation.recommended_split && (
                <div style={{marginTop: '1rem'}}>
                  {Object.entries(meta_ads_campaign.budget_allocation.recommended_split).map(([key, value]: [string, any], idx: number) => (
                    <div key={idx} className="meta-item">
                      <span className="meta-label" style={{textTransform: 'capitalize'}}>{key} ({value.percentage}):</span>
                      <code>{value.amount} - {value.focus}</code>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </section>
      )}

      {/* CRM/Email Section */}
      {crm_plan && (
        <section className="results-section">
          <h3 className="section-title">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M2 4L10 10L18 4M2 4V16H18V4H2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Email Marketing & CRM Strategy
          </h3>

          {crm_plan.welcome_series && (
            <div className="email-campaign-section">
              <h5>Welcome Email Series ({crm_plan.welcome_series.length} emails)</h5>
              <div className="email-list">
                {crm_plan.welcome_series.slice(0, 3).map((email: any, idx: number) => (
                  <div key={idx} className="content-card">
                    <div className="email-type-badge">Email {idx + 1}</div>
                    <h6>{email.subject_line || email.subject}</h6>
                    <p className="email-preview">{email.preheader || email.preview_text}</p>
                    <div className="email-timing">
                      <span className="stat-label">Send timing:</span> {email.send_timing}
                    </div>
                    {email.html_template && (
                      <button
                        className="preview-btn"
                        onClick={() => setEmailPreview({
                          subject: email.subject_line || email.subject,
                          html: email.html_template
                        })}
                      >
                        👁️ Preview Email
                      </button>
                    )}
                    {!email.html_template && email.mjml_template && (
                      <div className="email-meta">
                        <span className="stat-label">✓ MJML Template ({email.mjml_template.length} chars)</span>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {crm_plan.cart_abandonment && (
            <div className="email-campaign-section">
              <h5>Cart Abandonment Email</h5>
              <div className="content-card">
                <h6>{crm_plan.cart_abandonment.subject}</h6>
                <p className="email-preview">{crm_plan.cart_abandonment.preview_text}</p>
              </div>
            </div>
          )}

          {crm_plan.segmentation_strategy && (
            <div className="strategy-card">
              <h5>Segmentation Strategy</h5>
              {crm_plan.segmentation_strategy.segments && crm_plan.segmentation_strategy.segments.slice(0, 3).map((segment: any, idx: number) => (
                <div key={idx} className="meta-item">
                  <span className="meta-label">{segment.name}:</span>
                  <code>{segment.criteria}</code>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Analyst Insights Section */}
      {analyst_insights && (
        <section className="results-section">
          <h3 className="section-title">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M3 17V3H17V17H3Z" stroke="currentColor" strokeWidth="2"/>
              <path d="M7 13L10 9L13 11L17 7" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            Performance Insights & Recommendations
          </h3>

          {analyst_insights.timeline && (
            <div className="timeline-grid">
              {Object.entries(analyst_insights.timeline).slice(0, 3).map(([key, phase]: [string, any], idx: number) => (
                <div key={idx} className="content-card">
                  <h6>{key.replace(/_/g, ' ').toUpperCase()}</h6>
                  <p className="phase-duration">{phase.duration}</p>
                  <ul className="activity-list">
                    {phase.activities?.slice(0, 3).map((activity: string, aIdx: number) => (
                      <li key={aIdx}>{activity}</li>
                    ))}
                  </ul>
                </div>
              ))}
            </div>
          )}

          {analyst_insights.success_metrics && (
            <div className="metrics-card">
              <h5>Success Metrics</h5>
              {Object.entries(analyst_insights.success_metrics).map(([metric, target]: [string, any], idx: number) => (
                <div key={idx} className="meta-item">
                  <span className="meta-label">{metric.replace(/_/g, ' ')}:</span>
                  <code>{JSON.stringify(target)}</code>
                </div>
              ))}
            </div>
          )}
        </section>
      )}

      {/* Email Preview Modal */}
      {emailPreview && (
        <div className="email-preview-modal" onClick={() => setEmailPreview(null)}>
          <div className="email-preview-content" onClick={(e) => e.stopPropagation()}>
            <div className="email-preview-header">
              <h3>📧 {emailPreview.subject}</h3>
              <button className="close-btn" onClick={() => setEmailPreview(null)}>✕</button>
            </div>
            <div className="email-preview-body">
              <iframe
                srcDoc={emailPreview.html}
                title="Email Preview"
                sandbox="allow-same-origin"
                style={{ width: '100%', height: '500px', border: 'none', background: '#fff' }}
              />
            </div>
            <div className="email-preview-footer">
              <button
                className="copy-btn"
                onClick={() => {
                  navigator.clipboard.writeText(emailPreview.html);
                  alert('HTML copied to clipboard!');
                }}
              >
                📋 Copy HTML
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignResults;
