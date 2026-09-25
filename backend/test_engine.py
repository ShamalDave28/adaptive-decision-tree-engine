import sys
import os
from pathlib import Path
import pytest
from unittest.mock import patch

BASE_DIR = Path(__file__).resolve().parent
REPO_ROOT = BASE_DIR.parent
for p in [str(REPO_ROOT), str(BASE_DIR)]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app.tree_manager import TreeManager, build_default_tree, tree_to_dict
from app.nlp_validator import NLPValidator

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

@patch("app.tree_manager.DatabaseManager")
def test_tree_manager_initialization(mock_db_cls):
    mock_db = mock_db_cls.return_value
    mock_db.load_tree_data.return_value = None
    
    manager = TreeManager()
    assert manager.root is not None
    assert manager.root.question == "Does it live in water?"

@patch("app.tree_manager.DatabaseManager")
def test_tree_navigation(mock_db_cls):
    mock_db = mock_db_cls.return_value
    mock_db.load_tree_data.return_value = None

    manager = TreeManager()
    target_node = manager.navigate(["yes", "yes"])
    assert target_node.guess == "Dolphin"

def test_nlp_validation_valid():
    is_valid, cleaned = NLPValidator.validate_question("does it bark")
    assert is_valid is True
    assert cleaned == "Does it bark?"

def test_nlp_validation_invalid_length():
    is_valid, msg = NLPValidator.validate_question("No?")
    assert is_valid is False
    assert "too brief" in msg.lower()

def test_animal_name_validation():
    is_valid, cleaned = NLPValidator.validate_animal_name("golden retriever")
    assert is_valid is True
    assert cleaned == "Golden Retriever"

def test_duplicate_question_detection():
    root = build_default_tree()
    tree_dict = tree_to_dict(root)
    is_dup, msg = NLPValidator.check_duplicate_question("does it live in water?", tree_dict)
    assert is_dup is True
    assert "similar" in msg.lower()