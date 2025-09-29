<template>
  <q-page padding>
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <h4 class="q-my-none">Goals</h4>
        <p class="text-grey-7">Manage project goals and objectives</p>
      </div>
      <q-btn
        color="primary"
        icon="add"
        label="New Goal"
        @click="showCreateDialog = true"
      />
    </div>

    <div class="row q-mb-md q-gutter-sm">
      <q-btn-toggle
        v-model="statusFilter"
        toggle-color="primary"
        :options="[
          { label: 'All', value: 'all' },
          { label: 'Active', value: 'active' },
          { label: 'Draft', value: 'draft' },
          { label: 'Completed', value: 'completed' },
        ]"
      />
      <q-space />
      <q-toggle
        v-model="rootOnly"
        label="Root Goals Only"
        @update:model-value="loadGoals"
      />
    </div>

    <q-linear-progress v-if="goalsStore.loading" indeterminate color="primary" />

    <div class="row q-col-gutter-md">
      <div
        v-for="goal in filteredGoals"
        :key="goal.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <goal-card
          :goal="goal"
          @analyze="analyzeGoal(goal.id)"
          @decompose="decomposeGoal(goal.id)"
          @edit="editGoal(goal)"
          @delete="deleteGoal(goal.id)"
        />
      </div>
    </div>

    <div v-if="filteredGoals.length === 0 && !goalsStore.loading" class="text-center q-mt-xl">
      <q-icon name="flag" size="64px" color="grey-5" />
      <p class="text-h6 text-grey-6">No goals found</p>
      <q-btn
        color="primary"
        label="Create First Goal"
        @click="showCreateDialog = true"
      />
    </div>

    <!-- Create/Edit Dialog -->
    <q-dialog v-model="showCreateDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">{{ editingGoal ? 'Edit Goal' : 'New Goal' }}</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="goalForm.title"
            label="Title *"
            outlined
            class="q-mb-md"
          />
          <q-input
            v-model="goalForm.description"
            label="Description"
            type="textarea"
            outlined
            rows="3"
            class="q-mb-md"
          />
          <q-select
            v-model="goalForm.category"
            label="Category"
            :options="['business', 'technical', 'personal', 'team']"
            outlined
            class="q-mb-md"
          />
          <q-select
            v-model="goalForm.priority"
            label="Priority"
            :options="['low', 'medium', 'high', 'critical']"
            outlined
            class="q-mb-md"
          />
          <q-input
            v-model="goalForm.target_date"
            label="Target Date"
            type="date"
            outlined
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Save"
            @click="saveGoal"
            :loading="goalsStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useGoalsStore } from 'src/stores/goals';
import GoalCard from 'src/components/goals/GoalCard.vue';
import type { Goal, GoalCreate } from 'src/types/goals';
import { useQuasar } from 'quasar';

const route = useRoute();
const goalsStore = useGoalsStore();
const $q = useQuasar();

const projectId = computed(() => route.params.projectId as string);

const showCreateDialog = ref(false);
const statusFilter = ref('all');
const rootOnly = ref(false);
const editingGoal = ref<Goal | null>(null);

const goalForm = ref<GoalCreate>({
  title: '',
  description: '',
  category: '',
  priority: 'medium',
});

const filteredGoals = computed(() => {
  if (statusFilter.value === 'all') {
    return goalsStore.goals;
  }
  return goalsStore.goalsByStatus(statusFilter.value as Goal['status']);
});

onMounted(() => {
  loadGoals();
});

async function loadGoals() {
  await goalsStore.fetchGoals(projectId.value, rootOnly.value);
}

async function saveGoal() {
  try {
    if (editingGoal.value) {
      await goalsStore.updateGoal(editingGoal.value.id, goalForm.value);
    } else {
      await goalsStore.createGoal(projectId.value, goalForm.value);
    }
    showCreateDialog.value = false;
    resetForm();
  } catch (error) {
    console.error('Error saving goal:', error);
  }
}

function editGoal(goal: Goal) {
  editingGoal.value = goal;
  goalForm.value = {
    title: goal.title,
    description: goal.description,
    category: goal.category,
    priority: goal.priority,
    target_date: goal.target_date,
  };
  showCreateDialog.value = true;
}

async function deleteGoal(goalId: string) {
  $q.dialog({
    title: 'Confirm Delete',
    message: 'Are you sure you want to delete this goal?',
    cancel: true,
  }).onOk(async () => {
    await goalsStore.deleteGoal(goalId);
  });
}

async function analyzeGoal(goalId: string) {
  $q.loading.show({ message: 'AI Analysis in progress...' });
  try {
    await goalsStore.analyzeGoal(goalId);
  } finally {
    $q.loading.hide();
  }
}

async function decomposeGoal(goalId: string) {
  $q.loading.show({ message: 'Decomposing goal...' });
  try {
    await goalsStore.decomposeGoal(goalId, 3);
    await loadGoals(); // Refresh to show subgoals
  } finally {
    $q.loading.hide();
  }
}

function resetForm() {
  editingGoal.value = null;
  goalForm.value = {
    title: '',
    description: '',
    category: '',
    priority: 'medium',
  };
}
</script>
