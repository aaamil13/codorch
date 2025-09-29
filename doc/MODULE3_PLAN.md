# Module 3: Research Engine - Implementation Plan

**Status**: 🚧 IN PROGRESS  
**Start Date**: 30 September 2025  

---

## 🎯 Module Overview

**Research Engine** е AI-powered research assistant, който:
- Провежда задълбочени изследвания на базата на контекст от RefMemTree
- Поддържа интерактивни chat сесии с AI
- Автоматично документира insights и findings
- Прави семантично търсене в историята
- Интегрира се с Goals и Opportunities

---

## 📋 Core Features

### 1. Research Sessions
- Създаване на research сесия за конкретен goal/opportunity/node
- Автоматично извличане на контекст от RefMemTree
- Session management (active, archived)
- Research history tracking

### 2. AI-Powered Chat
- Real-time chat с AI Research Team
- Context-aware responses (uses RefMemTree context)
- Multi-turn conversations
- Streaming responses (WebSocket)

### 3. Research Team (AI Agents)
- **WebResearchAgent**: Simulates web research, trends, market data
- **DomainExpertAgent**: Domain-specific knowledge and insights
- **AnalyzerAgent**: Analyzes and synthesizes information
- **SupervisorAgent**: Coordinates research workflow

### 4. Knowledge Management
- Automatic insight extraction from chat
- Finding categorization (technical, market, user, competitor)
- Source tracking and citations
- Semantic search across all research

### 5. Integration with RefMemTree
- Context aggregation from tree nodes
- Automatic node enrichment with research findings
- Parent/child context awareness
- Cross-tree semantic search

---

## 🏗️ Architecture

### Backend Structure
```
backend/
├── modules/
│   └── research/
│       ├── __init__.py
│       ├── schemas.py           # Pydantic models
│       ├── models.py            # SQLAlchemy models
│       ├── repository.py        # Data access
│       ├── service.py           # Business logic
│       ├── context_manager.py  # RefMemTree integration
│       └── websocket.py        # Real-time chat
├── ai_agents/
│   └── research_team.py        # 4 AI agents
└── api/
    └── v1/
        └── research.py         # API endpoints
```

### Frontend Structure
```
frontend/
└── src/
    ├── types/
    │   └── research.ts         # TypeScript interfaces
    ├── services/
    │   └── researchApi.ts      # API client
    ├── stores/
    │   └── research.ts         # Pinia store
    ├── components/
    │   └── research/
    │       ├── ResearchChat.vue
    │       ├── ContextPanel.vue
    │       ├── FindingCard.vue
    │       └── SessionList.vue
    └── pages/
        ├── ResearchPage.vue
        └── ResearchSessionPage.vue
```

---

## 📊 Database Models

### ResearchSession
```python
- id: UUID
- project_id: UUID (FK)
- goal_id: UUID (FK, nullable)
- opportunity_id: UUID (FK, nullable)
- tree_node_id: UUID (FK, nullable)
- title: str
- description: str
- context_summary: dict  # RefMemTree aggregated context
- status: str (active, completed, archived)
- created_by: UUID (FK User)
- created_at: datetime
- updated_at: datetime
```

### ResearchMessage
```python
- id: UUID
- session_id: UUID (FK)
- role: str (user, assistant, system)
- content: str
- metadata: dict  # agent info, tokens, etc.
- created_at: datetime
```

### ResearchFinding
```python
- id: UUID
- session_id: UUID (FK)
- finding_type: str (technical, market, user, competitor)
- title: str
- description: str
- sources: list[str]
- confidence_score: float
- relevance_score: float
- created_at: datetime
```

---

## 🔌 API Endpoints

### Sessions
```
POST   /api/v1/research/sessions               # Create session
GET    /api/v1/research/sessions               # List sessions
GET    /api/v1/research/sessions/{id}          # Get session details
PUT    /api/v1/research/sessions/{id}          # Update session
DELETE /api/v1/research/sessions/{id}          # Delete session
POST   /api/v1/research/sessions/{id}/archive  # Archive session
```

### Chat & Messages
```
POST   /api/v1/research/sessions/{id}/messages # Send message (REST)
GET    /api/v1/research/sessions/{id}/messages # Get message history
WS     /ws/research/sessions/{id}              # WebSocket for streaming
```

### Findings
```
GET    /api/v1/research/sessions/{id}/findings # Get all findings
POST   /api/v1/research/sessions/{id}/findings # Create finding
PUT    /api/v1/research/findings/{id}          # Update finding
DELETE /api/v1/research/findings/{id}          # Delete finding
```

### Context & Search
```
GET    /api/v1/research/context/{node_id}      # Get RefMemTree context
POST   /api/v1/research/search                 # Semantic search
```

---

## 🤖 AI Agents Design

### 1. WebResearchAgent
**Роля**: Симулира web research и търсене на актуална информация  
**Модел**: Gemini 2.5 Flash  
**Задачи**:
- Market trends analysis
- Competitor research
- Technology landscape
- Industry insights

