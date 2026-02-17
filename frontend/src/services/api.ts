/**
 * API service for communicating with the backend
 */
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface Campaign {
  id: string;
  user_id: string;
  category_url: string;
  category_name: string | null;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'partial';
  created_at: string;
  completed_at: string | null;
  budget: string | null;
  launch_date: string | null;
  current_step: string | null;
  progress_percentage: number | null;
}

export interface CampaignCreate {
  category_url: string;
  budget?: number;
  launch_date?: string;
}

export interface CampaignResults {
  campaign_id: string;
  category_url?: string;
  status: string;
  created_at: string;
  completed_at: string | null;
  results: {
    research_data?: any;
    content_outputs?: any;
    social_media_plan?: any;
    ppc_campaign?: any;
    meta_ads_campaign?: any;
    crm_plan?: any;
    analyst_insights?: any;
  } | null;
}

export const campaignService = {
  /**
   * Create a new campaign
   */
  async createCampaign(data: CampaignCreate): Promise<Campaign> {
    const response = await api.post<Campaign>('/api/campaigns', data);
    return response.data;
  },

  /**
   * Get all campaigns
   */
  async getCampaigns(): Promise<Campaign[]> {
    const response = await api.get<Campaign[]>('/api/campaigns');
    return response.data;
  },

  /**
   * Get a specific campaign
   */
  async getCampaign(id: string): Promise<Campaign> {
    const response = await api.get<Campaign>(`/api/campaigns/${id}`);
    return response.data;
  },

  /**
   * Get campaign results
   */
  async getCampaignResults(id: string): Promise<CampaignResults> {
    const response = await api.get<CampaignResults>(`/api/campaigns/${id}/results`);
    return response.data;
  },

  /**
   * Delete a campaign
   */
  async deleteCampaign(id: string): Promise<void> {
    await api.delete(`/api/campaigns/${id}`);
  },

  /**
   * Generate a full article from a content idea
   */
  async generateArticle(campaignId: string, contentIdea: {
    content_idea_id: string;
    title: string;
    intro: string;
    type: string;
    key_topics: string[];
    target_audience: string;
    seo_keywords?: string[];
  }): Promise<any> {
    const response = await api.post(`/api/campaigns/${campaignId}/generate-article`, contentIdea);
    return response.data;
  },
};

export default api;
