from pydantic import BaseModel
from typing import Optional, List

# 1. Contract for teaching the AI a new animal
class TeachRequest(BaseModel):
    node_path: List[str]       # History of answers, e.g. ["no", "yes"]
    correct_animal: str        # The name of the new animal (e.g. "Cheetah")
    new_question: str          # The question to distinguish it (e.g. "Is it fast?")
    answer_for_new: str        # "Yes" or "No" for the new animal

# 2. Contract for what the backend returns to the user at each step
class GameStateResponse(BaseModel):
    question: Optional[str] = None   # Current question to ask (if not at a guess)
    guess: Optional[str] = None      # The guess (if reached a leaf node)
    is_leaf: bool = False            # True if it's guessing an animal; False if it's asking a question