### 2. DomainExpertAgent
**Роля**: Предоставя domain-specific експертиза  
**Модел**: Gemini 2.5 Pro  
**Задачи**:
- Technical feasibility analysis
- Architecture recommendations
- Best practices
- Risk assessment

### 3. AnalyzerAgent
**Роля**: Анализира и синтезира информация  
**Модел**: Gemini 2.5 Pro  
**Задачи**:
- Data synthesis
- Pattern recognition
- Insight extraction
- Recommendation generation

### 4. SupervisorAgent
**Роля**: Координира research workflow  
**Модел**: Gemini 2.5 Pro  
**Задачи**:
- Query routing to appropriate agents
- Response aggregation
- Quality control
- Context management

---

## 🎨 Frontend Components

### 1. ResearchPage.vue
- Main research dashboard
- Session list
- Create new session button
- Recent findings

### 2. ResearchSessionPage.vue
- Active research session view
- Chat interface
- Context panel (sidebar)
- Findings list

### 3. ResearchChat.vue
- Message history
- Input field
- Streaming responses
- Agent indicators

### 4. ContextPanel.vue
- Shows active context from RefMemTree
- Goal/Opportunity details
- Parent/sibling context
- Relevant metrics

### 5. FindingCard.vue
- Finding display card
- Type badge (technical/market/user/competitor)
- Confidence & relevance scores
- Sources
- Actions (edit, delete, export)

### 6. SessionList.vue
- List of research sessions
- Filters (status, date)
- Search
- Quick actions

---

## 🔗 Integration Points

### With RefMemTree
- Context aggregation for sessions
- Automatic node enrichment with findings
- Semantic search across tree

### With Goals (Module 1)
- Start research from goal
- Link findings to goals
- Goal-specific context

### With Opportunities (Module 2)
- Start research from opportunity
- Market/technical research for opportunities
- Validation insights

### With Projects
- Project-level research sessions
- Cross-session insights
- Project knowledge base

---

## ✅ Implementation Phases

### Phase 1: Backend Core (Priority 1)
- [ ] Database models (ResearchSession, ResearchMessage, ResearchFinding)
- [ ] Pydantic schemas
- [ ] Repository pattern
- [ ] Basic service layer
- [ ] Database migration

### Phase 2: AI Agents (Priority 1)
- [ ] WebResearchAgent implementation
- [ ] DomainExpertAgent implementation
- [ ] AnalyzerAgent implementation
- [ ] SupervisorAgent implementation
- [ ] Agent coordination logic

### Phase 3: API & WebSocket (Priority 1)
- [ ] REST API endpoints (sessions, messages, findings)
- [ ] WebSocket endpoint for streaming
- [ ] Context manager (RefMemTree integration)
- [ ] Semantic search implementation

### Phase 4: Testing (Priority 1)
- [ ] Unit tests (services, agents)
- [ ] Integration tests (API)
- [ ] WebSocket tests
- [ ] End-to-end tests

### Phase 5: Frontend Core (Priority 2)
- [ ] TypeScript types
- [ ] API service (Axios + WebSocket)
- [ ] Pinia store
- [ ] ResearchChat component
- [ ] ContextPanel component

### Phase 6: Frontend Pages (Priority 2)
- [ ] ResearchPage
- [ ] ResearchSessionPage
- [ ] FindingCard component
- [ ] SessionList component
- [ ] Routing and navigation

### Phase 7: Polish & Optimization (Priority 3)
- [ ] Streaming UI polish
- [ ] Loading states
- [ ] Error handling
- [ ] Performance optimization
- [ ] UI/UX refinements

---

## 🧪 Testing Strategy

### Backend Tests
```python
# test_research.py
- test_create_session
- test_send_message
- test_agent_response
- test_extract_findings
- test_semantic_search
- test_context_aggregation
```

### Frontend Tests
```typescript
// research.spec.ts
- test_session_creation
- test_chat_interface
- test_message_streaming
- test_finding_display
- test_context_panel
```

---

## 📈 Success Metrics

### Functional
- ✅ Create research sessions
- ✅ Real-time AI chat
- ✅ Context-aware responses
- ✅ Automatic finding extraction
- ✅ Semantic search

### Performance
- Session creation: <200ms
- AI response time: 3-8s
- Streaming latency: <500ms
- Search query: <1s

### Quality
- Response relevance: >85%
- Finding accuracy: >80%
- Context utilization: >90%
- User satisfaction: >8/10

---

## 🚀 Implementation Order

1. **Start**: Database models & migrations
2. **Then**: AI Agents (core intelligence)
3. **Then**: API endpoints (REST + WebSocket)
4. **Then**: Backend tests
5. **Then**: Frontend types & services
6. **Then**: Frontend components
7. **Then**: Integration testing
8. **Finally**: Polish & optimization

---

## 📝 Notes

- WebSocket е критичен за streaming responses
- RefMemTree context aggregation е ключов за качество
- AI agents трябва да работят координирано
- Semantic search ще използва embedding models
- Frontend трябва да handle streaming gracefully

---

**Ready to start!** 🚀

Next steps:
1. Create database models
2. Create Alembic migration
3. Implement AI agents
4. Build API endpoints
5. Add tests
6. Build frontend

Let's go! 💪
