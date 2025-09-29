<template>
  <q-page padding>
    <div v-if="loading" class="flex flex-center" style="min-height: 400px">
      <q-spinner color="primary" size="3em" />
    </div>

    <div v-else-if="project">
      <div class="row items-center q-mb-lg">
        <div class="col">
          <h4 class="q-my-none">{{ project.name }}</h4>
          <p class="text-body2 text-grey-7">{{ project.description }}</p>
        </div>
        <div class="col-auto">
          <q-btn flat round icon="mdi-dots-vertical">
            <q-menu>
              <q-list>
                <q-item clickable v-close-popup>
                  <q-item-section>Edit</q-item-section>
                </q-item>
                <q-item clickable v-close-popup>
                  <q-item-section>Archive</q-item-section>
                </q-item>
                <q-separator />
                <q-item clickable v-close-popup class="text-negative">
                  <q-item-section>Delete</q-item-section>
                </q-item>
              </q-list>
            </q-menu>
          </q-btn>
        </div>
      </div>

      <q-tabs v-model="currentTab" class="text-grey-7" active-color="primary">
        <q-tab name="overview" label="Overview" icon="mdi-view-dashboard" />
        <q-tab name="goals" label="Goals" icon="mdi-target" />
        <q-tab name="opportunities" label="Opportunities" icon="mdi-lightbulb-on" />
        <q-tab name="research" label="Research" icon="mdi-magnify" />
        <q-tab name="architecture" label="Architecture" icon="mdi-sitemap" />
        <q-tab name="requirements" label="Requirements" icon="mdi-file-document-outline" />
        <q-tab name="code" label="Code" icon="mdi-code-tags" />
      </q-tabs>

      <q-separator />

      <q-tab-panels v-model="currentTab" animated>
        <q-tab-panel name="overview">
          <div class="text-h6 q-mb-md">Project Overview</div>
          <p>{{ project.goal }}</p>
        </q-tab-panel>

        <q-tab-panel name="goals">
          <div class="text-h6 q-mb-md">Goals</div>
          <p class="text-grey-6">Goals module coming soon...</p>
        </q-tab-panel>

        <q-tab-panel name="opportunities">
          <div class="text-h6 q-mb-md">Opportunities</div>
          <p class="text-grey-6">Opportunities module coming soon...</p>
        </q-tab-panel>

        <q-tab-panel name="research">
          <div class="text-h6 q-mb-md">Research</div>
          <p class="text-grey-6">Research module coming soon...</p>
        </q-tab-panel>

        <q-tab-panel name="architecture">
          <div class="text-h6 q-mb-md">Architecture</div>
          <p class="text-grey-6">Architecture module coming soon...</p>
        </q-tab-panel>

        <q-tab-panel name="requirements">
          <div class="text-h6 q-mb-md">Requirements</div>
          <p class="text-grey-6">Requirements module coming soon...</p>
        </q-tab-panel>

        <q-tab-panel name="code">
          <div class="text-h6 q-mb-md">Code Generation</div>
          <p class="text-grey-6">Code generation module coming soon...</p>
        </q-tab-panel>
      </q-tab-panels>
    </div>
  </q-page>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

interface Project {
  id: string;
  name: string;
  description: string;
  goal: string;
  status: string;
}

const route = useRoute();
const loading = ref<boolean>(true);
const currentTab = ref<string>('overview');
const project = ref<Project | null>(null);

onMounted(() => {
  loadProject();
});

function loadProject(): void {
  loading.value = true;
  const projectId = route.params.id as string;

  // TODO: Load project from API
  setTimeout(() => {
    project.value = {
      id: projectId,
      name: 'Sample Project',
      description: 'This is a sample project',
      goal: 'Build an AI-powered platform',
      status: 'active',
    };
    loading.value = false;
  }, 500);
}
</script>
