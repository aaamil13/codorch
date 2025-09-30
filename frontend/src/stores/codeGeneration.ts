/**
 * Pinia store for Code Generation Module
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type {
  CodeGenerationSession,
  CodeGenerationSessionCreate,
  PreGenerationValidation,
  GeneratedFile,
  ApprovalRequest,
} from 'src/types/codeGeneration';
import * as codeGenApi from 'src/services/codeGenerationApi';

export const useCodeGenerationStore = defineStore('codeGeneration', () => {
  // State
  const sessions = ref<CodeGenerationSession[]>([]);
  const currentSession = ref<CodeGenerationSession | null>(null);
  const validation = ref<PreGenerationValidation | null>(null);
  const files = ref<GeneratedFile[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  async function validateProject(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      validation.value = await codeGenApi.validateProject(projectId);
      return validation.value;
    } catch (err) {
      error.value = `Validation failed: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function createSession(data: CodeGenerationSessionCreate) {
    loading.value = true;
    error.value = null;
    try {
      const session = await codeGenApi.createSession(data);
      sessions.value.unshift(session);
      currentSession.value = session;
      return session;
    } catch (err) {
      error.value = `Failed to create session: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchSession(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      currentSession.value = await codeGenApi.getSession(sessionId);
    } catch (err) {
      error.value = `Failed to fetch session: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchSessions(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      sessions.value = await codeGenApi.listSessions(projectId);
    } catch (err) {
      error.value = `Failed to fetch sessions: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function generateScaffold(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      const session = await codeGenApi.generateScaffold(sessionId);
      currentSession.value = session;
      return session;
    } catch (err) {
      error.value = `Scaffold generation failed: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function approveScaffold(sessionId: string, data: ApprovalRequest) {
    loading.value = true;
    error.value = null;
    try {
      const response = await codeGenApi.approveScaffold(sessionId, data);
      if (currentSession.value) {
        await fetchSession(sessionId);
      }
      return response;
    } catch (err) {
      error.value = `Approval failed: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function generateImplementation(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      const session = await codeGenApi.generateImplementation(sessionId);
      currentSession.value = session;
      return session;
    } catch (err) {
      error.value = `Code generation failed: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function approveCode(sessionId: string, data: ApprovalRequest) {
    loading.value = true;
    error.value = null;
    try {
      const response = await codeGenApi.approveCode(sessionId, data);
      if (currentSession.value) {
        await fetchSession(sessionId);
      }
      return response;
    } catch (err) {
      error.value = `Approval failed: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function fetchFiles(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      files.value = await codeGenApi.listFiles(sessionId);
    } catch (err) {
      error.value = `Failed to fetch files: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function deleteSession(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      await codeGenApi.deleteSession(sessionId);
      sessions.value = sessions.value.filter((s) => s.id !== sessionId);
      if (currentSession.value?.id === sessionId) {
        currentSession.value = null;
      }
    } catch (err) {
      error.value = `Failed to delete session: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  function clear() {
    sessions.value = [];
    currentSession.value = null;
    validation.value = null;
    files.value = [];
  }

  return {
    // State
    sessions,
    currentSession,
    validation,
    files,
    loading,
    error,
    // Actions
    validateProject,
    createSession,
    fetchSession,
    fetchSessions,
    generateScaffold,
    approveScaffold,
    generateImplementation,
    approveCode,
    fetchFiles,
    deleteSession,
    clear,
  };
});
