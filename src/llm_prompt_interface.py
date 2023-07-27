from typing import List, Dict, Optional, Tuple
import sys
import logging

sys.path.insert(1, '../coqpylspclient')

from coqlspclient.proof_view import ProofView
from pylspclient.lsp_structs import Range, Position

sys.path.pop()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("LLMPromptInterface")


class LLMPromptInterface:
    def __init__(
        self, 
        path_to_coq_file: str, 
        path_to_root_dir: str,
        train_theorems: List[str],
        test_theorems: List[str],
        proof_view: Optional[ProofView] = None
    ) -> None:
        self.proof_view = proof_view if proof_view is not None else ProofView(path_to_coq_file, path_to_root_dir)
        self.coq_file = path_to_coq_file
        self.root_dir = path_to_root_dir
        self.prompt_strategy = self.__class__.__name__

        logger.info(f"Start preprocessing {self.coq_file} to obtain the training info.")
        self.theorems_from_file = self.proof_view.parse_file()

        self.train_theorems = train_theorems
        self.test_theorems = test_theorems

        self.theorems_for_eval = list(
            filter(
                lambda th: th.name in self.test_theorems, 
                self.theorems_from_file
            )
        )

        try: 
            self.statements_to_ranges = {
                theorem.statement : Range(
                    start=theorem.statement_range.start, 
                    end=theorem.proof.end_pos.end
                )
                for theorem in self.theorems_for_eval
            }
        except AttributeError:
            raise Exception("Some theorems in the file do not have proofs.")

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
        if self.statements_to_ranges is not None:
            with open(self.coq_file, "r") as f:
                context = f.read()                
                thr_line_index = self.statements_to_ranges[thr_st].start.line
                context = "\n".join(context.split('\n')[:thr_line_index])
                
        check_proof = self.proof_view.check_proof(thr_st, proof, context)
        return check_proof

    def verify_proofs(self, thr_st: str, proofs: List[str]) -> List[Tuple[bool, str]]:
        """
        Verifies k proofs using the ProofView class. Return 
        a list of tuples (bool, str) where the first element
        is the result of the verification and the second is
        the error message if the verification failed.
        Either verification stops when the first proof is
        verified or all proofs are verified and failed.
        """
        context = ""
        if self.statements_to_ranges is not None:
            with open(self.coq_file, "r") as f:
                context = f.read()                
                thr_line_index = self.statements_to_ranges[thr_st].start.line
                context = "\n".join(context.split('\n')[:thr_line_index])
                
        result = self.proof_view.check_proofs(context, thr_st, proofs)
        return result
    
    def get_theorems_for_evaluation(self) -> List[str]:
        """
        Returns the list of theorems on which we 
        want to evaluate the LLM.
        """
        return [theorem.statement for theorem in self.theorems_for_eval]

    def restart_proof_view(self) -> None:
        """
        Restarts the ProofView class.
        """
        self.proof_view = ProofView(self.coq_file, self.root_dir)
    
    def stop(self) -> None: 
        """
        Free up resources.
        """
        self.proof_view.exit()