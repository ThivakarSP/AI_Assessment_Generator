/**
 * API Service - Handles all backend API calls
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Generate educational content for a given grade and topic
 */
export async function generateContent(grade, topic) {
  const response = await fetch(`${API_BASE_URL}/api/generate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ grade, topic }),
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || 'Failed to generate content');
  }

  return response.json();
}

/**
 * Get session status by ID
 */
export async function getSession(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`);

  if (!response.ok) {
    throw new Error('Failed to fetch session');
  }

  return response.json();
}

/**
 * Get all generations for a session
 */
export async function getSessionGenerations(sessionId) {
  const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/generations`);

  if (!response.ok) {
    throw new Error('Failed to fetch generations');
  }

  return response.json();
}

/**
 * Check API health
 */
export async function checkHealth() {
  const response = await fetch(`${API_BASE_URL}/api/health`);

  if (!response.ok) {
    throw new Error('API is not healthy');
  }

  return response.json();
}

export default {
  generateContent,
  getSession,
  getSessionGenerations,
  checkHealth,
};
