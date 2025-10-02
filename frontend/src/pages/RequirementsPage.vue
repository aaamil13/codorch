<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- Header -->
      <div class="col-12">
        <div class="row items-center justify-between">
          <div class="col">
            <div class="text-h4">📋 Requirements Definition</div>
            <div class="text-subtitle2 text-grey-7">
              Define and manage detailed requirements with AI validation
            </div>
          </div>
          <div class="col-auto">
            <q-btn
              color="secondary"
              icon="auto_awesome"
              label="Generate Tech Stack"
              class="q-mr-sm"
              @click="showTechDialog = true"
              :loading="requirementsStore.loading"
            />
            <q-btn
              color="primary"
              icon="add"
              label="New Requirement"
              @click="showCreateDialog = true"
            />
          </div>
        </div>
      </div>

      <!-- Summary Cards -->
      <div class="col-md-3 col-6" v-if="requirementsStore.summary">
        <q-card>
          <q-card-section>
            <div class="text-h3">{{ requirementsStore.summary.total_count }}</div>
            <div class="text-caption">Total Requirements</div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-3 col-6" v-if="requirementsStore.summary">
        <q-card>
          <q-card-section>
            <div class="text-h3">{{ requirementsStore.summary.validation_coverage.toFixed(0) }}%</div>
            <div class="text-caption">Validated</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Filters -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="row q-col-gutter-md">
              <div class="col-md-3 col-12">
                <q-select
                  v-model="filters.type_filter"
                  :options="typeOptions"
                  label="Type"
                  clearable
                  @update:model-value="handleFilterChange"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-select
                  v-model="filters.status_filter"
                  :options="statusOptions"
                  label="Status"
                  clearable
                  @update:model-value="handleFilterChange"
                />
              </div>
              <div class="col-md-3 col-12">
                <q-select
                  v-model="filters.priority_filter"
                  :options="priorityOptions"
                  label="Priority"
                  clearable
                  @update:model-value="handleFilterChange"
                />
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Requirements List -->
      <div class="col-12">
        <q-card>
          <q-list v-if="requirementsStore.requirements.length > 0" separator>
            <q-item
              v-for="req in requirementsStore.requirements"
              :key="req.id"
              clickable
              @click="selectRequirement(req)"
            >
              <q-item-section avatar>
                <q-icon
                  :name="getTypeIcon(req.type)"
                  :color="getTypeColor(req.type)"
                  size="md"
                />
              </q-item-section>

              <q-item-section>
                <q-item-label>
                  {{ req.title }}
                  <q-badge v-if="req.ai_generated" color="purple" class="q-ml-sm">AI</q-badge>
                </q-item-label>
                <q-item-label caption lines="2">
                  {{ req.description }}
                </q-item-label>
                <q-item-label caption class="q-mt-xs">
                  Type: {{ req.type }} • Priority: {{ req.priority }}
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="column q-gutter-sm">
                  <q-chip
                    :color="getStatusColor(req.status)"
                    text-color="white"
                    size="sm"
                  >
                    {{ req.status }}
                  </q-chip>
                  <div class="row q-gutter-xs">
                    <q-btn
                      flat
                      dense
                      icon="check_circle"
                      color="primary"
                      size="sm"
                      @click.stop="handleValidate(req.id)"
                    >
                      <q-tooltip>Validate</q-tooltip>
                    </q-btn>
                    <q-btn
                      flat
                      dense
                      icon="edit"
                      size="sm"
                      @click.stop="handleEdit(req)"
                    >
                      <q-tooltip>Edit</q-tooltip>
                    </q-btn>
                    <q-btn
                      v-if="req.status === 'validated'"
                      flat
                      dense
                      icon="done_all"
                      color="positive"
                      size="sm"
                      @click.stop="handleApprove(req.id)"
                    >
                      <q-tooltip>Approve</q-tooltip>
                    </q-btn>
                  </div>
                </div>
              </q-item-section>
            </q-item>
          </q-list>

          <q-card-section v-else class="text-center text-grey-6">
            <q-icon name="description" size="64px" class="q-mb-md" />
            <div>No requirements defined</div>
            <div class="text-caption">Create requirements or link architecture modules</div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Technology Recommendations -->
      <div class="col-12" v-if="requirementsStore.technologies.length > 0">
        <q-card>
          <q-card-section>
            <div class="text-h6">🚀 Technology Recommendations</div>
          </q-card-section>
          <q-separator />
          <q-list>
            <q-item v-for="tech in requirementsStore.technologies" :key="tech.id">
              <q-item-section avatar>
                <q-avatar color="primary" text-color="white">
                  {{ tech.suitability_score.toFixed(1) }}
                </q-avatar>
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ tech.name }} <span v-if="tech.version">v{{ tech.version }}</span></q-item-label>
                <q-item-label caption>{{ tech.technology_type }}</q-item-label>
                <q-item-label caption class="q-mt-xs">{{ tech.reasoning }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <div class="row q-gutter-xs">
                  <q-btn
                    flat
                    dense
                    icon="check"
                    color="positive"
                    @click="handleAcceptTech(tech.id)"
                    :disable="tech.status === 'accepted'"
                  >
                    <q-tooltip>Accept</q-tooltip>
                  </q-btn>
                  <q-btn
                    flat
                    dense
                    icon="close"
                    color="negative"
                    @click="handleRejectTech(tech.id)"
                    :disable="tech.status === 'rejected'"
                  >
                    <q-tooltip>Reject</q-tooltip>
                  </q-btn>
                </div>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card>
      </div>
    </div>

    <!-- Create Dialog -->
    <q-dialog v-model="showCreateDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Create Requirement</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-select
            v-model="newRequirement.type"
            :options="typeOptions"
            label="Type *"
            filled
            class="q-mb-md"
          />
          <q-input
            v-model="newRequirement.title"
            label="Title *"
            filled
            class="q-mb-md"
          />
          <q-input
            v-model="newRequirement.description"
            label="Description *"
            type="textarea"
            filled
            rows="5"
            class="q-mb-md"
          />
          <q-select
            v-model="newRequirement.priority"
            :options="priorityOptions"
            label="Priority"
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Create"
            @click="handleCreate"
            :loading="requirementsStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Tech Generation Dialog -->
    <q-dialog v-model="showTechDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Generate Technology Recommendations</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="text-caption text-grey-7 q-mb-md">
            AI will analyze requirements and recommend suitable technologies
          </div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Generate"
            @click="handleGenerateTech"
            :loading="requirementsStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useRequirementsStore } from 'src/stores/requirements';
import { Notify } from 'quasar';
import type { Requirement, RequirementCreate } from 'src/types/requirements';

const route = useRoute();
const requirementsStore = useRequirementsStore();

const showCreateDialog = ref(false);
const showTechDialog = ref(false);

const filters = ref({
  type_filter: null as string | null,
  status_filter: null as string | null,
  priority_filter: null as string | null,
});

const newRequirement = ref<RequirementCreate>({
  project_id: '',
  type: 'functional',
  title: '',
  description: '',
  priority: 'should_have',
});

const typeOptions = ['functional', 'non_functional', 'technical', 'api', 'data', 'testing'];
const statusOptions = ['draft', 'validated', 'approved', 'implemented'];
const priorityOptions = ['must_have', 'should_have', 'nice_to_have'];

onMounted(async () => {
  const projectId = route.params.projectId as string;
  if (projectId) {
    newRequirement.value.project_id = projectId;
    await requirementsStore.fetchRequirements(projectId);
    await requirementsStore.fetchSummary(projectId);
    await requirementsStore.fetchTechnologyRecommendations(projectId);
  }
});

function getTypeIcon(type: string): string {
  const icons: Record<string, string> = {
    functional: 'functions',
    non_functional: 'speed',
    technical: 'build',
    api: 'api',
    data: 'storage',
    testing: 'bug_report',
  };
  return icons[type] || 'description';
}

function getTypeColor(type: string): string {
  const colors: Record<string, string> = {
    functional: 'blue',
    non_functional: 'purple',
    technical: 'orange',
    api: 'green',
    data: 'teal',
    testing: 'red',
  };
  return colors[type] || 'grey';
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'grey',
    validated: 'orange',
    approved: 'green',
    implemented: 'blue',
  };
  return colors[status] || 'grey';
}

