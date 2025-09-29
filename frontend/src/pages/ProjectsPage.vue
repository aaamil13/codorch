<template>
  <q-page padding>
    <div class="row items-center q-mb-md">
      <div class="col">
        <h4 class="q-my-none">Projects</h4>
      </div>
      <div class="col-auto">
        <q-btn
          color="primary"
          label="New Project"
          icon="mdi-plus"
          @click="showCreateDialog = true"
        />
      </div>
    </div>

    <div v-if="loading" class="flex flex-center" style="min-height: 400px">
      <q-spinner color="primary" size="3em" />
    </div>

    <div v-else-if="projects.length === 0" class="text-center q-pa-xl">
      <q-icon name="mdi-folder-open-outline" size="80px" color="grey-5" />
      <p class="text-h6 text-grey-6 q-mt-md">No projects yet</p>
      <p class="text-body2 text-grey-5">
        Create your first project to get started
      </p>
    </div>

    <div v-else class="row q-col-gutter-md">
      <div
        v-for="project in projects"
        :key="project.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <q-card class="cursor-pointer" @click="openProject(project.id)">
          <q-card-section>
            <div class="text-h6">{{ project.name }}</div>
            <div class="text-caption text-grey-7">{{ project.description }}</div>
          </q-card-section>

          <q-card-section>
            <q-chip
              size="sm"
              :color="getStatusColor(project.status)"
              text-color="white"
            >
              {{ project.status }}
            </q-chip>
          </q-card-section>

          <q-card-actions align="right">
            <q-btn flat color="primary" label="Open" icon="mdi-arrow-right" />
          </q-card-actions>
        </q-card>
      </div>
    </div>

    <!-- Create Project Dialog -->
    <q-dialog v-model="showCreateDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Create New Project</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="newProject.name"
            label="Project Name"
            outlined
            dense
          />
          <q-input
            v-model="newProject.description"
            label="Description"
            type="textarea"
            outlined
            dense
            class="q-mt-md"
          />
          <q-input
            v-model="newProject.goal"
            label="Main Goal"
            type="textarea"
            outlined
            dense
            class="q-mt-md"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Create"
            @click="createProject"
            :loading="creating"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';

interface Project {
  id: string;
  name: string;
  description: string;
  goal: string;
  status: string;
}

const router = useRouter();
const loading = ref<boolean>(false);
const creating = ref<boolean>(false);
const showCreateDialog = ref<boolean>(false);
const projects = ref<Project[]>([]);

const newProject = ref({
  name: '',
  description: '',
  goal: '',
});

onMounted(() => {
  loadProjects();
});

function loadProjects(): void {
  loading.value = true;
  // TODO: Load projects from API
  setTimeout(() => {
    loading.value = false;
  }, 500);
}

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    active: 'positive',
    completed: 'info',
    archived: 'grey',
  };
  return colors[status] || 'grey';
}

function openProject(id: string): void {
  router.push({ name: 'project-detail', params: { id } });
}

function createProject(): void {
  creating.value = true;
  // TODO: Create project via API
  setTimeout(() => {
    creating.value = false;
    showCreateDialog.value = false;
    newProject.value = { name: '', description: '', goal: '' };
    loadProjects();
  }, 1000);
}
</script>
