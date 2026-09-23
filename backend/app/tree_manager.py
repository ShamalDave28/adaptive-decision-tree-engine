import json
import os
from typing import List, Optional
from app.database import DatabaseManager

TREE_FILE = "tree.json"

class Node:
    def __init__(self, question: Optional[str] = None, yes: Optional['Node'] = None, no: Optional['Node'] = None, guess: Optional[str] = None):
        self.question = question
        self.yes = yes
        self.no = no
        self.guess = guess

def build_default_tree() -> Node:
    return Node(
        "Does it live in water?",
        yes=Node(
            "Is it a mammal?",
            yes=Node(guess="Dolphin"),
            no=Node(guess="Shark")
        ),
        no=Node(
            "Is it a pet?",
            yes=Node(guess="Dog"),
            no=Node(guess="Lion")
        )
    )

def tree_to_dict(node: Optional[Node]) -> Optional[dict]:
    if node is None:
        return None
    return {
        "question": node.question,
        "guess": node.guess,
        "yes": tree_to_dict(node.yes),
        "no": tree_to_dict(node.no)
    }

def dict_to_tree(data: Optional[dict]) -> Optional[Node]:
    if data is None:
        return None
    return Node(
        question=data.get("question"),
        guess=data.get("guess"),
        yes=dict_to_tree(data.get("yes")),
        no=dict_to_tree(data.get("no"))
    )

class TreeManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.root = self.load_tree()

    def load_tree(self) -> Node:
        # Priority 1: Check MongoDB
        data = self.db.load_tree_data()
        if data:
            tree = dict_to_tree(data)
            if tree:
                return tree

        # Priority 2: Fallback to local JSON file
        if os.path.exists(TREE_FILE):
            try:
                with open(TREE_FILE, "r") as f:
                    data = json.load(f)
                    tree = dict_to_tree(data)
                    if tree is not None:
                        return tree
            except Exception:
                pass

        # Priority 3: Default starter tree
        return build_default_tree()

    def save_tree(self, learned_animal: str = None):
        tree_dict = tree_to_dict(self.root)

        # 1. Save to MongoDB if connected
        self.db.save_tree_data(tree_dict, learned_animal)

        # 2. Always persist a local JSON copy as an offline backup
        with open(TREE_FILE, "w") as f:
            json.dump(tree_dict, f, indent=4)

    def navigate(self, path: List[str]) -> Node:
        curr = self.root
        for step in path:
            if step == "yes" and curr.yes:
                curr = curr.yes
            elif step == "no" and curr.no:
                curr = curr.no
        return curr

    def teach(self, path: List[str], correct_animal: str, new_question: str, answer_for_new: str):
        node = self.navigate(path)
        old_guess = node.guess

        node.question = new_question
        node.guess = None

        if answer_for_new.lower() == "yes":
            node.yes = Node(guess=correct_animal)
            node.no = Node(guess=old_guess)
        else:
            node.no = Node(guess=correct_animal)
            node.yes = Node(guess=old_guess)

        self.save_tree(learned_animal=correct_animal)