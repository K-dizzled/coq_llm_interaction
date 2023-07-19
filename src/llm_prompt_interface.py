from typing import List, Dict, Optional, Tuple
import sys

sys.path.insert(1, '../coqpylspclient')

from coqlspclient.proof_view import ProofView

sys.path.pop()

class LLMPromptInterface:
    def __init__(
        self, 
        path_to_coq_file: str, 
        train_theorems: List[str],
        test_theorems: List[str]
    ) -> None:
        self.coq_file = path_to_coq_file
        self.prompt_strategy = self.__class__.__name__

        self.proof_view = ProofView(self.coq_file)
        self.theorems_from_file = self.proof_view.parse_file()
        self.statements_to_lines = None

        self.train_theorems = train_theorems
        self.test_theorems = test_theorems

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

    def verify_proof(self, thr_st: str, proof: str) -> Tuple[bool, str]:
        """
        Verifies the proof using the ProofView class.
        """
        context = ""
        if self.statements_to_lines is not None:
            with open(self.coq_file, "r") as f:
                context = f.read()                
                thr_line_index = self.statements_to_lines[thr_st]
                context = "\n".join(context.split('\n')[:thr_line_index])
                
        check_proof = self.proof_view.check_proof(thr_st, proof, context)
        return check_proof
    
    def get_theorems_for_evaluation(self) -> List[str]:
        """
        Returns the list of theorems on which we 
        want to evaluate the LLM.
        """
        theorems_for_eval = list(
            filter(
                lambda th: th.name in self.test_theorems, 
                self.theorems_from_file
            )
        )
        self.statements_to_lines = {
            theorem.statement : theorem.statement_range.start.line 
            for theorem in theorems_for_eval
        }

        return [theorem.statement for theorem in theorems_for_eval]
    
    def stop(self) -> None: 
        """
        Free up resources.
        """
        self.proof_view.exit()