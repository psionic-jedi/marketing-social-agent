import React, { useState, useEffect } from 'react';
import CampaignForm from './components/CampaignForm';
import CampaignResults from './components/CampaignResults';
import CampaignProgress from './components/CampaignProgress';
import { Campaign, CampaignResults as CampaignResultsType, campaignService } from './services/api';
import './App.css';

function App() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
  const [campaignResults, setCampaignResults] = useState<CampaignResultsType | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load campaigns on mount
  useEffect(() => {
    loadCampaigns();
  }, []);

  // Load campaign results when selected
  useEffect(() => {
    if (selectedCampaign) {
      loadCampaignResults(selectedCampaign);
    }
  }, [selectedCampaign]);

  const loadCampaigns = async () => {
    try {
      const data = await campaignService.getCampaigns();
      // Sort campaigns: completed first, then by creation date (newest first)
      const sorted = data.sort((a, b) => {
        // Prioritize completed campaigns
        if (a.status === 'completed' && b.status !== 'completed') return -1;
        if (a.status !== 'completed' && b.status === 'completed') return 1;
        // Then sort by creation date (newest first)
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
      setCampaigns(sorted);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    }
  };

  const loadCampaignResults = async (id: string) => {
    setIsLoading(true);
    try {
      const results = await campaignService.getCampaignResults(id);
      setCampaignResults(results);
    } catch (error) {
      console.error('Failed to load campaign results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCampaignCreated = (campaign: Campaign) => {
    setCampaigns([campaign, ...campaigns]);
    setSelectedCampaign(campaign.id);
  };

  const handleProgressComplete = () => {
    // Reload campaigns list
    loadCampaigns();
    // Load results
    if (selectedCampaign) {
      loadCampaignResults(selectedCampaign);
    }
  };

  const handleDeleteCampaign = async (campaignId: string, event?: React.MouseEvent) => {
    // Prevent card click when clicking delete button
    if (event) {
      event.stopPropagation();
      event.preventDefault();
    }

    console.log('Delete button clicked for campaign:', campaignId);

    if (!window.confirm('Are you sure you want to delete this campaign? This action cannot be undone.')) {
      console.log('Delete cancelled by user');
      return;
    }

    console.log('Deleting campaign:', campaignId);

    try {
      await campaignService.deleteCampaign(campaignId);
      console.log('Campaign deleted successfully:', campaignId);

      // If we're viewing the deleted campaign, go back to homepage
      if (selectedCampaign === campaignId) {
        setSelectedCampaign(null);
        setCampaignResults(null);
      }

      // Reload campaigns list
      loadCampaigns();
    } catch (error: any) {
      console.error('Failed to delete campaign:', error);
      console.error('Error details:', error?.response?.data || error?.message);
      alert(`Failed to delete campaign: ${error?.response?.data?.detail || error?.message || 'Unknown error'}`);
    }
  };

  // Get the selected campaign object
  const selectedCampaignObj = campaigns.find(c => c.id === selectedCampaign);
  const isRunning = selectedCampaignObj?.status === 'running' || selectedCampaignObj?.status === 'pending';

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="url(#gradient)"/>
                <path d="M16 8L8 13L16 18L24 13L16 8Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 18L16 23L24 18" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <defs>
                  <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                    <stop stopColor="#6366f1"/>
                    <stop offset="1" stopColor="#8b5cf6"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <h1>Childrensalon Agentic Campaign System</h1>
          </div>
          <div className="header-right">
            <p className="header-subtitle">AI-Powered Marketing Campaigns</p>
            <div className="stat-badge">
              <span className="stat-label">Total Campaigns</span>
              <span className="stat-value">{campaigns.length}</span>
            </div>
            {selectedCampaign && (
              <button className="nav-home-btn" onClick={() => setSelectedCampaign(null)}>
                ← Campaigns
              </button>
            )}
          </div>
        </div>
      </header>

      {/* Main Container */}
      <div className="main-container">
        {!selectedCampaign ? (
          <>
            {/* Sidebar */}
            <aside className="sidebar">
              <div className="sidebar-section">
                <h3>Create New Campaign</h3>
                <CampaignForm onCampaignCreated={handleCampaignCreated} />
              </div>
            </aside>

            {/* Main Content - Campaign Grid */}
            <main className="main-content homepage">
              <div className="campaigns-header">
                <h2>Your Campaigns</h2>
              </div>

              {campaigns.length === 0 ? (
                <div className="empty-state">
                  <h3>No campaigns yet</h3>
                  <p>Create your first AI-powered marketing campaign using the form on the left!</p>
                </div>
              ) : (
                <div className="campaigns-grid">
                  {campaigns.map((campaign: Campaign) => (
                    <div
                      key={campaign.id}
                      className={`campaign-card status-${campaign.status}`}
                      onClick={() => setSelectedCampaign(campaign.id)}
                    >
                      <div className="campaign-card-header">
                        <h3>{new URL(campaign.category_url).hostname}</h3>
                        <span className={`status-badge badge-${campaign.status}`}>
                          {campaign.status}
                        </span>
                      </div>
                      <div className="campaign-card-url">
                        {campaign.category_url}
                      </div>
                      <div className="campaign-card-footer">
                        <span>{new Date(campaign.created_at).toLocaleDateString()}</span>
                        {campaign.budget && <span>£{campaign.budget}</span>}
                        {campaign.progress_percentage !== null && campaign.status !== 'completed' && (
                          <span>{Number(campaign.progress_percentage).toFixed(0)}%</span>
                        )}
                        <button
                          className="delete-btn delete-btn-card"
                          onClick={(e) => handleDeleteCampaign(campaign.id, e)}
                          title="Delete campaign"
                        >
                          🗑️
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </main>
          </>
        ) : (
          <main className="main-content campaign-details">
            {isRunning ? (
              <CampaignProgress
                campaignId={selectedCampaign}
                onComplete={handleProgressComplete}
              />
            ) : isLoading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading campaign results...</p>
              </div>
            ) : campaignResults ? (
              <CampaignResults
                results={campaignResults}
                onDelete={() => handleDeleteCampaign(selectedCampaign)}
              />
            ) : null}
          </main>
        )}
      </div>
    </div>
  );
}

export default App;
