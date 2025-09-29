<template>
  <q-card class="goal-card" :class="{ 'goal-card--completed': goal.status === 'completed' }">
    <q-card-section>
      <div class="row items-center justify-between">
        <div class="col">
          <div class="text-h6">{{ goal.title }}</div>
          <div class="text-caption text-grey-7">{{ categoryLabel }}</div>
        </div>
        <div class="col-auto">
          <q-badge
            :color="statusColor"
            :label="statusLabel"
            class="q-mr-sm"
          />
          <q-badge
            v-if="goal.priority"
            :color="priorityColor"
            :label="goal.priority"
            outline
          />
        </div>
      </div>
    </q-card-section>

    <q-card-section v-if="goal.description">
      <div class="text-body2">{{ goal.description }}</div>
    </q-card-section>

    <q-card-section v-if="goal.is_smart_validated">
      <div class="row items-center q-gutter-sm">
        <q-icon name="verified" :color="smartColor" size="sm" />
        <span class="text-weight-medium">SMART Score:</span>
        <q-chip
          :color="smartColor"
          text-color="white"
          size="sm"
        >
          {{ smartScore.toFixed(1) }}/10
        </q-chip>
        <q-linear-progress
          :value="smartScore / 10"
          :color="smartColor"
          size="8px"
          class="col"
        />
      </div>
    </q-card-section>

    <q-card-section v-if="goal.target_date">
      <div class="row items-center q-gutter-sm">
        <q-icon name="event" size="sm" />
        <span class="text-caption">Target Date:</span>
        <span class="text-weight-medium">{{ formatDate(goal.target_date) }}</span>
      </div>
    </q-card-section>

    <q-card-section v-if="goal.completion_percentage > 0">
      <div class="text-caption q-mb-xs">
        Progress: {{ goal.completion_percentage }}%
      </div>
      <q-linear-progress
        :value="goal.completion_percentage / 100"
        color="primary"
        size="12px"
      />
    </q-card-section>

    <q-card-section v-if="goal.metrics && goal.metrics.length > 0">
      <div class="text-caption q-mb-sm">Metrics:</div>
      <div class="row q-gutter-sm">
        <q-chip
          v-for="metric in goal.metrics"
          :key="metric.name"
          size="sm"
          outline
        >
          {{ metric.name }}: {{ metric.target_value }} {{ metric.unit }}
        </q-chip>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-actions align="right">
      <q-btn
        flat
        color="primary"
        icon="analytics"
        label="Analyze"
        @click="$emit('analyze')"
      />
      <q-btn
        flat
        color="secondary"
        icon="account_tree"
        label="Decompose"
        @click="$emit('decompose')"
      />
      <q-btn
        flat
        color="grey-7"
        icon="edit"
        @click="$emit('edit')"
      />
      <q-btn
        flat
        color="negative"
        icon="delete"
        @click="$emit('delete')"
      />
    </q-card-actions>
  </q-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import type { Goal } from 'src/types/goals';

interface Props {
  goal: Goal;
}

const props = defineProps<Props>();

defineEmits<{
  analyze: [];
  decompose: [];
  edit: [];
  delete: [];
}>();

const smartScore = computed(() => props.goal.overall_smart_score ?? 0);

const smartColor = computed(() => {
  const score = smartScore.value;
  if (score >= 8) return 'positive';
  if (score >= 7) return 'warning';
  return 'negative';
});

const statusColor = computed(() => {
  switch (props.goal.status) {
    case 'active': return 'primary';
    case 'completed': return 'positive';
    case 'archived': return 'grey';
    default: return 'grey-5';
  }
});

const statusLabel = computed(() => {
  const labels = {
    draft: 'Draft',
    active: 'Active',
    completed: 'Completed',
    archived: 'Archived',
  };
  return labels[props.goal.status] || props.goal.status;
});

const priorityColor = computed(() => {
  switch (props.goal.priority) {
    case 'critical': return 'negative';
    case 'high': return 'warning';
    case 'medium': return 'info';
    default: return 'grey-6';
  }
});

const categoryLabel = computed(() => {
  return props.goal.category || 'Uncategorized';
});

function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('bg-BG', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}
</script>

<style scoped lang="scss">
.goal-card {
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  &--completed {
    opacity: 0.85;
  }
}
</style>
