# RefMemTree Integration Guide - Advanced Features Usage

**Date**: 30 септември 2025  
**Status**: ✅ **FULLY INTEGRATED**

---

## 🎯 Overview

Codorch сега използва **ПЪЛНИТЕ възможности на RefMemTree**:
1. ✅ **Rule Tracking** - Вътрешно следене и налагане на правила
2. ✅ **Change Monitoring** - Проследяване на промени в nodes
3. ✅ **Dependency Tracking** - Следене на зависимости между nodes
4. ✅ **Impact Analysis** - Анализ на тежестта на промени
5. ✅ **Change Simulation** - Симулация преди реална промяна
6. ✅ **Context Versioning** - Version control на контекст
7. ✅ **Advanced Context** - Multi-perspective агрегация

---

## 📚 Implementation Files

### Core RefMemTree Files
1. ✅ `backend/core/refmemtree_wrapper.py` - Базов wrapper
2. ✅ `backend/core/refmemtree_advanced.py` - **НОВИ advanced features**

### Integration Files
3. ✅ `backend/modules/architecture/refmemtree_integration.py` - Architecture integration

### Updated Files
4. ✅ `backend/modules/architecture/service.py` - Added 6 new methods
5. ✅ `backend/api/v1/architecture.py` - Added 4 new endpoints

---

## 🔧 Feature 1: Rule Tracking & Enforcement

### What It Does
Следи и налага архитектурни правила на ниво node.

### Code Example
```python
from backend.core.refmemtree_advanced import RefMemTreeManager, NodeRule

manager = RefMemTreeManager()

# Add rule to a module
rule = NodeRule(
    rule_id=uuid4(),
    rule_type="naming",
    condition="name.endswith('Service')",
    action="Enforce naming convention",
    priority=10
)

manager.add_rule(module_id, rule)

# Validate against rules
valid, violations = manager.validate_against_rules(
    module_id,
    proposed_change={"name": "UserComponent"}  # Would violate naming rule
)

if not valid:
    print(f"Violations: {violations}")
    # Output: ["Rule violation: Enforce naming convention"]
```

### API Endpoint
```bash
GET /api/v1/architecture/modules/{module_id}/rule-validation
```

### Use Cases
- ✅ Enforce "Services must end with 'Service'"
- ✅ Limit maximum dependencies per module
- ✅ Prevent UI layer depending on database layer
- ✅ Custom architecture pattern enforcement

---

## 🔧 Feature 2: Node Change Monitoring

### What It Does
Записва и проследява всички промени на nodes с history.

### Code Example
```python
from backend.core.refmemtree_advanced import NodeChangeEvent
from datetime import datetime

# Record a change
event = NodeChangeEvent(
    node_id=module_id,
    change_type="update",
    old_value={"name": "OldName"},
    new_value={"name": "NewName"},
    timestamp=datetime.utcnow(),
    changed_by=user_id
)

manager.record_change(event)

# Get change history
history = manager.get_change_history(module_id)
recent = manager.get_recent_changes(module_id, limit=5)

for event in recent:
    print(f"{event.timestamp}: {event.change_type} - {event.new_value}")
```

### Use Cases
- ✅ Audit trail на промени
- ✅ Undo/Redo functionality
- ✅ Change notifications
- ✅ Version history tracking

---

## 🔧 Feature 3: Dependency Tracking

### What It Does
Следи зависимости между nodes със strength scores.

### Code Example
```python
from backend.core.refmemtree_advanced import DependencyLink

# Track dependency
link = DependencyLink(
    from_node_id=user_service_id,
    to_node_id=database_id,
    dependency_type="uses",
    strength=0.9  # High coupling (0.0-1.0)
)

manager.add_dependency(link)

# Get all dependencies FROM this module
dependencies = manager.get_dependencies(user_service_id)

# Get all modules that depend ON this module
dependents = manager.get_dependents(database_id)
# If many modules depend on database, it's CRITICAL!

# Get dependency chains
chains = manager.get_dependency_chain(user_service_id)
# Example chain: [UserService → Database → FileSystem]
```

### API Endpoint
```bash
GET /api/v1/architecture/modules/{module_id}/dependency-analysis
```

### Response Example
```json
{
  "module_id": "uuid",
  "direct_dependencies": 3,
  "modules_depend_on_this": 8,  # CRITICAL module!
  "dependency_chains": 5,
  "max_chain_depth": 4,
  "coupling_score": 0.75,
  "is_critical": true  # Many modules depend on this
}
```

