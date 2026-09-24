import pytest
from unittest.mock import patch
from backend.app.tree_manager import TreeManager, build_default_tree, tree_to_dict
from backend.app.nlp_validator import validate_question, validate_target_entity

def test_default_tree_structure():
    root = build_default_tree()
    assert root is not None
    assert root.question == "Does it live in water?"
    assert root.yes is not None
    assert root.no is not None

def test_tree_to_dict_conversion():
    root = build_default_tree()
    tree_dict = tree_to_dict(root)
    assert isinstance(tree_dict, dict)
    assert tree_dict["question"] == "Does it live in water?"
    assert "yes" in tree_dict
    assert "no" in tree_dict

@patch("backend.app.database.DatabaseManager.load_tree_data", return_value=None)
def test_tree_manager_initialization(mock_load):
    manager = TreeManager()
    assert manager.root is not None
    assert manager.root.question == "Does it live in water?"

@patch("backend.app.database.DatabaseManager.load_tree_data", return_value=None)
def test_tree_navigation(mock_load):
    manager = TreeManager()
    # Step down: live in water (yes) -> mammal (yes) -> Dolphin
    target_node = manager.navigate(["yes", "yes"])
    assert target_node.guess == "Dolphin"

def test_nlp_validation_valid():
    is_valid, msg = validate_question("Does it bark?")
    assert is_valid is True

def test_nlp_validation_invalid_length():
    is_valid, msg = validate_question("No?")
    assert is_valid is False

def test_entity_validation():
    is_valid, msg = validate_target_entity("Golden Retriever")
    assert is_valid is True