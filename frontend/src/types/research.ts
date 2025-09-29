/**
 * TypeScript types for Research Module (Module 3)
 */

export interface ResearchSession {
  id: string;
  project_id: string;
  goal_id?: string | null;
  opportunity_id?: string | null;
  tree_node_id?: string | null;
  title: string;
  description?: string | null;
  status: 'active' | 'completed' | 'archived';
  context_summary?: Record<string, unknown> | null;
  message_count: number;
  finding_count: number;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ResearchSessionCreate {
  project_id: string;
  title: string;
  description?: string | null;
  goal_id?: string | null;
  opportunity_id?: string | null;
  tree_node_id?: string | null;
}

export interface ResearchSessionUpdate {
  title?: string;
  description?: string | null;
  status?: 'active' | 'completed' | 'archived';
}

export interface ResearchMessage {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  metadata?: Record<string, unknown> | null;
  created_at: string;
}

export interface ChatRequest {
  message: string;
  stream?: boolean;
}

export interface ChatResponse {
  message_id: string;
  content: string;
  agent?: string | null;
  metadata?: Record<string, unknown> | null;
}

export interface ResearchFinding {
  id: string;
  session_id: string;
  finding_type: 'technical' | 'market' | 'user' | 'competitor' | 'other';
  title: string;
  description: string;
  sources: string[];
  confidence_score: number;
  relevance_score: number;
  created_at: string;
}

export interface ResearchFindingCreate {
  session_id: string;
  finding_type: 'technical' | 'market' | 'user' | 'competitor' | 'other';
  title: string;
  description: string;
  sources?: string[];
  confidence_score?: number;
  relevance_score?: number;
}

export interface ResearchFindingUpdate {
  finding_type?: 'technical' | 'market' | 'user' | 'competitor' | 'other';
  title?: string;
  description?: string;
  sources?: string[];
  confidence_score?: number;
  relevance_score?: number;
}

export interface SessionStatistics {
  session_id: string;
  message_count: number;
  finding_count: number;
  findings_by_type: Record<string, number>;
}