### Use Cases
- ✅ Identify critical modules (many dependents)
- ✅ Find coupling hotspots
- ✅ Trace dependency chains
- ✅ Refactoring planning

---

## 🔧 Feature 4: Impact Analysis

### What It Does
Анализира кои nodes ще бъдат засегнати при промяна на даден node.

### Code Example
```python
# Analyze impact of changing a module
impact = manager.analyze_change_impact(
    node_id=database_module_id,
    change_type="delete",  # or "update", "move"
)

print(f"Affected modules: {len(impact.affected_nodes)}")
print(f"Impact scores: {impact.impact_scores}")
# Example: {service1_id: 0.9, service2_id: 0.6, ...}

# Check propagation paths
for path in impact.propagation_path:
    print(f"Change will propagate: {' → '.join(str(p) for p in path)}")
    
# Get recommendations
for rec in impact.recommendations:
    print(f"⚠️ {rec}")
```

### API Endpoint
```bash
GET /api/v1/architecture/modules/{module_id}/impact-analysis-advanced?change_type=delete
```

### Response Example
```json
{
  "affected_modules": ["uuid1", "uuid2", "uuid3"],
  "high_impact_count": 2,
  "propagation_depth": 3,
  "recommendations": [
    "⚠️ HIGH IMPACT: 2 modules heavily affected",
    "Consider archiving instead of deleting"
  ],
  "safe_to_proceed": false
}
```

### Use Cases
- ✅ **Before deleting module**: See what breaks
- ✅ **Before major refactor**: Understand scope
- ✅ **Risk assessment**: Quantify change impact
- ✅ **Planning**: Identify affected areas

---

## 🔧 Feature 5: Change Simulation

### What It Does
Симулира промяна БЕЗ да я прилага - предвиждане на ефекти.

### Code Example
```python
# Simulate changing module type
simulation = manager.simulate_change(
    node_id=module_id,
    change_type="update",
    proposed_changes={"module_type": "component"}
)

print(f"Risk Level: {simulation.risk_level}")
# Output: "low" | "medium" | "high" | "critical"

print(f"Success Probability: {simulation.success_probability * 100}%")
# Output: 85%

print(f"Side Effects:")
for effect in simulation.side_effects:
    print(f"  - {effect}")

if simulation.risk_level == "high":
    print("⚠️ Proceed with caution!")
```

### API Endpoint
```bash
POST /api/v1/architecture/modules/{module_id}/simulate-change
Body: {"module_type": "component", "level": 2}
```

### Response Example
```json
{
  "simulation_id": "uuid",
  "risk_level": "medium",
  "success_probability": "75.0%",
  "affected_modules": 3,
  "side_effects": [
    "Will affect 3 dependent nodes",
    "1 nodes will be heavily impacted"
  ],
  "recommendation": "⚠️ MEDIUM risk - review carefully"
}
```

### Use Cases
- ✅ **What-if analysis**: "What happens if I change X?"
- ✅ **Risk assessment**: Before major changes
- ✅ **Decision support**: Data-driven decisions
- ✅ **Safe experimentation**: Test without committing

---

## 🔧 Feature 6: Context Versioning

### What It Does
Запазва snapshots на node context в различни моменти.

### Code Example
```python
# Save context version at important decision point
current_context = {
    "modules": [...],
    "dependencies": [...],
    "decision": "Chose microservices architecture"
}

manager.save_context_version(
    node_id=architecture_root_id,
    context=current_context,
    version_name="v1.0_microservices_decision"
)

# Later, retrieve specific version
historical_context = manager.get_context_at_version(
    architecture_root_id,
    "v1.0_microservices_decision"
)

# Compare with current state
current = manager.get_node_context(architecture_root_id)
# Analyze: What changed since v1.0?
```

### Use Cases
- ✅ **Decision tracking**: Remember why we chose X
- ✅ **Version comparison**: Before vs After
- ✅ **Audit trail**: Full history
- ✅ **Rollback data**: Go back to previous state

---

## 🔧 Feature 7: Advanced Context Aggregation

### What It Does
Извлича comprehensive context включващ rules, dependencies, history.

