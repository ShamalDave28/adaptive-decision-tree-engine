import re
from rapidfuzz import fuzz
from typing import List, Tuple

class NLPValidator:
    @staticmethod
    def clean_text(text: str) -> str:
        """Strip excess whitespace and normalize casing."""
        return re.sub(r'\s+', ' ', text).strip()

    @staticmethod
    def validate_animal_name(animal: str) -> Tuple[bool, str]:
        cleaned = NLPValidator.clean_text(animal)
        if len(cleaned) < 2:
            return False, "Animal name is too short."
        if not re.match(r"^[A-Za-z\s\-]+$", cleaned):
            return False, "Animal name should only contain letters, spaces, or hyphens."
        return True, cleaned.title()

    @staticmethod
    def validate_question(question: str) -> Tuple[bool, str]:
        cleaned = NLPValidator.clean_text(question)
        if len(cleaned.split()) < 3:
            return False, "Question is too brief. Please provide a descriptive YES/NO question."
        
        # Ensure it ends with a question mark
        if not cleaned.endswith("?"):
            cleaned += "?"
            
        cleaned = cleaned[0].upper() + cleaned[1:]
        return True, cleaned

    @staticmethod
    def extract_all_questions(node_dict: dict) -> List[str]:
        """Traverses the tree to collect all existing questions."""
        questions = []
        if not node_dict:
            return questions
        if node_dict.get("question"):
            questions.append(node_dict["question"])
        if node_dict.get("yes"):
            questions.extend(NLPValidator.extract_all_questions(node_dict["yes"]))
        if node_dict.get("no"):
            questions.extend(NLPValidator.extract_all_questions(node_dict["no"]))
        return questions

    @classmethod
    def check_duplicate_question(cls, new_question: str, tree_dict: dict, threshold: int = 85) -> Tuple[bool, str]:
        """Checks if a semantically similar question already exists in the tree."""
        existing_questions = cls.extract_all_questions(tree_dict)
        cleaned_new = cls.clean_text(new_question).lower()

        for q in existing_questions:
            cleaned_existing = cls.clean_text(q).lower()
            similarity = fuzz.token_sort_ratio(cleaned_new, cleaned_existing)
            if similarity >= threshold:
                return True, f"This question is too similar to an existing question: '{q}' (Similarity: {similarity:.0f}%)"

        return False, ""