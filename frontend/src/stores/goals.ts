/**
 * Goals Store - Module 1
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  Goal,
  GoalCreate,
  GoalUpdate,
  GoalAnalysisResponse,
  GoalDecomposeResponse,
} from 'src/types/goals';
import { goalsApi } from 'src/services/goalsApi';
import { Notify } from 'quasar';

export const useGoalsStore = defineStore('goals', () => {
  // State
  const goals = ref<Goal[]>([]);
  const currentGoal = ref<Goal | null>(null);
  const loading = ref(false);
  const analyzing = ref(false);
  const decomposing = ref(false);

  // Getters
  const rootGoals = computed(() =>
    goals.value.filter((g) => !g.parent_goal_id)
  );

  const goalsByStatus = computed(() => (status: Goal['status']) =>
    goals.value.filter((g) => g.status === status)
  );

  const smartCompliantGoals = computed(() =>
    goals.value.filter(
      (g) => g.is_smart_validated && (g.overall_smart_score ?? 0) >= 7.0
    )
  );

  const goalById = computed(() => (id: string) =>
    goals.value.find((g) => g.id === id)
  );

  // Actions
  async function fetchGoals(projectId: string, rootOnly = false) {
    loading.value = true;
    try {
      const data = await goalsApi.list(projectId, rootOnly);
      goals.value = data;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при зареждане на цели',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function fetchGoal(goalId: string) {
    loading.value = true;
    try {
      const data = await goalsApi.get(goalId);
      currentGoal.value = data;

      // Update in list if exists
      const index = goals.value.findIndex((g) => g.id === goalId);
      if (index !== -1) {
        goals.value[index] = data;
      } else {
        goals.value.push(data);
      }

      return data;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при зареждане на цел',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function createGoal(projectId: string, data: GoalCreate) {
    loading.value = true;
    try {
      const newGoal = await goalsApi.create(projectId, data);
      goals.value.push(newGoal);

      Notify.create({
        type: 'positive',
        message: 'Целта е създадена успешно',
      });

      return newGoal;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при създаване на цел',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function updateGoal(goalId: string, data: GoalUpdate) {
    loading.value = true;
    try {
      const updated = await goalsApi.update(goalId, data);

      // Update in list
      const index = goals.value.findIndex((g) => g.id === goalId);
      if (index !== -1) {
        goals.value[index] = updated;
      }

      if (currentGoal.value?.id === goalId) {
        currentGoal.value = updated;
      }

      Notify.create({
        type: 'positive',
        message: 'Целта е актуализирана',
      });

      return updated;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при актуализация на цел',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function deleteGoal(goalId: string) {
    loading.value = true;
    try {
      await goalsApi.delete(goalId);

      // Remove from list
      goals.value = goals.value.filter((g) => g.id !== goalId);

      if (currentGoal.value?.id === goalId) {
        currentGoal.value = null;
      }

      Notify.create({
        type: 'positive',
        message: 'Целта е изтрита',
      });
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при изтриване на цел',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function analyzeGoal(goalId: string, advanced = false) {
    analyzing.value = true;
    try {
      const analysis = await goalsApi.analyze(goalId, {
        advanced_analysis: advanced,
      });

      // Update goal with analysis results
      await fetchGoal(goalId);

      Notify.create({
        type: 'positive',
        message: 'AI анализ завършен',
        caption: `SMART Score: ${analysis.smart_scores.overall_smart_score.toFixed(
          1
        )}/10`,
      });

      return analysis;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при AI анализ',
      });
      throw error;
    } finally {
      analyzing.value = false;
    }
  }

  async function decomposeGoal(goalId: string, numSubgoals = 3) {
    decomposing.value = true;
    try {
      const result = await goalsApi.decompose(goalId, {
        num_subgoals: numSubgoals,
        include_metrics: true,
      });

      Notify.create({
        type: 'positive',
        message: 'Целта е декомпозирана',
        caption: `${result.subgoals.length} подцели предложени`,
      });

      return result;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при декомпозиция',
      });
      throw error;
    } finally {
      decomposing.value = false;
    }
  }

  function clearCurrentGoal() {
    currentGoal.value = null;
  }

  function reset() {
    goals.value = [];
    currentGoal.value = null;
    loading.value = false;
    analyzing.value = false;
    decomposing.value = false;
  }

  return {
    // State
    goals,
    currentGoal,
    loading,
    analyzing,
    decomposing,

    // Getters
    rootGoals,
    goalsByStatus,
    smartCompliantGoals,
    goalById,

    // Actions
    fetchGoals,
    fetchGoal,
    createGoal,
    updateGoal,
    deleteGoal,
    analyzeGoal,
    decomposeGoal,
    clearCurrentGoal,
    reset,
  };
});
