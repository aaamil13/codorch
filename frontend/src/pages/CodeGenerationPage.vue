<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- Header -->
      <div class="col-12">
        <div class="text-h4">⚡ Code Generation</div>
        <div class="text-subtitle2 text-grey-7">
          AI-powered code generation with validation and approval workflow
        </div>
      </div>

      <!-- Validation Card -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center justify-between">
              <div class="text-h6">Pre-Generation Validation</div>
              <q-btn
                color="primary"
                label="Validate Project"
                @click="handleValidate"
                :loading="codeGenStore.loading"
              />
            </div>
          </q-card-section>

          <q-card-section v-if="codeGenStore.validation">
            <div class="row q-col-gutter-md q-mb-md">
              <div class="col-md-3 col-6">
                <div class="text-caption">Architecture</div>
                <div class="text-h5">{{ codeGenStore.validation.architecture_completeness.toFixed(0) }}%</div>
              </div>
              <div class="col-md-3 col-6">
                <div class="text-caption">Requirements</div>
                <div class="text-h5">{{ codeGenStore.validation.requirements_clarity.toFixed(0) }}%</div>
              </div>
              <div class="col-md-3 col-6">
                <div class="text-caption">Overall Readiness</div>
                <div class="text-h5">{{ codeGenStore.validation.overall_readiness.toFixed(0) }}%</div>
              </div>
              <div class="col-md-3 col-6">
                <div class="text-caption">Status</div>
                <q-chip
                  :color="codeGenStore.validation.can_proceed ? 'green' : 'red'"
                  text-color="white"
                >
                  {{ codeGenStore.validation.can_proceed ? 'Ready' : 'Not Ready' }}
                </q-chip>
              </div>
            </div>

            <q-separator class="q-my-md" />

            <div v-if="codeGenStore.validation.blocking_issues.length > 0" class="q-mb-md">
              <div class="text-subtitle2 text-negative q-mb-sm">Blocking Issues:</div>
              <q-list bordered>
                <q-item v-for="(issue, idx) in codeGenStore.validation.blocking_issues" :key="idx">
                  <q-item-section avatar>
                    <q-icon name="error" color="red" />
                  </q-item-section>
                  <q-item-section>{{ issue }}</q-item-section>
                </q-item>
              </q-list>
            </div>

            <q-btn
              v-if="codeGenStore.validation.can_proceed"
              color="positive"
              icon="rocket_launch"
              label="Start Code Generation"
              @click="handleStartGeneration"
              :loading="codeGenStore.loading"
            />
          </q-card-section>
        </q-card>
      </div>

      <!-- Sessions List -->
      <div class="col-12" v-if="codeGenStore.sessions.length > 0">
        <q-card>
          <q-card-section>
            <div class="text-h6">Generation Sessions</div>
          </q-card-section>
          <q-separator />
          <q-list>
            <q-item
              v-for="session in codeGenStore.sessions"
              :key="session.id"
              clickable
              @click="selectSession(session)"
            >
              <q-item-section avatar>
                <q-icon :name="getStatusIcon(session.status)" :color="getStatusColor(session.status)" />
              </q-item-section>
              <q-item-section>
                <q-item-label>Session {{ session.id.substring(0, 8) }}</q-item-label>
                <q-item-label caption>{{ new Date(session.created_at).toLocaleString() }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-chip :color="getStatusColor(session.status)" text-color="white">
                  {{ session.status }}
                </q-chip>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>

      <!-- Current Session Workflow -->
      <div class="col-12" v-if="codeGenStore.currentSession">
        <q-card>
          <q-card-section>
            <div class="text-h6">Active Session Workflow</div>
          </q-card-section>
          <q-separator />
          <q-card-section>
            <q-stepper v-model="currentStep" vertical color="primary">
              <q-step :name="1" title="Validation" icon="check_circle" :done="currentStep > 1">
                <div>Pre-generation validation completed</div>
              </q-step>

              <q-step :name="2" title="Scaffold Generation" icon="account_tree" :done="currentStep > 2">
                <div class="q-mb-md">Generate project scaffold</div>
                <q-btn
                  v-if="codeGenStore.currentSession.status === 'ready'"
                  color="primary"
                  label="Generate Scaffold"
                  @click="handleGenerateScaffold"
                  :loading="codeGenStore.loading"
                />
              </q-step>

              <q-step :name="3" title="Approve Scaffold" icon="done_all" :done="currentStep > 3">
                <div class="q-mb-md">Review and approve scaffold</div>
                <div v-if="codeGenStore.currentSession.scaffold_code" class="q-mb-md">
                  <div class="text-caption">Scaffold generated!</div>
                </div>
                <div class="row q-gutter-sm">
                  <q-btn
                    color="positive"
                    label="Approve"
                    @click="handleApproveScaffold(true)"
                    :loading="codeGenStore.loading"
                  />
                  <q-btn
                    color="negative"
                    label="Reject"
                    @click="handleApproveScaffold(false)"
                  />
                </div>
              </q-step>

              <q-step :name="4" title="Implementation" icon="code" :done="currentStep > 4">
                <div class="q-mb-md">Generate full implementation</div>
                <q-btn
                  color="primary"
                  label="Generate Code"
                  @click="handleGenerateCode"
                  :loading="codeGenStore.loading"
                />
              </q-step>

              <q-step :name="5" title="Approve Code" icon="verified" :done="currentStep > 5">
                <div class="q-mb-md">Review and approve generated code</div>
                <div class="row q-gutter-sm">
                  <q-btn
                    color="positive"
                    label="Approve & Complete"
                    @click="handleApproveCode(true)"
                    :loading="codeGenStore.loading"
                  />
                  <q-btn
                    color="negative"
                    label="Reject"
                    @click="handleApproveCode(false)"
                  />
                </div>
              </q-step>

              <q-step :name="6" title="Completed" icon="celebration">
                <div class="text-positive text-h6">✓ Code Generation Complete!</div>
                <div class="q-mt-md">
                  <q-btn color="primary" label="Download Files" icon="download" />
                </div>
              </q-step>
            </q-stepper>
          </q-card-section>
        </q-card>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useCodeGenerationStore } from 'src/stores/codeGeneration';
