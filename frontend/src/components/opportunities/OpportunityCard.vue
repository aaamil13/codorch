<template>
  <q-card class="opportunity-card">
    <q-card-section>
      <div class="row items-center justify-between">
        <div class="col">
          <div class="text-h6">{{ opportunity.title }}</div>
          <div class="text-caption text-grey-7">
            <q-icon
              v-if="opportunity.ai_generated"
              name="psychology"
              size="xs"
              class="q-mr-xs"
            />
            {{ opportunity.category || 'Business' }}
          </div>
        </div>
        <div class="col-auto">
          <q-badge
            :color="statusColor"
            :label="statusLabel"
          />
        </div>
      </div>
    </q-card-section>

    <q-card-section v-if="opportunity.description">
      <div class="text-body2">{{ opportunity.description }}</div>
    </q-card-section>

    <q-card-section v-if="opportunity.score !== undefined">
      <div class="text-subtitle2 q-mb-sm">Overall Score</div>
      <div class="row items-center q-gutter-md">
        <q-circular-progress
          :value="(opportunity.score / 10) * 100"
          size="60px"
          :thickness="0.15"
          :color="scoreColor"
          track-color="grey-3"
          show-value
        >
          <div class="text-caption">{{ opportunity.score?.toFixed(1) }}</div>
        </q-circular-progress>

        <div class="col">
          <div class="row q-gutter-xs">
            <q-chip
              v-if="opportunity.feasibility_score"
              size="sm"
              color="blue-2"
              text-color="blue-9"
            >
              F: {{ opportunity.feasibility_score.toFixed(1) }}
            </q-chip>
            <q-chip
              v-if="opportunity.impact_score"
              size="sm"
              color="green-2"
              text-color="green-9"
            >
              I: {{ opportunity.impact_score.toFixed(1) }}
            </q-chip>
            <q-chip
              v-if="opportunity.innovation_score"
              size="sm"
              color="purple-2"
              text-color="purple-9"
            >
              N: {{ opportunity.innovation_score.toFixed(1) }}
            </q-chip>
            <q-chip
              v-if="opportunity.resource_score"
              size="sm"
              color="orange-2"
              text-color="orange-9"
            >
              R: {{ opportunity.resource_score.toFixed(1) }}
            </q-chip>
          </div>
        </div>
      </div>
    </q-card-section>

    <q-card-section v-if="opportunity.value_proposition">
      <div class="text-caption text-grey-8">Value Proposition:</div>
      <div class="text-body2 text-weight-medium">
        {{ opportunity.value_proposition }}
      </div>
    </q-card-section>

    <q-card-section>
      <div class="row q-gutter-sm text-caption">
        <div v-if="opportunity.estimated_effort" class="col-auto">
          <q-icon name="schedule" size="xs" />
          {{ opportunity.estimated_effort }}
        </div>
        <div v-if="opportunity.estimated_timeline" class="col-auto">
          <q-icon name="timeline" size="xs" />
          {{ opportunity.estimated_timeline }}
        </div>
      </div>
    </q-card-section>

    <q-separator />

    <q-card-actions align="right">
      <q-btn
        flat
        color="primary"
        icon="visibility"
        label="Details"
        @click="$emit('view')"
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
import type { Opportunity } from 'src/types/opportunities';

interface Props {
  opportunity: Opportunity;
}

const props = defineProps<Props>();

defineEmits<{
  view: [];
  edit: [];
  delete: [];
}>();

const scoreColor = computed(() => {
  const score = props.opportunity.score ?? 0;
  if (score >= 8) return 'positive';
  if (score >= 6) return 'warning';
  return 'negative';
});

const statusColor = computed(() => {
  switch (props.opportunity.status) {
    case 'approved': return 'positive';
    case 'active': return 'primary';
    case 'rejected': return 'negative';
    case 'archived': return 'grey';
    default: return 'info';
  }
});

const statusLabel = computed(() => {
  const labels = {
    proposed: 'Proposed',
    active: 'Active',
    approved: 'Approved',
    rejected: 'Rejected',
    archived: 'Archived',
  };
  return labels[props.opportunity.status] || props.opportunity.status;
});
</script>

<style scoped lang="scss">
.opportunity-card {
  transition: all 0.3s ease;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}
</style>
