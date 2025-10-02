<template>
  <q-page class="q-pa-md">
    <div class="row q-col-gutter-md">
      <!-- Header -->
      <div class="col-12">
        <div class="row items-center justify-between">
          <div class="col">
            <div class="text-h4">🏗️ Architecture Designer</div>
            <div class="text-subtitle2 text-grey-7">
              AI-powered architecture generation and visualization
            </div>
          </div>
          <div class="col-auto">
            <q-btn
              color="secondary"
              icon="grid_on"
              label="Open Canvas"
              class="q-mr-sm"
              @click="openCanvas"
            />
            <q-btn
              color="primary"
              icon="auto_awesome"
              label="Generate Architecture"
              @click="showGenerateDialog = true"
            />
          </div>
        </div>
      </div>

      <!-- Modules List -->
      <div class="col-12">
        <q-card>
          <q-card-section>
            <div class="row items-center">
              <div class="text-h6">Architecture Modules</div>
              <q-space />
              <q-btn
                flat
                color="primary"
                icon="add"
                label="Add Module"
                @click="showCreateModuleDialog = true"
              />
            </div>
          </q-card-section>

          <q-separator />

          <q-list v-if="architectureStore.modules.length > 0" separator>
            <q-item
              v-for="module in architectureStore.modules"
              :key="module.id"
            >
              <q-item-section avatar>
                <q-icon
                  :name="getModuleIcon(module.module_type)"
                  :color="getModuleColor(module.status)"
                />
              </q-item-section>

              <q-item-section>
                <q-item-label>
                  {{ module.name }}
                  <q-chip
                    v-if="module.ai_generated"
                    size="sm"
                    color="purple"
                    text-color="white"
                  >
                    AI
                  </q-chip>
                </q-item-label>
                <q-item-label caption>
                  {{ module.description || 'No description' }}
                </q-item-label>
                <q-item-label caption class="q-mt-xs">
                  Type: {{ module.module_type }} • Level: {{ module.level }}
                </q-item-label>
              </q-item-section>

              <q-item-section side>
                <div class="row q-gutter-sm">
                  <q-chip
                    :color="getStatusColor(module.status)"
                    text-color="white"
                    size="sm"
                  >
                    {{ module.status }}
                  </q-chip>
                  <q-btn
                    flat
                    dense
                    icon="more_vert"
                    @click.stop="showModuleMenu(module)"
                  />
                </div>
              </q-item-section>
            </q-item>
          </q-list>

          <q-card-section v-else class="text-center text-grey-6">
            <q-icon name="architecture" size="64px" class="q-mb-md" />
            <div>No architecture modules</div>
            <div class="text-caption">
              Generate architecture using AI or create modules manually
            </div>
          </q-card-section>
        </q-card>
      </div>

      <!-- Analysis Cards -->
      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">Validation</div>
          </q-card-section>
          <q-card-section>
            <q-btn
              color="primary"
              label="Validate Architecture"
              @click="handleValidate"
              :loading="architectureStore.loading"
            />
            <div v-if="architectureStore.validation" class="q-mt-md">
              <div
                :class="{
                  'text-green': architectureStore.validation.is_valid,
                  'text-red': !architectureStore.validation.is_valid,
                }"
              >
                {{
                  architectureStore.validation.is_valid ? 'Valid ✓' : 'Invalid ✗'
                }}
              </div>
              <div class="text-caption q-mt-sm">
                Errors: {{ architectureStore.validation.errors_count }} •
                Warnings: {{ architectureStore.validation.warnings_count }}
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>

      <div class="col-md-6 col-12">
        <q-card>
          <q-card-section>
            <div class="text-h6">Complexity Analysis</div>
          </q-card-section>
          <q-card-section>
            <q-btn
              color="secondary"
              label="Analyze Complexity"
              @click="handleAnalyzeComplexity"
              :loading="architectureStore.loading"
            />
            <div v-if="architectureStore.complexity" class="q-mt-md">
              <div class="text-h4">
                {{ architectureStore.complexity.overall_complexity.toFixed(1) }}
                <span class="text-caption">/10</span>
              </div>
              <div class="text-caption">
                {{ architectureStore.complexity.metrics.module_count }} modules •
                {{ architectureStore.complexity.hotspots.length }} hotspots
              </div>
            </div>
          </q-card-section>
        </q-card>
      </div>
    </div>

    <!-- Generate Dialog -->
    <q-dialog v-model="showGenerateDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Generate Architecture with AI</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-select
            v-model="generateRequest.goal_ids"
            label="Goals"
            :options="[]"
            multiple
            filled
            class="q-mb-md"
          />
          <q-select
            v-model="generateRequest.opportunity_ids"
            label="Opportunities"
            :options="[]"
            multiple
            filled
            class="q-mb-md"
          />
          <q-input
            v-model="generateRequest.architectural_style"
            label="Architectural Style (optional)"
            filled
            hint="e.g., layered, microservices, hexagonal"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Generate"
            @click="handleGenerate"
            :loading="architectureStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Create Module Dialog -->
    <q-dialog v-model="showCreateModuleDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Create Module</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="newModule.name"
            label="Name *"
            filled
            class="q-mb-md"
          />
          <q-input
            v-model="newModule.description"
            label="Description"
            type="textarea"
            filled
            rows="3"
            class="q-mb-md"
          />
          <q-select
            v-model="newModule.module_type"
            :options="moduleTypes"
            label="Module Type"
            filled
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Create"
            @click="handleCreateModule"
            :loading="architectureStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useArchitectureStore } from 'src/stores/architecture';
