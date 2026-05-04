import axios from 'axios';

// Use localhost for development, environment variable for production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Functions
export const interviewAPI = {
  // Start new interview
  startInterview: async (candidateName, targetSkills, email = null) => {
    const response = await api.post('/api/interview/start', {
      candidate_name: candidateName,
      target_skills: targetSkills,
      candidate_email: email,
    });
    return response.data;
  },

  // Submit response
  submitResponse: async (sessionId, responseText) => {
    const response = await api.post('/api/interview/respond', {
      session_id: sessionId,
      response_text: responseText,
    });
    return response.data;
  },

  // Get interview report
  getReport: async (sessionId) => {
    const response = await api.get(`/api/interview/${sessionId}/report`);
    return response.data;
  },

  // Get interview status
  getStatus: async (sessionId) => {
    const response = await api.get(`/api/interview/${sessionId}/status`);
    return response.data;
  },

  // Get recent interviews
  getRecentInterviews: async (limit = 10) => {
    const response = await api.get(`/api/interviews/recent?limit=${limit}`);
    return response.data;
  },
};

// Health check
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

// Get questions
export const getQuestions = async () => {
  const response = await api.get('/api/questions');
  return response.data;
};

// Get dataset stats
export const getDatasetStats = async () => {
  const response = await api.get('/api/analytics/dataset-stats');
  return response.data;
};

export default api;
