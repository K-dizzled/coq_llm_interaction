from src.llm_interface import LLMInterface
from src.llm_prompt_interface import LLMPromptInterface
from datetime import datetime
import os

class Interactor: 
    def __init__(
        self, 
        llm_prompt: LLMPromptInterface, 
        llm_interface: LLMInterface, 
    ) -> None: 
        self.llm_prompt = llm_prompt
        self.llm_interface = llm_interface
        self.log_f_path = None

    def __log(self, text: str) -> None: 
        with open(self.log_f_path, "a") as f:
            f.write(text)
        
    def run(self, shots: int = 1, log_attempts: bool = False) -> float:
        """ 
        Retrieves theorems we want to evaluate the LLM on 
        from the LLMPrompt object, then sends them to the
        LLMInterface object for evaluation. 
        Then tries to check the proof returned by the LLM
        using the LLMPrompt object with the ProofView inside.
        Returns the ratio of theorems for which the proof has
        been found successfully to the amount of theorems 
        provided for evaluation.
        """
        if log_attempts:
            date_time_now = datetime.now().strftime("%d_%m__%H_%M_%S")        
            if not os.path.exists("logs"):
                os.makedirs("logs")
            
            self.log_f_path = f"logs/log_{date_time_now}.v"
            with open(self.log_f_path, "w") as log_file:
                log_file.write(f"(*\n    Date: {date_time_now}\n*)\n\n")
                context = self.llm_prompt.get_context_for_log()
                log_file.write(f"(* Start context *)\n{context}\n(* End context *)\n\n")

        statements = self.llm_prompt.get_theorems_for_evaluation()
        successfull_proofs = 0
        for thr_index, statement in enumerate(statements):
            llm_response = self.llm_interface.send_message_wout_history_change(
                message=statement, 
                choices=shots
            )
            print(llm_response)
            for response_index, response in enumerate(llm_response):
                if log_attempts:
                    self.__log(f"(* Attempt {response_index + 1} for theorem {thr_index + 1} *)\n")
                    self.__log(f"{statement}\n{response}\n")

                if self.llm_prompt.verify_proof(statement, response):
                    successfull_proofs += 1
                    if log_attempts:
                        self.__log(f"(* Attempt {response_index + 1} for theorem {thr_index + 1} successful *)\n\n")
                    break
                else:
                    if log_attempts:
                        self.__log(f"(* Attempt {response_index + 1} for theorem {thr_index + 1} unsuccessful *)\n\n")


        return successfull_proofs / len(statements)
                    