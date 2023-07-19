from src.llm_prompt_interface import LLMPromptInterface
from typing import List, Dict, Optional, Tuple
import sys
import os

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
