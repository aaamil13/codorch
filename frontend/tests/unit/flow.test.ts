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
  createGoal: vi.fn(),
  listGoals: vi.fn(),
}));

vi.mock('src/services/opportunitiesApi', () => ({
  generateOpportunities: vi.fn(),
  listOpportunities: vi.fn(),
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

      vi.mocked(goalsApi.createGoal).mockResolvedValue({
        id: 'goal-1',
        title: 'Build SaaS Platform',
        description: 'Create subscription-based SaaS',
        smart_score: 8.5,
      });

      const goal = await goalsStore.createGoal({
        project_id: projectId,
        title: 'Build SaaS Platform',
        description: 'Create subscription-based SaaS',
      });

      expect(goal).toBeDefined();
      expect(goalsStore.goals.length).toBe(1);

      // Step 2: Generate Opportunities
      const opportunitiesStore = useOpportunitiesStore();

      vi.mocked(opportunitiesApi.generateOpportunities).mockResolvedValue({
        opportunities: [
          {
            id: 'opp-1',
            title: 'Subscription Management',
            description: 'Handle subscriptions',
            overall_score: 8.0,
          },
          {
            id: 'opp-2',
            title: 'User Dashboard',
            description: 'Analytics dashboard',
            overall_score: 7.5,
          },
        ],
        count: 2,
      });

      const opportunities = await opportunitiesStore.generateOpportunities(projectId, {
        project_id: projectId,
        goal_ids: [goal.id],
      });

      expect(opportunities?.opportunities.length).toBe(2);
      expect(opportunitiesStore.opportunities.length).toBe(2);

      // Step 3: Generate Architecture
      const architectureStore = useArchitectureStore();

      vi.mocked(architectureApi.generateArchitecture).mockResolvedValue({
        modules: [
          { id: 'arch-m1', name: 'Backend', module_type: 'package' },
          { id: 'arch-m2', name: 'Frontend', module_type: 'package' },
        ],
        dependencies: [],
        rules: [],
        overall_score: 8.2,
      });

      const architecture = await architectureStore.generateArchitecture(projectId, {
        project_id: projectId,
        goal_ids: [goal.id],
        opportunity_ids: [opportunities.opportunities[0].id],
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
        { id: 'm1', name: 'UserService', module_type: 'service' },
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
      vi.mocked(goalsApi.createGoal).mockRejectedValueOnce(
        new Error('Network error')
      );

      const result1 = await store.createGoal({
        project_id: 'p1',
        title: 'Test',
        description: 'Test',
      });

      expect(result1).toBeNull();
      expect(store.error).toBeDefined();

      // Second call succeeds
      vi.mocked(goalsApi.createGoal).mockResolvedValueOnce({
        id: 'g1',
        title: 'Test',
        description: 'Test',
        smart_score: 7,
      });

      const result2 = await store.createGoal({
        project_id: 'p1',
        title: 'Test',
        description: 'Test',
      });

      expect(result2).toBeDefined();
      expect(store.error).toBeNull(); // Error cleared
      expect(store.goals.length).toBe(1);
    });
  });

  describe('Flow: Concurrent Operations', () => {
    it('should handle concurrent API calls', async () => {
      const store = useGoalsStore();

      vi.mocked(goalsApi.createGoal).mockImplementation(
        (data) =>
          new Promise((resolve) =>
            setTimeout(
              () =>
                resolve({
                  id: Math.random().toString(),
                  ...data,
                  smart_score: 7,
                }),
              10
            )
          )
      );

      // Fire multiple creates concurrently
      const promises = [
        store.createGoal({ project_id: 'p1', title: 'Goal 1', description: 'Test' }),
        store.createGoal({ project_id: 'p1', title: 'Goal 2', description: 'Test' }),
        store.createGoal({ project_id: 'p1', title: 'Goal 3', description: 'Test' }),
      ];

      await Promise.all(promises);

      // All should be created
      expect(store.goals.length).toBe(3);
    });
  });
});