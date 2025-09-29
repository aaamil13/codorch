/**
 * Opportunities Store - Module 2
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  Opportunity,
  OpportunityCreate,
  OpportunityUpdate,
  OpportunityGenerateRequest,
  OpportunityGenerateResponse,
} from 'src/types/opportunities';
import { opportunitiesApi } from 'src/services/opportunitiesApi';
import { Notify } from 'quasar';

export const useOpportunitiesStore = defineStore('opportunities', () => {
  // State
  const opportunities = ref<Opportunity[]>([]);
  const currentOpportunity = ref<Opportunity | null>(null);
  const loading = ref(false);
  const generating = ref(false);
  const lastGeneration = ref<OpportunityGenerateResponse | null>(null);

  // Getters
  const opportunitiesByStatus = computed(
    () => (status: Opportunity['status']) =>
      opportunities.value.filter((o) => o.status === status)
  );

  const topOpportunities = computed(() =>
    [...opportunities.value]
      .filter((o) => o.score !== undefined && o.score !== null)
      .sort((a, b) => (b.score ?? 0) - (a.score ?? 0))
      .slice(0, 10)
  );

  const aiGeneratedOpportunities = computed(() =>
    opportunities.value.filter((o) => o.ai_generated)
  );

  const opportunityById = computed(() => (id: string) =>
    opportunities.value.find((o) => o.id === id)
  );

  const averageScore = computed(() => {
    const scored = opportunities.value.filter(
      (o) => o.score !== undefined && o.score !== null
    );
    if (scored.length === 0) return 0;
    const sum = scored.reduce((acc, o) => acc + (o.score ?? 0), 0);
    return sum / scored.length;
  });

  // Actions
  async function fetchOpportunities(projectId: string) {
    loading.value = true;
    try {
      const data = await opportunitiesApi.list(projectId);
      opportunities.value = data;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при зареждане на възможности',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function fetchOpportunity(opportunityId: string) {
    loading.value = true;
    try {
      const data = await opportunitiesApi.get(opportunityId);
      currentOpportunity.value = data;

      // Update in list if exists
      const index = opportunities.value.findIndex((o) => o.id === opportunityId);
      if (index !== -1) {
        opportunities.value[index] = data;
      } else {
        opportunities.value.push(data);
      }

      return data;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при зареждане на възможност',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function createOpportunity(
    projectId: string,
    data: OpportunityCreate
  ) {
    loading.value = true;
    try {
      const newOpportunity = await opportunitiesApi.create(projectId, data);
      opportunities.value.push(newOpportunity);

      Notify.create({
        type: 'positive',
        message: 'Възможността е създадена',
      });

      return newOpportunity;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при създаване на възможност',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function updateOpportunity(
    opportunityId: string,
    data: OpportunityUpdate
  ) {
    loading.value = true;
    try {
      const updated = await opportunitiesApi.update(opportunityId, data);

      // Update in list
      const index = opportunities.value.findIndex((o) => o.id === opportunityId);
      if (index !== -1) {
        opportunities.value[index] = updated;
      }

      if (currentOpportunity.value?.id === opportunityId) {
        currentOpportunity.value = updated;
      }

      Notify.create({
        type: 'positive',
        message: 'Възможността е актуализирана',
      });

      return updated;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при актуализация',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function deleteOpportunity(opportunityId: string) {
    loading.value = true;
    try {
      await opportunitiesApi.delete(opportunityId);

      // Remove from list
      opportunities.value = opportunities.value.filter(
        (o) => o.id !== opportunityId
      );

      if (currentOpportunity.value?.id === opportunityId) {
        currentOpportunity.value = null;
      }

      Notify.create({
        type: 'positive',
        message: 'Възможността е изтрита',
      });
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при изтриване',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function generateOpportunities(
    projectId: string,
    request: OpportunityGenerateRequest
  ) {
    generating.value = true;
    try {
      const result = await opportunitiesApi.generate(projectId, request);
      lastGeneration.value = result;

      // Refresh opportunities list
      await fetchOpportunities(projectId);

      Notify.create({
        type: 'positive',
        message: 'AI генерация завършена',
        caption: `${result.opportunities.length} възможности генерирани`,
      });

      return result;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при AI генерация',
      });
      throw error;
    } finally {
      generating.value = false;
    }
  }

  async function fetchTopOpportunities(projectId: string, limit = 10) {
    loading.value = true;
    try {
      const data = await opportunitiesApi.getTop(projectId, limit);
      // Merge with existing
      data.forEach((opp) => {
        const index = opportunities.value.findIndex((o) => o.id === opp.id);
        if (index !== -1) {
          opportunities.value[index] = opp;
        } else {
          opportunities.value.push(opp);
        }
      });
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при зареждане на топ възможности',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  async function compareOpportunities(opportunityIds: string[]) {
    loading.value = true;
    try {
      const result = await opportunitiesApi.compare({ opportunity_ids: opportunityIds });

      Notify.create({
        type: 'positive',
        message: 'Сравнение завършено',
      });

      return result;
    } catch (error) {
      Notify.create({
        type: 'negative',
        message: 'Грешка при сравнение',
      });
      throw error;
    } finally {
      loading.value = false;
    }
  }

  function clearCurrentOpportunity() {
    currentOpportunity.value = null;
  }

  function reset() {
    opportunities.value = [];
    currentOpportunity.value = null;
    loading.value = false;
    generating.value = false;
    lastGeneration.value = null;
  }

  return {
    // State
    opportunities,
    currentOpportunity,
    loading,
    generating,
    lastGeneration,

    // Getters
    opportunitiesByStatus,
    topOpportunities,
    aiGeneratedOpportunities,
    opportunityById,
    averageScore,

    // Actions
    fetchOpportunities,
    fetchOpportunity,
    createOpportunity,
    updateOpportunity,
    deleteOpportunity,
    generateOpportunities,
    fetchTopOpportunities,
    compareOpportunities,
    clearCurrentOpportunity,
    reset,
  };
});
