// Pain Point Finder API Service
const API_BASE_URL = 'http://localhost:8001';

// Pain Points API
export const painPointsApi = {
  // Pain Point 목록 조회
  getAll: async (params = {}) => {
    const queryParams = new URLSearchParams({
      skip: params.skip || 0,
      limit: params.limit || 20,
      ...(params.severity && { severity: params.severity }),
      ...(params.category && { category: params.category }),
      ...(params.source && { source: params.source }),
      ...(params.min_confidence && { min_confidence: params.min_confidence }),
    });

    const response = await fetch(`${API_BASE_URL}/api/pain-points/?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch pain points');
    return response.json();
  },

  // Pain Point 상세 조회
  getDetail: async (id) => {
    const response = await fetch(`${API_BASE_URL}/api/pain-points/${id}`);
    if (!response.ok) throw new Error('Failed to fetch pain point detail');
    return response.json();
  },

  // Pain Point 통계
  getStats: async () => {
    const response = await fetch(`${API_BASE_URL}/api/pain-points/stats`);
    if (!response.ok) throw new Error('Failed to fetch pain point stats');
    return response.json();
  },
};

// SaaS Ideas API
export const ideasApi = {
  // 아이디어 목록 조회
  getAll: async (params = {}) => {
    const queryParams = new URLSearchParams({
      skip: params.skip || 0,
      limit: params.limit || 20,
      ...(params.min_score && { min_score: params.min_score }),
      ...(params.business_model && { business_model: params.business_model }),
      ...(params.complexity && { complexity: params.complexity }),
    });

    const response = await fetch(`${API_BASE_URL}/api/ideas/?${queryParams}`);
    if (!response.ok) throw new Error('Failed to fetch ideas');
    return response.json();
  },

  // Top 아이디어 조회
  getTop: async (limit = 10) => {
    const response = await fetch(`${API_BASE_URL}/api/ideas/top?limit=${limit}`);
    if (!response.ok) throw new Error('Failed to fetch top ideas');
    return response.json();
  },

  // 아이디어 상세 조회
  getDetail: async (id) => {
    const response = await fetch(`${API_BASE_URL}/api/ideas/${id}`);
    if (!response.ok) throw new Error('Failed to fetch idea detail');
    return response.json();
  },

  // 아이디어 통계
  getStats: async () => {
    const response = await fetch(`${API_BASE_URL}/api/ideas/stats/overview`);
    if (!response.ok) throw new Error('Failed to fetch idea stats');
    return response.json();
  },
};

// Dashboard API (기존 stats API 활용)
export const dashboardApi = {
  getStats: async () => {
    const response = await fetch(`${API_BASE_URL}/api/stats/`);
    if (!response.ok) throw new Error('Failed to fetch dashboard stats');
    return response.json();
  },
};

export default {
  painPoints: painPointsApi,
  ideas: ideasApi,
  dashboard: dashboardApi,
};
