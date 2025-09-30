/**
 * TypeScript types for Requirements Module (Module 5)
 */

export interface Requirement {
  id: string;
  project_id: string;
  module_id?: string | null;
  type: 'functional' | 'non_functional' | 'technical' | 'api' | 'data' | 'testing';
  category?: string | null;
  title: string;
  description: string;
  priority: 'must_have' | 'should_have' | 'nice_to_have';
  acceptance_criteria: string[];
  technical_specs: Record<string, unknown>;
  dependencies: string[];
  ai_generated: boolean;
  ai_validation_result?: Record<string, unknown> | null;
  ai_suggestions: string[];
  status: 'draft' | 'validated' | 'approved' | 'implemented';
  approved_by?: string | null;
  approved_at?: string | null;
  created_at: string;
  updated_at: string;
  created_by: string;
}

export interface RequirementCreate {
  project_id: string;
  module_id?: string | null;
  type: 'functional' | 'non_functional' | 'technical' | 'api' | 'data' | 'testing';
  category?: string | null;
  title: string;
  description: string;
  priority?: 'must_have' | 'should_have' | 'nice_to_have';
  acceptance_criteria?: string[];
  technical_specs?: Record<string, unknown>;
  dependencies?: string[];
}

export interface RequirementUpdate {
  type?: 'functional' | 'non_functional' | 'technical' | 'api' | 'data' | 'testing';
  category?: string | null;
  title?: string;
  description?: string;
  priority?: 'must_have' | 'should_have' | 'nice_to_have';
  acceptance_criteria?: string[];
  technical_specs?: Record<string, unknown>;
  dependencies?: string[];
  status?: 'draft' | 'validated' | 'approved' | 'implemented';
}

export interface ValidationIssue {
  type: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  suggestion?: string | null;
}

export interface RequirementValidationResult {
  requirement_id: string;
  overall_score: number;
  completeness_score: number;
  clarity_score: number;
  consistency_score: number;
  feasibility_score: number;
  issues: ValidationIssue[];
  suggestions: string[];
  is_valid: boolean;
}

export interface TechnologyRecommendation {
  id: string;
  project_id: string;
  module_id?: string | null;
  technology_type: string;
  name: string;
  version?: string | null;
  reasoning: string;
  suitability_score: number;
  popularity_score?: number | null;
  learning_curve_score?: number | null;
  ai_generated: boolean;
  alternatives: Record<string, unknown>[];
  status: 'suggested' | 'accepted' | 'rejected';
  created_at: string;
  updated_at: string;
}

export interface TechnologyRecommendationCreate {
  project_id: string;
  module_id?: string | null;
  technology_type: string;
  name: string;
  version?: string | null;
  reasoning: string;
  suitability_score: number;
  popularity_score?: number | null;
  learning_curve_score?: number | null;
  alternatives?: Record<string, unknown>[];
}

export interface TechnologyRecommendationUpdate {
  technology_type?: string;
  name?: string;
  version?: string | null;
  reasoning?: string;
  suitability_score?: number;
  popularity_score?: number | null;
  learning_curve_score?: number | null;
  alternatives?: Record<string, unknown>[];
  status?: 'suggested' | 'accepted' | 'rejected';
}

export interface TechnologyRecommendationRequest {
  project_id: string;
  module_id?: string | null;
  requirements?: string[];
  preferences?: Record<string, unknown>;
}

export interface TechnologyRecommendationSummary {
  recommendations: TechnologyRecommendation[];
  total_count: number;
  by_type: Record<string, number>;
}

export interface APISpecification {
  id: string;
  requirement_id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
  path: string;
  description: string;
  request_schema?: Record<string, unknown> | null;
  response_schema?: Record<string, unknown> | null;
  error_codes: Record<string, unknown>[];
  authentication_required: boolean;
  rate_limit?: string | null;
  examples: Record<string, unknown>[];
  created_at: string;
  updated_at: string;
}

export interface APISpecificationCreate {
  requirement_id: string;
  method: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
  path: string;
  description: string;
  request_schema?: Record<string, unknown> | null;
  response_schema?: Record<string, unknown> | null;
  error_codes?: Record<string, unknown>[];
  authentication_required?: boolean;
  rate_limit?: string | null;
  examples?: Record<string, unknown>[];
}

export interface APISpecificationUpdate {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH' | 'HEAD' | 'OPTIONS';
  path?: string;
  description?: string;
  request_schema?: Record<string, unknown> | null;
  response_schema?: Record<string, unknown> | null;
  error_codes?: Record<string, unknown>[];
  authentication_required?: boolean;
  rate_limit?: string | null;
  examples?: Record<string, unknown>[];
}

export interface RequirementsSummary {
  total_count: number;
  by_type: Record<string, number>;
  by_status: Record<string, number>;
  by_priority: Record<string, number>;
  validation_coverage: number;
}

export interface RequirementsReport {
  project_id: string;
  summary: RequirementsSummary;
  requirements: Requirement[];
  technology_recommendations: TechnologyRecommendation[];
  api_specifications_count: number;
  generated_at: string;
}

export interface BatchValidationRequest {
  project_id: string;
  requirement_ids?: string[];
}

export interface BatchValidationResponse {
  project_id: string;
  total_validated: number;
  results: RequirementValidationResult[];
  overall_quality_score: number;
  issues_count: number;
  critical_issues_count: number;
}