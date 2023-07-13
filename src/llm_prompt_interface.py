from typing import List, Dict, Optional

class LLMPromptInterface:
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

    def verify_proof(self, thr_st: str, proof: str) -> bool: 
        """
        Verifies the proof using the ProofView class.
        """
        pass

    def get_theorems_for_evaluation(self) -> List[str]:
        """
        Returns the list of theorems on which we 
        want to evaluate the LLM.
        """
        pass

    def get_context_for_log(self) -> str: 
        """
        Coq context to be added to the log fil preceding the proof.
        """
        pass

    def stop(self) -> None: 
        """
        Free up resources.
        """
        pass