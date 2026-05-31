import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
});

export async function getAllRoads() {
  const response = await api.get('/roads');
  return response.data;
}

export async function getRoadById(id) {
  const response = await api.get(`/roads/${id}`);
  return response.data;
}

export async function searchRoads(query) {
  const response = await api.get('/roads/search', {
    params: { q: query },
  });
  return response.data;
}

