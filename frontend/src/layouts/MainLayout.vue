<template>
  <q-layout view="hHh lpR fFf">
    <q-header elevated class="bg-primary text-white">
      <q-toolbar>
        <q-toolbar-title>
          <q-icon name="mdi-code-braces" size="sm" class="q-mr-sm" />
          Codorch
        </q-toolbar-title>

        <q-btn flat round dense icon="mdi-view-dashboard" to="/" />
        <q-btn flat round dense icon="mdi-folder-multiple" to="/projects" />

        <q-space />

        <q-btn flat round dense icon="mdi-bell-outline" />
        <q-btn flat round dense icon="mdi-account-circle" />
      </q-toolbar>
    </q-header>

    <q-drawer v-model="drawer" show-if-above bordered class="bg-grey-2">
      <q-list>
        <q-item-label header>Navigation</q-item-label>

        <q-item clickable to="/" exact>
          <q-item-section avatar>
            <q-icon name="mdi-view-dashboard" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Dashboard</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable to="/projects">
          <q-item-section avatar>
            <q-icon name="mdi-folder-multiple" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Projects</q-item-label>
          </q-item-section>
        </q-item>

        <q-separator class="q-my-md" />

        <q-item-label header>Modules</q-item-label>

        <q-item clickable>
          <q-item-section avatar>
            <q-icon name="mdi-target" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Goals</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable>
          <q-item-section avatar>
            <q-icon name="mdi-lightbulb-on" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Opportunities</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable>
          <q-item-section avatar>
            <q-icon name="mdi-magnify" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Research</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable>
          <q-item-section avatar>
            <q-icon name="mdi-sitemap" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Architecture</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable>
          <q-item-section avatar>
            <q-icon name="mdi-file-document-outline" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Requirements</q-item-label>
          </q-item-section>
        </q-item>

        <q-item clickable>
          <q-item-section avatar>
            <q-icon name="mdi-code-tags" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Code Generation</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const drawer = ref<boolean>(true);
</script>
