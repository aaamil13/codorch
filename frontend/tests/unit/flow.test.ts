/**
 * Flow Tests - User workflow scenarios
 *
 * Tests complete user journeys through the application.
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useGoalsStore } from 'src/stores/goals';
import { useOpportunitiesStore } from 'src/stores/opportunities';
import { useArchitectureStore } from 'src/stores/architecture';

vi.mock('src/services/goalsApi', () => ({
  goalsApi: {
    list: vi.fn(),
    get: vi.fn(),
    create: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    analyze: vi.fn(),
    decompose: vi.fn(),
  },
}));

vi.mock('src/services/opportunitiesApi', () => ({
  opportunitiesApi: {
    generate: vi.fn(),
    list: vi.fn(),
    create: vi.fn(),
    get: vi.fn(),
    update: vi.fn(),
    delete: vi.fn(),
    getTop: vi.fn(),
    compare: vi.fn(),
  },
}));

vi.mock('src/services/architectureApi', () => ({
  generateArchitecture: vi.fn(),
  validateArchitecture: vi.fn(),
  listModules: vi.fn(),
}));

import * as goalsApi from 'src/services/goalsApi';
import * as opportunitiesApi from 'src/services/opportunitiesApi';
import * as architectureApi from 'src/services/architectureApi';

describe('User Flow Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  describe('Flow: Goal → Opportunity → Architecture', () => {
    it('should complete full workflow', async () => {
      const projectId = 'project-123';

      // Step 1: Create Goal
      const goalsStore = useGoalsStore();

      vi.mocked(goalsApi.goalsApi.create).mockResolvedValue({
        id: 'goal-1',
        title: 'Build SaaS Platform',
        description: 'Create subscription-based SaaS',
        overall_smart_score: 8.5,
        project_id: projectId,
        is_smart_validated: true,
        completion_percentage: 0,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      const goal = await goalsStore.createGoal(projectId, {
        title: 'Build SaaS Platform',
        description: 'Create subscription-based SaaS',
      });

      expect(goal).toBeDefined();
      expect(goalsStore.goals.length).toBe(1);

      // Step 2: Generate Opportunities
      const opportunitiesStore = useOpportunitiesStore();

      const generatedOpportunities = [
        {
          id: 'opp-1',
          title: 'Subscription Management',
          description: 'Handle subscriptions',
          overall_score: 8.0,
          project_id: projectId,
          ai_generated: true,
            status: 'proposed' as const,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
        {
          id: 'opp-2',
          title: 'User Dashboard',
          description: 'Analytics dashboard',
          overall_score: 7.5,
          project_id: projectId,
          ai_generated: true,
          status: 'proposed' as const,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      vi.mocked(opportunitiesApi.opportunitiesApi.generate).mockResolvedValue({
        opportunities: [
          {
            title: 'Subscription Management',
            description: 'Handle subscriptions',
            category: 'Finance',
            target_market: 'SaaS Businesses',
            value_proposition: 'Streamlines subscription billing',
            estimated_effort: 'Medium',
            estimated_timeline: '3 months',
            innovation_level: 'High',
            reasoning: 'AI generated for efficient billing',
          },
          {
            title: 'User Dashboard',
            description: 'Analytics dashboard',
            category: 'Analytics',
            target_market: 'SaaS Users',
            value_proposition: 'Provides key insights to users',
            estimated_effort: 'Medium',
            estimated_timeline: '2 months',
            innovation_level: 'Medium',
            reasoning: 'AI generated for user engagement',
          },
        ],
        project_id: projectId,
        generation_metadata: {},
      });

      vi.mocked(opportunitiesApi.opportunitiesApi.list).mockResolvedValue(generatedOpportunities);

      const opportunities = await opportunitiesStore.generateOpportunities(projectId, {
        goal_id: goal.id,
      });

      expect(opportunities?.opportunities.length).toBe(2);
      expect(opportunitiesStore.opportunities.length).toBe(2);

      // Step 3: Generate Architecture
      const architectureStore = useArchitectureStore();

      vi.mocked(architectureApi.generateArchitecture).mockResolvedValue({
        modules: [
          {
            id: 'arch-m1',
            project_id: projectId,
            name: 'Backend',
            module_type: 'package',
            level: 1,
            ai_generated: true,
            status: 'draft',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
          {
            id: 'arch-m2',
            project_id: projectId,
            name: 'Frontend',
            module_type: 'package',
            level: 1,
            ai_generated: true,
            status: 'draft',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
          },
        ],
        dependencies: [],
        rules: [],
        overall_score: 8.2,
        architectural_style: 'Microservices',
        reasoning: 'Generated based on goals and opportunities.',
      });

      const architecture = await architectureStore.generateArchitecture(projectId, {
        project_id: projectId,
        goal_ids: [goal.id],
        opportunity_ids: [opportunitiesStore.opportunities[0]!.id],
      });

      expect(architecture).toBeDefined();
      expect(architectureStore.modules.length).toBe(2);

      // Verify workflow state
      expect(goalsStore.goals.length).toBe(1);
      expect(opportunitiesStore.opportunities.length).toBe(2);
      expect(architectureStore.modules.length).toBe(2);
    });
  });

  describe('Flow: Architecture → Requirements → Code', () => {
    it('should flow from architecture to code generation', async () => {
      const projectId = 'project-123';
      const architectureStore = useArchitectureStore();

      // Setup architecture
      architectureStore.modules = [
        {
          id: 'm1',
          project_id: projectId,
          name: 'UserService',
          module_type: 'service',
          level: 1,
          ai_generated: false,
          status: 'implemented',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        },
      ];

      // Validate architecture (RefMemTree powered)
      vi.mocked(architectureApi.validateArchitecture).mockResolvedValue({
        is_valid: true,
        issues: [],
        errors_count: 0,
        warnings_count: 0,
      });

      await architectureStore.validateArchitecture(projectId);

      expect(architectureStore.validation?.is_valid).toBe(true);

      // Can proceed to requirements
      // Can proceed to code generation
    });
  });

  describe('Flow: Error Recovery', () => {
    it('should recover gracefully from errors', async () => {
      const store = useGoalsStore();

      // First call fails
      vi.mocked(goalsApi.goalsApi.create).mockRejectedValueOnce(
        new Error('Network error')
      );

      await expect(
        store.createGoal('p1', {
          title: 'Test',
          description: 'Test',
        })
      ).rejects.toThrow('Network error');

      // Second call succeeds
      vi.mocked(goalsApi.goalsApi.create).mockResolvedValueOnce({
        id: 'g1',
        title: 'Test',
        description: 'Test',
        overall_smart_score: 7,
        project_id: 'p1',
        is_smart_validated: true,
        completion_percentage: 0,
        status: 'active',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      const result2 = await store.createGoal('p1', {
        title: 'Test',
        description: 'Test',
      });

      expect(result2).toBeDefined();
      expect(store.goals.length).toBe(1);
    });
  });

  describe('Flow: Concurrent Operations', () => {
    it('should handle concurrent API calls', async () => {
      const store = useGoalsStore();

      vi.mocked(goalsApi.goalsApi.create).mockImplementation(
        (projectId, data) =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  id: Math.random().toString(),
                  title: data.title,
                  description: data.description || '', // Ensure description is string
                  overall_smart_score: 7,
                  project_id: projectId,
                  is_smart_validated: true,
                  completion_percentage: 0,
                  status: 'active',
                  created_at: new Date().toISOString(),
                  updated_at: new Date().toISOString(),
                }),
              10
            )
          )
      );

      // Fire multiple creates concurrently
      const promises = [
        store.createGoal('p1', { title: 'Goal 1', description: 'Test' }),
        store.createGoal('p1', { title: 'Goal 2', description: 'Test' }),
        store.createGoal('p1', { title: 'Goal 3', description: 'Test' }),
      ];

      await Promise.all(promises);

      // All should be created
      expect(store.goals.length).toBe(3);
    });
  });
});
