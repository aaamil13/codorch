/**
 * Requirements API service
 */

import { api } from 'boot/axios';
import type {
  Requirement,
  RequirementCreate,
  RequirementUpdate,
  RequirementValidationResult,
  TechnologyRecommendation,
  TechnologyRecommendationCreate,
  TechnologyRecommendationUpdate,
  TechnologyRecommendationRequest,
  TechnologyRecommendationSummary,
  APISpecification,
  APISpecificationCreate,
  APISpecificationUpdate,
  RequirementsSummary,
  RequirementsReport,
  BatchValidationRequest,
  BatchValidationResponse,
} from 'src/types/requirements';

// Requirements
export async function createRequirement(data: RequirementCreate): Promise<Requirement> {
  const response = await api.post<Requirement>('/api/v1/requirements', data);
  return response.data;
}

export async function listRequirements(
  projectId: string,
  params?: {
    skip?: number;
    limit?: number;
    type_filter?: string;
    status_filter?: string;
    priority_filter?: string;
    module_id?: string;
  }
): Promise<Requirement[]> {
  const response = await api.get<Requirement[]>(
    `/api/v1/requirements/projects/${projectId}`,
    { params }
  );
  return response.data;
}

export async function getRequirement(id: string): Promise<Requirement> {
  const response = await api.get<Requirement>(`/api/v1/requirements/${id}`);
  return response.data;
}

export async function updateRequirement(id: string, data: RequirementUpdate): Promise<Requirement> {
  const response = await api.put<Requirement>(`/api/v1/requirements/${id}`, data);
  return response.data;
}

export async function deleteRequirement(id: string): Promise<void> {
  await api.delete(`/api/v1/requirements/${id}`);
}

export async function approveRequirement(id: string): Promise<Requirement> {
  const response = await api.post<Requirement>(`/api/v1/requirements/${id}/approve`);
  return response.data;
}

export async function validateRequirement(id: string): Promise<RequirementValidationResult> {
  const response = await api.post<RequirementValidationResult>(`/api/v1/requirements/${id}/validate`);
  return response.data;
}

export async function validateBatch(projectId: string, data: BatchValidationRequest): Promise<BatchValidationResponse> {
  const response = await api.post<BatchValidationResponse>(
    `/api/v1/requirements/projects/${projectId}/validate-batch`,
    data
  );
  return response.data;
}

// Technology Recommendations
export async function generateTechnologyRecommendations(
  projectId: string,
  data: TechnologyRecommendationRequest
): Promise<TechnologyRecommendationSummary> {
  const response = await api.post<TechnologyRecommendationSummary>(
    `/api/v1/requirements/projects/${projectId}/technology-recommendations/generate`,
    data
  );
  return response.data;
}

export async function listTechnologyRecommendations(
  projectId: string,
  params?: { technology_type?: string; status_filter?: string }
): Promise<TechnologyRecommendation[]> {
  const response = await api.get<TechnologyRecommendation[]>(
    `/api/v1/requirements/projects/${projectId}/technology-recommendations`,
    { params }
  );
  return response.data;
}

export async function updateTechnologyRecommendation(
  id: string,
  data: TechnologyRecommendationUpdate
): Promise<TechnologyRecommendation> {
  const response = await api.put<TechnologyRecommendation>(
    `/api/v1/requirements/technology-recommendations/${id}`,
    data
  );
  return response.data;
}

export async function deleteTechnologyRecommendation(id: string): Promise<void> {
  await api.delete(`/api/v1/requirements/technology-recommendations/${id}`);
}

// API Specifications
export async function createAPISpecification(data: APISpecificationCreate): Promise<APISpecification> {
  const response = await api.post<APISpecification>('/api/v1/requirements/api-specifications', data);
  return response.data;
}

export async function listAPISpecifications(requirementId: string): Promise<APISpecification[]> {
  const response = await api.get<APISpecification[]>(
    `/api/v1/requirements/requirements/${requirementId}/api-specifications`
  );
  return response.data;
}

export async function updateAPISpecification(
  id: string,
  data: APISpecificationUpdate
): Promise<APISpecification> {
  const response = await api.put<APISpecification>(`/api/v1/requirements/api-specifications/${id}`, data);
  return response.data;
}

export async function deleteAPISpecification(id: string): Promise<void> {
  await api.delete(`/api/v1/requirements/api-specifications/${id}`);
}

// Reports
export async function getRequirementsSummary(projectId: string): Promise<RequirementsSummary> {
  const response = await api.get<RequirementsSummary>(`/api/v1/requirements/projects/${projectId}/summary`);
  return response.data;
}

export async function getRequirementsReport(projectId: string): Promise<RequirementsReport> {
  const response = await api.get<RequirementsReport>(`/api/v1/requirements/projects/${projectId}/report`);
  return response.data;
}
