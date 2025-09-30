<template>
  <q-page class="architecture-canvas-page">
    <!-- Toolbar -->
    <div class="canvas-toolbar">
      <div class="toolbar-left">
        <q-btn
          flat
          icon="arrow_back"
          label="Back"
          @click="router.back()"
        />
        <q-separator vertical class="q-mx-sm" />
        <div class="text-h6">Architecture Canvas</div>
      </div>

      <div class="toolbar-center">
        <q-btn
          flat
          icon="add"
          label="Add Module"
          @click="showAddModuleDialog = true"
        />
        <q-btn
          flat
          icon="link"
          label="Add Dependency"
          @click="showAddDependencyDialog = true"
          :disable="!selectedModule"
        />
        <q-separator vertical class="q-mx-sm" />
        <q-btn
          flat
          icon="check_circle"
          label="Validate"
          @click="handleValidate"
          :loading="architectureStore.loading"
        />
        <q-btn
          flat
          icon="analytics"
          label="Complexity"
          @click="handleComplexity"
          :loading="architectureStore.loading"
        />
        <q-separator vertical class="q-mx-sm" />
        <q-btn
          flat
          icon="science"
          label="Impact Analysis"
          color="purple"
          @click="handleImpactAnalysisAdvanced"
          :disable="!selectedModule"
          :loading="architectureStore.loading"
        >
          <q-tooltip>RefMemTree Advanced: Analyze change impact</q-tooltip>
        </q-btn>
        <q-btn
          flat
          icon="psychology"
          label="Simulate Change"
          color="deep-purple"
          @click="showSimulateDialog = true"
          :disable="!selectedModule"
        >
          <q-tooltip>RefMemTree Advanced: Simulate before changing</q-tooltip>
        </q-btn>
      </div>

      <div class="toolbar-right">
        <q-btn
          flat
          icon="auto_awesome"
          label="AI Generate"
          color="primary"
          @click="showGenerateDialog = true"
        />
        <q-separator vertical class="q-mx-sm" />
        <q-btn
          flat
          icon="save"
          label="Save"
          color="positive"
          @click="handleSave"
        />
      </div>
    </div>

    <!-- Vue Flow Canvas -->
    <div class="canvas-container">
      <VueFlow
        v-model:nodes="nodes"
        v-model:edges="edges"
        :default-viewport="{ zoom: 0.8 }"
        :min-zoom="0.2"
        :max-zoom="4"
        @nodes-change="onNodesChange"
        @edges-change="onEdgesChange"
        @node-click="onNodeClick"
        @edge-click="onEdgeClick"
        @pane-click="onPaneClick"
        @connect="onConnect"
        fit-view-on-init
      >
        <!-- Custom Node Type -->
        <template #node-module="props">
          <ModuleNode :data="props.data" />
        </template>

        <!-- Background -->
        <Background
          pattern-color="#aaa"
          :gap="16"
          variant="dots"
        />

        <!-- Controls -->
        <Controls>
          <ControlButton @click="fitView">
            <q-icon name="fit_screen" />
          </ControlButton>
          <ControlButton @click="zoomIn">
            <q-icon name="zoom_in" />
          </ControlButton>
          <ControlButton @click="zoomOut">
            <q-icon name="zoom_out" />
          </ControlButton>
        </Controls>

        <!-- MiniMap -->
        <MiniMap
          pannable
          zoomable
          :node-color="getNodeColor"
        />
      </VueFlow>
    </div>

    <!-- Side Panel -->
    <q-drawer
      v-model="showSidePanel"
      side="right"
      overlay
      elevated
      :width="400"
      :breakpoint="700"
    >
      <q-scroll-area class="fit">
        <div class="q-pa-md">
          <div v-if="selectedModule" class="module-details">
            <div class="text-h6 q-mb-md">
              {{ selectedModule.data.name }}
              <q-badge
                v-if="selectedModule.data.ai_generated"
                color="purple"
                class="q-ml-sm"
              >
                AI Generated
              </q-badge>
            </div>

            <q-separator class="q-mb-md" />

            <!-- Module Info -->
            <div class="q-mb-md">
              <div class="text-subtitle2">Type</div>
              <q-chip>{{ selectedModule.data.module_type }}</q-chip>
            </div>

            <div class="q-mb-md">
              <div class="text-subtitle2">Status</div>
              <q-chip :color="getStatusColor(selectedModule.data.status)">
                {{ selectedModule.data.status }}
              </q-chip>
            </div>

            <div class="q-mb-md">
              <div class="text-subtitle2">Description</div>
              <div>{{ selectedModule.data.description || 'No description' }}</div>
            </div>

            <div class="q-mb-md">
              <div class="text-subtitle2">Level</div>
              <div>{{ selectedModule.data.level }}</div>
            </div>

            <!-- Actions -->
            <div class="q-mt-md">
              <q-btn
                color="primary"
                label="Edit"
                class="q-mr-sm"
                @click="handleEditModule"
              />
              <q-btn
                v-if="selectedModule.data.status === 'draft'"
                color="positive"
                label="Approve"
                class="q-mr-sm"
                @click="handleApproveModule"
              />
              <q-btn
                color="negative"
                label="Delete"
                @click="handleDeleteModule"
              />
            </div>

            <!-- Dependencies -->
            <q-separator class="q-my-md" />
            <div class="text-subtitle2 q-mb-sm">Dependencies</div>
            <div v-if="getModuleDependencies(selectedModule.id).length > 0">
              <q-chip
                v-for="dep in getModuleDependencies(selectedModule.id)"
                :key="dep.id"
                removable
                @remove="handleRemoveDependency(dep.id)"
                class="q-mr-sm q-mb-sm"
              >
                {{ getModuleName(dep.to_module_id) }} ({{ dep.dependency_type }})
              </q-chip>
            </div>
            <div v-else class="text-grey-6">No dependencies</div>
          </div>

          <div v-else class="text-center text-grey-6 q-pa-xl">
            Click on a module to view details
          </div>
        </div>
      </q-scroll-area>
    </q-drawer>

    <!-- Generate Dialog -->
    <q-dialog v-model="showGenerateDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Generate Architecture with AI</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <q-input
            v-model="generateRequest.architectural_style"
            label="Architectural Style (optional)"
            filled
            hint="e.g., layered, microservices, hexagonal"
            class="q-mb-md"
          />
          <div class="text-caption text-grey-7">
            AI will analyze existing goals and opportunities to generate architecture
          </div>
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

    <!-- Add Module Dialog -->
    <q-dialog v-model="showAddModuleDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Add Module</div>
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
            @click="handleAddModule"
            :loading="architectureStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Add Dependency Dialog -->
    <q-dialog v-model="showAddDependencyDialog">
      <q-card style="min-width: 400px">
        <q-card-section>
          <div class="text-h6">Add Dependency</div>
        </q-card-section>

        <q-card-section class="q-pt-none">
          <div class="q-mb-md">
            <strong>From:</strong> {{ selectedModule?.data.name }}
          </div>
          <q-select
            v-model="newDependency.to_module_id"
            :options="availableModules"
            option-value="id"
            option-label="name"
            emit-value
            map-options
            label="To Module *"
            filled
            class="q-mb-md"
          />
          <q-select
            v-model="newDependency.dependency_type"
            :options="dependencyTypes"
            label="Dependency Type"
            filled
            class="q-mb-md"
          />
          <q-input
            v-model="newDependency.description"
            label="Description"
            type="textarea"
            filled
            rows="2"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Create"
            @click="handleAddDependency"
            :loading="architectureStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Validation Results Dialog -->
    <q-dialog v-model="showValidationDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Validation Results</div>
        </q-card-section>

        <q-card-section v-if="architectureStore.validation">
          <div
            :class="{
              'text-positive': architectureStore.validation.is_valid,
              'text-negative': !architectureStore.validation.is_valid,
            }"
            class="text-h5 q-mb-md"
          >
            {{
              architectureStore.validation.is_valid
                ? '✓ Architecture is Valid'
                : '✗ Architecture has Issues'
            }}
          </div>

          <div class="q-mb-md">
            <q-chip color="red" text-color="white">
              {{ architectureStore.validation.errors_count }} Errors
            </q-chip>
            <q-chip color="orange" text-color="white">
              {{ architectureStore.validation.warnings_count }} Warnings
            </q-chip>
          </div>

          <q-list v-if="architectureStore.validation.issues.length > 0" bordered>
            <q-item
              v-for="(issue, idx) in architectureStore.validation.issues"
              :key="idx"
            >
              <q-item-section avatar>
                <q-icon
                  :name="
                    issue.severity === 'critical'
                      ? 'error'
                      : issue.severity === 'warning'
                      ? 'warning'
                      : 'info'
                  "
                  :color="
                    issue.severity === 'critical'
                      ? 'red'
                      : issue.severity === 'warning'
                      ? 'orange'
                      : 'blue'
                  "
                />
              </q-item-section>
              <q-item-section>
                <q-item-label>{{ issue.message }}</q-item-label>
                <q-item-label caption>Type: {{ issue.type }}</q-item-label>
              </q-item-section>
            </q-item>
          </q-list>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Complexity Dialog -->
    <q-dialog v-model="showComplexityDialog">
      <q-card style="min-width: 600px">
        <q-card-section>
          <div class="text-h6">Complexity Analysis</div>
        </q-card-section>

        <q-card-section v-if="architectureStore.complexity">
          <div class="text-h3 text-center q-mb-md">
            {{ architectureStore.complexity.overall_complexity.toFixed(1) }}
            <span class="text-caption">/10</span>
          </div>

          <q-separator class="q-my-md" />

          <div class="row q-col-gutter-md q-mb-md">
            <div class="col-6">
              <div class="text-subtitle2">Module Count</div>
              <div class="text-h5">
                {{ architectureStore.complexity.metrics.module_count }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-subtitle2">Avg Dependencies</div>
              <div class="text-h5">
                {{ architectureStore.complexity.metrics.avg_dependencies.toFixed(1) }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-subtitle2">Max Depth</div>
              <div class="text-h5">
                {{ architectureStore.complexity.metrics.max_depth }}
              </div>
            </div>
            <div class="col-6">
              <div class="text-subtitle2">Coupling Score</div>
              <div class="text-h5">
                {{ architectureStore.complexity.metrics.coupling_score.toFixed(1) }}
              </div>
            </div>
          </div>

          <q-separator class="q-my-md" />

          <div class="text-subtitle2 q-mb-sm">Hotspots</div>
          <q-list v-if="architectureStore.complexity.hotspots.length > 0" bordered>
            <q-item
              v-for="hotspot in architectureStore.complexity.hotspots"
              :key="hotspot.module_id"
            >
              <q-item-section>
                <q-item-label>{{ hotspot.module_name }}</q-item-label>
                <q-item-label caption>{{ hotspot.reason }}</q-item-label>
              </q-item-section>
              <q-item-section side>
                <q-chip :color="getComplexityColor(hotspot.complexity_score)">
                  {{ hotspot.complexity_score.toFixed(1) }}
                </q-chip>
              </q-item-section>
            </q-item>
          </q-list>
          <div v-else class="text-grey-6">No hotspots detected</div>

          <q-separator class="q-my-md" />

          <div class="text-subtitle2 q-mb-sm">Recommendations</div>
          <ul v-if="architectureStore.complexity.recommendations.length > 0">
            <li
              v-for="(rec, idx) in architectureStore.complexity.recommendations"
              :key="idx"
            >
              {{ rec }}
            </li>
          </ul>
          <div v-else class="text-grey-6">No recommendations</div>
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Close" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { VueFlow, useVueFlow } from '@vue-flow/core';
import { Background } from '@vue-flow/background';
import { Controls, ControlButton } from '@vue-flow/controls';
import { MiniMap } from '@vue-flow/minimap';
import type { Node, Edge, Connection } from '@vue-flow/core';
import { useArchitectureStore } from 'src/stores/architecture';
import ModuleNode from 'src/components/ModuleNode.vue';
import type {
  ArchitectureModule,
  ArchitectureModuleCreate,
  ArchitectureGenerationRequest,
  ModuleDependencyCreate,
} from 'src/types/architecture';

const route = useRoute();
const router = useRouter();
const architectureStore = useArchitectureStore();
const { fitView: vueFlowFitView, zoomIn: vueFlowZoomIn, zoomOut: vueFlowZoomOut } = useVueFlow();

// State
const nodes = ref<Node[]>([]);
const edges = ref<Edge[]>([]);
const selectedModule = ref<Node<ArchitectureModule> | null>(null);
const showSidePanel = ref(false);
const showGenerateDialog = ref(false);
const showAddModuleDialog = ref(false);
const showAddDependencyDialog = ref(false);
const showValidationDialog = ref(false);
const showComplexityDialog = ref(false);
const showImpactDialog = ref(false);
const showSimulateDialog = ref(false);
const impactResult = ref<any>(null);
const simulationResult = ref<any>(null);

const projectId = computed(() => route.params.projectId as string);

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

const newDependency = ref<ModuleDependencyCreate>({
  project_id: '',
  from_module_id: '',
  to_module_id: '',
  dependency_type: 'uses',
  description: '',
});

const moduleTypes = [
  'package',
  'class',
  'interface',
  'service',
  'component',
  'module',
];

const dependencyTypes = ['import', 'extends', 'uses', 'implements', 'depends_on'];

const availableModules = computed(() => {
  if (!selectedModule.value) return [];
  return architectureStore.modules
    .filter((m) => m.id !== selectedModule.value?.id)
    .map((m) => ({ id: m.id, name: m.name }));
});

// Lifecycle
onMounted(async () => {
  if (projectId.value) {
    generateRequest.value.project_id = projectId.value;
    newModule.value.project_id = projectId.value;
    newDependency.value.project_id = projectId.value;

    await architectureStore.fetchModules(projectId.value);
    await architectureStore.fetchDependencies(projectId.value);

    updateNodesAndEdges();
  }
});

// Watch for changes
watch(
  () => architectureStore.modules,
  () => {
    updateNodesAndEdges();
  }
);

watch(
  () => architectureStore.dependencies,
  () => {
    updateNodesAndEdges();
  }
);

// Functions
function updateNodesAndEdges() {
  // Convert modules to nodes
  nodes.value = architectureStore.modules.map((module, index) => ({
    id: module.id,
    type: 'module',
    position: {
      x: module.position_x ?? (index % 4) * 300,
      y: module.position_y ?? Math.floor(index / 4) * 250,
    },
    data: {
      ...module,
      onNodeClick: handleNodeDataClick,
    },
  }));

  // Convert dependencies to edges
  edges.value = architectureStore.dependencies.map((dep) => ({
    id: dep.id,
    source: dep.from_module_id,
    target: dep.to_module_id,
    label: dep.dependency_type,
    type: 'smoothstep',
    animated: dep.dependency_type === 'depends_on',
    style: { stroke: getDependencyColor(dep.dependency_type) },
  }));
}

function handleNodeDataClick(module: ArchitectureModule) {
  const node = nodes.value.find((n) => n.id === module.id);
  if (node) {
    selectedModule.value = node as Node<ArchitectureModule>;
    showSidePanel.value = true;
  }
}

function onNodeClick(event: { node: Node }) {
  selectedModule.value = event.node as Node<ArchitectureModule>;
  showSidePanel.value = true;
}

function onEdgeClick(event: { edge: Edge }) {
  console.log('Edge clicked:', event.edge);
}

function onPaneClick() {
  selectedModule.value = null;
  showSidePanel.value = false;
}

function onNodesChange(changes: any) {
  // Update positions in store when nodes are dragged
  changes.forEach((change: any) => {
    if (change.type === 'position' && change.position) {
      const module = architectureStore.modules.find((m) => m.id === change.id);
      if (module) {
        architectureStore.updateModule(change.id, {
          position_x: Math.round(change.position.x),
          position_y: Math.round(change.position.y),
        });
      }
    }
  });
}

function onEdgesChange(changes: any) {
  console.log('Edges changed:', changes);
}

async function onConnect(connection: Connection) {
  if (!connection.source || !connection.target) return;

  const dep: ModuleDependencyCreate = {
    project_id: projectId.value,
    from_module_id: connection.source,
    to_module_id: connection.target,
    dependency_type: 'uses',
    description: '',
  };

  await architectureStore.createDependency(dep);
}

function fitView() {
  vueFlowFitView({ padding: 0.2, duration: 300 });
}

function zoomIn() {
  vueFlowZoomIn({ duration: 300 });
}

function zoomOut() {
  vueFlowZoomOut({ duration: 300 });
}

async function handleGenerate() {
  const result = await architectureStore.generateArchitecture(
    projectId.value,
    generateRequest.value
  );

  if (result) {
    showGenerateDialog.value = false;
    generateRequest.value.architectural_style = null;
  }
}

async function handleAddModule() {
  if (!newModule.value.name) return;

  const module = await architectureStore.createModule(newModule.value);
  if (module) {
    showAddModuleDialog.value = false;
    newModule.value = {
      project_id: projectId.value,
      name: '',
      description: '',
      module_type: 'package',
    };
  }
}

async function handleAddDependency() {
  if (!selectedModule.value || !newDependency.value.to_module_id) return;

  newDependency.value.from_module_id = selectedModule.value.id;

  const dep = await architectureStore.createDependency(newDependency.value);
  if (dep) {
    showAddDependencyDialog.value = false;
    newDependency.value = {
      project_id: projectId.value,
      from_module_id: '',
      to_module_id: '',
      dependency_type: 'uses',
      description: '',
    };
  }
}

async function handleValidate() {
  await architectureStore.validateArchitecture(projectId.value);
  showValidationDialog.value = true;
}

async function handleComplexity() {
  await architectureStore.analyzeComplexity(projectId.value);
  showComplexityDialog.value = true;
}

function handleSave() {
  // Positions are auto-saved on drag
  console.log('Architecture saved');
}

function handleEditModule() {
  // TODO: Implement edit dialog
  console.log('Edit module:', selectedModule.value);
}

async function handleApproveModule() {
  if (!selectedModule.value) return;
  await architectureStore.approveModule(selectedModule.value.id);
}

async function handleDeleteModule() {
  if (!selectedModule.value) return;
  if (confirm('Are you sure you want to delete this module?')) {
    await architectureStore.deleteModule(selectedModule.value.id);
    selectedModule.value = null;
    showSidePanel.value = false;
  }
}

async function handleRemoveDependency(depId: string) {
  await architectureStore.deleteDependency(depId);
}

function getModuleDependencies(moduleId: string) {
  return architectureStore.dependencies.filter((d) => d.from_module_id === moduleId);
}

function getModuleName(moduleId: string): string {
  const module = architectureStore.modules.find((m) => m.id === moduleId);
  return module?.name || 'Unknown';
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'orange',
    approved: 'green',
    implemented: 'blue',
  };
  return colors[status] || 'grey';
}

function getNodeColor(node: Node): string {
  const module = node.data as ArchitectureModule;
  const colors: Record<string, string> = {
    draft: '#f57c00',
    approved: '#43a047',
    implemented: '#1e88e5',
  };
  return colors[module.status] || '#999';
}

function getDependencyColor(type: string): string {
  const colors: Record<string, string> = {
    import: '#1976d2',
    extends: '#7b1fa2',
    uses: '#388e3c',
    implements: '#d32f2f',
    depends_on: '#f57c00',
  };
  return colors[type] || '#999';
}

function getComplexityColor(score: number): string {
  if (score < 3) return 'green';
  if (score < 6) return 'orange';
  return 'red';
}
</script>

<style scoped lang="scss">
.architecture-canvas-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.canvas-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 16px;
  background: white;
  border-bottom: 1px solid #e0e0e0;
  flex-shrink: 0;
}

.toolbar-left,
.toolbar-center,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.canvas-container {
  flex: 1;
  position: relative;
  background: #f5f5f5;
}

.module-details {
  padding: 16px;
}

/* Vue Flow Styles */
:deep(.vue-flow__edge-path) {
  stroke-width: 2;
}

:deep(.vue-flow__edge-label) {
  font-size: 10px;
  background: white;
  padding: 2px 6px;
  border-radius: 4px;
  border: 1px solid #ccc;
}
</style>

<style>
/* Import Vue Flow styles */
@import '@vue-flow/core/dist/style.css';
@import '@vue-flow/core/dist/theme-default.css';
@import '@vue-flow/controls/dist/style.css';
@import '@vue-flow/minimap/dist/style.css';
</style>