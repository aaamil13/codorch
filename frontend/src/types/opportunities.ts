/**
 * TypeScript types for Opportunities (Module 2)
 */

export interface OpportunityScores {
  feasibility_score: number;
  impact_score: number;
  innovation_score: number;
  resource_score: number;
  overall_score: number;
}

export interface Opportunity {
  id: string;
  project_id: string;
  goal_id?: string;
  tree_node_id?: string;
  title: string;
  description?: string;
  category?: string;
  ai_generated: boolean;
  generation_prompt?: string;
  ai_reasoning?: Record<string, unknown>;
  score?: number;
  feasibility_score?: number;
  impact_score?: number;
  innovation_score?: number;
  resource_score?: number;
  scoring_details?: OpportunityScores;
  target_market?: string;
  value_proposition?: string;
  estimated_effort?: string;
  estimated_timeline?: string;
  required_resources?: Record<string, unknown>;
  status: 'proposed' | 'active' | 'approved' | 'rejected' | 'archived';
  approved_at?: string;
  approved_by?: string;
  created_at: string;
  updated_at: string;
}

export interface OpportunityCreate {
  title: string;
  description?: string;
  category?: string;
  goal_id?: string;
  target_market?: string;
  value_proposition?: string;
  estimated_effort?: string;
  estimated_timeline?: string;
  required_resources?: Record<string, unknown>;
}

export interface OpportunityUpdate {
  title?: string;
  description?: string;
  category?: string;
  target_market?: string;
  value_proposition?: string;
  estimated_effort?: string;
  estimated_timeline?: string;
  status?: 'proposed' | 'active' | 'approved' | 'rejected' | 'archived';
  required_resources?: Record<string, unknown>;
}

export interface AIGeneratedOpportunity {
  title: string;
  description: string;
  category: string;
  target_market: string;
  value_proposition: string;
  estimated_effort: string;
  estimated_timeline: string;
  innovation_level: string;
  reasoning: string;
}

export interface OpportunityGenerateRequest {
  goal_id?: string;
  context?: string;
  num_opportunities?: number;
  creativity_level?: 'conservative' | 'balanced' | 'creative';
  include_scoring?: boolean;
}

export interface OpportunityGenerateResponse {
  project_id: string;
  goal_id?: string;
  opportunities: AIGeneratedOpportunity[];
  generation_metadata: Record<string, unknown>;
}

export interface OpportunityCompareRequest {
  opportunity_ids: string[];
  criteria?: string[];
}

export interface OpportunityComparison {
  opportunity_id: string;
  title: string;
  scores: OpportunityScores;
  rank: number;
  strengths: string[];
  weaknesses: string[];
}

export interface OpportunityCompareResponse {
  opportunities: OpportunityComparison[];
  winner_id: string;
  reasoning: string;
  comparison_matrix: Record<string, unknown>;
}
