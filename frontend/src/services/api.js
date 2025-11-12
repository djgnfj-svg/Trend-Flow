const API_BASE_URL = 'http://localhost:8001/api';

export const api = {
  // Stats endpoints
  async getOverviewStats() {
    const response = await fetch(`${API_BASE_URL}/stats/overview`);
    if (!response.ok) throw new Error('Failed to fetch overview stats');
    return response.json();
  },

  async getDailyStats() {
    const response = await fetch(`${API_BASE_URL}/stats/daily`);
    if (!response.ok) throw new Error('Failed to fetch daily stats');
    return response.json();
  },

  // Trends endpoints
  async getTrends(params = {}) {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    if (params.per_page) queryParams.append('per_page', params.per_page);
    if (params.source) queryParams.append('source', params.source);
    if (params.analyzed_only) queryParams.append('analyzed_only', 'true');

    const response = await fetch(`${API_BASE_URL}/trends?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch trends');
    return response.json();
  },

  async getLatestTrends() {
    const response = await fetch(`${API_BASE_URL}/trends/latest`);
    if (!response.ok) throw new Error('Failed to fetch latest trends');
    return response.json();
  },

  async getTrendById(id) {
    const response = await fetch(`${API_BASE_URL}/trends/${id}`);
    if (!response.ok) throw new Error('Failed to fetch trend');
    return response.json();
  },

  // Solutions endpoints
  async getSolutions() {
    const response = await fetch(`${API_BASE_URL}/solutions`);
    if (!response.ok) throw new Error('Failed to fetch solutions');
    return response.json();
  },

  async getSolutionsByTrendId(trendId) {
    const response = await fetch(`${API_BASE_URL}/solutions/trend/${trendId}`);
    if (!response.ok) throw new Error('Failed to fetch solutions');
    return response.json();
  },
};
