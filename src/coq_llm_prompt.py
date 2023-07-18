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
    
    def get_context_for_log(self) -> str: 
        return "(* EMPTY_CONTEXT *)"
    
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
        theorems = self.proof_view_train.parse_file()

        history = []
        for theorem in theorems: 
            history.append({"role": "user", "content": theorem.statement})
            history.append({"role": "assistant", "content": theorem.proof.only_text()})
        
        return history