/**
 * Research API service - HTTP client for Research Module
 */

import { api } from 'boot/axios';
import type {
  ChatRequest,
  ChatResponse,
  ResearchFinding,
  ResearchFindingCreate,
  ResearchFindingUpdate,
  ResearchMessage,
  ResearchSession,
  ResearchSessionCreate,
  ResearchSessionUpdate,
  SessionStatistics,
} from 'src/types/research';

// ============================================================================
// Research Sessions
// ============================================================================

export async function createResearchSession(
  data: ResearchSessionCreate
): Promise<ResearchSession> {
  const response = await api.post<ResearchSession>(
    '/api/v1/research/sessions',
    data
  );
  return response.data;
}

export async function listResearchSessions(
  projectId: string,
  params?: {
    skip?: number;
    limit?: number;
    status_filter?: 'active' | 'completed' | 'archived';
  }
): Promise<ResearchSession[]> {
  const response = await api.get<ResearchSession[]>(
    '/api/v1/research/sessions',
    {
      params: { project_id: projectId, ...params },
    }
  );
  return response.data;
}

export async function getResearchSession(
  sessionId: string
): Promise<ResearchSession> {
  const response = await api.get<ResearchSession>(
    `/api/v1/research/sessions/${sessionId}`
  );
  return response.data;
}

export async function updateResearchSession(
  sessionId: string,
  data: ResearchSessionUpdate
): Promise<ResearchSession> {
  const response = await api.put<ResearchSession>(
    `/api/v1/research/sessions/${sessionId}`,
    data
  );
  return response.data;
}

export async function deleteResearchSession(sessionId: string): Promise<void> {
  await api.delete(`/api/v1/research/sessions/${sessionId}`);
}

export async function archiveResearchSession(
  sessionId: string
): Promise<ResearchSession> {
  const response = await api.post<ResearchSession>(
    `/api/v1/research/sessions/${sessionId}/archive`
  );
  return response.data;
}

// ============================================================================
// Chat & Messages
// ============================================================================

export async function getSessionMessages(
  sessionId: string,
  params?: { skip?: number; limit?: number }
): Promise<ResearchMessage[]> {
  const response = await api.get<ResearchMessage[]>(
    `/api/v1/research/sessions/${sessionId}/messages`,
    { params }
  );
  return response.data;
}

export async function sendChatMessage(
  sessionId: string,
  request: ChatRequest
): Promise<ChatResponse> {
  const response = await api.post<ChatResponse>(
    `/api/v1/research/sessions/${sessionId}/chat`,
    request
  );
  return response.data;
}

// ============================================================================
// Findings
// ============================================================================

export async function getSessionFindings(
  sessionId: string,
  findingType?: string
): Promise<ResearchFinding[]> {
  const response = await api.get<ResearchFinding[]>(
    `/api/v1/research/sessions/${sessionId}/findings`,
    { params: { finding_type: findingType } }
  );
  return response.data;
}

export async function createFinding(
  data: ResearchFindingCreate
): Promise<ResearchFinding> {
  const response = await api.post<ResearchFinding>(
    '/api/v1/research/findings',
    data
  );
  return response.data;
}

export async function getFinding(findingId: string): Promise<ResearchFinding> {
  const response = await api.get<ResearchFinding>(
    `/api/v1/research/findings/${findingId}`
  );
  return response.data;
}

export async function updateFinding(
  findingId: string,
  data: ResearchFindingUpdate
): Promise<ResearchFinding> {
  const response = await api.put<ResearchFinding>(
    `/api/v1/research/findings/${findingId}`,
    data
  );
  return response.data;
}

export async function deleteFinding(findingId: string): Promise<void> {
  await api.delete(`/api/v1/research/findings/${findingId}`);
}

// ============================================================================
// Statistics
// ============================================================================

export async function getSessionStatistics(
  sessionId: string
): Promise<SessionStatistics> {
  const response = await api.get<SessionStatistics>(
    `/api/v1/research/sessions/${sessionId}/statistics`
  );
  return response.data;
}
