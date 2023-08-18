from src.llm_prompt_interface import LLMPromptInterface, ProofView
from typing import List, Dict, Optional, Tuple
import random

class CoqPromptBasic(LLMPromptInterface): 
    def get_system_message(self) -> str: 
        return ('Generate proof of the theorem from user input in Coq. '
                'You should only generate proofs in Coq.'
                'Never add special comments to the proof.'
                'Your answer should be a valid Coq proof.'
                'It should start with "Proof." and end with "Qed.".'
               )

    def get_msg_history(self) -> List[Dict[str, str]]:
        return []
        
    def verify_proof(self, thr_st: str, proof: str) -> Tuple[bool, str]:
        return self.proof_view.check_proof(thr_st, proof, "")

class CoqPromptKShot(LLMPromptInterface): 
    def get_system_message(self) -> str: 
        return ('Generate proof of the theorem from user input in Coq. '
                'You should only generate proofs in Coq.'
                'Never add special comments to the proof.'
                'Your answer should be a valid Coq proof.'
                'It should start with "Proof." and end with "Qed.".'
               )

    def get_msg_history(self) -> List[Dict[str, str]]:
        theorems = self.theorems_from_file

        history = []
        for theorem in theorems: 
            if theorem.name in self.train_theorems:
                history.append({"role": "user", "content": theorem.statement})
                thr_proof = theorem.proof.only_text() if theorem.proof is not None else "Admitted."
                history.append({"role": "assistant", "content": thr_proof})
        
        return history


class CoqPromptKShotWithContext(LLMPromptInterface): 
    def get_system_message(self) -> str: 
        return ('Generate proof of the theorem from user input in Coq. '
                'You should only generate proofs in Coq. '
                'Never add special comments to the proof. '
                'Your answer should be a valid Coq proof. '
                'It should start with "Proof." and end with "Qed.".'
                'In the examples, context would be present inside '
                ' (* [CONTEXT] ... *), as well as the goal (* [GOAL] ... *). '
                'These two together represent the state of the proof after '
                'each tactic call. This can help to better understand the proof '
                'and how given tactics modify the context. You dont have to '
                'generate the GOAL and CONTEXT. Just give the proof as the output.'
                '"Proof. {proof} Qed." Do not ever use Admitted. or Abort.'
               )

    def get_msg_history(self) -> List[Dict[str, str]]:
        theorems = self.theorems_from_file

        history = []
        for theorem in theorems: 
            if theorem.name in self.train_theorems:
                history.append({"role": "user", "content": theorem.statement})
                thr_proof = str(theorem.proof) if theorem.proof is not None else "Admitted."
                history.append({"role": "assistant", "content": thr_proof})
        
        return history


class CoqPromptKShotRandomEvalChoice(CoqPromptKShotWithContext): 
    def __init__(
        self, 
        path_to_coq_file: str, 
        path_to_root_dir: str,
        train_fraction: float,
    ) -> None:
        if train_fraction < 0 or train_fraction > 1: 
            raise ValueError("train_fraction must be between 0 and 1")
        proof_view = ProofView(path_to_coq_file, path_to_root_dir)
        all_theorems = proof_view.all_theorem_names()
        self.train_fraction = train_fraction
        # Split self.theorems_from_file into train and test 
        # according to train_fraction
        train_theorems = []
        test_theorems = []
        for theorem in all_theorems:
            if random.random() < train_fraction:
                train_theorems.append(theorem)
            else:
                test_theorems.append(theorem)
        # make both lists 4 times shorter cause otherwise 
        # we reach the token limit when using gpt
        random_indexes_train = random.sample(range(len(train_theorems)), len(train_theorems)//4)
        random_indexes_test = random.sample(range(len(test_theorems)), len(test_theorems)//6)
        train_theorems = [train_theorems[i] for i in random_indexes_train]
        test_theorems = [test_theorems[i] for i in random_indexes_test]
        
        print(f"Train theorems: {train_theorems}")
        print(f"Test theorems: {test_theorems}")
        super().__init__(path_to_coq_file, path_to_root_dir, train_theorems, test_theorems, proof_view=proof_view)


class CoqPromptSolveAdmitted(CoqPromptKShotWithContext): 
    def __init__(
        self, 
        path_to_coq_file: str, 
        path_to_root_dir: str
    ) -> None:
        proof_view = ProofView(path_to_coq_file, path_to_root_dir)
        all_theorems = proof_view.parse_file()
        train_theorems = []
        test_theorems = []
        for theorem in all_theorems:
            if "Admitted." in str(theorem.proof): 
                test_theorems.append(theorem)
            else:
                train_theorems.append(theorem)
        super().__init__(path_to_coq_file, path_to_root_dir, train_theorems, test_theorems, proof_view=proof_view)