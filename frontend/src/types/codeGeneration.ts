/**
 * TypeScript types for Code Generation Module (Module 6)
 */

export interface ValidationCheck {
  check_name: string;
  passed: boolean;
  score: number;
  message: string;
  issues: string[];
}

export interface PreGenerationValidation {
  architecture_completeness: number;
  requirements_clarity: number;
  dependencies_resolved: boolean;
  circular_dependencies: boolean;
  overall_readiness: number;
  checks: ValidationCheck[];
  can_proceed: boolean;
  blocking_issues: string[];
}

export interface CodeGenerationSession {
  id: string;
  project_id: string;
  architecture_module_id?: string | null;
  status: string;
  validation_result?: Record<string, unknown> | null;
  scaffold_code?: Record<string, unknown> | null;
  generated_code?: Record<string, unknown> | null;
  test_code?: Record<string, unknown> | null;
  documentation?: Record<string, unknown> | null;
  human_approved_scaffold: boolean;
  human_approved_code: boolean;
  approved_by?: string | null;
  approved_at?: string | null;
  error_message?: string | null;
  created_at: string;
  updated_at: string;
}

export interface CodeGenerationSessionCreate {
  project_id: string;
  architecture_module_id?: string | null;
}

export interface GeneratedFile {
  id: string;
  session_id: string;
  file_path: string;
  file_type: 'source' | 'test' | 'config' | 'documentation';
  language?: string | null;
  content: string;
  ai_generated: boolean;
  review_status: string;
  review_comments: string[];
  created_at: string;
  updated_at: string;
}

export interface ApprovalRequest {
  approved: boolean;
  comments?: string | null;
}

export interface ApprovalResponse {
  session_id: string;
  stage: string;
  approved: boolean;
  next_step: string;
}
