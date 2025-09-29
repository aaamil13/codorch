diff --git a/REFMEMTREE_USE_CASES.md b/REFMEMTREE_USE_CASES.md
--- a/REFMEMTREE_USE_CASES.md
+++ b/REFMEMTREE_USE_CASES.md
@@ -0,0 +1,724 @@
+# RefMemTree Use Cases - Практически Сценарии
+
+Този документ показва как RefMemTree възможностите решават реални проблеми в нашата система.
+
+---
+
+## 🎯 Use Case 1: Генериране на Възможности с Пълен Контекст
+
+### Проблем
+Когато AI генерира бизнес възможности, трябва да разбира:
+- Основната цел на проекта
+- Constraints и ограничения
+- Вече генерирани възможности (да не се повтаря)
+- Индустрия и пазарен контекст
+- Успешни минали проекти
+
+Без RefMemTree: Ръчно трябва да съберем всички тези данни и да ги подадем на AI.
+
+### Решение с RefMemTree
+
+```python
+async def generate_opportunities_smart(project_id: str, goal_node_id: str):
+    tree = AdvancedProjectTree(project_id)
+    
+    # 1. MULTI-PERSPECTIVE CONTEXT
+    # RefMemTree автоматично събира контекст от множество перспективи
+    perspectives = tree.get_multi_perspective_context(goal_node_id)
+    
+    context_for_ai = f"""
+    === YOUR MISSION ===
+    Generate innovative business opportunities for this goal.
+    
+    {perspectives['bottom_up']}  # Goal hierarchy (where we're going)
+    {perspectives['horizontal']}  # Related goals (what else we're considering)
+    {perspectives['semantic']}    # Similar successful projects
+    """
+    
+    # 2. SEMANTIC SEARCH FOR INSPIRATION
+    # Намираме подобни успешни възможности от минали проекти
+    similar_successes = tree.semantic_search(
+        query=tree.get_node(goal_node_id).data['title'],
+        node_types=["opportunity"],
+        filters={"status": "approved", "outcome": "success"},
+        top_k=3
+    )
+    
+    context_for_ai += "\n=== INSPIRATION FROM PAST SUCCESSES ===\n"
+    for success in similar_successes:
+        context_for_ai += f"- {success['title']}: {success['outcome']}\n"
+    
+    # 3. EXISTING OPPORTUNITIES (избягваме дублиране)
+    existing = tree.get_node(goal_node_id).children
+    context_for_ai += f"\n=== AVOID DUPLICATING ===\n"
+    for opp in existing:
+        context_for_ai += f"- {opp.data['title']}\n"
+    
+    # 4. GENERATE with full context
+    opportunities = await opportunity_team.generate(context_for_ai)
+    
+    # 5. CREATE NODES with automatic context inheritance
+    for opp in opportunities:
+        opp_node = tree.create_node(
+            parent_id=goal_node_id,
+            node_type="opportunity",
+            data=opp
+        )
+        # RefMemTree автоматично:
+        # - Наследява контекст от goal
+        # - Поддържа link към parent
+        # - Индексира за semantic search
+    
+    return opportunities
+```
+
+### Какво печелим с RefMemTree:
+✅ Автоматична контекстна агрегация  
+✅ Semantic search в исторически данни  
+✅ Избягване на дублиране  
+✅ Контекстно наследяване  
+✅ Не забравяме защо генерирахме тази възможност  
+
+---
+
+## 🏗️ Use Case 2: Експериментиране с Архитектурни Подходи
+
+### Проблем
+Искаме да пробваме 3 различни архитектурни подхода (microservices, monolith, serverless), но:
+- Не искаме да губим оригиналните изисквания
+- Искаме да сравним подходите един до друг
+- Искаме да запазим всички варианти преди да вземем решение
+- Искаме да можем да се върнем назад ако сгрешим
+
+### Решение с RefMemTree Branching
+
+```python
+async def explore_architecture_approaches(project_id: str, requirements_node_id: str):
+    tree = AdvancedProjectTree(project_id)
+    
+    # СЪЗДАВАМЕ 3 ЕКСПЕРИМЕНТАЛНИ КЛОНА
+    approaches = {
+        "microservices": {
+            "prompt": "Design a microservices architecture...",
+            "emphasis": ["scalability", "independence", "deployment"]
+        },
+        "monolith": {
+            "prompt": "Design a modular monolith architecture...",
+            "emphasis": ["simplicity", "consistency", "development_speed"]
+        },
+        "serverless": {
+            "prompt": "Design a serverless architecture...",
+            "emphasis": ["cost", "scalability", "maintenance"]
+        }
+    }
+    
+    branches = {}
+    results = {}
+    
+    for approach_name, config in approaches.items():
+        # Create experimental branch
+        branch = tree.create_experimental_branch(
+            node_id=requirements_node_id,
+            branch_name=f"arch_{approach_name}",
+            branch_type="alternative"
+        )
+        branches[approach_name] = branch
+        
+        # Get context adapted for this approach
+        context = tree.adapt_context_for_agent(
+            node_id=branch.id,
+            agent_type="architect",
+            agent_expertise=config["emphasis"]
+        )
+        
+        # Generate architecture in this branch
+        architecture = await architecture_team.generate({
+            "context": context,
+            "prompt": config["prompt"],
+            "approach": approach_name
+        })
+        
+        # Store in branch - не засяга main tree
+        arch_node = tree.create_node(
+            parent_id=branch.id,
+            node_type="architecture",
+            data=architecture
+        )
+        
+        results[approach_name] = {
+            "branch_id": branch.id,
+            "architecture": architecture,
+            "node_id": arch_node.id
+        }
+    
+    # СРАВНЯВАМЕ ВСИЧКИ ПОДХОДИ
+    comparison = tree.compare_branches(
+        original_node_id=requirements_node_id,
+        branch_ids=[b.id for b in branches.values()]
+    )
+    
+    # Добавяме AI analysis за всеки
+    for approach_name, result in results.items():
+        analysis = await architecture_reviewer.analyze({
+            "architecture": result["architecture"],
+            "context": tree.get_smart_context(result["node_id"])
+        })
+        comparison[approach_name]["ai_analysis"] = analysis
+    
+    # HUMAN DECISION
+    print("🎯 Presenting 3 architecture approaches for decision:")
+    for approach_name, data in comparison.items():
+        print(f"\n{approach_name}:")
+        print(f"  Complexity: {data['ai_analysis']['complexity_score']}")
+        print(f"  Scalability: {data['ai_analysis']['scalability_score']}")
+        print(f"  Cost estimate: {data['ai_analysis']['cost_estimate']}")
+    
+    chosen = await get_human_choice(comparison)
+    
+    # MERGE CHOSEN BRANCH
+    tree.merge_branch(
+        branch_id=branches[chosen].id,
+        target_node_id=requirements_node_id,
+        merge_strategy="replace"
+    )
+    
+    # OTHER BRANCHES remain in history - можем да се върнем
+    for approach_name, branch in branches.items():
+        if approach_name != chosen:
+            tree.archive_branch(branch.id, reason="alternative_not_chosen")
+    
+    return {
+        "chosen": chosen,
+        "all_approaches": comparison,
+        "archived_branches": [a for a in approaches.keys() if a != chosen]
+    }
+```
+
+### Какво печелим:
+✅ Експериментираме без страх  
+✅ Сравняваме objectively  
+✅ Не губим алтернативи  
+✅ Пълна history  
+✅ Можем да се върнем  
+
+---
+
+## 🔍 Use Case 3: Context-Aware Research Sessions
+
+### Проблем
+При AI research session искаме да:
+- Не повтаряме вече проучено
+- Фокусираме се на важното за нашия контекст
+- Свързваме insights с релевантни части от проекта
+- Можем да "продължим" research по-късно
+
+### Решение с RefMemTree Context Management
+
+```python
+async def conduct_smart_research(
+    project_id: str,
+    topic: str,
+    related_node_id: str  # Например opportunity node
+):
+    tree = AdvancedProjectTree(project_id)
+    
+    # 1. ПРОВЕРКА ЗА ПРЕДИШНИ RESEARCH
+    # Semantic search за подобни проучвания
+    previous_research = tree.semantic_search(
+        query=topic,
+        node_types=["research_session"],
+        top_k=5
+    )
+    
+    already_covered = []
+    if previous_research:
+        print(f"📚 Found {len(previous_research)} related research sessions")
+        for res in previous_research:
+            context = tree.get_smart_context(res["node_id"])
+            already_covered.extend(
+                context.get("key_findings", [])
+            )
+    
+    # 2. GET FULL PROJECT CONTEXT
+    # Multi-perspective за разбиране на big picture
+    perspectives = tree.get_multi_perspective_context(related_node_id)
+    
+    # 3. FIND RELATED NODES ACROSS PROJECT
+    # Може да има relevant information в други части
+    related_nodes = tree.find_related_nodes(
+        node_id=related_node_id,
+        relation_type="semantic",
+        max_results=10
+    )
+    
+    # 4. CREATE RESEARCH SESSION NODE
+    research_session = tree.create_node(
+        parent_id=related_node_id,
+        node_type="research_session",
+        data={
+            "topic": topic,
+            "status": "active",
+            "started_at": datetime.now().isoformat()
+        }
+    )
+    
+    # 5. CREATE CONTEXT SNAPSHOT
+    # Запазваме точния контекст на началото
+    initial_snapshot = tree.create_context_snapshot(
+        research_session.id,
+        "research_start"
+    )
+    
+    # 6. BUILD RESEARCH PROMPT
+    research_prompt = f"""
+    === RESEARCH TOPIC ===
+    {topic}
+    
+    === PROJECT CONTEXT ===
+    {tree.get_pruned_context_for_ai(related_node_id, "ai_analysis", max_tokens=3000)}
+    
+    === ALREADY COVERED (don't repeat) ===
+    {chr(10).join(f"- {item}" for item in already_covered[:10])}
+    
+    === RELATED AREAS TO EXPLORE ===
+    {chr(10).join(f"- {node.data.get('title', 'N/A')}" for node in related_nodes[:5])}
+    
+    Please conduct thorough research focusing on NEW insights we don't have yet.
+    """
+    
+    # 7. CONDUCT RESEARCH with AI team
+    findings = await research_team.conduct({
+        "prompt": research_prompt,
+        "depth": "thorough",
+        "sources": ["academic", "industry", "competitors"]
+    })
+    
+    # 8. STORE FINDINGS AS CHILD NODES
+    for finding in findings:
+        finding_node = tree.create_node(
+            parent_id=research_session.id,
+            node_type="research_finding",
+            data=finding
+        )
+        
+        # CREATE REFERENCES to related nodes
+        if finding.get("relates_to"):
+            for related_id in finding["relates_to"]:
+                tree.create_reference(
+                    from_node_id=finding_node.id,
+                    to_node_id=related_id,
+                    reference_type="relates_to"
+                )
+    
+    # 9. CREATE END SNAPSHOT
+    end_snapshot = tree.create_context_snapshot(
+        research_session.id,
+        "research_complete"
+    )
+    
+    # 10. UPDATE SESSION
+    tree.update_node(research_session.id, {
+        "status": "completed",
+        "ended_at": datetime.now().isoformat(),
+        "findings_count": len(findings),
+        "snapshots": {
+            "start": initial_snapshot.id,
+            "end": end_snapshot.id
+        }
+    })
+    
+    return {
+        "session_id": research_session.id,
+        "findings": findings,
+        "avoided_duplication": len(already_covered),
+        "related_nodes": len(related_nodes)
+    }
+
+
+# ПРОДЪЛЖАВАНЕ НА RESEARCH ПО-КЪСНО
+async def continue_research(project_id: str, session_id: str, new_focus: str):
+    tree = AdvancedProjectTree(project_id)
+    
+    # Get full history
+    history = tree.get_context_history(session_id)
+    
+    # Get previous findings
+    previous_findings = tree.get_node(session_id).children
+    
+    # Continue with full context
+    continued_research = await research_team.conduct({
+        "previous_context": history,
+        "previous_findings": previous_findings,
+        "new_focus": new_focus
+    })
+    
+    return continued_research
+```
+
+### Какво печелим:
+✅ Не повтаряме research  
+✅ Фокус на важното  
+✅ Връзка с проекта  
+✅ Пълна история  
+✅ Можем да продължим  
+
+---
+
+## 🔗 Use Case 4: Dependency Tracking & Impact Analysis
+
+### Проблем
+Когато променим един модул в архитектурата:
+- Кои други модули зависят от него?
+- Какъв е impact-а на промяната?
+- Има ли circular dependencies?
+- Кои test-ове трябва да се пуснат?
+
+### Решение с RefMemTree References
+
+```python
+async def analyze_change_impact(
+    project_id: str,
+    module_id: str,
+    proposed_change: dict
+):
+    tree = AdvancedProjectTree(project_id)
+    
+    # 1. GET ALL DEPENDENCIES
+    # Traverse reference graph
+    dependencies = tree.traverse_references(
+        start_node_id=module_id,
+        reference_type="depends_on",
+        max_depth=10
+    )
+    
+    # 2. GET REVERSE DEPENDENCIES (кой зависи от нас)
+    dependents = tree.get_node_references(
+        node_id=module_id,
+        reference_type="depends_on",
+        direction="incoming"  # Кой ни reference-ва
+    )
+    
+    # 3. CHECK FOR CIRCULAR DEPENDENCIES
+    circular = tree.tree.detect_circular_references()
+    if circular:
+        print("⚠️  WARNING: Circular dependencies detected:")
+        for cycle in circular:
+            print(f"  {' -> '.join([n.data['name'] for n in cycle])}")
+    
+    # 4. GET FULL CONTEXT OF AFFECTED MODULES
+    impact_analysis = {
+        "direct_dependencies": len(dependencies),
+        "modules_depending_on_us": len(dependents),
+        "affected_modules": []
+    }
+    
+    for dependent in dependents:
+        # Get context за всеки affected module
+        dep_context = tree.get_smart_context(
+            dependent["node_id"],
+            context_type="code_generation"
+        )
+        
+        # AI analysis на impact
+        ai_impact = await impact_analyzer.analyze({
+            "module": tree.get_node(dependent["node_id"]),
+            "change": proposed_change,
+            "context": dep_context
+        })
+        
+        impact_analysis["affected_modules"].append({
+            "module_id": dependent["node_id"],
+            "module_name": tree.get_node(dependent["node_id"]).data["name"],
+            "impact_level": ai_impact["impact_level"],  # low, medium, high
+            "requires_changes": ai_impact["requires_changes"],
+            "suggested_updates": ai_impact["suggested_updates"]
+        })
+    
+    # 5. VISUALIZE DEPENDENCY GRAPH
+    dependency_graph = tree.build_dependency_graph(
+        root_node_id=module_id,
+        include_transitive=True
+    )
+    
+    # 6. DETERMINE TEST SCOPE
+    modules_to_test = set([module_id])
+    for affected in impact_analysis["affected_modules"]:
+        if affected["impact_level"] in ["medium", "high"]:
+            modules_to_test.add(affected["module_id"])
+            
+            # Add their dependencies too
+            transitive = tree.traverse_references(
+                affected["module_id"],
+                "depends_on",
+                max_depth=2
+            )
+            modules_to_test.update([n.id for n in transitive])
+    
+    impact_analysis["test_scope"] = list(modules_to_test)
+    
+    # 7. CREATE SNAPSHOT BEFORE CHANGE
+    before_snapshot = tree.create_context_snapshot(
+        module_id,
+        f"before_change_{proposed_change['type']}"
+    )
+    
+    impact_analysis["rollback_snapshot"] = before_snapshot.id
+    
+    return impact_analysis
+
+
+# EXAMPLE: Променяме API на модул
+async def change_module_api(project_id: str, module_id: str, new_api: dict):
+    tree = AdvancedProjectTree(project_id)
+    
+    # 1. ANALYZE IMPACT
+    impact = await analyze_change_impact(
+        project_id,
+        module_id,
+        {"type": "api_change", "details": new_api}
+    )
+    
+    print(f"📊 Impact Analysis:")
+    print(f"  Direct dependencies: {impact['direct_dependencies']}")
+    print(f"  Affected modules: {len(impact['affected_modules'])}")
+    print(f"  Modules to test: {len(impact['test_scope'])}")
+    
+    # 2. SHOW DETAILS
+    for affected in impact["affected_modules"]:
+        print(f"\n  ⚠️  {affected['module_name']}:")
+        print(f"     Impact: {affected['impact_level']}")
+        if affected["requires_changes"]:
+            print(f"     Required updates:")
+            for update in affected["suggested_updates"]:
+                print(f"       - {update}")
+    
+    # 3. HUMAN APPROVAL
+    approved = await ask_human(
+        f"Proceed with change affecting {len(impact['affected_modules'])} modules?"
+    )
+    
+    if not approved:
+        print("❌ Change cancelled")
+        return
+    
+    # 4. APPLY CHANGE
+    tree.update_node(module_id, {"api": new_api})
+    
+    # 5. UPDATE AFFECTED MODULES (if AI suggested auto-updates)
+    for affected in impact["affected_modules"]:
+        if affected["requires_changes"] and affected.get("auto_fixable"):
+            # AI generates update
+            update = await code_updater.generate_update({
+                "module_id": affected["module_id"],
+                "required_changes": affected["suggested_updates"],
+                "context": tree.get_smart_context(affected["module_id"])
+            })
+            
+            # Apply with human review
+            await apply_update_with_review(affected["module_id"], update)
+    
+    # 6. CREATE SNAPSHOT AFTER
+    after_snapshot = tree.create_context_snapshot(
+        module_id,
+        f"after_change_{new_api['version']}"
+    )
+    
+    return {
+        "success": True,
+        "impact": impact,
+        "snapshots": {
+            "before": impact["rollback_snapshot"],
+            "after": after_snapshot.id
+        }
+    }
+```
+
+### Какво печелим:
+✅ Знаем impact преди промяна  
+✅ Circular dependency detection  
+✅ Автоматично определяне на test scope  
+✅ AI suggestions за updates  
+✅ Rollback възможност  
+
+---
+
+## 💾 Use Case 5: Code Reuse & Pattern Discovery
+
+### Проблем
+Имаме нов requirement за authentication module. Може би сме правили нещо подобно преди?
+
+### Решение с Semantic Search
+
+```python
+async def find_reusable_implementations(
+    project_id: str,
+    requirement: str,
+    requirement_type: str
+):
+    tree = AdvancedProjectTree(project_id)
+    
+    # 1. SEMANTIC SEARCH across entire project history
+    similar_implementations = tree.semantic_search(
+        query=requirement,
+        search_scope="entire_tree",
+        node_types=["module", "implementation", "component"],
+        top_k=10
+    )
+    
+    # 2. FILTER by success and relevance
+    candidates = []
+    for impl in similar_implementations:
+        impl_node = tree.get_node(impl["node_id"])
+        
+        # Get metadata
+        metadata = impl_node.data.get("metadata", {})
+        
+        # Skip failed implementations
+        if metadata.get("status") == "failed":
+            continue
+        
+        # Get full context
+        context = tree.get_smart_context(
+            impl["node_id"],
+            context_type="code_generation"
+        )
+        
+        # Get code if exists
+        code_node = tree.find_child_by_type(impl["node_id"], "generated_code")
+        
+        # Get test results if exists
+        test_node = tree.find_child_by_type(impl["node_id"], "test_results")
+        
+        candidates.append({
+            "node_id": impl["node_id"],
+            "title": impl["title"],
+            "relevance": impl["relevance_score"],
+            "context": context,
+            "code": code_node.data if code_node else None,
+            "test_results": test_node.data if test_node else None,
+            "success_score": metadata.get("success_score", 0.5)
+        })
+    
+    # 3. RANK by combined score
+    for candidate in candidates:
+        candidate["combined_score"] = (
+            candidate["relevance"] * 0.4 +
+            candidate["success_score"] * 0.6
+        )
+    
+    candidates.sort(key=lambda x: x["combined_score"], reverse=True)
+    
+    # 4. AI ANALYSIS of reusability
+    reuse_analysis = []
+    for candidate in candidates[:3]:  # Top 3
+        analysis = await code_analyzer.analyze_reusability({
+            "existing_code": candidate["code"],
+            "existing_context": candidate["context"],
+            "new_requirement": requirement,
+            "requirement_type": requirement_type
+        })
+        
+        reuse_analysis.append({
+            "candidate": candidate,
+            "reusability_score": analysis["reusability_score"],
+            "adaptation_needed": analysis["adaptation_needed"],
+            "estimated_time_saved": analysis["time_saved"],
+            "suggested_modifications": analysis["modifications"]
+        })
+    
+    return {
+        "found_similar": len(similar_implementations),
+        "reusable_candidates": reuse_analysis,
+        "recommendation": reuse_analysis[0] if reuse_analysis else None
+    }
+
+
+# EXAMPLE: Creating new auth module
+async def create_auth_module(project_id: str, requirements: dict):
+    tree = AdvancedProjectTree(project_id)
+    
+    # 1. SEARCH for similar implementations
+    reusable = await find_reusable_implementations(
+        project_id,
+        "user authentication and authorization module",
+        "security"
+    )
+    
+    if reusable["reusable_candidates"]:
+        best = reusable["recommendation"]
+        
+        print(f"💡 Found reusable implementation!")
+        print(f"   From: {best['candidate']['title']}")
+        print(f"   Reusability: {best['reusability_score']:.0%}")
+        print(f"   Time saved: {best['estimated_time_saved']}")
+        
+        # Human decision
+        use_existing = await ask_human(
+            f"Use existing implementation with modifications?"
+        )
+        
+        if use_existing:
+            # Clone and adapt
+            adapted_code = await code_adapter.adapt({
+                "base_code": best["candidate"]["code"],
+                "base_context": best["candidate"]["context"],
+                "new_requirements": requirements,
+                "modifications": best["suggested_modifications"]
+            })
+            
+            # Create reference to original
+            new_module = tree.create_node(
+                parent_id=requirements["parent_id"],
+                node_type="module",
+                data={
+                    "name": "auth_module",
+                    "based_on": best["candidate"]["node_id"],
+                    "adapted": True
+                }
+            )
+            
+            tree.create_reference(
+                from_node_id=new_module.id,
+                to_node_id=best["candidate"]["node_id"],
+                reference_type="adapted_from"
+            )
+            
+            return {
+                "reused": True,
+                "time_saved": best["estimated_time_saved"],
+                "code": adapted_code
+            }
+    
+    # No reusable found - create from scratch
+    print("🆕 Creating new implementation from scratch")
+    return await create_from_scratch(project_id, requirements)
+```
+
+### Какво печелим:
+✅ Не измисляме топлата вода  
+✅ Reuse на proven solutions  
+✅ Significant time savings  
+✅ Pattern discovery  
+✅ Knowledge retention  
+
+---
+
+## 🎯 Заключение
+
+RefMemTree не е просто "дърво за данни". Той е **intelligent context management system** който:
+
+1. **Помни всичко** - но показва само релевантното
+2. **Свързва информация** - чрез semantics, не само structure
+3. **Позволява експерименти** - без страх от загуба
+4. **Проследява dependencies** - и предсказва impact
+5. **Открива patterns** - за reuse и learning
+6. **Адаптира контекста** - за различни AI agents и tasks
+
+Това прави AI агентите **МНОГО по-интелигентни** защото имат:
+- ✅ Right context at the right time
+- ✅ Historical knowledge
+- ✅ Relationship awareness
+- ✅ Pattern recognition
+- ✅ Impact prediction
+
+**RefMemTree е невроните на системата, не само костите! 🧠**