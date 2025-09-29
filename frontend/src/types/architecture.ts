/**
 * TypeScript types for Architecture Module (Module 4)
 */

export interface ArchitectureModule {
  id: string;
  project_id: string;
  parent_id?: string | null;
  tree_node_id?: string | null;
  name: string;
  description?: string | null;
  module_type: string;
  level: number;
  position_x?: number | null;
  position_y?: number | null;
  ai_generated: boolean;
  generation_reasoning?: Record<string, unknown> | null;
  status: 'draft' | 'approved' | 'implemented';
  approved_at?: string | null;
  approved_by?: string | null;
  module_metadata?: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface ArchitectureModuleCreate {
  project_id: string;
  parent_id?: string | null;
  tree_node_id?: string | null;
  name: string;
  description?: string | null;
  module_type?: string;
  level?: number;
  position_x?: number | null;
  position_y?: number | null;
  module_metadata?: Record<string, unknown> | null;
}

export interface ArchitectureModuleUpdate {
  name?: string;
  description?: string | null;
  module_type?: string;
  level?: number;
  position_x?: number | null;
  position_y?: number | null;
  module_metadata?: Record<string, unknown> | null;
  status?: 'draft' | 'approved' | 'implemented';
}

export interface ModuleDependency {
  id: string;
  project_id: string;
  from_module_id: string;
  to_module_id: string;
  dependency_type: string;
  description?: string | null;
  dependency_metadata?: Record<string, unknown> | null;
  created_at: string;
}

export interface ModuleDependencyCreate {
  project_id: string;
  from_module_id: string;
  to_module_id: string;
  dependency_type: string;
  description?: string | null;
  dependency_metadata?: Record<string, unknown> | null;
}

export interface ArchitectureRule {
  id: string;
  project_id: string;
  module_id?: string | null;
  level: 'global' | 'module' | 'component';
  rule_type: 'naming' | 'dependency' | 'layer' | 'tech' | 'security';
  rule_definition: Record<string, unknown>;
  ai_generated: boolean;
  active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ArchitectureRuleCreate {
  project_id: string;
  module_id?: string | null;
  level: 'global' | 'module' | 'component';
  rule_type: 'naming' | 'dependency' | 'layer' | 'tech' | 'security';
  rule_definition: Record<string, unknown>;
  ai_generated?: boolean;
  active?: boolean;
}

export interface ArchitectureGenerationRequest {
  project_id: string;
  goal_ids?: string[];
  opportunity_ids?: string[];
  architectural_style?: string | null;
  preferences?: Record<string, unknown>;
}

export interface ArchitectureGenerationResponse {
  modules: ArchitectureModule[];
  dependencies: ModuleDependency[];
  rules: ArchitectureRule[];
  architectural_style: string;
  reasoning: string;
  overall_score: number;
}

export interface ValidationIssue {
  type: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  affected_modules: string[];
  suggestions: string[];
}

export interface ArchitectureValidationResponse {
  is_valid: boolean;
  issues: ValidationIssue[];
  warnings_count: number;
  errors_count: number;
}

export interface ComplexityMetrics {
  module_count: number;
  avg_dependencies: number;
  max_depth: number;
  cyclomatic_complexity: number;
  coupling_score: number;
  cohesion_score: number;
}

export interface ComplexityHotspot {
  module_id: string;
  module_name: string;
  complexity_score: number;
  reason: string;
  suggestions: string[];
}

export interface ComplexityAnalysisResponse {
  overall_complexity: number;
  metrics: ComplexityMetrics;
  hotspots: ComplexityHotspot[];
  recommendations: string[];
}

export interface ImpactAnalysisRequest {
  module_id: string;
  change_type: 'modify' | 'delete' | 'add';
}

export interface AffectedModule {
  module_id: string;
  module_name: string;
  impact_level: 'direct' | 'indirect' | 'cascading';
  affected_features: string[];
}

export interface ImpactAnalysisResponse {
  module_id: string;
  change_type: string;
  affected_modules: AffectedModule[];
  breaking_changes: boolean;
  testing_scope: string[];
  recommendations: string[];
}

export interface SharedModuleInfo {
  module_id: string;
  module_name: string;
  usage_count: number;
  used_by: string[];
}

export interface SharedModulesResponse {
  shared_modules: SharedModuleInfo[];
  total_count: number;
}
