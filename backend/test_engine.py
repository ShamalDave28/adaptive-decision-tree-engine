import pytest
from backend.app.tree_manager import DecisionTreeEngine
from backend.app.nlp_validator import validate_question, validate_target_entity

def test_engine_initialization():
    engine = DecisionTreeEngine()
    root = engine.get_current_question()
    assert root is not None
    assert "text" in root

def test_nlp_validation_valid():
    is_valid, msg = validate_question("Does it bark?")
    assert is_valid is True

def test_nlp_validation_invalid_length():
    is_valid, msg = validate_question("No?")
    assert is_valid is False

def test_entity_validation():
    is_valid, msg = validate_target_entity("Golden Retriever")
    assert is_valid is True