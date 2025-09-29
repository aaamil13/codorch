<template>
  <q-page class="research-session-page">
    <div class="row q-col-gutter-md q-pa-md" style="height: calc(100vh - 50px)">
      <!-- Chat Section -->
      <div class="col-8">
        <q-card class="full-height column">
          <q-card-section class="bg-primary text-white">
            <div class="text-h6">{{ researchStore.currentSession?.title || 'Research Session' }}</div>
            <div class="text-caption">AI-powered research chat</div>
          </q-card-section>

          <!-- Messages -->
          <q-card-section class="col scroll" style="max-height: calc(100vh - 300px)">
            <div v-for="message in researchStore.messages" :key="message.id" class="q-mb-md">
              <div :class="message.role === 'user' ? 'text-right' : ''">
                <q-chat-message
                  :name="message.role === 'user' ? 'You' : 'AI Research Team'"
                  :text="[message.content]"
                  :sent="message.role === 'user'"
                  :bg-color="message.role === 'user' ? 'primary' : 'grey-3'"
                  :text-color="message.role === 'user' ? 'white' : 'black'"
                />
              </div>
            </div>

            <div v-if="researchStore.loading" class="text-center text-grey-6 q-my-md">
              <q-spinner-dots size="40px" />
              <div>AI Team is researching...</div>
            </div>
          </q-card-section>

          <!-- Input -->
          <q-card-section class="q-pt-none">
            <q-input
              v-model="messageInput"
              placeholder="Ask a question..."
              filled
              @keyup.enter="handleSendMessage"
              :loading="researchStore.loading"
            >
              <template #append>
                <q-btn
                  icon="send"
                  flat
                  round
                  @click="handleSendMessage"
                  :loading="researchStore.loading"
                />
              </template>
            </q-input>
          </q-card-section>
        </q-card>
      </div>

      <!-- Findings Sidebar -->
      <div class="col-4">
        <q-card class="full-height">
          <q-card-section class="bg-secondary text-white">
            <div class="text-h6">📊 Findings</div>
            <div class="text-caption">{{ researchStore.findings.length }} insights discovered</div>
          </q-card-section>

          <q-card-section class="scroll" style="max-height: calc(100vh - 200px)">
            <div
              v-for="finding in researchStore.findings"
              :key="finding.id"
              class="q-mb-md"
            >
              <q-card>
                <q-card-section>
                  <div class="row items-center q-mb-sm">
                    <q-chip
                      :color="getFindingColor(finding.finding_type)"
                      text-color="white"
                      size="sm"
                    >
                      {{ finding.finding_type }}
                    </q-chip>
                    <q-space />
                    <div class="text-caption text-grey-6">
                      {{ (finding.confidence_score * 100).toFixed(0) }}%
                    </div>
                  </div>

                  <div class="text-subtitle2 text-weight-bold">
                    {{ finding.title }}
                  </div>
                  <div class="text-caption q-mt-sm">
                    {{ finding.description }}
                  </div>
                </q-card-section>
              </q-card>
            </div>

            <div
              v-if="researchStore.findings.length === 0"
              class="text-center text-grey-6 q-mt-lg"
            >
              <q-icon name="lightbulb" size="48px" class="q-mb-md" />
              <div>No findings yet</div>
              <div class="text-caption">Start chatting to discover insights</div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useResearchStore } from 'src/stores/research';

const route = useRoute();
const researchStore = useResearchStore();

const messageInput = ref('');

onMounted(async () => {
  const sessionId = route.params.sessionId as string;
  if (sessionId) {
    await Promise.all([
      researchStore.fetchSession(sessionId),
      researchStore.fetchMessages(sessionId),
      researchStore.fetchFindings(sessionId),
    ]);
  }
});

async function handleSendMessage() {
  if (!messageInput.value.trim() || researchStore.loading) {
    return;
  }

  const sessionId = route.params.sessionId as string;
  const message = messageInput.value;
  messageInput.value = '';

  await researchStore.sendMessage(sessionId, {
    message,
    stream: false,
  });

  // Refresh findings after AI response
  await researchStore.fetchFindings(sessionId);
}

function getFindingColor(type: string): string {
  const colors: Record<string, string> = {
    technical: 'blue',
    market: 'green',
    user: 'orange',
    competitor: 'red',
    other: 'grey',
  };
  return colors[type] || 'grey';
}
</script>

<style scoped>
.research-session-page {
  background: #f5f5f5;
}
</style>
