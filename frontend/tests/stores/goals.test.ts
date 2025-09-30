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

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { setActivePinia, createPinia } from 'pinia';
import { useGoalsStore } from 'src/stores/goals';

// Mock API module properly
vi.mock('src/services/goalsApi', () => ({
  listGoals: vi.fn(),
  createGoal: vi.fn(),
  updateGoal: vi.fn(),
  deleteGoal: vi.fn(),
  analyzeGoal: vi.fn(),
  decomposeGoal: vi.fn(),
}));

import * as goalsApi from 'src/services/goalsApi';

describe('Goals Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.clearAllMocks();
  });

  describe('State Management', () => {
    it('should initialize with empty state', () => {
      const store = useGoalsStore();

      expect(store.goals).toEqual([]);
      expect(store.currentGoal).toBeNull();
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
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
        { id: '1', title: 'Goal 1', description: 'Test', smart_score: 8.5 },
        { id: '2', title: 'Goal 2', description: 'Test', smart_score: 7.0 },
      ];

      vi.mocked(goalsApi.listGoals).mockResolvedValue(mockGoals);

      await store.fetchGoals('project-123');

      expect(store.goals).toEqual(mockGoals);
      expect(store.loading).toBe(false);
      expect(store.error).toBeNull();
    });

    it('should handle fetch errors', async () => {
      const store = useGoalsStore();

      vi.mocked(goalsApi.listGoals).mockRejectedValue(new Error('API Error'));

      await store.fetchGoals('project-123');

      expect(store.goals).toEqual([]);
      expect(store.error).toContain('Failed to fetch goals');
    });

    it('should set loading state correctly', async () => {
      const store = useGoalsStore();

      vi.mocked(goalsApi.listGoals).mockImplementation(
        () => new Promise((resolve) => setTimeout(resolve, 100))
      );

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
        smart_score: 0,
      };

      vi.mocked(goalsApi.createGoal).mockResolvedValue(createdGoal);

      const result = await store.createGoal(newGoal);

      expect(result).toEqual(createdGoal);
      expect(store.goals).toContain(createdGoal);
    });

    it('should handle create errors', async () => {
      const store = useGoalsStore();

      vi.mocked(goalsApi.createGoal).mockRejectedValue(new Error('Create failed'));

      const result = await store.createGoal({
        project_id: 'p1',
        title: 'Test',
        description: 'Test',
      });

      expect(result).toBeNull();
      expect(store.error).toContain('Failed to create goal');
    });
  });

  describe('updateGoal Action', () => {
    it('should update goal in store', async () => {
      const store = useGoalsStore();

      // Setup initial state
      store.goals = [
        { id: '1', title: 'Old Title', description: 'Test', smart_score: 7 },
      ];

      const updated = { id: '1', title: 'New Title', description: 'Test', smart_score: 8 };

      vi.mocked(goalsApi.updateGoal).mockResolvedValue(updated);

      await store.updateGoal('1', { title: 'New Title' });

      expect(store.goals[0].title).toBe('New Title');
      expect(store.goals[0].smart_score).toBe(8);
    });

    it('should maintain consistency after update', async () => {
      const store = useGoalsStore();

      store.goals = [
        { id: '1', title: 'Goal 1', description: 'Test', smart_score: 7 },
        { id: '2', title: 'Goal 2', description: 'Test', smart_score: 8 },
      ];

      const updated = { id: '1', title: 'Updated', description: 'Test', smart_score: 9 };

      vi.mocked(goalsApi.updateGoal).mockResolvedValue(updated);

      await store.updateGoal('1', { title: 'Updated' });

      // Should only update goal with id '1'
      expect(store.goals.length).toBe(2);
      expect(store.goals[0].title).toBe('Updated');
      expect(store.goals[1].title).toBe('Goal 2'); // Unchanged
    });
  });

  describe('deleteGoal Action', () => {
    it('should remove goal from store', async () => {
      const store = useGoalsStore();

      store.goals = [
        { id: '1', title: 'Goal 1', description: 'Test', smart_score: 7 },
        { id: '2', title: 'Goal 2', description: 'Test', smart_score: 8 },
      ];

      vi.mocked(goalsApi.deleteGoal).mockResolvedValue(undefined);

      await store.deleteGoal('1');

      expect(store.goals.length).toBe(1);
      expect(store.goals[0].id).toBe('2');
    });
  });

  describe('Store Consistency', () => {
    it('should maintain data integrity across operations', async () => {
      const store = useGoalsStore();

      // Create
      vi.mocked(goalsApi.createGoal).mockResolvedValue({
        id: '1',
        title: 'Goal',
        description: 'Test',
        smart_score: 7,
      });

      await store.createGoal({ project_id: 'p1', title: 'Goal', description: 'Test' });

      expect(store.goals.length).toBe(1);

      // Update
      vi.mocked(goalsApi.updateGoal).mockResolvedValue({
        id: '1',
        title: 'Updated',
        description: 'Test',
        smart_score: 8,
      });

      await store.updateGoal('1', { title: 'Updated' });

      expect(store.goals.length).toBe(1); // Same count
      expect(store.goals[0].title).toBe('Updated'); // Updated

      // Delete
      vi.mocked(goalsApi.deleteGoal).mockResolvedValue(undefined);

      await store.deleteGoal('1');

      expect(store.goals.length).toBe(0); // Removed
    });
  });
});