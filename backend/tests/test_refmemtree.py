"""Tests for RefMemTree wrapper."""

from uuid import uuid4

import pytest

from backend.core.refmemtree_wrapper import AdvancedProjectTree, ProjectTreeNode


def test_create_project_tree() -> None:
    """Test creating project tree."""
    project_id = uuid4()
    tree = AdvancedProjectTree(project_id)

    assert tree.project_id == project_id
    assert tree.root is None


def test_create_root_node() -> None:
    """Test creating root node."""
    project_id = uuid4()
    tree = AdvancedProjectTree(project_id)

    root = tree.create_root_node(node_type="goal", data={"title": "Main Goal"})

    assert root is not None
    assert root.node_type == "goal"
    assert root.data["title"] == "Main Goal"
    assert tree.root == root


def test_add_child_node() -> None:
    """Test adding child node."""
    project_id = uuid4()
    tree = AdvancedProjectTree(project_id)

    root = tree.create_root_node(node_type="goal", data={"title": "Main Goal"})
    child = tree.add_child_node(parent_id=root.id, node_type="opportunity", data={"title": "Opportunity 1"})

    assert child.parent_id == root.id
    assert child in root.children
    assert tree.get_node(child.id) == child


def test_get_smart_context() -> None:
    """Test getting smart context for node."""
    project_id = uuid4()
    tree = AdvancedProjectTree(project_id)

    root = tree.create_root_node(node_type="goal", data={"title": "Main Goal"})
    child1 = tree.add_child_node(parent_id=root.id, node_type="opportunity", data={"title": "Opportunity 1"})
    child2 = tree.add_child_node(parent_id=root.id, node_type="opportunity", data={"title": "Opportunity 2"})

    context = tree.get_smart_context(child1.id)

    assert context["target_node"]["id"] == str(child1.id)
    assert len(context["siblings"]) == 1
    assert len(context["ancestors"]) >= 1


def test_create_branch() -> None:
    """Test creating experimental branch."""
    project_id = uuid4()
    tree = AdvancedProjectTree(project_id)

    root = tree.create_root_node(node_type="goal", data={"title": "Main Goal"})
    branch_id = tree.create_branch(source_node_id=root.id, branch_name="experiment-1")

    branch = tree.get_node(branch_id)
    assert branch is not None
    assert branch.data["is_branch"] is True
    assert branch.data["branch_name"] == "experiment-1"


def test_tree_snapshot() -> None:
    """Test tree snapshot and restoration."""
    project_id = uuid4()
    tree = AdvancedProjectTree(project_id)

    root = tree.create_root_node(node_type="goal", data={"title": "Main Goal"})
    tree.add_child_node(parent_id=root.id, node_type="opportunity", data={"title": "Opp 1"})

    # Get snapshot
    snapshot = tree.get_tree_snapshot()
    assert snapshot["project_id"] == str(project_id)
    assert "root" in snapshot

    # Load into new tree
    new_tree = AdvancedProjectTree(project_id)
    new_tree.load_from_snapshot(snapshot)

    assert new_tree.root is not None
    assert new_tree.root.data["title"] == "Main Goal"
    assert len(new_tree.root.children) == 1