import type {
  ArchitectureModule,
  ArchitectureModuleCreate,
  ArchitectureGenerationRequest,
} from 'src/types/architecture';

const route = useRoute();
const router = useRouter();
const architectureStore = useArchitectureStore();

const showGenerateDialog = ref(false);
const showCreateModuleDialog = ref(false);

const generateRequest = ref<ArchitectureGenerationRequest>({
  project_id: '',
  goal_ids: [],
  opportunity_ids: [],
  architectural_style: null,
  preferences: {},
});

const newModule = ref<ArchitectureModuleCreate>({
  project_id: '',
  name: '',
  description: '',
  module_type: 'package',
});

const moduleTypes = [
  'package',
  'class',
  'interface',
  'service',
  'component',
  'module',
];

onMounted(async () => {
  const projectId = route.params.projectId as string;
  if (projectId) {
    generateRequest.value.project_id = projectId;
    newModule.value.project_id = projectId;
    await architectureStore.fetchModules(projectId);
    await architectureStore.fetchDependencies(projectId);
  }
});

function getModuleIcon(type: string): string {
  const icons: Record<string, string> = {
    package: 'folder',
    class: 'code',
    interface: 'api',
    service: 'settings',
    component: 'widgets',
    module: 'view_module',
  };
  return icons[type] || 'article';
}

function getModuleColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'grey',
    approved: 'green',
    implemented: 'blue',
  };
  return colors[status] || 'grey';
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'orange',
    approved: 'green',
    implemented: 'blue',
  };
  return colors[status] || 'grey';
}

async function handleGenerate() {
  const result = await architectureStore.generateArchitecture(
    generateRequest.value.project_id,
    generateRequest.value
  );

  if (result) {
    showGenerateDialog.value = false;
    // Reset form
    generateRequest.value.goal_ids = [];
    generateRequest.value.opportunity_ids = [];
    generateRequest.value.architectural_style = null;
  }
}

async function handleCreateModule() {
  if (!newModule.value.name) {
    return;
  }

  const module = await architectureStore.createModule(newModule.value);
  if (module) {
    showCreateModuleDialog.value = false;
    newModule.value = {
      project_id: newModule.value.project_id,
      name: '',
      description: '',
      module_type: 'package',
    };
  }
}

async function handleValidate() {
  void await architectureStore.validateArchitecture(
    generateRequest.value.project_id
  );
}

async function handleAnalyzeComplexity() {
  await architectureStore.analyzeComplexity(generateRequest.value.project_id);
}

function showModuleMenu(module: ArchitectureModule) {
  // TODO: Show module actions menu
  console.log('Module menu:', module);
}

function openCanvas() {
  router.push({
    name: 'architecture-canvas',
    params: { projectId: route.params.projectId },
  });
}
</script>
