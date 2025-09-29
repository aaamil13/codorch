diff --git a/TECHNICAL_ARCHITECTURE.md b/TECHNICAL_ARCHITECTURE.md
--- a/TECHNICAL_ARCHITECTURE.md
+++ b/TECHNICAL_ARCHITECTURE.md
@@ -0,0 +1,1086 @@
+# Техническа Архитектура - Детайли
+
+## 1. Database Schema
+
+### PostgreSQL Tables
+
+```sql
+-- Projects table
+CREATE TABLE projects (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    name VARCHAR(255) NOT NULL,
+    description TEXT,
+    goal TEXT NOT NULL,
+    current_stage VARCHAR(50),
+    tree_snapshot JSONB, -- RefMemTree snapshot
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+    created_by UUID,
+    status VARCHAR(50) DEFAULT 'active'
+);
+
+-- Tree nodes (for persistence)
+CREATE TABLE tree_nodes (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    parent_id UUID REFERENCES tree_nodes(id) ON DELETE CASCADE,
+    node_type VARCHAR(50) NOT NULL, -- goal, opportunity, module, etc.
+    data JSONB NOT NULL,
+    position INTEGER,
+    level INTEGER,
+    path TEXT, -- Materialized path for querying
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+CREATE INDEX idx_tree_nodes_project ON tree_nodes(project_id);
+CREATE INDEX idx_tree_nodes_parent ON tree_nodes(parent_id);
+CREATE INDEX idx_tree_nodes_path ON tree_nodes(path);
+
+-- Goals
+CREATE TABLE goals (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    tree_node_id UUID REFERENCES tree_nodes(id),
+    title VARCHAR(255) NOT NULL,
+    description TEXT,
+    is_smart_validated BOOLEAN DEFAULT FALSE,
+    metrics JSONB,
+    target_date DATE,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- Opportunities
+CREATE TABLE opportunities (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    tree_node_id UUID REFERENCES tree_nodes(id),
+    title VARCHAR(255) NOT NULL,
+    description TEXT,
+    ai_generated BOOLEAN DEFAULT FALSE,
+    score DECIMAL(5,2),
+    scoring_details JSONB,
+    feasibility_score DECIMAL(5,2),
+    impact_score DECIMAL(5,2),
+    effort_estimate VARCHAR(50),
+    status VARCHAR(50) DEFAULT 'proposed',
+    approved_at TIMESTAMP,
+    approved_by UUID,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- Research sessions
+CREATE TABLE research_sessions (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    tree_node_id UUID REFERENCES tree_nodes(id),
+    context JSONB,
+    insights JSONB,
+    status VARCHAR(50) DEFAULT 'active',
+    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+    ended_at TIMESTAMP
+);
+
+-- Chat messages
+CREATE TABLE chat_messages (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    research_session_id UUID REFERENCES research_sessions(id) ON DELETE CASCADE,
+    role VARCHAR(20) NOT NULL, -- user, assistant, system
+    content TEXT NOT NULL,
+    metadata JSONB,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+CREATE INDEX idx_chat_messages_session ON chat_messages(research_session_id);
+
+-- Architecture modules
+CREATE TABLE architecture_modules (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    tree_node_id UUID REFERENCES tree_nodes(id),
+    name VARCHAR(255) NOT NULL,
+    module_type VARCHAR(50), -- backend, frontend, shared, etc.
+    description TEXT,
+    position JSONB, -- {x, y} for canvas
+    properties JSONB,
+    complexity_score DECIMAL(5,2),
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- Module dependencies
+CREATE TABLE module_dependencies (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    from_module_id UUID REFERENCES architecture_modules(id) ON DELETE CASCADE,
+    to_module_id UUID REFERENCES architecture_modules(id) ON DELETE CASCADE,
+    dependency_type VARCHAR(50), -- import, extends, uses, etc.
+    metadata JSONB,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+    UNIQUE(from_module_id, to_module_id, dependency_type)
+);
+CREATE INDEX idx_deps_from ON module_dependencies(from_module_id);
+CREATE INDEX idx_deps_to ON module_dependencies(to_module_id);
+
+-- Architecture rules
+CREATE TABLE architecture_rules (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    module_id UUID REFERENCES architecture_modules(id) ON DELETE CASCADE, -- null = global
+    level VARCHAR(50), -- global, module, component
+    rule_type VARCHAR(50),
+    rule_definition JSONB,
+    ai_generated BOOLEAN DEFAULT FALSE,
+    active BOOLEAN DEFAULT TRUE,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- Requirements
+CREATE TABLE requirements (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    module_id UUID REFERENCES architecture_modules(id),
+    requirement_type VARCHAR(50), -- functional, non-functional
+    title VARCHAR(255) NOT NULL,
+    description TEXT,
+    priority VARCHAR(20),
+    validation_score DECIMAL(5,2),
+    validation_feedback JSONB,
+    status VARCHAR(50) DEFAULT 'draft',
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- Technology stack
+CREATE TABLE tech_stack (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    module_id UUID REFERENCES architecture_modules(id),
+    category VARCHAR(50), -- language, framework, database, etc.
+    technology VARCHAR(100),
+    version VARCHAR(50),
+    justification TEXT,
+    ai_recommended BOOLEAN DEFAULT FALSE,
+    approved BOOLEAN DEFAULT FALSE,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- Code generation
+CREATE TABLE code_generations (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    module_id UUID REFERENCES architecture_modules(id),
+    generation_type VARCHAR(50), -- scaffold, implementation, tests
+    validation_passed BOOLEAN,
+    validation_results JSONB,
+    generated_code JSONB, -- {files: [{path, content}]}
+    status VARCHAR(50) DEFAULT 'pending',
+    approved_at TIMESTAMP,
+    approved_by UUID,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- AI workflows
+CREATE TABLE ai_workflows (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    workflow_type VARCHAR(50),
+    workflow_name VARCHAR(100),
+    config JSONB,
+    status VARCHAR(50),
+    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
+    completed_at TIMESTAMP,
+    result JSONB,
+    error TEXT
+);
+
+-- AI agent executions
+CREATE TABLE ai_agent_executions (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    workflow_id UUID REFERENCES ai_workflows(id),
+    agent_name VARCHAR(100),
+    agent_type VARCHAR(50), -- specialist, generator, analyzer, supervisor
+    input JSONB,
+    output JSONB,
+    confidence DECIMAL(5,2),
+    execution_time_ms INTEGER,
+    status VARCHAR(50),
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+
+-- Human approvals
+CREATE TABLE human_approvals (
+    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
+    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
+    entity_type VARCHAR(50), -- goal, opportunity, architecture, etc.
+    entity_id UUID,
+    stage VARCHAR(50),
+    status VARCHAR(50) DEFAULT 'pending', -- pending, approved, rejected
+    feedback TEXT,
+    approved_by UUID,
+    decided_at TIMESTAMP,
+    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
+);
+```
+
+---
+
+## 2. API Endpoints - Complete List
+
+### Authentication
+```
+POST   /api/v1/auth/register
+POST   /api/v1/auth/login
+POST   /api/v1/auth/logout
+POST   /api/v1/auth/refresh
+GET    /api/v1/auth/me
+```
+
+### Projects
+```
+POST   /api/v1/projects
+GET    /api/v1/projects
+GET    /api/v1/projects/{id}
+PUT    /api/v1/projects/{id}
+DELETE /api/v1/projects/{id}
+GET    /api/v1/projects/{id}/tree
+POST   /api/v1/projects/{id}/initialize  # Runs initialization workflow
+GET    /api/v1/projects/{id}/status
+```
+
+### Goals (Module 1)
+```
+POST   /api/v1/projects/{project_id}/goals
+GET    /api/v1/projects/{project_id}/goals
+GET    /api/v1/goals/{id}
+PUT    /api/v1/goals/{id}
+DELETE /api/v1/goals/{id}
+POST   /api/v1/goals/{id}/analyze        # AI analysis
+POST   /api/v1/goals/{id}/decompose      # AI decomposition
+POST   /api/v1/goals/{id}/validate-smart
+```
+
+### Opportunities (Module 2)
+```
+POST   /api/v1/projects/{project_id}/opportunities
+GET    /api/v1/projects/{project_id}/opportunities
+GET    /api/v1/opportunities/{id}
+PUT    /api/v1/opportunities/{id}
+DELETE /api/v1/opportunities/{id}
+POST   /api/v1/opportunities/generate    # AI team generation
+POST   /api/v1/opportunities/{id}/subtree
+GET    /api/v1/opportunities/compare
+POST   /api/v1/opportunities/{id}/score
+POST   /api/v1/opportunities/{id}/approve
+```
+
+### Research (Module 3)
+```
+POST   /api/v1/projects/{project_id}/research/sessions
+GET    /api/v1/research/sessions/{id}
+POST   /api/v1/research/sessions/{id}/chat
+POST   /api/v1/research/{node_id}/start
+GET    /api/v1/research/{node_id}/context
+GET    /api/v1/research/search           # Semantic search
+POST   /api/v1/research/sessions/{id}/end
+GET    /api/v1/research/sessions/{id}/insights
+```
+
+### Architecture (Module 4)
+```
+POST   /api/v1/projects/{project_id}/architecture/generate
+GET    /api/v1/projects/{project_id}/architecture
+POST   /api/v1/architecture/modules
+GET    /api/v1/architecture/modules/{id}
+PUT    /api/v1/architecture/modules/{id}
+DELETE /api/v1/architecture/modules/{id}
+PUT    /api/v1/architecture/modules/{id}/position
+POST   /api/v1/architecture/dependencies
+DELETE /api/v1/architecture/dependencies/{id}
+GET    /api/v1/architecture/{project_id}/validate
+POST   /api/v1/architecture/rules
+GET    /api/v1/architecture/rules
+PUT    /api/v1/architecture/rules/{id}
+DELETE /api/v1/architecture/rules/{id}
+GET    /api/v1/architecture/{project_id}/complexity
+POST   /api/v1/architecture/{project_id}/impact-analysis
+GET    /api/v1/architecture/{project_id}/shared-modules
+POST   /api/v1/architecture/modules/{id}/approve
+```
+
+### Requirements (Module 5)
+```
+POST   /api/v1/architecture/modules/{module_id}/requirements
+GET    /api/v1/architecture/modules/{module_id}/requirements
+GET    /api/v1/requirements/{id}
+PUT    /api/v1/requirements/{id}
+DELETE /api/v1/requirements/{id}
+POST   /api/v1/requirements/{id}/validate  # AI validation
+POST   /api/v1/requirements/{module_id}/generate  # AI generation
+POST   /api/v1/tech-stack
+GET    /api/v1/projects/{project_id}/tech-stack
+POST   /api/v1/tech-stack/{id}/approve
+POST   /api/v1/tech-stack/recommend  # AI recommendations
+```
+
+### Code Generation (Module 6)
+```
+POST   /api/v1/projects/{project_id}/code-gen/validate
+POST   /api/v1/projects/{project_id}/code-gen/generate-scaffold
+POST   /api/v1/projects/{project_id}/code-gen/generate-implementation
+POST   /api/v1/projects/{project_id}/code-gen/generate-tests
+POST   /api/v1/projects/{project_id}/code-gen/generate-docs
+GET    /api/v1/code-gen/{id}
+GET    /api/v1/projects/{project_id}/code-gen/status
+POST   /api/v1/code-gen/{id}/approve
+GET    /api/v1/code-gen/{id}/download
+```
+
+### Tree Management
+```
+GET    /api/v1/tree/nodes/{id}
+POST   /api/v1/tree/nodes/{id}/children
+PUT    /api/v1/tree/nodes/{id}
+DELETE /api/v1/tree/nodes/{id}
+GET    /api/v1/tree/nodes/{id}/context
+POST   /api/v1/tree/nodes/{id}/branch
+GET    /api/v1/tree/{project_id}/export
+```
+
+### Workflows
+```
+GET    /api/v1/workflows
+GET    /api/v1/workflows/{id}
+POST   /api/v1/workflows/{id}/cancel
+GET    /api/v1/workflows/{id}/logs
+```
+
+### Approvals
+```
+GET    /api/v1/approvals/pending
+POST   /api/v1/approvals/{id}/approve
+POST   /api/v1/approvals/{id}/reject
+GET    /api/v1/projects/{project_id}/approvals
+```
+
+### WebSocket Endpoints
+```
+WS     /ws/chat/{session_id}
+WS     /ws/project/{project_id}/updates
+WS     /ws/workflow/{workflow_id}/progress
+```
+
+---
+
+## 3. Backend Services Architecture
+
+```
+backend/
+├── main.py                           # FastAPI app
+├── config.py                         # Configuration
+├── dependencies.py                   # DI dependencies
+│
+├── core/
+│   ├── tree_manager/
+│   │   ├── __init__.py
+│   │   ├── ref_mem_tree_manager.py   # RefMemTree wrapper
+│   │   ├── context_builder.py        # Context aggregation
+│   │   └── persistence.py            # DB persistence
+│   │
+│   ├── ai_orchestrator/
+│   │   ├── __init__.py
+│   │   ├── agent_factory.py          # Creates agents
+│   │   ├── team_manager.py           # Manages AI teams
+│   │   └── config.py                 # Agent configs
+│   │
+│   ├── workflow_engine/
+│   │   ├── __init__.py
+│   │   ├── base_workflows.py         # Base workflow classes
+│   │   └── workflow_registry.py      # Registry of all workflows
+│   │
+│   └── validation/
+│       ├── __init__.py
+│       ├── schemas.py                # Pydantic schemas
+│       └── validators.py             # Custom validators
+│
+├── db/
+│   ├── __init__.py
+│   ├── session.py                    # DB session management
+│   ├── models.py                     # SQLAlchemy models
+│   ├── migrations/                   # Alembic migrations
+│   └── repositories/                 # Repository pattern
+│       ├── project_repo.py
+│       ├── goal_repo.py
+│       ├── opportunity_repo.py
+│       └── ...
+│
+├── api/
+│   ├── __init__.py
+│   ├── deps.py                       # API dependencies
+│   └── v1/
+│       ├── __init__.py
+│       ├── auth.py
+│       ├── projects.py
+│       ├── goals.py
+│       ├── opportunities.py
+│       ├── research.py
+│       ├── architecture.py
+│       ├── requirements.py
+│       ├── code_gen.py
+│       ├── workflows.py
+│       └── websocket.py
+│
+├── modules/
+│   ├── goal_definition/
+│   │   ├── __init__.py
+│   │   ├── service.py                # Business logic
+│   │   └── workflows.py              # Prefect workflows
+│   │
+│   ├── opportunity_engine/
+│   │   ├── __init__.py
+│   │   ├── service.py
+│   │   ├── scoring.py
+│   │   └── workflows.py
+│   │
+│   ├── research_module/
+│   │   ├── __init__.py
+│   │   ├── service.py
+│   │   ├── context_manager.py
+│   │   └── semantic_search.py
+│   │
+│   ├── architecture_designer/
+│   │   ├── __init__.py
+│   │   ├── service.py
+│   │   ├── complexity_analyzer.py
+│   │   ├── dependency_validator.py
+│   │   ├── rules_engine.py
+│   │   └── workflows.py
+│   │
+│   ├── requirements_module/
+│   │   ├── __init__.py
+│   │   ├── service.py
+│   │   └── workflows.py
+│   │
+│   └── code_generator/
+│       ├── __init__.py
+│       ├── service.py
+│       ├── validation_pipeline.py
+│       ├── generators/
+│       │   ├── scaffold_generator.py
+│       │   ├── implementation_generator.py
+│       │   ├── test_generator.py
+│       │   └── docs_generator.py
+│       └── workflows.py
+│
+├── ai_agents/
+│   ├── __init__.py
+│   ├── base.py                       # Base agent classes
+│   ├── specialist.py
+│   ├── idea_generator.py
+│   ├── analyzer.py
+│   ├── supervisor.py
+│   └── prompts/                      # Prompt templates
+│       ├── goal_analysis.txt
+│       ├── opportunity_generation.txt
+│       ├── architecture_review.txt
+│       └── ...
+│
+├── services/
+│   ├── __init__.py
+│   ├── vector_db.py                  # Qdrant/Pinecone
+│   ├── cache.py                      # Redis cache
+│   └── notification.py               # Notifications
+│
+└── utils/
+    ├── __init__.py
+    ├── logging.py
+    ├── exceptions.py
+    └── helpers.py
+```
+
+---
+
+## 4. Frontend Components Architecture
+
+```
+frontend/src/
+├── layouts/
+│   ├── MainLayout.vue                # Main app layout
+│   └── AuthLayout.vue                # Auth pages layout
+│
+├── pages/
+│   ├── Index.vue                     # Landing/home
+│   ├── Dashboard.vue
+│   │
+│   ├── GoalDefinition/
+│   │   ├── Index.vue
+│   │   └── GoalDetail.vue
+│   │
+│   ├── OpportunityExplorer/
+│   │   ├── Index.vue
+│   │   ├── OpportunityList.vue
+│   │   ├── OpportunityDetail.vue
+│   │   └── ComparisonView.vue
+│   │
+│   ├── Research/
+│   │   ├── Index.vue
+│   │   ├── SessionView.vue
+│   │   └── InsightsDashboard.vue
+│   │
+│   ├── ArchitectureDesigner/
+│   │   ├── Index.vue
+│   │   ├── CanvasView.vue
+│   │   └── AnalysisView.vue
+│   │
+│   ├── Requirements/
+│   │   ├── Index.vue
+│   │   └── ModuleRequirements.vue
+│   │
+│   └── CodeGenerator/
+│       ├── Index.vue
+│       ├── ValidationView.vue
+│       └── GenerationView.vue
+│
+├── components/
+│   ├── common/
+│   │   ├── AppHeader.vue
+│   │   ├── AppSidebar.vue
+│   │   ├── AppFooter.vue
+│   │   ├── LoadingSpinner.vue
+│   │   └── ErrorAlert.vue
+│   │
+│   ├── tree/
+│   │   ├── TreeVisualizer.vue        # Main tree component
+│   │   ├── TreeNode.vue
+│   │   ├── CheckableTree.vue
+│   │   └── TreeControls.vue
+│   │
+│   ├── ai/
+│   │   ├── AIChat.vue                # Chat interface
+│   │   ├── AITeamStatus.vue          # Shows team status
+│   │   ├── AIGeneratorPanel.vue      # Control panel
+│   │   └── ConfidenceIndicator.vue
+│   │
+│   ├── architecture/
+│   │   ├── ArchitectureCanvas.vue    # Vue Flow canvas
+│   │   ├── ModuleNode.vue
+│   │   ├── ConnectionLine.vue
+│   │   ├── ModulePropertiesPanel.vue
+│   │   ├── DependencyEditor.vue
+│   │   ├── InheritancePanel.vue
+│   │   ├── SharedModulesPanel.vue
+│   │   ├── RulesEditor.vue
+│   │   ├── ComplexityDashboard.vue
+│   │   └── ImpactAnalyzer.vue
+│   │
+│   ├── opportunities/
+│   │   ├── OpportunityCard.vue
+│   │   ├── OpportunityList.vue
+│   │   ├── ScoringPanel.vue
+│   │   ├── ComparisonMatrix.vue
+│   │   └── SubtreeVisualizer.vue
+│   │
+│   ├── research/
+│   │   ├── NodeSelector.vue
+│   │   ├── ResearchChat.vue
+│   │   ├── ContextPanel.vue
+│   │   ├── ResearchHistory.vue
+│   │   └── InsightsBoard.vue
+│   │
+│   ├── requirements/
+│   │   ├── RequirementsEditor.vue
+│   │   ├── TechStackSelector.vue
+│   │   ├── APISpecBuilder.vue
+│   │   ├── DataSchemaEditor.vue
+│   │   └── ValidationPanel.vue
+│   │
+│   ├── codegen/
+│   │   ├── ValidationDashboard.vue
+│   │   ├── CodePreview.vue
+│   │   ├── DiffViewer.vue
+│   │   └── TestResults.vue
+│   │
+│   └── approvals/
+│       ├── ApprovalCard.vue
+│       ├── ApprovalDialog.vue
+│       └── ApprovalHistory.vue
+│
+├── composables/
+│   ├── useAPI.ts                     # API calls
+│   ├── useAIChat.ts                  # Chat functionality
+│   ├── useTree.ts                    # Tree operations
+│   ├── useWebSocket.ts               # WebSocket connection
+│   ├── useApprovals.ts               # Approval workflow
+│   └── useWorkflow.ts                # Workflow status
+│
+├── stores/
+│   ├── project.ts                    # Project state
+│   ├── auth.ts                       # Authentication
+│   ├── tree.ts                       # Tree state
+│   ├── ai.ts                         # AI state
+│   ├── architecture.ts               # Architecture state
+│   └── ui.ts                         # UI state
+│
+├── services/
+│   ├── api.ts                        # Axios instance
+│   ├── websocket.ts                  # WebSocket client
+│   └── storage.ts                    # LocalStorage wrapper
+│
+├── utils/
+│   ├── format.ts
+│   ├── validation.ts
+│   └── constants.ts
+│
+└── types/
+    ├── project.ts
+    ├── tree.ts
+    ├── ai.ts
+    ├── architecture.ts
+    └── api.ts
+```
+
+---
+
+## 5. Key Technology Integration Details
+
+### RefMemTree Integration Example
+
+```python
+# core/tree_manager/ref_mem_tree_manager.py
+
+from refmemtree import RefMemTree, Node
+from typing import Dict, List, Optional
+import json
+
+class ProjectTreeManager:
+    def __init__(self, project_id: str):
+        self.project_id = project_id
+        self.tree = RefMemTree()
+        self._load_or_create()
+    
+    def _load_or_create(self):
+        """Load existing tree or create new"""
+        # Load from DB if exists
+        tree_data = self._load_from_db()
+        if tree_data:
+            self.tree = RefMemTree.from_dict(tree_data)
+        
+    def create_goal_node(self, goal_data: Dict) -> Node:
+        """Create goal as root or child"""
+        node = self.tree.add_node(
+            data={
+                "type": "goal",
+                "title": goal_data["title"],
+                "description": goal_data["description"],
+                "metrics": goal_data.get("metrics", {}),
+                "created_at": datetime.now().isoformat()
+            },
+            parent_id=goal_data.get("parent_id")
+        )
+        self._persist_to_db(node)
+        return node
+    
+    def get_ai_context(
+        self, 
+        node_id: str, 
+        context_depth: int = 3,
+        include_siblings: bool = False
+    ) -> str:
+        """Build context string for AI from tree"""
+        node = self.tree.get_node(node_id)
+        
+        context_parts = []
+        
+        # Current node
+        context_parts.append(f"Current Context: {node.data['type']}")
+        context_parts.append(f"Title: {node.data.get('title', 'N/A')}")
+        context_parts.append(f"Description: {node.data.get('description', 'N/A')}")
+        
+        # Parent chain
+        parents = self._get_parent_chain(node, depth=context_depth)
+        if parents:
+            context_parts.append("\nParent Context:")
+            for i, parent in enumerate(parents):
+                indent = "  " * i
+                context_parts.append(
+                    f"{indent}- {parent.data['type']}: {parent.data.get('title', 'N/A')}"
+                )
+        
+        # Siblings if requested
+        if include_siblings:
+            siblings = self._get_siblings(node)
+            if siblings:
+                context_parts.append("\nSibling Context:")
+                for sib in siblings:
+                    context_parts.append(
+                        f"  - {sib.data['type']}: {sib.data.get('title', 'N/A')}"
+                    )
+        
+        # Children summary
+        children = self.tree.get_children(node_id)
+        if children:
+            context_parts.append(f"\nHas {len(children)} child nodes")
+        
+        return "\n".join(context_parts)
+    
+    def create_experimental_branch(
+        self, 
+        node_id: str, 
+        branch_name: str
+    ) -> Node:
+        """Create a copy of subtree for experimentation"""
+        original_node = self.tree.get_node(node_id)
+        
+        # Create branch marker node
+        branch_node = self.tree.add_node(
+            data={
+                "type": "branch",
+                "name": branch_name,
+                "original_node_id": node_id,
+                "created_at": datetime.now().isoformat()
+            },
+            parent_id=original_node.parent_id
+        )
+        
+        # Deep copy subtree
+        self._copy_subtree(original_node, branch_node.id)
+        
+        return branch_node
+    
+    def merge_branch(self, branch_id: str, delete_branch: bool = True):
+        """Merge experimental branch back"""
+        # Implementation for merging changes
+        pass
+    
+    def _persist_to_db(self, node: Node):
+        """Persist node to database"""
+        # Save to tree_nodes table
+        pass
+    
+    def export_to_dict(self) -> Dict:
+        """Export tree to dict for storage"""
+        return self.tree.to_dict()
+```
+
+### Pydantic AI Agent Example
+
+```python
+# ai_agents/opportunity_generator.py
+
+from pydantic_ai import Agent, RunContext
+from pydantic import BaseModel, Field
+from typing import List
+
+class OpportunityContext(BaseModel):
+    goal: str
+    existing_opportunities: List[str]
+    constraints: List[str]
+    industry: str
+
+class GeneratedOpportunity(BaseModel):
+    title: str = Field(description="Clear, concise title")
+    description: str = Field(description="Detailed description")
+    feasibility_score: float = Field(ge=0, le=10)
+    impact_score: float = Field(ge=0, le=10)
+    effort_estimate: str = Field(description="One of: low, medium, high")
+    key_risks: List[str]
+    success_factors: List[str]
+    reasoning: str = Field(description="Why this is a good opportunity")
+
+class OpportunityOutput(BaseModel):
+    opportunities: List[GeneratedOpportunity]
+    total_generated: int
+    generation_confidence: float
+
+# Create specialized agent
+opportunity_generator = Agent(
+    'openai:gpt-4-turbo',
+    result_type=OpportunityOutput,
+    system_prompt="""
+    You are an expert business strategist and opportunity analyzer.
+    Your role is to generate creative, feasible business opportunities
+    based on the given goal and context.
+    
+    Consider:
+    - Market viability
+    - Technical feasibility
+    - Resource requirements
+    - Potential impact
+    - Risks and mitigation strategies
+    
+    Generate diverse opportunities that cover different approaches
+    and market segments.
+    """,
+)
+
+@opportunity_generator.tool
+def search_market_trends(industry: str) -> str:
+    """Search for current market trends in the industry"""
+    # Integration with market research APIs
+    return "Market trends data..."
+
+@opportunity_generator.tool
+def analyze_competition(industry: str, opportunity_type: str) -> str:
+    """Analyze competitive landscape"""
+    # Integration with competitive analysis tools
+    return "Competition analysis..."
+
+# Usage in service
+async def generate_opportunities(context: OpportunityContext) -> OpportunityOutput:
+    result = await opportunity_generator.run(
+        f"""
+        Generate 5 diverse business opportunities for:
+        Goal: {context.goal}
+        Industry: {context.industry}
+        
+        Existing opportunities to avoid duplicating:
+        {chr(10).join(f'- {opp}' for opp in context.existing_opportunities)}
+        
+        Constraints to consider:
+        {chr(10).join(f'- {c}' for c in context.constraints)}
+        """,
+        message_history=[]  # Can include previous context
+    )
+    
+    return result.data
+```
+
+### Prefect Workflow Example
+
+```python
+# modules/architecture_designer/workflows.py
+
+from prefect import flow, task
+from prefect.task_runners import ConcurrentTaskRunner
+from typing import Dict, List
+import asyncio
+
+@task(name="Gather Requirements")
+async def gather_requirements(project_id: str) -> Dict:
+    """Collect all requirements from project"""
+    # Query database for requirements
+    return {"functional": [...], "non_functional": [...]}
+
+@task(name="Generate Base Architecture")
+async def generate_base_architecture(
+    requirements: Dict,
+    architect_agent
+) -> Dict:
+    """Generate initial architecture using AI"""
+    result = await architect_agent.run(
+        f"Generate system architecture for requirements: {requirements}"
+    )
+    return result.data
+
+@task(name="Validate Dependencies")
+async def validate_dependencies(architecture: Dict) -> Dict:
+    """Check for circular dependencies and issues"""
+    validator = DependencyValidator()
+    return validator.validate(architecture)
+
+@task(name="Calculate Complexity")
+async def calculate_complexity(architecture: Dict) -> float:
+    """Calculate complexity metrics"""
+    analyzer = ComplexityAnalyzer()
+    return analyzer.calculate(architecture)
+
+@task(name="Review Architecture")
+async def review_architecture(
+    architecture: Dict,
+    validation: Dict,
+    complexity: float,
+    reviewer_agent
+) -> Dict:
+    """AI review of generated architecture"""
+    review = await reviewer_agent.run(
+        f"""Review this architecture:
+        {architecture}
+        
+        Validation results: {validation}
+        Complexity score: {complexity}
+        
+        Provide detailed feedback and suggestions.
+        """
+    )
+    return review.data
+
+@task(name="Request Human Approval")
+async def request_human_approval(
+    project_id: str,
+    architecture: Dict,
+    review: Dict
+) -> bool:
+    """Create approval request and wait for human decision"""
+    approval_id = create_approval_request(
+        project_id=project_id,
+        entity_type="architecture",
+        data={"architecture": architecture, "review": review}
+    )
+    
+    # Poll for approval (in real system, would use webhook/event)
+    max_wait = 24 * 3600  # 24 hours
+    interval = 60  # check every minute
+    elapsed = 0
+    
+    while elapsed < max_wait:
+        approval = get_approval_status(approval_id)
+        if approval.status != "pending":
+            return approval.status == "approved"
+        await asyncio.sleep(interval)
+        elapsed += interval
+    
+    return False  # Timeout
+
+@task(name="Save Architecture")
+def save_architecture(project_id: str, architecture: Dict):
+    """Persist approved architecture"""
+    # Save to database
+    pass
+
+@flow(
+    name="Generate Architecture",
+    task_runner=ConcurrentTaskRunner(),
+    retries=1,
+    retry_delay_seconds=60
+)
+async def generate_architecture_workflow(
+    project_id: str,
+    architect_agent,
+    reviewer_agent
+) -> Dict:
+    """Complete workflow for architecture generation"""
+    
+    # Step 1: Gather input
+    requirements = await gather_requirements(project_id)
+    
+    # Step 2: Generate
+    architecture = await generate_base_architecture(
+        requirements, 
+        architect_agent
+    )
+    
+    # Step 3 & 4: Validate and analyze (parallel)
+    validation, complexity = await asyncio.gather(
+        validate_dependencies(architecture),
+        calculate_complexity(architecture)
+    )
+    
+    # Step 5: AI Review
+    review = await review_architecture(
+        architecture,
+        validation,
+        complexity,
+        reviewer_agent
+    )
+    
+    # Step 6: Human approval
+    approved = await request_human_approval(
+        project_id,
+        architecture,
+        review
+    )
+    
+    if not approved:
+        raise Exception("Architecture not approved by human reviewer")
+    
+    # Step 7: Save
+    save_architecture(project_id, architecture)
+    
+    return {
+        "status": "completed",
+        "architecture": architecture,
+        "validation": validation,
+        "complexity": complexity,
+        "review": review
+    }
+```
+
+---
+
+## 6. Performance Considerations
+
+### Caching Strategy
+
+```python
+# services/cache.py
+
+import redis
+from typing import Optional, Any
+import json
+
+class CacheService:
+    def __init__(self):
+        self.redis = redis.Redis(
+            host='localhost',
+            port=6379,
+            decode_responses=True
+        )
+    
+    def cache_tree_context(
+        self, 
+        project_id: str, 
+        node_id: str, 
+        context: str,
+        ttl: int = 3600
+    ):
+        """Cache tree context for AI"""
+        key = f"tree_context:{project_id}:{node_id}"
+        self.redis.setex(key, ttl, context)
+    
+    def get_cached_context(
+        self, 
+        project_id: str, 
+        node_id: str
+    ) -> Optional[str]:
+        """Retrieve cached context"""
+        key = f"tree_context:{project_id}:{node_id}"
+        return self.redis.get(key)
+    
+    def cache_ai_result(
+        self,
+        workflow_id: str,
+        agent_name: str,
+        result: Any,
+        ttl: int = 7200
+    ):
+        """Cache AI agent results"""
+        key = f"ai_result:{workflow_id}:{agent_name}"
+        self.redis.setex(key, ttl, json.dumps(result))
+    
+    def invalidate_project_cache(self, project_id: str):
+        """Invalidate all caches for project"""
+        pattern = f"*:{project_id}:*"
+        keys = self.redis.keys(pattern)
+        if keys:
+            self.redis.delete(*keys)
+```
+
+### Database Query Optimization
+
+```python
+# Eager loading for tree structures
+from sqlalchemy.orm import joinedload
+
+def get_architecture_with_deps(project_id: str):
+    return db.query(ArchitectureModule)\
+        .options(
+            joinedload(ArchitectureModule.dependencies),
+            joinedload(ArchitectureModule.tree_node)
+        )\
+        .filter(ArchitectureModule.project_id == project_id)\
+        .all()
+
+# Pagination for large lists
+def get_opportunities_paginated(
+    project_id: str, 
+    page: int = 1, 
+    page_size: int = 20
+):
+    offset = (page - 1) * page_size
+    return db.query(Opportunity)\
+        .filter(Opportunity.project_id == project_id)\
+        .order_by(Opportunity.score.desc())\
+        .offset(offset)\
+        .limit(page_size)\
+        .all()
+```
+
+---
+
+Това е подробната техническа архитектура. Следва да създам още документи за workflow дефиниции и frontend спецификации.