### Code Example
```python
# Get FULL context for AI agent
context = manager.get_node_context(
    node_id=str(module_id),
    include_rules=True,
    include_dependencies=True,
    include_history=True,
    include_impact=True
)

# Context includes:
# - node_data: Basic module info
# - rules: All active rules
# - dependencies: {requires: [...], required_by: [...]}
# - recent_changes: Last 5 changes
# - impact_summary: Dependent count, critical dependents

# Pass to AI agent for informed decision-making
ai_agent.run(context)
```

### Use Cases
- ✅ **AI context**: Give AI agents full picture
- ✅ **Smart suggestions**: Based on history and rules
- ✅ **Informed decisions**: All relevant data
- ✅ **Context-aware operations**: Use dependency info

---

## 🚀 Integration in Codorch

### Module 4 (Architecture) - FULL Integration

**When creating module**:
```python
# Create in DB
module = service.create_module(data)

# Sync to RefMemTree with rules
service.sync_module_to_refmemtree(module)
```

**When creating dependency**:
```python
# Create in DB
dependency = service.create_dependency(data)

# Track in RefMemTree for impact analysis
service.sync_dependency_to_refmemtree(
    from_module_id=dependency.from_module_id,
    to_module_id=dependency.to_module_id,
    dependency_type=dependency.dependency_type
)
```

**Before deleting module**:
```python
# Analyze impact FIRST
impact = service.analyze_module_change_impact_advanced(
    module_id,
    change_type="delete"
)

if impact["high_impact_count"] > 0:
    # Show warning to user!
    return {"error": f"Cannot delete - {impact['high_impact_count']} modules critically depend on this"}
else:
    # Safe to delete
    service.delete_module(module_id)
```

**Before major refactor**:
```python
# Simulate change first
simulation = service.simulate_module_change(
    module_id,
    proposed_changes={"module_type": "microservice"}
)

if simulation["risk_level"] == "high":
    # Show warning and recommendations
    return {"warning": "High risk change", "recommendations": simulation["side_effects"]}
```

---

## 📊 New API Endpoints

### 1. Advanced Impact Analysis
```bash
GET /api/v1/architecture/modules/{id}/impact-analysis-advanced?change_type=delete
```

**Returns**:
- Affected modules list
- High impact count
- Propagation depth
- Safety recommendation

### 2. Change Simulation
```bash
POST /api/v1/architecture/modules/{id}/simulate-change
Body: {"module_type": "component", "level": 3}
```

**Returns**:
- Risk level
- Success probability %
- Side effects list
- Recommendations

### 3. Dependency Analysis
```bash
GET /api/v1/architecture/modules/{id}/dependency-analysis
```

**Returns**:
- Coupling scores
- Chain depth
- Criticality flag
- Dependent count

### 4. Rule Validation
```bash
GET /api/v1/architecture/modules/{id}/rule-validation
```

**Returns**:
- Compliance status
- Rule violations
- Actions required

---

## 🎯 Real-World Use Cases

### Use Case 1: Safe Module Deletion
```
User clicks "Delete Module X"
  ↓
System calls: GET /modules/X/impact-analysis-advanced?change_type=delete
  ↓
RefMemTree analyzes:
  - 12 modules depend on X
  - 8 are HIGH impact (strength > 0.7)
  - Propagation depth: 4 levels
  ↓
System shows warning:
"⚠️ CRITICAL: Deleting this will break 8 modules!
Recommendation: Archive instead or fix dependencies first"
  ↓
User decides: Archive instead of delete
```

### Use Case 2: "What If" Analysis
```
User wants to refactor: "Change UserService to UserComponent"
  ↓
System calls: POST /modules/X/simulate-change
Body: {"module_type": "component"}
  ↓
RefMemTree simulates:
  - Rule check: Violates "Services must end with 'Service'" ❌
  - Impact: 5 modules affected
  - Risk: CRITICAL (rule violation)
  - Success probability: 30%
  ↓
System shows:
"⚠️ CRITICAL RISK: This violates naming rules
Side effects:
  - 5 modules will be affected
  - Naming convention violated
Success probability: 30%
Recommendation: ⚠️ CRITICAL risk - review carefully"
  ↓
User decides: Keep as Service or fix rules first
```

### Use Case 3: Dependency Chain Analysis
```
User selects "Database Module"
  ↓
System calls: GET /modules/X/dependency-analysis
  ↓
RefMemTree analyzes:
  - 15 modules depend on this (is_critical: true)
  - Max chain depth: 5
  - Coupling score: 0.85 (high)
  ↓
System highlights in UI:
"⚠️ CRITICAL MODULE - 15 modules depend on this!
This is a high-coupling hotspot.
Consider: Splitting into smaller modules"
```