import { Notify } from 'quasar';
import type { CodeGenerationSession } from 'src/types/codeGeneration';

const route = useRoute();
const codeGenStore = useCodeGenerationStore();

const currentStep = computed(() => {
  if (!codeGenStore.currentSession) return 1;
  const status = codeGenStore.currentSession.status;
  if (status === 'completed') return 6;
  if (status === 'generating_code' || status === 'reviewing_code') return 5;
  if (status === 'ready_for_implementation') return 4;
  if (status === 'reviewing_scaffold') return 3;
  if (status === 'generating_scaffold') return 2;
  return 1;
});

onMounted(async () => {
  const projectId = route.params.projectId as string;
  if (projectId) {
    await codeGenStore.fetchSessions(projectId);
  }
});

async function handleValidate() {
  const projectId = route.params.projectId as string;
  const result = await codeGenStore.validateProject(projectId);
  if (result) {
    Notify.create({
      type: result.can_proceed ? 'positive' : 'warning',
      message: result.can_proceed
        ? `Ready for generation! Readiness: ${result.overall_readiness.toFixed(0)}%`
        : 'Project not ready - fix blocking issues',
    });
  }
}

async function handleStartGeneration() {
  const projectId = route.params.projectId as string;
  const session = await codeGenStore.createSession({ project_id: projectId });
  if (session) {
    Notify.create({ type: 'positive', message: 'Generation session created' });
  }
}

async function handleGenerateScaffold() {
  if (!codeGenStore.currentSession) return;
  const session = await codeGenStore.generateScaffold(codeGenStore.currentSession.id);
  if (session) {
    Notify.create({ type: 'positive', message: 'Scaffold generated successfully' });
  }
}

async function handleApproveScaffold(approved: boolean) {
  if (!codeGenStore.currentSession) return;
  const result = await codeGenStore.approveScaffold(codeGenStore.currentSession.id, { approved });
  if (result) {
    Notify.create({
      type: approved ? 'positive' : 'info',
      message: approved ? 'Scaffold approved' : 'Scaffold rejected',
    });
  }
}

async function handleGenerateCode() {
  if (!codeGenStore.currentSession) return;
  const session = await codeGenStore.generateImplementation(codeGenStore.currentSession.id);
  if (session) {
    Notify.create({ type: 'positive', message: 'Code generated successfully' });
  }
}

async function handleApproveCode(approved: boolean) {
  if (!codeGenStore.currentSession) return;
  const result = await codeGenStore.approveCode(codeGenStore.currentSession.id, { approved });
  if (result) {
    Notify.create({
      type: approved ? 'positive' : 'info',
      message: approved ? '✓ Code generation complete!' : 'Code rejected',
    });
  }
}

function selectSession(session: CodeGenerationSession) {
  codeGenStore.currentSession = session;
}

function getStatusIcon(status: string): string {
  const icons: Record<string, string> = {
    validating: 'hourglass_empty',
    ready: 'check_circle',
    generating_scaffold: 'account_tree',
    reviewing_scaffold: 'rate_review',
    generating_code: 'code',
    reviewing_code: 'fact_check',
    completed: 'celebration',
    failed: 'error',
  };
  return icons[status] || 'help';
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    validating: 'orange',
    ready: 'green',
    generating_scaffold: 'blue',
    reviewing_scaffold: 'purple',
    generating_code: 'indigo',
    reviewing_code: 'purple',
    completed: 'positive',
    failed: 'negative',
  };
  return colors[status] || 'grey';
}
</script>
