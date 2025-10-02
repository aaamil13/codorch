/**
 * Tests for Goals Pinia Store
 *
 * Tests:
 * - State management
 * - Actions (CRUD)
 * - API integration
 * - Error handling
 * - Consistency
 */

import { describe, it, expect, beforeEach, vi, type MockedFunction } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useGoalsStore } from 'src/stores/goals';
import * as goalsApiModule from 'src/services/goalsApi'; // Import as module

// Mock the goalsApi object directly
vi.mock('src/services/goalsApi', async (importOriginal) => {
  const actual = await importOriginal<typeof goalsApiModule>();
  return {
    goalsApi: {
      ...actual.goalsApi, // Keep original non-mocked methods if any
      list: vi.fn(),
      create: vi.fn(),
      get: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
      analyze: vi.fn(),
      decompose: vi.fn(),
    },
  };
});

describe('Goals Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    // Clear mocks on the specific functions, as goalsApi itself is now mocked
    (
      goalsApiModule.goalsApi.create as MockedFunction<typeof goalsApiModule.goalsApi.create>
    ).mockClear();
    (
      goalsApiModule.goalsApi.list as MockedFunction<typeof goalsApiModule.goalsApi.list>
    ).mockClear();
    (goalsApiModule.goalsApi.get as MockedFunction<typeof goalsApiModule.goalsApi.get>).mockClear();
    (
      goalsApiModule.goalsApi.update as MockedFunction<typeof goalsApiModule.goalsApi.update>
    ).mockClear();
    (
      goalsApiModule.goalsApi.delete as MockedFunction<typeof goalsApiModule.goalsApi.delete>
    ).mockClear();
    (
      goalsApiModule.goalsApi.analyze as MockedFunction<typeof goalsApiModule.goalsApi.analyze>
    ).mockClear();
    (
      goalsApiModule.goalsApi.decompose as MockedFunction<typeof goalsApiModule.goalsApi.decompose>
    ).mockClear();
  });

  describe('State Management', () => {
    it('should initialize with empty state', () => {
      const store = useGoalsStore();

      expect(store.goals).toEqual([]);
      expect(store.currentGoal).toBeNull();
      expect(store.loading).toBe(false);
    });

    it('should maintain state consistency', () => {
      const store = useGoalsStore();

      // State should be reactive
      expect(Array.isArray(store.goals)).toBe(true);
      expect(typeof store.loading).toBe('boolean');
    });
  });

  describe('fetchGoals Action', () => {
    it('should fetch goals successfully', async () => {
      const store = useGoalsStore();
      const mockGoals = [
        {
          id: '1',
          title: 'Goal 1',
          description: 'Test',
          overall_smart_score: 8.5,
          is_smart_validated: true,
          completion_percentage: 0,
          status: 'active' as const, // Explicit literal type
          project_id: 'p1',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
        {
          id: '2',
          title: 'Goal 2',
          description: 'Test',
          overall_smart_score: 7.0,
          is_smart_validated: true,
          completion_percentage: 0,
          status: 'active' as const, // Explicit literal type
          project_id: 'p1',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      ];

      (
        goalsApiModule.goalsApi.list as MockedFunction<typeof goalsApiModule.goalsApi.list>
      ).mockResolvedValue(mockGoals);

      await store.fetchGoals('project-123');

      expect(store.goals).toEqual(mockGoals);
      expect(store.loading).toBe(false);
    });

    it('should handle fetch errors', async () => {
      const store = useGoalsStore();

      (
        goalsApiModule.goalsApi.list as MockedFunction<typeof goalsApiModule.goalsApi.list>
      ).mockRejectedValue(new Error('API Error'));

      await expect(store.fetchGoals('project-123')).rejects.toThrow('API Error');
      expect(store.goals).toEqual([]); // Ensure state is still empty after error
    });

    it('should set loading state correctly', async () => {
      const store = useGoalsStore();

      (
        goalsApiModule.goalsApi.list as MockedFunction<typeof goalsApiModule.goalsApi.list>
      ).mockImplementation(() => new Promise((resolve) => setTimeout(resolve, 100)));

      const promise = store.fetchGoals('project-123');

      expect(store.loading).toBe(true);

      await promise;

      expect(store.loading).toBe(false);
    });
  });

  describe('createGoal Action', () => {
    it('should create goal and add to store', async () => {
      const store = useGoalsStore();
      const newGoal = {
        project_id: 'project-123',
        title: 'New Goal',
        description: 'Test goal',
      };

      const createdGoal = {
        id: 'goal-123',
        ...newGoal,
        overall_smart_score: 0,
        is_smart_validated: false,
        completion_percentage: 0,
        status: 'draft' as const, // Explicit literal type
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      };

      (
        goalsApiModule.goalsApi.create as MockedFunction<typeof goalsApiModule.goalsApi.create>
      ).mockResolvedValue(createdGoal);

      await store.createGoal(newGoal.project_id, newGoal);

      expect(store.goals).toEqual([createdGoal]);
    });

    it('should handle create errors', async () => {
      const store = useGoalsStore();

      (
        goalsApiModule.goalsApi.create as MockedFunction<typeof goalsApiModule.goalsApi.create>
      ).mockRejectedValue(new Error('Create failed'));

      await expect(
        store.createGoal('p1', {
          title: 'Test',
          description: 'Test',
        })
      ).rejects.toThrow('Create failed');
    });
  });

  describe('updateGoal Action', () => {
    it('should update goal in store', async () => {
      const store = useGoalsStore();

      // Setup initial state
      store.goals = [
        {
          id: '1',
          title: 'Old Title',
          description: 'Test',
          overall_smart_score: 0,
          is_smart_validated: false,
          completion_percentage: 0,
          status: 'draft' as const, // Explicit literal type
          project_id: 'p1',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      ];

      const updated = {
        id: '1',
        title: 'New Title',
        description: 'Test',
        overall_smart_score: 8,
        is_smart_validated: true,
        completion_percentage: 0,
        status: 'active' as const, // Explicit literal type
        project_id: 'p1',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      };

      (
        goalsApiModule.goalsApi.update as MockedFunction<typeof goalsApiModule.goalsApi.update>
      ).mockResolvedValue(updated);

      await store.updateGoal('1', { title: 'New Title' });

      expect(store.goals[0]!.title).toBe('New Title');
      expect(store.goals[0]!.overall_smart_score).toBe(8);
    });

    it('should maintain consistency after update', async () => {
      const store = useGoalsStore();

      store.goals = [
        {
          id: '1',
          title: 'Goal 1',
          description: 'Test',
          overall_smart_score: 7,
          project_id: 'p1',
          is_smart_validated: false,
          completion_percentage: 0,
          status: 'draft' as const, // Explicit literal type
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
        {
          id: '2',
          title: 'Goal 2',
          description: 'Test',
          overall_smart_score: 8,
          project_id: 'p1',
          is_smart_validated: false,
          completion_percentage: 0,
          status: 'draft' as const, // Explicit literal type
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      ];

      const updated = {
        id: '1',
        title: 'Updated',
        description: 'Test',
        overall_smart_score: 9,
        is_smart_validated: true,
        completion_percentage: 0,
        status: 'active' as const, // Explicit literal type
        project_id: 'p1',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      };

      (
        goalsApiModule.goalsApi.update as MockedFunction<typeof goalsApiModule.goalsApi.update>
      ).mockResolvedValue(updated);

      await store.updateGoal('1', { title: 'Updated' });

      expect(store.goals.length).toBe(2);
      expect(store.goals[0]!.title).toBe('Updated');
      expect(store.goals[1]!.title).toBe('Goal 2');
    });
  });

  describe('deleteGoal Action', () => {
    it('should remove goal from store', async () => {
      const store = useGoalsStore();

      store.goals = [
        {
          id: '1',
          title: 'Goal 1',
          description: 'Test',
          overall_smart_score: 7,
          project_id: 'p1',
          is_smart_validated: false,
          completion_percentage: 0,
          status: 'draft' as const,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
        {
          id: '2',
          title: 'Goal 2',
          description: 'Test',
          overall_smart_score: 8,
          project_id: 'p1',
          is_smart_validated: false,
          completion_percentage: 0,
          status: 'draft' as const,
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      ];

      (
        goalsApiModule.goalsApi.delete as MockedFunction<typeof goalsApiModule.goalsApi.delete>
      ).mockResolvedValue(undefined);

      await store.deleteGoal('1');

      expect(store.goals.length).toBe(1);
      expect(store.goals[0]!.id).toBe('2');
    });
  });

  describe('Store Consistency', () => {
    it('should maintain data integrity across operations', async () => {
      const store = useGoalsStore();

      (
        goalsApiModule.goalsApi.create as MockedFunction<typeof goalsApiModule.goalsApi.create>
      ).mockResolvedValue({
        id: '1',
        title: 'Goal',
        description: 'Test',
        overall_smart_score: 7,
        is_smart_validated: false,
        completion_percentage: 0,
        status: 'draft' as const, // Explicit literal type
        project_id: 'p1',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      });

      await store.createGoal('p1', { title: 'Goal', description: 'Test' });

      expect(store.goals.length).toBe(1);

      (
        goalsApiModule.goalsApi.update as MockedFunction<typeof goalsApiModule.goalsApi.update>
      ).mockResolvedValue({
        id: '1',
        title: 'Updated',
        description: 'Test',
        overall_smart_score: 8,
        is_smart_validated: false,
        completion_percentage: 0,
        status: 'draft' as const, // Explicit literal type
        project_id: 'p1',
        created_at: '2023-01-01T00:00:00Z',
        updated_at: '2023-01-01T00:00:00Z',
      });

      await store.updateGoal('1', { title: 'Updated' });

      expect(store.goals.length).toBe(1);
      expect(store.goals[0]!.title).toBe('Updated');

      (
        goalsApiModule.goalsApi.delete as MockedFunction<typeof goalsApiModule.goalsApi.delete>
      ).mockResolvedValue(undefined);

      await store.deleteGoal('1');

      expect(store.goals.length).toBe(0);
    });
  });
});
