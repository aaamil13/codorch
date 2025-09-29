# Module 4: Architecture Designer - Implementation Plan

**Status**: 🚧 **IN PLANNING**  
**Start Date**: 30 септември 2025  
**Priority**: HIGH  
**Complexity**: ★★★★★ (Най-сложен модул)

---

## 📋 Overview

Module 4 е **Architecture Designer** - AI-powered система за генериране и визуално редактиране на софтуерна архитектура. Това е най-сложният и най-важен модул, който трансформира Goals и Opportunities в конкретна архитектура.

### Key Features
- 🤖 AI генериране на първоначална архитектура
- 🎨 Drag & Drop визуален редактор (Vue Flow)
- 🔗 Dependency management (connectors)
- 🏗️ Наследяване и композиция
- 📦 Shared modules management
- ⚙️ Dynamic level rules
- 📊 Complexity analysis
- 💥 Impact analysis при промени

---

## 🎯 Core Functionality

### 1. AI Architecture Generation
**Цел**: Автоматично генериране на архитектурно дърво от goals и opportunities

**Workflow**:
```
1. User selects goals/opportunities
2. AI Architect analyzes requirements
3. Proposes modular architecture tree
4. Dependency Expert validates dependencies
5. Complexity Analyzer assesses complexity
6. Architecture Reviewer reviews proposal
7. User reviews and edits visually
8. Save to RefMemTree
```

### 2. Visual Architecture Editor
**Цел**: Интерактивен canvas за редактиране на архитектура

**Features**:
- Drag & Drop nodes (modules/components)
- Visual connections (dependencies)
- Inheritance lines
- Shared modules indicators
- Real-time validation
- Undo/Redo support

### 3. Dependency Management
**Цел**: Управление на зависимости между модули

**Types**:
- `import` - Директен import
- `extends` - Наследяване
- `uses` - Използва (loose coupling)
- `implements` - Имплементация на интерфейс
- `depends_on` - Обща зависимост

