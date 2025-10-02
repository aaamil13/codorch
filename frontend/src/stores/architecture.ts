/**
 * Pinia store for Architecture Module
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type {
  ArchitectureModule,
  ArchitectureModuleCreate,
  ArchitectureModuleUpdate,
  ArchitectureGenerationRequest,
  ModuleDependency,
  ModuleDependencyCreate,
  ArchitectureRule,
  ComplexityAnalysisResponse,
  ArchitectureValidationResponse,
} from 'src/types/architecture';
import * as architectureApi from 'src/services/architectureApi';

export const useArchitectureStore = defineStore('architecture', () => {
  // State
  const modules = ref<ArchitectureModule[]>([]);
  const dependencies = ref<ModuleDependency[]>([]);
  const rules = ref<ArchitectureRule[]>([]);
  const currentModule = ref<ArchitectureModule | null>(null);
  const validation = ref<ArchitectureValidationResponse | null>(null);
  const complexity = ref<ComplexityAnalysisResponse | null>(null);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Actions - Generation
  async function generateArchitecture(
    projectId: string,
    request: ArchitectureGenerationRequest
  ) {
    loading.value = true;
    error.value = null;
    try {
      const response = await architectureApi.generateArchitecture(
        projectId,
        request
      );
      modules.value = response.modules;
      dependencies.value = response.dependencies;
      rules.value = response.rules;
      return response;
    } catch (err) {
      error.value = `Failed to generate architecture: ${(err as Error).message}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Modules
  async function fetchModules(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      modules.value = await architectureApi.listModules(projectId);
    } catch (err) {
      error.value = `Failed to fetch modules: ${(err as Error).message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchModule(moduleId: string) {
    loading.value = true;
    error.value = null;
    try {
      currentModule.value = await architectureApi.getModule(moduleId);
    } catch (err) {
      error.value = `Failed to fetch module: ${(err as Error).message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function createModule(data: ArchitectureModuleCreate) {
    loading.value = true;
    error.value = null;
    try {
      const module = await architectureApi.createModule(data);
      modules.value.push(module);
      return module;
    } catch (err) {
      error.value = `Failed to create module: ${(err as Error).message}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function updateModule(moduleId: string, data: ArchitectureModuleUpdate) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await architectureApi.updateModule(moduleId, data);
      const index = modules.value.findIndex((m) => m.id === moduleId);
      if (index !== -1) {
        modules.value[index] = updated;
      }
      if (currentModule.value?.id === moduleId) {
        currentModule.value = updated;
      }
      return updated;
    } catch (err) {
      error.value = `Failed to update module: ${(err as Error).message}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function deleteModule(moduleId: string) {
    loading.value = true;
    error.value = null;
    try {
      await architectureApi.deleteModule(moduleId);
      modules.value = modules.value.filter((m) => m.id !== moduleId);
    } catch (err) {
      error.value = `Failed to delete module: ${(err as Error).message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function approveModule(moduleId: string) {
    loading.value = true;
    error.value = null;
    try {
      const approved = await architectureApi.approveModule(moduleId);
      const index = modules.value.findIndex((m) => m.id === moduleId);
      if (index !== -1) {
        modules.value[index] = approved;
      }
      return approved;
    } catch (err) {
      error.value = `Failed to approve module: ${(err as Error).message}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Dependencies
  async function fetchDependencies(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      dependencies.value = await architectureApi.listDependencies(projectId);
    } catch (err) {
      error.value = `Failed to fetch dependencies: ${(err as Error).message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function createDependency(data: ModuleDependencyCreate) {
    loading.value = true;
    error.value = null;
    try {
      const dependency = await architectureApi.createDependency(data);
      dependencies.value.push(dependency);
      return dependency;
    } catch (err) {
      error.value = `Failed to create dependency: ${(err as Error).message}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function deleteDependency(dependencyId: string) {
    loading.value = true;
    error.value = null;
    try {
      await architectureApi.deleteDependency(dependencyId);
      dependencies.value = dependencies.value.filter(
        (d) => d.id !== dependencyId
      );
    } catch (err) {
      error.value = `Failed to delete dependency: ${(err as Error).message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  // Actions - Validation & Analysis
  async function validateArchitecture(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      validation.value = await architectureApi.validateArchitecture(projectId);
    } catch (err) {
      error.value = `Failed to validate architecture: ${(err as Error).message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function analyzeComplexity(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      complexity.value = await architectureApi.getComplexityAnalysis(projectId);
    } catch (err) {
      error.value = `Failed to analyze complexity: ${(err as Error).message}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  // Clear state
  function clear() {
    modules.value = [];
    dependencies.value = [];
    rules.value = [];
    currentModule.value = null;
    validation.value = null;
    complexity.value = null;
  }

  return {
    // State
    modules,
    dependencies,
    rules,
    currentModule,
    validation,
    complexity,
    loading,
    error,
    // Actions
    generateArchitecture,
    fetchModules,
    fetchModule,
    createModule,
    updateModule,
    deleteModule,
    approveModule,
    fetchDependencies,
    createDependency,
    deleteDependency,
    validateArchitecture,
    analyzeComplexity,
    clear,
  };
});
