/**
 * Pinia store for Requirements Module
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type {
  Requirement,
  RequirementCreate,
  RequirementUpdate,
  RequirementValidationResult,
  TechnologyRecommendation,
  TechnologyRecommendationRequest,
  TechnologyRecommendationSummary,
  APISpecification,
  APISpecificationCreate,
  RequirementsSummary,
} from 'src/types/requirements';
import * as requirementsApi from 'src/services/requirementsApi';

export const useRequirementsStore = defineStore('requirements', () => {
  // State
  const requirements = ref<Requirement[]>([]);
  const currentRequirement = ref<Requirement | null>(null);
  const validationResults = ref<Map<string, RequirementValidationResult>>(new Map());
  const technologies = ref<TechnologyRecommendation[]>([]);
  const apiSpecs = ref<APISpecification[]>([]);
  const summary = ref<RequirementsSummary | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Actions - Requirements
  async function fetchRequirements(
    projectId: string,
    filters?: {
      type_filter?: string;
      status_filter?: string;
      priority_filter?: string;
      module_id?: string;
    }
  ) {
    loading.value = true;
    error.value = null;
    try {
      requirements.value = await requirementsApi.listRequirements(projectId, filters);
    } catch (err) {
      error.value = `Failed to fetch requirements: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchRequirement(id: string) {
    loading.value = true;
    error.value = null;
    try {
      currentRequirement.value = await requirementsApi.getRequirement(id);
    } catch (err) {
      error.value = `Failed to fetch requirement: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function createRequirement(data: RequirementCreate) {
    loading.value = true;
    error.value = null;
    try {
      const requirement = await requirementsApi.createRequirement(data);
      requirements.value.unshift(requirement);
      return requirement;
    } catch (err) {
      error.value = `Failed to create requirement: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function updateRequirement(id: string, data: RequirementUpdate) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await requirementsApi.updateRequirement(id, data);
      const index = requirements.value.findIndex((r) => r.id === id);
      if (index !== -1) {
        requirements.value[index] = updated;
      }
      if (currentRequirement.value?.id === id) {
        currentRequirement.value = updated;
      }
      return updated;
    } catch (err) {
      error.value = `Failed to update requirement: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function deleteRequirement(id: string) {
    loading.value = true;
    error.value = null;
    try {
      await requirementsApi.deleteRequirement(id);
      requirements.value = requirements.value.filter((r) => r.id !== id);
      if (currentRequirement.value?.id === id) {
        currentRequirement.value = null;
      }
    } catch (err) {
      error.value = `Failed to delete requirement: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function approveRequirement(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const approved = await requirementsApi.approveRequirement(id);
      const index = requirements.value.findIndex((r) => r.id === id);
      if (index !== -1) {
        requirements.value[index] = approved;
      }
      return approved;
    } catch (err) {
      error.value = `Failed to approve requirement: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Validation
  async function validateRequirement(id: string) {
    loading.value = true;
    error.value = null;
    try {
      const result = await requirementsApi.validateRequirement(id);
      validationResults.value.set(id, result);
      return result;
    } catch (err) {
      error.value = `Failed to validate requirement: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Technology Recommendations
  async function generateTechnologyRecommendations(
    projectId: string,
    data: TechnologyRecommendationRequest
  ) {
    loading.value = true;
    error.value = null;
    try {
      const summary = await requirementsApi.generateTechnologyRecommendations(projectId, data);
      technologies.value = summary.recommendations;
      return summary;
    } catch (err) {
      error.value = `Failed to generate recommendations: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchTechnologyRecommendations(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      technologies.value = await requirementsApi.listTechnologyRecommendations(projectId);
    } catch (err) {
      error.value = `Failed to fetch technology recommendations: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function updateTechnologyRecommendation(id: string, status: 'accepted' | 'rejected') {
    loading.value = true;
    error.value = null;
    try {
      const updated = await requirementsApi.updateTechnologyRecommendation(id, { status });
      const index = technologies.value.findIndex((t) => t.id === id);
      if (index !== -1) {
        technologies.value[index] = updated;
      }
      return updated;
    } catch (err) {
      error.value = `Failed to update technology recommendation: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Actions - API Specifications
  async function createAPISpecification(data: APISpecificationCreate) {
    loading.value = true;
    error.value = null;
    try {
      const spec = await requirementsApi.createAPISpecification(data);
      apiSpecs.value.push(spec);
      return spec;
    } catch (err) {
      error.value = `Failed to create API specification: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchAPISpecifications(requirementId: string) {
    loading.value = true;
    error.value = null;
    try {
      apiSpecs.value = await requirementsApi.listAPISpecifications(requirementId);
    } catch (err) {
      error.value = `Failed to fetch API specifications: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  // Actions - Reports
  async function fetchSummary(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      summary.value = await requirementsApi.getRequirementsSummary(projectId);
    } catch (err) {
      error.value = `Failed to fetch summary: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  // Clear state
  function clear() {
    requirements.value = [];
    currentRequirement.value = null;
    validationResults.value.clear();
    technologies.value = [];
    apiSpecs.value = [];
    summary.value = null;
  }

  return {
    // State
    requirements,
    currentRequirement,
    validationResults,
    technologies,
    apiSpecs,
    summary,
    loading,
    error,
    // Actions
    fetchRequirements,
    fetchRequirement,
    createRequirement,
    updateRequirement,
    deleteRequirement,
    approveRequirement,
    validateRequirement,
    generateTechnologyRecommendations,
    fetchTechnologyRecommendations,
    updateTechnologyRecommendation,
    createAPISpecification,
    fetchAPISpecifications,
    fetchSummary,
    clear,
  };
});