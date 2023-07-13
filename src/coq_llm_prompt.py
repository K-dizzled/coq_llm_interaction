from src.llm_prompt_interface import LLMPromptInterface
from typing import List, Dict, Optional
import sys
import os

sys.path.insert(1, '../coqpylspclient')

from coqlspclient.proof_view import ProofView

sys.path.pop()

class CoqPromptBasic(LLMPromptInterface): 
    def __init__(self, path_to_coq_file: str) -> None: 
        self.coq_file = path_to_coq_file
        self.proof_view = ProofView(self.coq_file)
        self.theorems_from_file = self.proof_view.parse_file()

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
    
    def verify_proof(self, thr_st: str, proof: str) -> bool:
        check_proof = self.proof_view.check_proof(thr_st, proof, "")
        print(check_proof[1])
        return check_proof[0]
    
    def get_theorems_for_evaluation(self) -> List[str]:
        return [theorem.statement for theorem in self.theorems_from_file]
    
    def stop(self) -> None: 
        self.proof_view.exit()