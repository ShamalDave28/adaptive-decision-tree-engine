from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from app.tree_manager import TreeManager, tree_to_dict
from app.nlp_validator import NLPValidator

app = FastAPI(title="AI Animal Guessing Game API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

tree_mgr = TreeManager()

class TeachRequest(BaseModel):
    node_path: List[str]
    correct_animal: str
    new_question: str
    answer_for_new: str

@app.get("/api/state")
def get_state(path: Optional[str] = ""):
    steps = [p for p in path.split("/") if p]
    current_node = tree_mgr.navigate(steps)
    is_leaf = (current_node.guess is not None)
    return {
        "is_leaf": is_leaf,
        "question": current_node.question if not is_leaf else None,
        "guess": current_node.guess if is_leaf else None
    }

@app.get("/api/tree")
def get_full_tree():
    return tree_to_dict(tree_mgr.root)

@app.post("/api/teach")
def teach_ai(req: TeachRequest):
    # 1. Validate animal name syntax
    is_valid_animal, animal_res = NLPValidator.validate_animal_name(req.correct_animal)
    if not is_valid_animal:
        raise HTTPException(status_code=400, detail=animal_res)

    # 2. Validate question structure
    is_valid_q, question_res = NLPValidator.validate_question(req.new_question)
    if not is_valid_q:
        raise HTTPException(status_code=400, detail=question_res)

    # 3. Check for redundant/duplicate questions in the knowledge tree
    current_tree_dict = tree_to_dict(tree_mgr.root)
    is_duplicate, duplicate_msg = NLPValidator.check_duplicate_question(question_res, current_tree_dict)
    if is_duplicate:
        raise HTTPException(status_code=400, detail=duplicate_msg)

    # 4. Save and train
    tree_mgr.teach(
        path=req.node_path,
        correct_animal=animal_res,
        new_question=question_res,
        answer_for_new=req.answer_for_new
    )
    return {"status": "success", "message": f"Successfully learned {animal_res}"}