**Validation**:
- Circular dependency detection
- Valid dependency types
- Level constraints (low-level can't depend on high-level)

### 4. Rules Engine
**Цел**: Дефиниране и прилагане на архитектурни правила

**Levels**:
- **Global**: Важи за целия проект
- **Module**: Важи за конкретен модул
- **Component**: Важи за компонент

**Rule Types**:
- Naming conventions
- Dependency restrictions
- Layer constraints
- Technology requirements
- Security policies

### 5. Complexity Analysis
**Цел**: Оценка на сложността на архитектурата

**Metrics**:
- Module count
- Average dependencies per module
- Cyclomatic complexity
- Depth of inheritance
- Shared module coupling

### 6. Impact Analysis
**Цел**: Анализ на влиянието при промени

**Analysis**:
- Which modules are affected
- Cascade effects
- Breaking changes
- Testing scope

---

## 🗄️ Database Models

### ArchitectureModule
```python
class ArchitectureModule(Base):
    id: UUID
    project_id: UUID (FK)
    parent_id: UUID (FK, nullable) # Tree structure
    tree_node_id: UUID (FK, nullable) # RefMemTree link
    
    # Module info
    name: str
    description: str
    module_type: str  # package, class, interface, service, etc.
    level: int  # Depth in tree (0 = root)
    
    # Visual positioning (for canvas)
    position_x: int
    position_y: int
    
    # AI generation
    ai_generated: bool
    generation_reasoning: dict
    
    # Status
    status: str  # draft, approved, implemented
    approved_at: datetime
    approved_by: UUID (FK User)
    
    # Metadata
    metadata: dict  # Technologies, patterns, notes
    created_at: datetime
    updated_at: datetime
```

### ModuleDependency
```python
class ModuleDependency(Base):
    id: UUID
    project_id: UUID (FK)
    from_module_id: UUID (FK ArchitectureModule)
    to_module_id: UUID (FK ArchitectureModule)
    
    dependency_type: str  # import, extends, uses, implements, depends_on
    description: str
    
    # Metadata
    metadata: dict  # Specific dependency config
    created_at: datetime
```

### ArchitectureRule
```python
class ArchitectureRule(Base):
    id: UUID
    project_id: UUID (FK)
    module_id: UUID (FK, nullable)  # null = global rule
    
    level: str  # global, module, component
    rule_type: str  # naming, dependency, layer, tech, security
    rule_definition: dict  # Rule specification
    
    ai_generated: bool
    active: bool
    
    created_at: datetime
    updated_at: datetime
```

---

## 🤖 AI Agents (4 agents)

### 1. SoftwareArchitectAgent
**Role**: Главен архитект - генерира архитектурни решения

**Responsibilities**:
- Analyze goals and opportunities
- Propose modular architecture
- Suggest design patterns
- Define module boundaries
- Choose architectural styles (layered, microservices, etc.)

**Input**:
- Goals list
- Opportunities list
- Project context
- Technology constraints

**Output**:
```python
{
    "modules": [
        {
            "name": "UserService",
            "type": "service",
            "description": "...",
            "level": 1,
            "technologies": ["Python", "FastAPI"],
            "patterns": ["Repository", "Service Layer"]
        }
    ],
    "dependencies": [
        {
            "from": "UserService",
            "to": "DatabaseLayer",
            "type": "uses"
        }
    ],
    "reasoning": "...",
    "architectural_style": "Layered Architecture"
}
```

### 2. DependencyExpertAgent
**Role**: Експерт по зависимости - валидира и оптимизира

**Responsibilities**:
- Validate dependencies
- Detect circular dependencies
- Suggest dependency injection
- Optimize coupling
- Enforce dependency rules

**Input**:
- Proposed architecture
- Dependencies list

**Output**:
```python
{
    "validation_result": "pass/fail",
    "issues": [
        {
            "type": "circular_dependency",
            "modules": ["A", "B", "C"],
            "severity": "critical"
        }
    ],
    "suggestions": [
        "Use dependency injection for loose coupling",
        "Introduce interface to break circular dependency"
    ]
}
```

### 3. ComplexityAnalyzerAgent
**Role**: Анализатор на сложност

**Responsibilities**:
- Calculate complexity metrics
- Assess maintainability
- Identify hotspots
- Suggest simplifications
- Score architecture quality

**Input**:
- Architecture structure
- Module details

**Output**:
```python
{
    "overall_complexity": 7.5,
    "metrics": {
        "module_count": 25,
        "avg_dependencies": 3.2,
        "max_depth": 4,
        "cyclomatic_complexity": 42
    },
    "hotspots": [
        {
            "module": "CoreEngine",
            "complexity": 9.2,
            "reason": "Too many dependencies"
        }
    ],
    "suggestions": [
        "Split CoreEngine into smaller modules",
        "Reduce coupling in DataLayer"
    ]
}
```

### 4. ArchitectureReviewerAgent
**Role**: Reviewer - финален преглед и препоръки

**Responsibilities**:
- Review entire architecture
- Check best practices
- Validate scalability
- Assess security
- Provide final recommendations

**Input**:
- Complete architecture
- Validation results
- Complexity analysis

**Output**:
```python
{
    "approval_status": "approved_with_changes",
    "strengths": [
        "Good separation of concerns",
        "Clean layering"
    ],
    "weaknesses": [
        "Missing API gateway",
        "No caching layer"
    ],
    "recommendations": [
        "Add API Gateway for external access",
        "Introduce Redis for caching",
        "Consider event-driven architecture for scaling"
    ],
    "overall_score": 8.2
}
```

---

## 📡 API Endpoints (15 endpoints)

### Architecture Generation
```
POST   /api/v1/projects/{project_id}/architecture/generate
```
**Body**: 
```json
{
    "goal_ids": ["uuid1", "uuid2"],
    "opportunity_ids": ["uuid3"],
    "architectural_style": "layered",  // optional
    "preferences": {
        "microservices": false,
        "max_depth": 4
    }
}
```

### Module CRUD
```
POST   /api/v1/architecture/modules
GET    /api/v1/projects/{project_id}/architecture
GET    /api/v1/architecture/modules/{id}
PUT    /api/v1/architecture/modules/{id}
DELETE /api/v1/architecture/modules/{id}
PUT    /api/v1/architecture/modules/{id}/position  # Update canvas position
POST   /api/v1/architecture/modules/{id}/approve
```

### Dependency Management
```
POST   /api/v1/architecture/dependencies
DELETE /api/v1/architecture/dependencies/{id}
GET    /api/v1/projects/{project_id}/architecture/validate  # Validate all dependencies
```

### Rules Management
```
POST   /api/v1/architecture/rules
GET    /api/v1/projects/{project_id}/architecture/rules
PUT    /api/v1/architecture/rules/{id}
DELETE /api/v1/architecture/rules/{id}
```

### Analysis
```
GET    /api/v1/projects/{project_id}/architecture/complexity
POST   /api/v1/projects/{project_id}/architecture/impact-analysis
```
**Impact Analysis Body**:
```json
{
    "module_id": "uuid",
    "change_type": "modify"  // modify, delete, add
}
```

### Shared Modules
```
GET    /api/v1/projects/{project_id}/architecture/shared-modules
```

---

## 🎨 Frontend Components

### Pages
1. **ArchitecturePage.vue** - Main page with canvas
2. **ArchitectureGeneratorDialog.vue** - AI generation dialog

### Core Components
3. **ArchitectureCanvas.vue** - Vue Flow canvas (main editor)
4. **ModuleNode.vue** - Individual module node
5. **DependencyEdge.vue** - Connection line between modules
6. **ModuleDetailsPanel.vue** - Side panel for editing module details

### Feature Components
7. **ArchitectureToolbar.vue** - Toolbar (add node, zoom, etc.)
8. **DependencyEditor.vue** - Dialog for editing dependencies
9. **RulesPanel.vue** - Rules management panel
10. **ComplexityDashboard.vue** - Metrics and complexity visualization
11. **ImpactAnalysisDialog.vue** - Impact analysis results
12. **SharedModulesPanel.vue** - Shared modules management

---

## 🔄 Implementation Phases

### Phase 1: Backend Core (Tasks 1-5)
**Goal**: Database models, repositories, service layer

1. ✅ Create database models (ArchitectureModule, ModuleDependency, ArchitectureRule)
2. ✅ Alembic migration
3. ✅ Repository pattern (3 repos)
4. ✅ Service layer (ArchitectureService)
5. ✅ Basic validation logic

### Phase 2: AI Agents (Tasks 6-9)
**Goal**: 4 AI agents for architecture generation

6. ✅ SoftwareArchitectAgent
7. ✅ DependencyExpertAgent
8. ✅ ComplexityAnalyzerAgent
9. ✅ ArchitectureReviewerAgent
10. ✅ ArchitectureTeam (coordinator)

### Phase 3: API Endpoints (Tasks 11-12)
**Goal**: REST API for all operations

11. ✅ Module CRUD endpoints
12. ✅ Dependency management endpoints
13. ✅ Rules endpoints
14. ✅ Analysis endpoints (complexity, impact)
15. ✅ Generation endpoint

### Phase 4: Frontend Foundation (Tasks 16-19)
**Goal**: TypeScript types, API service, Pinia store

16. ✅ TypeScript interfaces
17. ✅ API service
18. ✅ Pinia store
19. ✅ Router integration

### Phase 5: Visual Editor (Tasks 20-24)
**Goal**: Vue Flow canvas with drag & drop

20. ✅ Install & configure Vue Flow
21. ✅ ArchitectureCanvas component
22. ✅ ModuleNode component
23. ✅ DependencyEdge component
24. ✅ Drag & drop functionality

### Phase 6: Feature Components (Tasks 25-30)
**Goal**: All UI features

25. ✅ ArchitectureToolbar
26. ✅ ModuleDetailsPanel
27. ✅ DependencyEditor
28. ✅ RulesPanel
29. ✅ ComplexityDashboard
30. ✅ ImpactAnalysisDialog

### Phase 7: Testing & Integration (Tasks 31-32)
**Goal**: Tests and integration

31. ✅ Backend tests (Repository, Service, API)
32. ✅ Integration testing

---

## 📊 Success Criteria

### Must Have ✅
- [ ] AI architecture generation from goals/opportunities
- [ ] Visual canvas with drag & drop
- [ ] Module CRUD operations
- [ ] Dependency management with validation
- [ ] Circular dependency detection
- [ ] Basic complexity metrics
- [ ] Save to RefMemTree

### Should Have 📋
- [ ] Rules engine
- [ ] Impact analysis
- [ ] Shared modules management
- [ ] Undo/Redo
- [ ] Export to diagram (PNG/SVG)

### Nice to Have 🌟
- [ ] Multiple architectural styles
- [ ] Architecture templates
- [ ] Collaborative editing
- [ ] Version history
- [ ] Auto-layout algorithms

---

## 🚧 Technical Challenges

### 1. Vue Flow Integration
- **Challenge**: Complex graph editor with custom nodes
- **Solution**: Use Vue Flow library, customize nodes and edges

### 2. Circular Dependency Detection
- **Challenge**: Efficient graph traversal
- **Solution**: DFS/BFS algorithm, cache results

### 3. Real-time Validation
- **Challenge**: Validate on every change
- **Solution**: Debounced validation, background workers

### 4. Large Architectures
- **Challenge**: Performance with 100+ modules
- **Solution**: Virtual scrolling, lazy loading, canvas optimization

### 5. AI Coordination
- **Challenge**: 4 agents working together
- **Solution**: Supervisor pattern, sequential workflow

---

## 📚 Dependencies

### Backend
- Existing: FastAPI, SQLAlchemy, Pydantic AI, RefMemTree
- New: `networkx` (graph algorithms for dependency analysis)

### Frontend
- Existing: Vue 3, Quasar, Pinia, TypeScript
- New: 
  - `@vue-flow/core` - Flow diagram library
  - `@vue-flow/controls` - Zoom, pan controls
  - `@vue-flow/background` - Grid background
  - `d3` (optional) - Advanced visualizations

---

## 🎯 Next Steps

1. Create database models and migration
2. Implement repository pattern
3. Create service layer with validation
4. Build 4 AI agents
5. Create API endpoints
6. Frontend types and store
7. Vue Flow canvas setup
8. Build UI components
9. Integration & testing

---

**Estimated Time**: 2-3 дни интензивна разработка  
**Priority**: HIGH - Foundation за Requirements и Code Generation  
**Risk**: HIGH - Най-сложен модул, критичен за проекта

Ready to start! 🚀