async function handleFilterChange() {
  const projectId = route.params.projectId as string;
  const requestFilters: {
    type_filter?: string;
    status_filter?: string;
    priority_filter?: string;
  } = {};

  if (filters.value.type_filter) {
    requestFilters.type_filter = filters.value.type_filter;
  }
  if (filters.value.status_filter) {
    requestFilters.status_filter = filters.value.status_filter;
  }
  if (filters.value.priority_filter) {
    requestFilters.priority_filter = filters.value.priority_filter;
  }

  await requirementsStore.fetchRequirements(projectId, requestFilters);
}

async function handleCreate() {
  if (!newRequirement.value.title || !newRequirement.value.description) {
    Notify.create({ type: 'warning', message: 'Please fill required fields' });
    return;
  }

  const result = await requirementsStore.createRequirement(newRequirement.value);
  if (result) {
    showCreateDialog.value = false;
    newRequirement.value = {
      project_id: newRequirement.value.project_id,
      type: 'functional',
      title: '',
      description: '',
      priority: 'should_have',
    };
    Notify.create({ type: 'positive', message: 'Requirement created' });
  }
}

async function handleValidate(id: string) {
  const result = await requirementsStore.validateRequirement(id);
  if (result) {
    Notify.create({
      type: result.is_valid ? 'positive' : 'warning',
      message: `Validation ${result.is_valid ? 'passed' : 'failed'} - Score: ${result.overall_score.toFixed(1)}/10`,
    });
  }
}

async function handleApprove(id: string) {
  const result = await requirementsStore.approveRequirement(id);
  if (result) {
    Notify.create({ type: 'positive', message: 'Requirement approved' });
  }
}

async function handleGenerateTech() {
  const projectId = route.params.projectId as string;
  const result = await requirementsStore.generateTechnologyRecommendations(projectId, {
    project_id: projectId,
    preferences: {},
  });
  if (result) {
    showTechDialog.value = false;
    Notify.create({ type: 'positive', message: `Generated ${result.total_count} recommendations` });
  }
}

async function handleAcceptTech(id: string) {
  await requirementsStore.updateTechnologyRecommendation(id, 'accepted');
  Notify.create({ type: 'positive', message: 'Technology accepted' });
}

async function handleRejectTech(id: string) {
  await requirementsStore.updateTechnologyRecommendation(id, 'rejected');
  Notify.create({ type: 'info', message: 'Technology rejected' });
}

function selectRequirement(req: Requirement) {
  console.log('Selected requirement:', req);
}

function handleEdit(req: Requirement) {
  console.log('Edit requirement:', req);
}
</script>