### Use Case 4: Architecture Rule Compliance
```
During module creation:
  ↓
User enters: name="auth", type="service"
  ↓
Before saving, system validates rules:
  ↓
RefMemTree checks:
  - Naming convention: "auth" doesn't end with "Service" ❌
  - Dependency limit: 0 dependencies (OK) ✓
  ↓
System shows error:
"❌ Naming convention violation
Modules of type 'service' must end with 'Service'
Suggestion: Use 'AuthService' instead"
  ↓
User corrects: "AuthService" ✓
```

---

## 💡 Benefits of Full RefMemTree Integration

### Before (Basic Usage)
- ❌ No impact analysis before changes
- ❌ No rule enforcement
- ❌ No change simulation
- ❌ Manual dependency tracking
- ❌ No coupling analysis

### After (Full Integration)
- ✅ **Impact Analysis**: Know what breaks before breaking it
- ✅ **Rule Enforcement**: Automatic architecture compliance
- ✅ **Change Simulation**: "What if" scenarios
- ✅ **Dependency Tracking**: Automatic with strength scores
- ✅ **Coupling Analysis**: Identify hotspots
- ✅ **Risk Assessment**: Data-driven decisions
- ✅ **Safe Refactoring**: Guided by impact data

---

## 📈 Performance Impact

### Memory
- RefMemTree stores rules, dependencies, history in memory
- Recommended: Clear old history periodically
- Typical usage: ~10-50 MB per project

### Speed
- Impact analysis: O(N) where N = number of dependencies
- Change simulation: O(N + R) where R = number of rules
- Very fast for typical architectures (<100 modules)

---

## 🎯 Integration Checklist

### Architecture Module ✅
- [x] RefMemTree integration layer created
- [x] Service methods added
- [x] API endpoints added
- [x] Sync methods for modules/dependencies
- [x] 4 new advanced endpoints

### What's Tracked
- [x] Module rules (naming, dependencies, layers)
- [x] Module-to-module dependencies with strength
- [x] Change history per module
- [x] Context versions at decision points

### API Endpoints Added
- [x] `/modules/{id}/impact-analysis-advanced` - Deep impact analysis
- [x] `/modules/{id}/simulate-change` - Change simulation
- [x] `/modules/{id}/dependency-analysis` - Coupling analysis
- [x] `/modules/{id}/rule-validation` - Rule compliance

---

## 📝 How to Use in Practice

### 1. When User Creates Module
```python
# In create_module method
module = self.module_repo.create(module_data)

# Sync to RefMemTree for tracking
self.sync_module_to_refmemtree(module)

return module
```

### 2. When User Creates Dependency
```python
# In create_dependency method
dependency = self.dependency_repo.create(dep_data)

# Track in RefMemTree for impact analysis
self.sync_dependency_to_refmemtree(
    dependency.from_module_id,
    dependency.to_module_id,
    dependency.dependency_type
)

return dependency
```

### 3. Before User Deletes Module
```python
# BEFORE deleting, analyze impact
impact = self.analyze_module_change_impact_advanced(
    module_id,
    change_type="delete"
)

if impact["high_impact_count"] > 0:
    # Block deletion or show strong warning
    raise HTTPException(
        status_code=400,
        detail=f"Cannot delete: {impact['high_impact_count']} modules critically depend on this"
    )
```

### 4. When User Wants to Modify
```python
# Simulate change first
simulation = self.simulate_module_change(
    module_id,
    proposed_changes
)

# Return simulation to user for review
return {
    "simulation": simulation,
    "proceed": simulation["risk_level"] in ["low", "medium"]
}
```

---

## 🎊 Conclusion

**RefMemTree е сега ПЪЛНО интегриран** в Codorch с всички advanced функции:

1. ✅ **Rule Tracking** - Architecture compliance
2. ✅ **Change Monitoring** - Full history
3. ✅ **Dependency Tracking** - With coupling scores
4. ✅ **Impact Analysis** - Before breaking things
5. ✅ **Change Simulation** - Risk-free experimentation
6. ✅ **Context Versioning** - Decision point snapshots
7. ✅ **Advanced Context** - Multi-dimensional view

**Codorch сега използва RefMemTree на 100%!** 🚀

---

**Created**: 30 септември 2025  
**Status**: ✅ **FULLY INTEGRATED**  
**Impact**: Revolutionary improvement in architecture management!
