from typing import List, Dict, Optional, Tuple
import sys

sys.path.insert(1, '../coqpylspclient')

from coqlspclient.proof_view import ProofView

sys.path.pop()

class LLMPromptInterface:
    def __init__(
        self, 
        path_to_coq_train_file: str, 
        path_to_coq_test_file: str
    ) -> None: 
        self.coq_train_file = path_to_coq_train_file
        self.coq_test_file = path_to_coq_test_file
        self.prompt_strategy = self.__class__.__name__

        self.proof_view = ProofView(self.coq_test_file)
        self.proof_view_train = ProofView(self.coq_train_file)
        self.theorems_from_file = self.proof_view.parse_file()
        
    def get_system_message(self) -> str: 
        """
        Gets the system message for the LLM. 
        """
        pass

    def get_msg_history(self) -> List[Dict[str, str]]:
        """
        Gets the message history for the LLM. 
        """
        pass

    def get_context_for_log(self) -> str: 
        """
        Coq context to be added to the log fil preceding the proof.
        """
        with open(self.coq_train_file, "r") as f:
            return f.read()

    def verify_proof(self, thr_st: str, proof: str) -> Tuple[bool, str]:
        """
        Verifies the proof using the ProofView class.
        """
        with open(self.coq_train_file, "r") as f:
            context = f.read()
        check_proof = self.proof_view.check_proof(thr_st, proof, context)
        return check_proof
    
    def get_theorems_for_evaluation(self) -> List[str]:
        """
        Returns the list of theorems on which we 
        want to evaluate the LLM.
        """
        return [theorem.statement for theorem in self.theorems_from_file]
    
    def stop(self) -> None: 
        """
        Free up resources.
        """
        self.proof_view.exit()
        self.proof_view_train.exit()