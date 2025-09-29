/**
 * Goals API Service
 */

import { api } from 'src/boot/axios';
import type {
  Goal,
  GoalCreate,
  GoalUpdate,
  GoalAnalysisRequest,
  GoalAnalysisResponse,
  GoalDecomposeRequest,
  GoalDecomposeResponse,
} from 'src/types/goals';

export const goalsApi = {
  /**
   * Create a new goal
   */
  async create(projectId: string, data: GoalCreate): Promise<Goal> {
    const response = await api.post<Goal>(
      `/goals/projects/${projectId}/goals`,
      data
    );
    return response.data;
  },

  /**
   * List all goals for a project
   */
  async list(projectId: string, rootOnly = false): Promise<Goal[]> {
    const response = await api.get<Goal[]>(
      `/goals/projects/${projectId}/goals`,
      { params: { root_only: rootOnly } }
    );
    return response.data;
  },

  /**
   * Get a single goal with subgoals
   */
  async get(goalId: string): Promise<Goal> {
    const response = await api.get<Goal>(`/goals/goals/${goalId}`);
    return response.data;
  },

  /**
   * Update a goal
   */
  async update(goalId: string, data: GoalUpdate): Promise<Goal> {
    const response = await api.put<Goal>(`/goals/goals/${goalId}`, data);
    return response.data;
  },

  /**
   * Delete a goal
   */
  async delete(goalId: string): Promise<void> {
    await api.delete(`/goals/goals/${goalId}`);
  },

  /**
   * Analyze goal with AI
   */
  async analyze(
    goalId: string,
    request?: GoalAnalysisRequest
  ): Promise<GoalAnalysisResponse> {
    const response = await api.post<GoalAnalysisResponse>(
      `/goals/goals/${goalId}/analyze`,
      request || {}
    );
    return response.data;
  },

  /**
   * Decompose goal into subgoals
   */
  async decompose(
    goalId: string,
    request?: GoalDecomposeRequest
  ): Promise<GoalDecomposeResponse> {
    const response = await api.post<GoalDecomposeResponse>(
      `/goals/goals/${goalId}/decompose`,
      request || {}
    );
    return response.data;
  },
};
