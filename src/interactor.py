from src.llm_interface import LLMInterface
from src.llm_prompt_interface import LLMPromptInterface
from datetime import datetime
from alive_progress import alive_bar
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Interactor")

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
                log_file.write(f"(*\n Date: {date_time_now}\n Strat: {self.llm_prompt.prompt_strategy}\n*)\n\n")
                context = self.llm_prompt.get_context_for_log()
                log_file.write(f"(* Start context *)\n{context}\n(* End context *)\n\n")

        statements = self.llm_prompt.get_theorems_for_evaluation()
        successfull_proofs = 0
        for thr_index, statement in enumerate(statements):
            logger.info(f"Fetching potential proofs for theorem {thr_index + 1}/{len(statements)}")
            llm_response = self.llm_interface.send_message_wout_history_change(
                message=statement, 
                choices=shots
            )
            with alive_bar(len(llm_response)) as bar:
                for response_index, response in enumerate(llm_response):
                    if log_attempts:
                        self.__log(f"(* Attempt {response_index + 1} for theorem {thr_index + 1} *)\n")

                    proof_status, error_msg = self.llm_prompt.verify_proof(statement, response)
                    if proof_status:
                        successfull_proofs += 1
                        if log_attempts:
                            self.__log(f"{statement}\n{response}\n")
                            self.__log(f"(* Attempt {response_index + 1} for theorem {thr_index + 1} successful *)\n\n")
                            logger.info(f"Attempt {response_index + 1} for theorem {thr_index + 1} successful")
                        break
                    else:
                        if log_attempts:
                            self.__log(f"(*\n{statement}\n{response}\n*)\n")
                            self.__log(f"(* Attempt {response_index + 1} for theorem {thr_index + 1} unsuccessful *)\n")
                            self.__log(f"(* ERROR message: {error_msg} *)\n\n")
                    bar()


        return successfull_proofs / len(statements)
                    