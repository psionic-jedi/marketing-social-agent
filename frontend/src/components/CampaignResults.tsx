import React from 'react';
import { CampaignResults as CampaignResultsType } from '../services/api';
import './CampaignResults.css';

interface CampaignResultsProps {
  results: CampaignResultsType;
}

const CampaignResults: React.FC<CampaignResultsProps> = ({ results }) => {
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

  const { research_data, content_outputs } = results.results;

  return (
    <div className="campaign-results">
      <div className="results-header">
        <div>
          <h2>Campaign Results</h2>
          <p className="campaign-id">ID: {results.campaign_id}</p>
        </div>
        <div className={`status-badge status-${results.status}`}>
          {results.status === 'completed' && '✓ '}
          {results.status}
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
        </section>
      )}
    </div>
  );
};

export default CampaignResults;
