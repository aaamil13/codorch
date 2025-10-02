<template>
  <q-page padding>
    <div class="row items-center justify-between q-mb-lg">
      <div>
        <h4 class="q-my-none">Opportunities</h4>
        <p class="text-grey-7">Explore and manage business opportunities</p>
      </div>
      <div class="row q-gutter-sm">
        <q-btn
          color="secondary"
          icon="psychology"
          label="Generate with AI"
          @click="showGenerateDialog = true"
        />
        <q-btn
          color="primary"
          icon="add"
          label="New Opportunity"
          @click="showCreateDialog = true"
        />
      </div>
    </div>

    <q-linear-progress
      v-if="opportunitiesStore.loading || opportunitiesStore.generating"
      indeterminate
      color="primary"
    />

    <div class="row q-col-gutter-md">
      <div
        v-for="opportunity in opportunitiesStore.opportunities"
        :key="opportunity.id"
        class="col-12 col-md-6 col-lg-4"
      >
        <opportunity-card
          :opportunity="opportunity"
          @view="viewOpportunity(opportunity.id)"
          @edit="editOpportunity(opportunity)"
          @delete="deleteOpportunity(opportunity.id)"
        />
      </div>
    </div>

    <div
      v-if="opportunitiesStore.opportunities.length === 0 && !opportunitiesStore.loading"
      class="text-center q-mt-xl"
    >
      <q-icon name="lightbulb" size="64px" color="grey-5" />
      <p class="text-h6 text-grey-6">No opportunities yet</p>
      <q-btn
        color="secondary"
        icon="psychology"
        label="Generate with AI"
        @click="showGenerateDialog = true"
      />
    </div>

    <!-- AI Generate Dialog -->
    <q-dialog v-model="showGenerateDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">Generate Opportunities with AI</div>
          <p class="text-caption text-grey-7">
            Our AI Team will generate innovative opportunities for your project
          </p>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="generateForm.context"
            label="Context"
            type="textarea"
            outlined
            rows="3"
            hint="Describe your project or business domain"
            class="q-mb-md"
          />
          <span class="text-caption">Number of opportunities:</span>
          <q-slider
            v-model="generateForm.num_opportunities"
            :min="1"
            :max="10"
            label
            label-always
            markers
            class="q-mb-md"
          />
          <q-select
            v-model="generateForm.creativity_level"
            label="Creativity Level"
            :options="[
              { label: 'Conservative', value: 'conservative' },
              { label: 'Balanced', value: 'balanced' },
              { label: 'Creative', value: 'creative' },
            ]"
            outlined
            emit-value
            map-options
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="secondary"
            icon="psychology"
            label="Generate"
            @click="generateOpportunities"
            :loading="opportunitiesStore.generating"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>

    <!-- Create/Edit Dialog (simplified) -->
    <q-dialog v-model="showCreateDialog">
      <q-card style="min-width: 500px">
        <q-card-section>
          <div class="text-h6">New Opportunity</div>
        </q-card-section>

        <q-card-section>
          <q-input
            v-model="opportunityForm.title"
            label="Title *"
            outlined
            class="q-mb-md"
          />
          <q-input
            v-model="opportunityForm.description"
            label="Description"
            type="textarea"
            outlined
            rows="3"
            class="q-mb-md"
          />
          <q-input
            v-model="opportunityForm.value_proposition"
            label="Value Proposition"
            type="textarea"
            outlined
            rows="2"
          />
        </q-card-section>

        <q-card-actions align="right">
          <q-btn flat label="Cancel" v-close-popup />
          <q-btn
            color="primary"
            label="Create"
            @click="saveOpportunity"
            :loading="opportunitiesStore.loading"
          />
        </q-card-actions>
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { useOpportunitiesStore } from 'src/stores/opportunities';
import OpportunityCard from 'src/components/opportunities/OpportunityCard.vue';
import type { Opportunity, OpportunityCreate } from 'src/types/opportunities';
import { useQuasar } from 'quasar';

const route = useRoute();
const opportunitiesStore = useOpportunitiesStore();
const $q = useQuasar();

const projectId = computed(() => route.params.projectId as string);

const showGenerateDialog = ref(false);
const showCreateDialog = ref(false);

const generateForm = ref({
  context: '',
  num_opportunities: 5,
  creativity_level: 'balanced' as 'conservative' | 'balanced' | 'creative',
});

const opportunityForm = ref<OpportunityCreate>({
  title: '',
  description: '',
  value_proposition: '',
});

onMounted(() => {
  loadOpportunities();
});

async function loadOpportunities() {
  await opportunitiesStore.fetchOpportunities(projectId.value);
}

async function generateOpportunities() {
  try {
    await opportunitiesStore.generateOpportunities(projectId.value, {
      ...generateForm.value,
      include_scoring: true,
    });
    showGenerateDialog.value = false;
  } catch (error) {
    console.error('Error generating opportunities:', (error as Error).message);
  }
}

async function saveOpportunity() {
  try {
    await opportunitiesStore.createOpportunity(projectId.value, opportunityForm.value);
    showCreateDialog.value = false;
    resetForm();
  } catch (error) {
    console.error('Error creating opportunity:', (error as Error).message);
  }
}

function viewOpportunity(id: string) {
  // Navigate to detail view (to be implemented)
  console.log('View opportunity:', id);
}

function editOpportunity(opportunity: Opportunity) {
  // Edit functionality (to be implemented)
  console.log('Edit opportunity:', opportunity);
}

function deleteOpportunity(opportunityId: string) {
  $q.dialog({
    title: 'Confirm Delete',
    message: 'Are_you sure you want to delete this opportunity?',
    cancel: true,
  }).onOk(() => {
    void opportunitiesStore.deleteOpportunity(opportunityId);
  });
}

function resetForm() {
  opportunityForm.value = {
    title: '',
    description: '',
    value_proposition: '',
  };
}
</script>
