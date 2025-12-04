import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

export const sendMessage = async (query, entityId) => {
    try {
        const response = await axios.post(`${API_BASE_URL}/query`, {
            query,
            entity_context: {
                entity_id: entityId
            },
            session_id: `entity-${entityId}`  // Use entity_id as session_id for memory
        });
        return response.data;
    } catch (error) {
        console.error('API Error:', error);
        throw new Error(error.response?.data?.detail || 'Failed to get response from AI');
    }
};

export const checkHealth = async () => {
    try {
        const response = await axios.get(`${API_BASE_URL}/health`);
        return response.data;
    } catch (error) {
        throw new Error('Backend is not reachable');
    }
};
