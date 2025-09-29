diff --git a/FRONTEND_SPECIFICATION.md b/FRONTEND_SPECIFICATION.md
--- a/FRONTEND_SPECIFICATION.md
+++ b/FRONTEND_SPECIFICATION.md
@@ -0,0 +1,1251 @@
+# Frontend Specification - Vue 3 + Quasar
+
+## Overview
+
+Modern, responsive SPA built with Vue 3 (Composition API), Quasar Framework, and TypeScript for managing the entire business requirements lifecycle.
+
+---
+
+## Application Structure
+
+### Route Structure
+
+```typescript
+// src/router/routes.ts
+
+const routes = [
+  {
+    path: '/',
+    component: () => import('layouts/MainLayout.vue'),
+    children: [
+      { 
+        path: '', 
+        name: 'dashboard',
+        component: () => import('pages/Dashboard.vue') 
+      },
+      {
+        path: '/projects',
+        name: 'projects',
+        component: () => import('pages/Projects/Index.vue')
+      },
+      {
+        path: '/projects/:id',
+        component: () => import('layouts/ProjectLayout.vue'),
+        children: [
+          {
+            path: '',
+            redirect: { name: 'project-dashboard' }
+          },
+          {
+            path: 'dashboard',
+            name: 'project-dashboard',
+            component: () => import('pages/Project/Dashboard.vue')
+          },
+          {
+            path: 'goals',
+            name: 'project-goals',
+            component: () => import('pages/GoalDefinition/Index.vue')
+          },
+          {
+            path: 'opportunities',
+            name: 'project-opportunities',
+            component: () => import('pages/OpportunityExplorer/Index.vue')
+          },
+          {
+            path: 'research',
+            name: 'project-research',
+            component: () => import('pages/Research/Index.vue')
+          },
+          {
+            path: 'research/:sessionId',
+            name: 'research-session',
+            component: () => import('pages/Research/SessionView.vue')
+          },
+          {
+            path: 'architecture',
+            name: 'project-architecture',
+            component: () => import('pages/ArchitectureDesigner/Index.vue')
+          },
+          {
+            path: 'requirements',
+            name: 'project-requirements',
+            component: () => import('pages/Requirements/Index.vue')
+          },
+          {
+            path: 'code-generation',
+            name: 'project-codegen',
+            component: () => import('pages/CodeGenerator/Index.vue')
+          }
+        ]
+      }
+    ]
+  },
+  {
+    path: '/auth',
+    component: () => import('layouts/AuthLayout.vue'),
+    children: [
+      { path: 'login', component: () => import('pages/Auth/Login.vue') },
+      { path: 'register', component: () => import('pages/Auth/Register.vue') }
+    ]
+  }
+]
+```
+
+---
+
+## Key Components Specification
+
+### 1. Tree Visualizer Component
+
+**Purpose**: Interactive tree visualization using D3.js or Vue Flow
+
+```vue
+<!-- components/tree/TreeVisualizer.vue -->
+<template>
+  <div class="tree-visualizer" ref="container">
+    <div class="tree-controls">
+      <q-btn-group>
+        <q-btn 
+          icon="zoom_in" 
+          @click="zoomIn"
+          flat
+        />
+        <q-btn 
+          icon="zoom_out" 
+          @click="zoomOut"
+          flat
+        />
+        <q-btn 
+          icon="center_focus_strong" 
+          @click="centerView"
+          flat
+        />
+        <q-btn 
+          icon="fullscreen" 
+          @click="toggleFullscreen"
+          flat
+        />
+      </q-btn-group>
+      
+      <q-space />
+      
+      <q-select
+        v-model="viewMode"
+        :options="viewModes"
+        dense
+        options-dense
+        style="min-width: 150px"
+      />
+    </div>
+    
+    <div 
+      ref="treeCanvas" 
+      class="tree-canvas"
+      @wheel="handleWheel"
+    >
+      <!-- D3.js renders here -->
+    </div>
+    
+    <!-- Context Menu -->
+    <q-menu
+      v-model="contextMenu.show"
+      :target="contextMenu.target"
+      context-menu
+    >
+      <q-list dense>
+        <q-item clickable @click="addChildNode">
+          <q-item-section avatar>
+            <q-icon name="add" />
+          </q-item-section>
+          <q-item-section>Добави подвъзел</q-item-section>
+        </q-item>
+        
+        <q-item clickable @click="editNode">
+          <q-item-section avatar>
+            <q-icon name="edit" />
+          </q-item-section>
+          <q-item-section>Редактирай</q-item-section>
+        </q-item>
+        
+        <q-item clickable @click="startResearch">
+          <q-item-section avatar>
+            <q-icon name="search" />
+          </q-item-section>
+          <q-item-section>Започни проучване</q-item-section>
+        </q-item>
+        
+        <q-separator />
+        
+        <q-item clickable @click="deleteNode" class="text-negative">
+          <q-item-section avatar>
+            <q-icon name="delete" />
+          </q-item-section>
+          <q-item-section>Изтрий</q-item-section>
+        </q-item>
+      </q-list>
+    </q-menu>
+  </div>
+</template>
+
+<script setup lang="ts">
+import { ref, onMounted, watch } from 'vue'
+import * as d3 from 'd3'
+import type { TreeNode } from '@/types/tree'
+
+interface Props {
+  treeData: TreeNode
+  editable?: boolean
+  draggable?: boolean
+  viewMode?: 'vertical' | 'horizontal' | 'radial'
+}
+
+const props = withDefaults(defineProps<Props>(), {
+  editable: false,
+  draggable: false,
+  viewMode: 'vertical'
+})
+
+const emit = defineEmits<{
+  'node-click': [node: TreeNode]
+  'node-drag': [node: TreeNode, position: { x: number, y: number }]
+  'node-edit': [node: TreeNode]
+  'node-add': [parentNode: TreeNode]
+  'node-delete': [node: TreeNode]
+}>()
+
+const container = ref<HTMLElement>()
+const treeCanvas = ref<HTMLElement>()
+const contextMenu = ref({ show: false, target: null })
+
+let svg: d3.Selection<SVGSVGElement, unknown, null, undefined>
+let g: d3.Selection<SVGGElement, unknown, null, undefined>
+let zoom: d3.ZoomBehavior<Element, unknown>
+
+onMounted(() => {
+  initializeTree()
+  renderTree()
+})
+
+watch(() => props.treeData, () => {
+  renderTree()
+}, { deep: true })
+
+function initializeTree() {
+  const width = treeCanvas.value?.clientWidth || 800
+  const height = treeCanvas.value?.clientHeight || 600
+  
+  svg = d3.select(treeCanvas.value)
+    .append('svg')
+    .attr('width', width)
+    .attr('height', height)
+  
+  g = svg.append('g')
+  
+  zoom = d3.zoom<SVGSVGElement, unknown>()
+    .scaleExtent([0.1, 4])
+    .on('zoom', (event) => {
+      g.attr('transform', event.transform)
+    })
+  
+  svg.call(zoom)
+}
+
+function renderTree() {
+  if (!g || !props.treeData) return
+  
+  // Clear previous render
+  g.selectAll('*').remove()
+  
+  // Create tree layout
+  const treeLayout = d3.tree<TreeNode>()
+    .size([800, 600])
+  
+  // Convert data to hierarchy
+  const root = d3.hierarchy(props.treeData)
+  const treeData = treeLayout(root)
+  
+  // Render links
+  const links = g.selectAll('.link')
+    .data(treeData.links())
+    .enter()
+    .append('path')
+    .attr('class', 'link')
+    .attr('d', d3.linkVertical()
+      .x((d: any) => d.x)
+      .y((d: any) => d.y)
+    )
+    .attr('fill', 'none')
+    .attr('stroke', '#ccc')
+    .attr('stroke-width', 2)
+  
+  // Render nodes
+  const nodes = g.selectAll('.node')
+    .data(treeData.descendants())
+    .enter()
+    .append('g')
+    .attr('class', 'node')
+    .attr('transform', (d: any) => `translate(${d.x},${d.y})`)
+    .on('click', (event, d: any) => {
+      event.stopPropagation()
+      emit('node-click', d.data)
+    })
+    .on('contextmenu', (event, d: any) => {
+      event.preventDefault()
+      contextMenu.value = {
+        show: true,
+        target: event.target
+      }
+    })
+  
+  // Add circles
+  nodes.append('circle')
+    .attr('r', 10)
+    .attr('fill', (d: any) => getNodeColor(d.data))
+    .attr('stroke', '#333')
+    .attr('stroke-width', 2)
+  
+  // Add labels
+  nodes.append('text')
+    .attr('dy', 25)
+    .attr('text-anchor', 'middle')
+    .text((d: any) => d.data.title || d.data.name)
+    .style('font-size', '12px')
+  
+  // Add drag behavior if enabled
+  if (props.draggable) {
+    const drag = d3.drag<SVGGElement, any>()
+      .on('drag', function(event, d) {
+        d.x = event.x
+        d.y = event.y
+        d3.select(this)
+          .attr('transform', `translate(${d.x},${d.y})`)
+        emit('node-drag', d.data, { x: d.x, y: d.y })
+      })
+    
+    nodes.call(drag)
+  }
+}
+
+function getNodeColor(node: TreeNode): string {
+  const colors = {
+    goal: '#4CAF50',
+    opportunity: '#2196F3',
+    module: '#FF9800',
+    requirement: '#9C27B0',
+    default: '#757575'
+  }
+  return colors[node.type as keyof typeof colors] || colors.default
+}
+
+function zoomIn() {
+  svg.transition().call(zoom.scaleBy, 1.3)
+}
+
+function zoomOut() {
+  svg.transition().call(zoom.scaleBy, 0.7)
+}
+
+function centerView() {
+  const width = treeCanvas.value?.clientWidth || 800
+  const height = treeCanvas.value?.clientHeight || 600
+  svg.transition().call(
+    zoom.transform,
+    d3.zoomIdentity.translate(width / 2, height / 2)
+  )
+}
+</script>
+
+<style scoped lang="scss">
+.tree-visualizer {
+  width: 100%;
+  height: 100%;
+  display: flex;
+  flex-direction: column;
+  background: #fafafa;
+  border: 1px solid #e0e0e0;
+  border-radius: 4px;
+}
+
+.tree-controls {
+  padding: 8px;
+  display: flex;
+  align-items: center;
+  border-bottom: 1px solid #e0e0e0;
+  background: white;
+}
+
+.tree-canvas {
+  flex: 1;
+  position: relative;
+  overflow: hidden;
+}
+</style>
+```
+
+---
+
+### 2. Architecture Canvas Component (Vue Flow)
+
+```vue
+<!-- components/architecture/ArchitectureCanvas.vue -->
+<template>
+  <div class="architecture-canvas">
+    <VueFlow
+      v-model:nodes="nodes"
+      v-model:edges="edges"
+      :default-viewport="{ zoom: 1 }"
+      :min-zoom="0.2"
+      :max-zoom="4"
+      @node-drag-stop="onNodeDragStop"
+      @edge-update="onEdgeUpdate"
+      @connect="onConnect"
+    >
+      <Background />
+      <Controls />
+      <MiniMap />
+      
+      <template #node-module="{ data }">
+        <ModuleNode
+          :module="data"
+          @edit="editModule"
+          @delete="deleteModule"
+        />
+      </template>
+      
+      <template #edge-custom="{ data, sourceX, sourceY, targetX, targetY }">
+        <ConnectionLine
+          :source-x="sourceX"
+          :source-y="sourceY"
+          :target-x="targetX"
+          :target-y="targetY"
+          :data="data"
+        />
+      </template>
+    </VueFlow>
+    
+    <!-- Toolbar -->
+    <div class="canvas-toolbar">
+      <q-btn-group>
+        <q-btn 
+          icon="add" 
+          label="Добави модул"
+          @click="showAddModuleDialog = true"
+        />
+        <q-btn 
+          icon="auto_awesome" 
+          label="AI генериране"
+          color="primary"
+          @click="generateArchitecture"
+        />
+        <q-btn 
+          icon="save" 
+          label="Запази"
+          @click="saveArchitecture"
+        />
+      </q-btn-group>
+    </div>
+    
+    <!-- Add Module Dialog -->
+    <q-dialog v-model="showAddModuleDialog">
+      <q-card style="min-width: 400px">
+        <q-card-section>
+          <div class="text-h6">Нов модул</div>
+        </q-card-section>
+        
+        <q-card-section>
+          <q-input
+            v-model="newModule.name"
+            label="Име на модула"
+            outlined
+          />
+          
+          <q-select
+            v-model="newModule.type"
+            :options="moduleTypes"
+            label="Тип"
+            outlined
+            class="q-mt-md"
+          />
+          
+          <q-input
+            v-model="newModule.description"
+            label="Описание"
+            type="textarea"
+            outlined
+            rows="3"
+            class="q-mt-md"
+          />
+        </q-card-section>
+        
+        <q-card-actions align="right">
+          <q-btn flat label="Откажи" v-close-popup />
+          <q-btn 
+            label="Добави" 
+            color="primary" 
+            @click="addModule"
+            v-close-popup
+          />
+        </q-card-actions>
+      </q-card>
+    </q-dialog>
+  </div>
+</template>
+
+<script setup lang="ts">
+import { ref, computed } from 'vue'
+import { VueFlow, Background, Controls, MiniMap } from '@vue-flow/core'
+import '@vue-flow/core/dist/style.css'
+import '@vue-flow/core/dist/theme-default.css'
+import ModuleNode from './ModuleNode.vue'
+import ConnectionLine from './ConnectionLine.vue'
+import type { ArchitectureModule, ModuleDependency } from '@/types/architecture'
+
+interface Props {
+  initialNodes?: any[]
+  initialEdges?: any[]
+}
+
+const props = withDefaults(defineProps<Props>(), {
+  initialNodes: () => [],
+  initialEdges: () => []
+})
+
+const emit = defineEmits<{
+  'update:nodes': [nodes: any[]]
+  'update:edges': [edges: any[]]
+  'save': [data: { nodes: any[], edges: any[] }]
+}>()
+
+const nodes = ref(props.initialNodes)
+const edges = ref(props.initialEdges)
+
+const showAddModuleDialog = ref(false)
+const newModule = ref({
+  name: '',
+  type: 'backend',
+  description: ''
+})
+
+const moduleTypes = [
+  { label: 'Backend', value: 'backend' },
+  { label: 'Frontend', value: 'frontend' },
+  { label: 'Shared', value: 'shared' },
+  { label: 'Database', value: 'database' },
+  { label: 'Service', value: 'service' }
+]
+
+function onNodeDragStop(event: any) {
+  emit('update:nodes', nodes.value)
+}
+
+function onEdgeUpdate(oldEdge: any, newConnection: any) {
+  const index = edges.value.findIndex(e => e.id === oldEdge.id)
+  if (index !== -1) {
+    edges.value[index] = { ...oldEdge, ...newConnection }
+    emit('update:edges', edges.value)
+  }
+}
+
+function onConnect(connection: any) {
+  const newEdge = {
+    id: `e${connection.source}-${connection.target}`,
+    source: connection.source,
+    target: connection.target,
+    type: 'custom',
+    data: {
+      dependencyType: 'uses'
+    }
+  }
+  edges.value.push(newEdge)
+  emit('update:edges', edges.value)
+}
+
+function addModule() {
+  const id = `module-${Date.now()}`
+  const newNode = {
+    id,
+    type: 'module',
+    position: { x: 100, y: 100 },
+    data: {
+      ...newModule.value,
+      id
+    }
+  }
+  nodes.value.push(newNode)
+  emit('update:nodes', nodes.value)
+  
+  // Reset form
+  newModule.value = {
+    name: '',
+    type: 'backend',
+    description: ''
+  }
+}
+
+function editModule(moduleId: string) {
+  // Handle edit
+}
+
+function deleteModule(moduleId: string) {
+  nodes.value = nodes.value.filter(n => n.id !== moduleId)
+  edges.value = edges.value.filter(e => 
+    e.source !== moduleId && e.target !== moduleId
+  )
+  emit('update:nodes', nodes.value)
+  emit('update:edges', edges.value)
+}
+
+async function generateArchitecture() {
+  // Call AI generation API
+}
+
+function saveArchitecture() {
+  emit('save', {
+    nodes: nodes.value,
+    edges: edges.value
+  })
+}
+</script>
+
+<style scoped lang="scss">
+.architecture-canvas {
+  width: 100%;
+  height: 100%;
+  position: relative;
+}
+
+.canvas-toolbar {
+  position: absolute;
+  top: 16px;
+  left: 16px;
+  z-index: 10;
+  background: white;
+  border-radius: 4px;
+  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
+  padding: 8px;
+}
+</style>
+```
+
+---
+
+### 3. AI Chat Component
+
+```vue
+<!-- components/ai/AIChat.vue -->
+<template>
+  <q-card class="ai-chat-card">
+    <q-card-section class="chat-header">
+      <div class="row items-center">
+        <q-avatar color="primary" text-color="white" icon="smart_toy" />
+        <div class="q-ml-md">
+          <div class="text-h6">AI Асистент</div>
+          <div class="text-caption">
+            <q-badge 
+              :color="aiStatus === 'thinking' ? 'orange' : 'green'"
+              :label="aiStatusLabel"
+            />
+          </div>
+        </div>
+        <q-space />
+        <q-btn 
+          icon="close" 
+          flat 
+          round 
+          dense 
+          v-if="closeable"
+          @click="emit('close')"
+        />
+      </div>
+    </q-card-section>
+    
+    <q-separator />
+    
+    <q-card-section class="chat-messages" ref="messagesContainer">
+      <div 
+        v-for="message in messages" 
+        :key="message.id"
+        :class="['message', `message-${message.role}`]"
+      >
+        <div class="message-avatar">
+          <q-avatar 
+            :color="message.role === 'user' ? 'grey-7' : 'primary'"
+            text-color="white"
+            :icon="message.role === 'user' ? 'person' : 'smart_toy'"
+            size="32px"
+          />
+        </div>
+        
+        <div class="message-content">
+          <div class="message-text">
+            <div v-html="formatMessage(message.content)"></div>
+          </div>
+          
+          <div class="message-meta">
+            <span class="text-caption text-grey">
+              {{ formatTime(message.created_at) }}
+            </span>
+            
+            <q-btn
+              v-if="message.role === 'assistant'"
+              icon="thumb_up"
+              flat
+              dense
+              size="sm"
+              @click="rateMessage(message.id, 'positive')"
+            />
+            <q-btn
+              v-if="message.role === 'assistant'"
+              icon="thumb_down"
+              flat
+              dense
+              size="sm"
+              @click="rateMessage(message.id, 'negative')"
+            />
+          </div>
+        </div>
+      </div>
+      
+      <!-- Typing indicator -->
+      <div v-if="aiStatus === 'thinking'" class="message message-assistant">
+        <div class="message-avatar">
+          <q-avatar color="primary" text-color="white" icon="smart_toy" size="32px" />
+        </div>
+        <div class="message-content">
+          <div class="typing-indicator">
+            <span></span>
+            <span></span>
+            <span></span>
+          </div>
+        </div>
+      </div>
+    </q-card-section>
+    
+    <q-separator />
+    
+    <q-card-section class="chat-input">
+      <div class="row items-end q-gutter-sm">
+        <div class="col">
+          <q-input
+            v-model="inputMessage"
+            type="textarea"
+            placeholder="Напишете съобщение..."
+            outlined
+            dense
+            autogrow
+            :rows="1"
+            :max-height="100"
+            @keydown.enter.exact.prevent="sendMessage"
+            :disable="aiStatus === 'thinking'"
+          >
+            <template v-slot:prepend>
+              <q-btn 
+                icon="attach_file" 
+                flat 
+                round 
+                dense
+                @click="attachFile"
+              />
+            </template>
+          </q-input>
+        </div>
+        
+        <div>
+          <q-btn
+            icon="send"
+            color="primary"
+            round
+            :disable="!inputMessage.trim() || aiStatus === 'thinking'"
+            @click="sendMessage"
+          />
+        </div>
+      </div>
+      
+      <!-- Quick actions -->
+      <div class="quick-actions q-mt-sm">
+        <q-chip
+          v-for="action in quickActions"
+          :key="action.label"
+          clickable
+          @click="useQuickAction(action)"
+          size="sm"
+        >
+          {{ action.label }}
+        </q-chip>
+      </div>
+    </q-card-section>
+  </q-card>
+</template>
+
+<script setup lang="ts">
+import { ref, watch, nextTick, computed } from 'vue'
+import { marked } from 'marked'
+import type { ChatMessage } from '@/types/chat'
+import { useAIChat } from '@/composables/useAIChat'
+
+interface Props {
+  sessionId?: string
+  context?: any
+  closeable?: boolean
+}
+
+const props = defineProps<Props>()
+
+const emit = defineEmits<{
+  'close': []
+  'message-sent': [message: string]
+}>()
+
+const {
+  messages,
+  sendMessage: send,
+  aiStatus,
+  addUserMessage,
+  addAssistantMessage
+} = useAIChat(props.sessionId)
+
+const messagesContainer = ref<HTMLElement>()
+const inputMessage = ref('')
+
+const aiStatusLabel = computed(() => {
+  return aiStatus.value === 'thinking' ? 'Мисля...' : 'Онлайн'
+})
+
+const quickActions = [
+  { label: 'Анализирай', prompt: 'Моля, анализирай текущия контекст' },
+  { label: 'Предложи подобрения', prompt: 'Какви подобрения можеш да предложиш?' },
+  { label: 'Генерирай идеи', prompt: 'Генерирай 5 нови идеи' }
+]
+
+watch(messages, async () => {
+  await nextTick()
+  scrollToBottom()
+}, { deep: true })
+
+async function sendMessage() {
+  if (!inputMessage.value.trim()) return
+  
+  const message = inputMessage.value
+  inputMessage.value = ''
+  
+  await send(message, props.context)
+  emit('message-sent', message)
+}
+
+function useQuickAction(action: any) {
+  inputMessage.value = action.prompt
+  sendMessage()
+}
+
+function formatMessage(content: string): string {
+  return marked(content)
+}
+
+function formatTime(timestamp: string): string {
+  return new Date(timestamp).toLocaleTimeString('bg-BG', {
+    hour: '2-digit',
+    minute: '2-digit'
+  })
+}
+
+function scrollToBottom() {
+  if (messagesContainer.value) {
+    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
+  }
+}
+
+function rateMessage(messageId: string, rating: 'positive' | 'negative') {
+  // Send rating to backend
+  console.log('Rating message:', messageId, rating)
+}
+
+function attachFile() {
+  // Handle file attachment
+}
+</script>
+
+<style scoped lang="scss">
+.ai-chat-card {
+  display: flex;
+  flex-direction: column;
+  height: 100%;
+  max-height: 700px;
+}
+
+.chat-header {
+  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
+  color: white;
+}
+
+.chat-messages {
+  flex: 1;
+  overflow-y: auto;
+  max-height: 500px;
+  padding: 16px;
+  background: #f5f5f5;
+  
+  .message {
+    display: flex;
+    margin-bottom: 16px;
+    
+    &.message-user {
+      flex-direction: row-reverse;
+      
+      .message-content {
+        align-items: flex-end;
+        
+        .message-text {
+          background: #2196F3;
+          color: white;
+        }
+      }
+    }
+    
+    &.message-assistant {
+      .message-text {
+        background: white;
+        color: #333;
+      }
+    }
+  }
+  
+  .message-avatar {
+    margin: 0 8px;
+  }
+  
+  .message-content {
+    display: flex;
+    flex-direction: column;
+    max-width: 70%;
+    
+    .message-text {
+      padding: 12px 16px;
+      border-radius: 12px;
+      word-wrap: break-word;
+    }
+    
+    .message-meta {
+      display: flex;
+      align-items: center;
+      gap: 8px;
+      margin-top: 4px;
+      padding: 0 8px;
+    }
+  }
+}
+
+.typing-indicator {
+  display: flex;
+  gap: 4px;
+  padding: 12px 16px;
+  background: white;
+  border-radius: 12px;
+  
+  span {
+    width: 8px;
+    height: 8px;
+    border-radius: 50%;
+    background: #999;
+    animation: typing 1.4s infinite;
+    
+    &:nth-child(2) {
+      animation-delay: 0.2s;
+    }
+    
+    &:nth-child(3) {
+      animation-delay: 0.4s;
+    }
+  }
+}
+
+@keyframes typing {
+  0%, 60%, 100% {
+    opacity: 0.3;
+    transform: scale(0.8);
+  }
+  30% {
+    opacity: 1;
+    transform: scale(1);
+  }
+}
+
+.chat-input {
+  background: white;
+}
+
+.quick-actions {
+  display: flex;
+  flex-wrap: wrap;
+  gap: 8px;
+}
+</style>
+```
+
+---
+
+### 4. Checkable Tree Component
+
+```vue
+<!-- components/tree/CheckableTree.vue -->
+<template>
+  <q-tree
+    ref="treeRef"
+    :nodes="nodes"
+    node-key="id"
+    :tick-strategy="tickStrategy"
+    v-model:ticked="checked"
+    v-model:expanded="expanded"
+    @update:ticked="handleCheck"
+    :filter="filter"
+    :filter-method="filterMethod"
+  >
+    <template v-slot:default-header="prop">
+      <div class="row items-center full-width tree-node-header">
+        <q-icon 
+          :name="getNodeIcon(prop.node)" 
+          :color="getNodeColor(prop.node)"
+          size="20px"
+          class="q-mr-sm"
+        />
+        
+        <div class="col">
+          <div class="text-weight-medium">
+            {{ prop.node.label }}
+          </div>
+          <div v-if="prop.node.description" class="text-caption text-grey-7">
+            {{ prop.node.description }}
+          </div>
+        </div>
+        
+        <q-space />
+        
+        <!-- Node actions -->
+        <div class="node-actions">
+          <q-btn 
+            icon="add" 
+            flat 
+            dense 
+            round
+            size="sm"
+            @click.stop="emit('add-child', prop.node)"
+            v-if="allowAdd"
+          >
+            <q-tooltip>Добави подвъзел</q-tooltip>
+          </q-btn>
+          
+          <q-btn 
+            icon="edit" 
+            flat 
+            dense 
+            round
+            size="sm"
+            @click.stop="emit('edit', prop.node)"
+            v-if="allowEdit"
+          >
+            <q-tooltip>Редактирай</q-tooltip>
+          </q-btn>
+          
+          <q-btn 
+            icon="chat" 
+            flat 
+            dense 
+            round
+            size="sm"
+            @click.stop="emit('chat', prop.node)"
+            v-if="allowChat"
+          >
+            <q-tooltip>Чат по този възел</q-tooltip>
+          </q-btn>
+          
+          <q-btn 
+            icon="auto_awesome" 
+            flat 
+            dense 
+            round
+            size="sm"
+            color="primary"
+            @click.stop="emit('ai-action', prop.node)"
+            v-if="allowAI"
+          >
+            <q-tooltip>AI действие</q-tooltip>
+          </q-btn>
+          
+          <q-btn 
+            icon="more_vert" 
+            flat 
+            dense 
+            round
+            size="sm"
+          >
+            <q-menu>
+              <q-list dense>
+                <q-item clickable @click="emit('duplicate', prop.node)">
+                  <q-item-section>Дублирай</q-item-section>
+                </q-item>
+                <q-item clickable @click="emit('move', prop.node)">
+                  <q-item-section>Премести</q-item-section>
+                </q-item>
+                <q-separator />
+                <q-item 
+                  clickable 
+                  @click="emit('delete', prop.node)"
+                  class="text-negative"
+                >
+                  <q-item-section>Изтрий</q-item-section>
+                </q-item>
+              </q-list>
+            </q-menu>
+          </q-btn>
+        </div>
+      </div>
+    </template>
+    
+    <template v-slot:default-body="prop" v-if="showDetails">
+      <div class="q-pa-sm tree-node-details">
+        <q-badge 
+          v-if="prop.node.status"
+          :label="prop.node.status"
+          :color="getStatusColor(prop.node.status)"
+        />
+        
+        <div v-if="prop.node.metadata" class="q-mt-xs">
+          <div class="text-caption">
+            Създаден: {{ formatDate(prop.node.metadata.created_at) }}
+          </div>
+          <div v-if="prop.node.metadata.updated_at" class="text-caption">
+            Обновен: {{ formatDate(prop.node.metadata.updated_at) }}
+          </div>
+        </div>
+      </div>
+    </template>
+  </q-tree>
+</template>
+
+<script setup lang="ts">
+import { ref, computed } from 'vue'
+import type { TreeNode } from '@/types/tree'
+
+interface Props {
+  nodes: TreeNode[]
+  tickStrategy?: 'leaf' | 'leaf-filtered' | 'strict' | 'none'
+  allowAdd?: boolean
+  allowEdit?: boolean
+  allowChat?: boolean
+  allowAI?: boolean
+  showDetails?: boolean
+  filter?: string
+}
+
+const props = withDefaults(defineProps<Props>(), {
+  tickStrategy: 'leaf',
+  allowAdd: true,
+  allowEdit: true,
+  allowChat: false,
+  allowAI: false,
+  showDetails: false
+})
+
+const emit = defineEmits<{
+  'update:checked': [checked: string[]]
+  'add-child': [node: TreeNode]
+  'edit': [node: TreeNode]
+  'chat': [node: TreeNode]
+  'ai-action': [node: TreeNode]
+  'duplicate': [node: TreeNode]
+  'move': [node: TreeNode]
+  'delete': [node: TreeNode]
+}>()
+
+const treeRef = ref()
+const checked = ref<string[]>([])
+const expanded = ref<string[]>([])
+
+function handleCheck(keys: string[]) {
+  emit('update:checked', keys)
+}
+
+function getNodeIcon(node: TreeNode): string {
+  const icons = {
+    goal: 'flag',
+    opportunity: 'lightbulb',
+    module: 'widgets',
+    requirement: 'assignment',
+    default: 'circle'
+  }
+  return icons[node.type as keyof typeof icons] || icons.default
+}
+
+function getNodeColor(node: TreeNode): string {
+  const colors = {
+    goal: 'green',
+    opportunity: 'blue',
+    module: 'orange',
+    requirement: 'purple',
+    default: 'grey'
+  }
+  return colors[node.type as keyof typeof colors] || colors.default
+}
+
+function getStatusColor(status: string): string {
+  const colors = {
+    draft: 'grey',
+    pending: 'orange',
+    approved: 'green',
+    rejected: 'red'
+  }
+  return colors[status as keyof typeof colors] || 'grey'
+}
+
+function formatDate(dateString: string): string {
+  return new Date(dateString).toLocaleDateString('bg-BG')
+}
+
+function filterMethod(node: TreeNode, filter: string): boolean {
+  const filt = filter.toLowerCase()
+  return (
+    node.label?.toLowerCase().includes(filt) ||
+    node.description?.toLowerCase().includes(filt) ||
+    false
+  )
+}
+
+// Expose methods
+defineExpose({
+  expandAll: () => treeRef.value?.expandAll(),
+  collapseAll: () => treeRef.value?.collapseAll(),
+  getChecked: () => checked.value
+})
+</script>
+
+<style scoped lang="scss">
+.tree-node-header {
+  padding: 4px 8px;
+  border-radius: 4px;
+  transition: background 0.2s;
+  
+  &:hover {
+    background: rgba(0, 0, 0, 0.05);
+    
+    .node-actions {
+      opacity: 1;
+    }
+  }
+}
+
+.node-actions {
+  opacity: 0;
+  transition: opacity 0.2s;
+  display: flex;
+  gap: 4px;
+}
+
+.tree-node-details {
+  background: rgba(0, 0, 0, 0.02);
+  border-radius: 4px;
+}
+</style>
+```
+
+---
+
+Това са основните frontend компоненти. Ще продължа със създаване на deployment guide и финален summary документ.