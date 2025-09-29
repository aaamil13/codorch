<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- Header -->
      <div class="col-12">
        <div class="row items-center justify-between">
          <div class="col">
            <div class="text-h4">🔬 Research Sessions</div>
            <div class="text-subtitle2 text-grey-7">
              AI-powered research and analysis
            </div>
          </div>
          <div class="col-auto">
            <q-btn
              color="primary"
              icon="add"
              label="New Session"
              @click="showCreateDialog = true"
            />
          </div>
        </div>
      </div>

      <!-- Sessions List -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">Active Sessions</div>
          </q-card-section>

          <q-separator />

          <q-list v-if="researchStore.activeSessions.length > 0" separator>
            <q-item
              v-for="session in researchStore.activeSessions"
              :key="session.id"
              clickable
              @click="goToSession(session.id)"
            >
              <q-item-section>
                <q-item-label>{{ session.title }}</q-item-label>
                <q-item-label caption>
                  {{ session.description || 'No description' }}
                </q-item-label>
                <q-item-label caption class="q-mt-xs">
                  {{ session.message_count }} messages •
                  {{ session.finding_count }} findings
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="text-grey-7 text-caption">
                  {{ formatDate(session.updated_at) }}
                </div>
              </q-item-section>
            </q-item>
          </q-list>

          <q-card-section v-else class="text-center text-grey-6">
            <q-icon name="science" size="64px" class="q-mb-md" />
            <div>No active research sessions</div>
            <div class="text-caption">Create your first session to start</div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Create Dialog -->
    <q-dialog v-model="showCreateDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">New Research Session</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newSession.title"
            label="Title *"
            filled
            class="q-mb-md"
          />
          <q-input
            v-model="newSession.description"
            label="Description"
            type="textarea"
            filled
            rows="3"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Create"
            @click="handleCreateSession"
            :loading="researchStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useResearchStore } from 'src/stores/research';
import type { ResearchSessionCreate } from 'src/types/research';

const router = useRouter();
const route = useRoute();
const researchStore = useResearchStore();

const showCreateDialog = ref(false);
const newSession = ref<ResearchSessionCreate>({
  project_id: '',
  title: '',
  description: '',
});

onMounted(async () => {
  const projectId = route.params.projectId as string;
  if (projectId) {
    newSession.value.project_id = projectId;
    await researchStore.fetchSessions(projectId);
  }
});

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString();
}

function goToSession(sessionId: string) {
  router.push({
    name: 'research-session',
    params: { sessionId },
  });
}

async function handleCreateSession() {
  if (!newSession.value.title) {
    return;
  }

  const session = await researchStore.createSession(newSession.value);
  if (session) {
    showCreateDialog.value = false;
    newSession.value = {
      project_id: newSession.value.project_id,
      title: '',
      description: '',
    };
    goToSession(session.id);
  }
}
</script>
