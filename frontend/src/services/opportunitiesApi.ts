/**
 * Opportunities API Service
 */

import { api } from 'src/boot/axios';
import type {
  Opportunity,
  OpportunityCreate,
  OpportunityUpdate,
  OpportunityGenerateRequest,
  OpportunityGenerateResponse,
  OpportunityCompareRequest,
} from 'src/types/opportunities';

export const opportunitiesApi = {
  /**
   * Create a new opportunity
   */
  async create(
    projectId: string,
    data: OpportunityCreate
  ): Promise<Opportunity> {
    const response = await api.post<Opportunity>(
      `/opportunities/projects/${projectId}/opportunities`,
      data
    );
    return response.data;
  },

  /**
   * List all opportunities for a project
   */
  async list(
    projectId: string,
    skip = 0,
    limit = 100
  ): Promise<Opportunity[]> {
    const response = await api.get<Opportunity[]>(
      `/opportunities/projects/${projectId}/opportunities`,
      { params: { skip, limit } }
    );
    return response.data;
  },

  /**
   * Get a single opportunity
   */
  async get(opportunityId: string): Promise<Opportunity> {
    const response = await api.get<Opportunity>(
      `/opportunities/opportunities/${opportunityId}`
    );
    return response.data;
  },

  /**
   * Update an opportunity
   */
  async update(
    opportunityId: string,
    data: OpportunityUpdate
  ): Promise<Opportunity> {
    const response = await api.put<Opportunity>(
      `/opportunities/opportunities/${opportunityId}`,
      data
    );
    return response.data;
  },

  /**
   * Delete an opportunity
   */
  async delete(opportunityId: string): Promise<void> {
    await api.delete(`/opportunities/opportunities/${opportunityId}`);
  },

  /**
   * Generate opportunities using AI Team
   */
  async generate(
    projectId: string,
    request: OpportunityGenerateRequest
  ): Promise<OpportunityGenerateResponse> {
    const response = await api.post<OpportunityGenerateResponse>(
      `/opportunities/projects/${projectId}/opportunities/generate`,
      request
    );
    return response.data;
  },

  /**
   * Get top-scored opportunities
   */
  async getTop(projectId: string, limit = 10): Promise<Opportunity[]> {
    const response = await api.get<Opportunity[]>(
      `/opportunities/projects/${projectId}/opportunities/top`,
      { params: { limit } }
    );
    return response.data;
  },

  /**
   * Compare multiple opportunities
   */
  async compare(
    request: OpportunityCompareRequest
  ): Promise<Record<string, unknown>> {
    const response = await api.post<Record<string, unknown>>(
      '/opportunities/opportunities/compare',
      request
    );
    return response.data;
  },
};
