/**
 * Code Generation API service
 */

import { api } from 'boot/axios';
import type {
  PreGenerationValidation,
  CodeGenerationSession,
  CodeGenerationSessionCreate,
  GeneratedFile,
  ApprovalRequest,
  ApprovalResponse,
} from 'src/types/codeGeneration';

export async function validateProject(projectId: string): Promise<PreGenerationValidation> {
  const response = await api.post<PreGenerationValidation>(
    `/api/v1/code-generation/projects/${projectId}/validate`
  );
  return response.data;
}

export async function createSession(data: CodeGenerationSessionCreate): Promise<CodeGenerationSession> {
  const response = await api.post<CodeGenerationSession>('/api/v1/code-generation/sessions', data);
  return response.data;
}

export async function getSession(sessionId: string): Promise<CodeGenerationSession> {
  const response = await api.get<CodeGenerationSession>(`/api/v1/code-generation/sessions/${sessionId}`);
  return response.data;
}

export async function listSessions(projectId: string): Promise<CodeGenerationSession[]> {
  const response = await api.get<CodeGenerationSession[]>(
    `/api/v1/code-generation/projects/${projectId}/sessions`
  );
  return response.data;
}

export async function generateScaffold(sessionId: string): Promise<CodeGenerationSession> {
  const response = await api.post<CodeGenerationSession>(
    `/api/v1/code-generation/sessions/${sessionId}/scaffold`
  );
  return response.data;
}

export async function approveScaffold(sessionId: string, data: ApprovalRequest): Promise<ApprovalResponse> {
  const response = await api.post<ApprovalResponse>(
    `/api/v1/code-generation/sessions/${sessionId}/approve-scaffold`,
    data
  );
  return response.data;
}

export async function generateImplementation(sessionId: string): Promise<CodeGenerationSession> {
  const response = await api.post<CodeGenerationSession>(
    `/api/v1/code-generation/sessions/${sessionId}/implementation`
  );
  return response.data;
}

export async function approveCode(sessionId: string, data: ApprovalRequest): Promise<ApprovalResponse> {
  const response = await api.post<ApprovalResponse>(
    `/api/v1/code-generation/sessions/${sessionId}/approve-code`,
    data
  );
  return response.data;
}

export async function listFiles(sessionId: string): Promise<GeneratedFile[]> {
  const response = await api.get<GeneratedFile[]>(`/api/v1/code-generation/sessions/${sessionId}/files`);
  return response.data;
}

export async function deleteSession(sessionId: string): Promise<void> {
  await api.delete(`/api/v1/code-generation/sessions/${sessionId}`);
}
