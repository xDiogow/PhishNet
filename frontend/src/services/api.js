import axios from 'axios';

// API base URL - configure based on environment
// In production (Docker), use relative path to leverage Nginx proxy
const API_BASE_URL = import.meta.env.VITE_API_URL || '';

// Create axios instance with default config
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10 seconds
});

// Request interceptor (for adding auth tokens in the future)
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (for handling errors globally)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      // Server responded with error status
      console.error('API Error:', error.response.status, error.response.data);
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    return Promise.reject(error);
  }
);

/**
 * Dashboard API Service
 */
export const dashboardAPI = {
  /**
   * Get system overview and statistics
   */
  getOverview: async () => {
    const response = await apiClient.get('/api/dashboard/overview');
    return response.data;
  },

  /**
   * Get all campaigns with tracking data
   */
  getCampaigns: async () => {
    const response = await apiClient.get('/api/dashboard/campaigns');
    return response.data;
  },

  /**
   * Get metrics for a specific campaign
   * @param {number} campaignId - Campaign ID
   */
  getCampaignMetrics: async (campaignId) => {
    const response = await apiClient.get(`/api/dashboard/campaigns/${campaignId}/metrics`);
    return response.data;
  },

  /**
   * Compare multiple campaigns
   * @param {number[]} campaignIds - Array of campaign IDs
   */
  compareCampaigns: async (campaignIds) => {
    const response = await apiClient.post('/api/dashboard/campaigns/compare', {
      campaign_ids: campaignIds,
    });
    return response.data;
  },

  /**
   * Send a phishing email
   * @param {Object} emailData - Email details
   */
  sendEmail: async (emailData) => {
    const response = await apiClient.post('/api/dashboard/email/send', emailData);
    return response.data;
  },

  /**
   * Get all email templates
   */
  getTemplates: async () => {
    const response = await apiClient.get('/api/dashboard/templates');
    return response.data;
  },

  /**
   * Get all target groups
   */
  getGroups: async () => {
    const response = await apiClient.get('/api/dashboard/groups');
    return response.data;
  },

  /**
   * Get all landing pages
   */
  getLandingPages: async () => {
    const response = await apiClient.get('/api/dashboard/landing-pages');
    return response.data;
  },

  /**
   * Get analytics timeline data
   * @param {Object} params - Query parameters (campaign_id, days)
   */
  getAnalyticsTimeline: async (params = {}) => {
    const response = await apiClient.get('/api/dashboard/analytics/timeline', { params });
    return response.data;
  },
};

/**
 * Tracking API Service
 */
export const trackingAPI = {
  /**
   * Get all page visits
   */
  getVisits: async () => {
    const response = await apiClient.get('/api/tracking/visits');
    return response.data;
  },

  /**
   * Get all form submissions
   * @param {boolean} revealPasswords - Whether to reveal actual passwords (default: false)
   */
  getSubmissions: async (revealPasswords = false) => {
    const response = await apiClient.get('/api/tracking/submissions', {
      params: { reveal_passwords: revealPasswords }
    });
    return response.data;
  },

  /**
   * Get tracking statistics for a campaign
   * @param {number} campaignId - Campaign ID
   */
  getStats: async (campaignId) => {
    const response = await apiClient.get(`/track/stats/${campaignId}`);
    return response.data;
  },
};

export default apiClient;
