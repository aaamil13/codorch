<template>
  <q-page class="flex flex-center">
    <div class="text-center">
      <q-icon name="mdi-code-braces" size="120px" color="primary" />
      <h3 class="q-mt-md">Welcome to Codorch</h3>
      <p class="text-subtitle1 text-grey-7">
        Orchestrating Ideas into Reality
      </p>

      <div class="q-mt-xl">
        <q-btn
          color="primary"
          label="Create New Project"
          icon="mdi-plus"
          size="lg"
          to="/projects"
        />
      </div>

      <div class="q-mt-lg q-gutter-sm">
        <q-chip color="primary" text-color="white">
          AI-Powered
        </q-chip>
        <q-chip color="secondary" text-color="white">
          RefMemTree
        </q-chip>
        <q-chip color="accent" text-color="white">
          Full Lifecycle
        </q-chip>
      </div>
    </div>
  </q-page>
</template>

<script setup lang="ts">
// Home page
</script>
