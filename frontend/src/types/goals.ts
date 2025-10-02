/**
 * TypeScript types for Goals (Module 1)
 */

export interface MetricDefinition {
  name: string;
  target_value: number;
  current_value?: number;
  unit: string;
}

export interface SMARTScores {
  specific_score: number;
  measurable_score: number;
  achievable_score: number;
  relevant_score: number;
  time_bound_score: number;
  overall_smart_score: number;
}

export interface AIFeedback {
  feedback: string[];
  suggestions: string[];
  strengths: string[];
  weaknesses: string[];
}

export interface Goal {
  id: string;
  project_id: string;
  tree_node_id?: string;
  parent_goal_id?: string;
  title: string;
  description?: string;
  category?: string;
  is_smart_validated: boolean;
  specific_score?: number;
  measurable_score?: number;
  achievable_score?: number;
  relevant_score?: number;
  time_bound_score?: number;
  overall_smart_score?: number;
  metrics?: MetricDefinition[];
  target_date?: string;
  completion_percentage: number;
  ai_feedback?: AIFeedback;
  ai_suggestions?: string[];
  status: 'draft' | 'active' | 'completed' | 'archived';
  priority?: 'low' | 'medium' | 'high' | 'critical';
  created_at: string;
  updated_at: string;
  subgoals?: Goal[];
}

export interface GoalCreate {
  title: string;
  description?: string | undefined; // Allow undefined
  category?: string | undefined;    // Allow undefined
  target_date?: string | undefined; // Allow undefined
  priority?: 'low' | 'medium' | 'high' | 'critical' | undefined; // Allow undefined
  metrics?: MetricDefinition[];
  parent_goal_id?: string;
}

export interface GoalUpdate {
  title?: string | undefined;
  description?: string | undefined;
  category?: string | undefined;
  target_date?: string | undefined;
  priority?: 'low' | 'medium' | 'high' | 'critical' | undefined;
  status?: 'draft' | 'active' | 'completed' | 'archived' | undefined;
  completion_percentage?: number;
  metrics?: MetricDefinition[];
}

export interface GoalAnalysisRequest {
  advanced_analysis?: boolean;
}

export interface GoalAnalysisResponse {
  goal_id: string;
  smart_scores: SMARTScores;
  feedback: AIFeedback;
  suggested_metrics: MetricDefinition[];
  suggested_subgoals?: SubgoalSuggestion[];
  is_smart_compliant: boolean;
}

export interface SubgoalSuggestion {
  title: string;
  description: string;
  estimated_duration?: string;
  priority?: string;
  reasoning: string;
}

export interface GoalDecomposeRequest {
  num_subgoals?: number;
  include_metrics?: boolean;
}

export interface GoalDecomposeResponse {
  goal_id: string;
  subgoals: SubgoalSuggestion[];
  reasoning: string;
}
