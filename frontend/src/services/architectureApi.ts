/**
 * Architecture API service - HTTP client for Architecture Module
 */

import { api } from 'boot/axios';
import type {
  ArchitectureGenerationRequest,
  ArchitectureGenerationResponse,
  ArchitectureModule,
  ArchitectureModuleCreate,
  ArchitectureModuleUpdate,
  ArchitectureRule,
  ArchitectureRuleCreate,
  ArchitectureValidationResponse,
  ComplexityAnalysisResponse,
  ImpactAnalysisRequest,
  ImpactAnalysisResponse,
  ModuleDependency,
  ModuleDependencyCreate,
  SharedModulesResponse,
} from 'src/types/architecture';

// ============================================================================
// Architecture Generation
// ============================================================================

export async function generateArchitecture(
  projectId: string,
  request: ArchitectureGenerationRequest
): Promise<ArchitectureGenerationResponse> {
  const response = await api.post<ArchitectureGenerationResponse>(
    `/api/v1/projects/${projectId}/architecture/generate`,
    request
  );
  return response.data;
}

// ============================================================================
// Module CRUD
// ============================================================================

export async function createModule(
  data: ArchitectureModuleCreate
): Promise<ArchitectureModule> {
  const response = await api.post<ArchitectureModule>(
    '/api/v1/architecture/modules',
    data
  );
  return response.data;
}

export async function listModules(
  projectId: string,
  params?: {
    skip?: number;
    limit?: number;
    parent_id?: string;
    module_type?: string;
    status_filter?: string;
  }
): Promise<ArchitectureModule[]> {
  const response = await api.get<ArchitectureModule[]>(
    `/api/v1/projects/${projectId}/architecture`,
    { params }
  );
  return response.data;
}

export async function getModule(moduleId: string): Promise<ArchitectureModule> {
  const response = await api.get<ArchitectureModule>(
    `/api/v1/architecture/modules/${moduleId}`
  );
  return response.data;
}

export async function updateModule(
  moduleId: string,
  data: ArchitectureModuleUpdate
): Promise<ArchitectureModule> {
  const response = await api.put<ArchitectureModule>(
    `/api/v1/architecture/modules/${moduleId}`,
    data
  );
  return response.data;
}

export async function deleteModule(moduleId: string): Promise<void> {
  await api.delete(`/api/v1/architecture/modules/${moduleId}`);
}

export async function approveModule(
  moduleId: string
): Promise<ArchitectureModule> {
  const response = await api.post<ArchitectureModule>(
    `/api/v1/architecture/modules/${moduleId}/approve`
  );
  return response.data;
}

// ============================================================================
// Dependency Management
// ============================================================================

export async function createDependency(
  data: ModuleDependencyCreate
): Promise<ModuleDependency> {
  const response = await api.post<ModuleDependency>(
    '/api/v1/architecture/dependencies',
    data
  );
  return response.data;
}

export async function listDependencies(
  projectId: string,
  dependencyType?: string
): Promise<ModuleDependency[]> {
  const response = await api.get<ModuleDependency[]>(
    `/api/v1/projects/${projectId}/architecture/dependencies`,
    { params: { dependency_type: dependencyType } }
  );
  return response.data;
}

export async function deleteDependency(dependencyId: string): Promise<void> {
  await api.delete(`/api/v1/architecture/dependencies/${dependencyId}`);
}

// ============================================================================
// Validation
// ============================================================================

export async function validateArchitecture(
  projectId: string
): Promise<ArchitectureValidationResponse> {
  const response = await api.get<ArchitectureValidationResponse>(
    `/api/v1/projects/${projectId}/architecture/validate`
  );
  return response.data;
}

// ============================================================================
// Rules Management
// ============================================================================

export async function createRule(
  data: ArchitectureRuleCreate
): Promise<ArchitectureRule> {
  const response = await api.post<ArchitectureRule>(
    '/api/v1/architecture/rules',
    data
  );
  return response.data;
}

export async function listRules(
  projectId: string,
  params?: {
    level?: string;
    rule_type?: string;
    active_only?: boolean;
  }
): Promise<ArchitectureRule[]> {
  const response = await api.get<ArchitectureRule[]>(
    `/api/v1/projects/${projectId}/architecture/rules`,
    { params }
  );
  return response.data;
}

export async function updateRule(
  ruleId: string,
  data: Partial<ArchitectureRuleCreate>
): Promise<ArchitectureRule> {
  const response = await api.put<ArchitectureRule>(
    `/api/v1/architecture/rules/${ruleId}`,
    data
  );
  return response.data;
}

export async function deleteRule(ruleId: string): Promise<void> {
  await api.delete(`/api/v1/architecture/rules/${ruleId}`);
}

// ============================================================================
// Analysis
// ============================================================================

export async function getComplexityAnalysis(
  projectId: string
): Promise<ComplexityAnalysisResponse> {
  const response = await api.get<ComplexityAnalysisResponse>(
    `/api/v1/projects/${projectId}/architecture/complexity`
  );
  return response.data;
}

export async function getImpactAnalysis(
  projectId: string,
  request: ImpactAnalysisRequest
): Promise<ImpactAnalysisResponse> {
  const response = await api.post<ImpactAnalysisResponse>(
    `/api/v1/projects/${projectId}/architecture/impact-analysis`,
    request
  );
  return response.data;
}

// ============================================================================
// Shared Modules
// ============================================================================

export async function getSharedModules(
  projectId: string
): Promise<SharedModulesResponse> {
  const response = await api.get<SharedModulesResponse>(
    `/api/v1/projects/${projectId}/architecture/shared-modules`
  );
  return response.data;
}
