/**
 * Pinia store for Research Module
 */

import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type {
  ResearchSession,
  ResearchSessionCreate,
  ResearchMessage,
  ResearchFinding,
  ChatRequest,
} from 'src/types/research';
import * as researchApi from 'src/services/researchApi';

export const useResearchStore = defineStore('research', () => {
  // State
  const sessions = ref<ResearchSession[]>([]);
  const currentSession = ref<ResearchSession | null>(null);
  const messages = ref<ResearchMessage[]>([]);
  const findings = ref<ResearchFinding[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // Getters
  const activeSessions = computed(() =>
    sessions.value.filter((s) => s.status === 'active')
  );

  const archivedSessions = computed(() =>
    sessions.value.filter((s) => s.status === 'archived')
  );

  // Actions - Sessions
  async function fetchSessions(projectId: string) {
    loading.value = true;
    error.value = null;
    try {
      sessions.value = await researchApi.listResearchSessions(projectId);
    } catch (err) {
      error.value = `Failed to fetch sessions: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function fetchSession(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      currentSession.value = await researchApi.getResearchSession(sessionId);
    } catch (err) {
      error.value = `Failed to fetch session: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function createSession(data: ResearchSessionCreate) {
    loading.value = true;
    error.value = null;
    try {
      const session = await researchApi.createResearchSession(data);
      sessions.value.unshift(session);
      return session;
    } catch (err) {
      error.value = `Failed to create session: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  async function archiveSession(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      const updated = await researchApi.archiveResearchSession(sessionId);
      const index = sessions.value.findIndex((s) => s.id === sessionId);
      if (index !== -1) {
        sessions.value[index] = updated;
      }
      if (currentSession.value?.id === sessionId) {
        currentSession.value = updated;
      }
    } catch (err) {
      error.value = `Failed to archive session: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  // Actions - Messages
  async function fetchMessages(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      messages.value = await researchApi.getSessionMessages(sessionId);
    } catch (err) {
      error.value = `Failed to fetch messages: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  async function sendMessage(sessionId: string, request: ChatRequest) {
    loading.value = true;
    error.value = null;
    try {
      const response = await researchApi.sendChatMessage(sessionId, request);
      
      // Add user message
      messages.value.push({
        id: crypto.randomUUID(),
        session_id: sessionId,
        role: 'user',
        content: request.message,
        created_at: new Date().toISOString(),
      });

      // Add assistant response
      messages.value.push({
        id: response.message_id,
        session_id: sessionId,
        role: 'assistant',
        content: response.content,
        metadata: response.metadata,
        created_at: new Date().toISOString(),
      });

      return response;
    } catch (err) {
      error.value = `Failed to send message: ${err}`;
      console.error(err);
      return null;
    } finally {
      loading.value = false;
    }
  }

  // Actions - Findings
  async function fetchFindings(sessionId: string) {
    loading.value = true;
    error.value = null;
    try {
      findings.value = await researchApi.getSessionFindings(sessionId);
    } catch (err) {
      error.value = `Failed to fetch findings: ${err}`;
      console.error(err);
    } finally {
      loading.value = false;
    }
  }

  // Clear state
  function clearCurrentSession() {
    currentSession.value = null;
    messages.value = [];
    findings.value = [];
  }

  return {
    // State
    sessions,
    currentSession,
    messages,
    findings,
    loading,
    error,
    // Getters
    activeSessions,
    archivedSessions,
    // Actions
    fetchSessions,
    fetchSession,
    createSession,
    archiveSession,
    fetchMessages,
    sendMessage,
    fetchFindings,
    clearCurrentSession,
  };
});
