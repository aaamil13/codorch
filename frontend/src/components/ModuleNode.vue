<template>
  <div
    class="module-node"
    :class="[`node-${data.status}`, `node-type-${data.module_type}`]"
    @click="handleClick"
  >
    <!-- Header -->
    <div class="node-header">
      <q-icon
        :name="getModuleIcon(data.module_type)"
        size="16px"
        class="q-mr-xs"
      />
      <span class="node-title">{{ data.name }}</span>
      <q-badge v-if="data.ai_generated" color="purple" class="q-ml-xs">AI</q-badge>
    </div>

    <!-- Body -->
    <div class="node-body">
      <div v-if="data.description" class="node-description">
        {{ truncate(data.description, 50) }}
      </div>
      <div class="node-meta">
        <q-chip size="xs" dense>{{ data.module_type }}</q-chip>
        <q-chip size="xs" dense>Level {{ data.level }}</q-chip>
      </div>
    </div>

    <!-- Status Badge -->
    <div class="node-footer">
      <q-badge
        :color="getStatusColor(data.status)"
        :label="data.status"
      />
    </div>

    <!-- Handles (connection points) -->
    <Handle
      id="top"
      type="target"
      :position="Position.Top"
      class="handle-top"
    />
    <Handle
      id="bottom"
      type="source"
      :position="Position.Bottom"
      class="handle-bottom"
    />
    <Handle
      id="left"
      type="target"
      :position="Position.Left"
      class="handle-left"
    />
    <Handle
      id="right"
      type="source"
      :position="Position.Right"
      class="handle-right"
    />
  </div>
</template>

<script setup lang="ts">
import { Handle, Position } from '@vue-flow/core';
import type { ArchitectureModule } from 'src/types/architecture';

interface Props {
  data: ArchitectureModule & {
    onNodeClick?: (module: ArchitectureModule) => void;
  };
}

const props = defineProps<Props>();

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

function getStatusColor(status: string): string {
  const colors: Record<string, string> = {
    draft: 'orange',
    approved: 'green',
    implemented: 'blue',
  };
  return colors[status] || 'grey';
}

function truncate(text: string, length: number): string {
  if (text.length <= length) return text;
  return text.substring(0, length) + '...';
}

function handleClick() {
  if (props.data.onNodeClick) {
    props.data.onNodeClick(props.data);
  }
}
</script>

<style scoped lang="scss">
.module-node {
  background: white;
  border: 2px solid #ccc;
  border-radius: 8px;
  padding: 0;
  min-width: 200px;
  max-width: 250px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2);
    transform: translateY(-2px);
  }

  &.node-draft {
    border-color: #f57c00;
  }

  &.node-approved {
    border-color: #43a047;
  }

  &.node-implemented {
    border-color: #1e88e5;
  }

  &.node-type-package {
    background: linear-gradient(135deg, #fff 0%, #f5f5f5 100%);
  }

  &.node-type-service {
    background: linear-gradient(135deg, #fff 0%, #e3f2fd 100%);
  }

  &.node-type-component {
    background: linear-gradient(135deg, #fff 0%, #f3e5f5 100%);
  }
}

.node-header {
  display: flex;
  align-items: center;
  padding: 8px 12px;
  background: rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid #e0e0e0;
  font-weight: 600;
  font-size: 13px;
}

.node-title {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.node-body {
  padding: 8px 12px;
}

.node-description {
  font-size: 11px;
  color: #666;
  margin-bottom: 6px;
  line-height: 1.3;
}

.node-meta {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.node-footer {
  padding: 6px 12px;
  border-top: 1px solid #e0e0e0;
  display: flex;
  justify-content: center;
}

/* Connection Handles */
:deep(.vue-flow__handle) {
  width: 10px;
  height: 10px;
  background: #1976d2;
  border: 2px solid white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3);

  &:hover {
    width: 12px;
    height: 12px;
    background: #1565c0;
  }
}

.handle-top {
  top: -5px;
}

.handle-bottom {
  bottom: -5px;
}

.handle-left {
  left: -5px;
}

.handle-right {
  right: -5px;
}
</style>