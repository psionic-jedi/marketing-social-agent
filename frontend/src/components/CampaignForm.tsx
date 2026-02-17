import React, { useState } from 'react';
import { campaignService, Campaign } from '../services/api';
import './CampaignForm.css';

interface CampaignFormProps {
  onCampaignCreated: (campaign: Campaign) => void;
}

const CampaignForm: React.FC<CampaignFormProps> = ({ onCampaignCreated }) => {
  const [url, setUrl] = useState('');
  const [budget, setBudget] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    try {
      const campaignData = {
        category_url: url,
        budget: budget ? parseFloat(budget) : undefined,
      };

      const campaign = await campaignService.createCampaign(campaignData);
      onCampaignCreated(campaign);

      // Reset form
      setUrl('');
      setBudget('');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create campaign');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="campaign-form-container">
      <div className="campaign-form-header">
        <h2>Create New Campaign</h2>
        <p>Generate a complete marketing campaign from any category page</p>
      </div>

      <form onSubmit={handleSubmit} className="campaign-form">
        <div className="form-group">
          <label htmlFor="url">
            Category URL
            <span className="required">*</span>
          </label>
          <input
            id="url"
            type="url"
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://example.com/baby-clothes"
            required
            className="form-input"
            disabled={isLoading}
          />
          <span className="form-hint">
            Enter the URL of the product category page you want to analyse
          </span>
        </div>

        <div className="form-group">
          <label htmlFor="budget">
            Campaign Budget
            <span className="optional">(optional)</span>
          </label>
          <div className="input-group">
            <span className="input-prefix">£</span>
            <input
              id="budget"
              type="number"
              value={budget}
              onChange={(e) => setBudget(e.target.value)}
              placeholder="5000"
              min="0"
              step="100"
              className="form-input with-prefix"
              disabled={isLoading}
            />
          </div>
          <span className="form-hint">
            Optional marketing budget for the campaign
          </span>
        </div>

        {error && (
          <div className="error-message">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 18C14.4183 18 18 14.4183 18 10C18 5.58172 14.4183 2 10 2C5.58172 2 2 5.58172 2 10C2 14.4183 5.58172 18 10 18Z" stroke="currentColor" strokeWidth="2"/>
              <path d="M10 6V10" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <path d="M10 14H10.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            {error}
          </div>
        )}

        <button
          type="submit"
          className="submit-button"
          disabled={isLoading || !url}
        >
          {isLoading ? (
            <>
              <span className="spinner"></span>
              Creating Campaign...
            </>
          ) : (
            <>
              <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M10 2L2 7L10 12L18 7L10 2Z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M2 12L10 17L18 12" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              Generate Campaign
            </>
          )}
        </button>
      </form>
    </div>
  );
};

export default CampaignForm;
