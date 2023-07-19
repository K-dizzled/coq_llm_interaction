from src.llm_interface import LLMInterface
from src.llm_prompt_interface import LLMPromptInterface
from src.eval_logger import EvalLogger
from alive_progress import alive_bar

class Interactor: 
    def __init__(
        self, 
        llm_prompt: LLMPromptInterface, 
        llm_interface: LLMInterface, 
    ) -> None: 
        self.llm_prompt = llm_prompt
        self.llm_interface = llm_interface
        self.llm_interface.init_history(llm_prompt)
        self.log_f_path = None
        self.contents = None
        self.contents_pointer = 0
    
    def run(self, shots: int = 1) -> float:
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
        run_logger = EvalLogger(self.llm_prompt.coq_file, self.llm_prompt.prompt_strategy, shots)

        statements = self.llm_prompt.get_theorems_for_evaluation()
        successfull_proofs = 0
        for thr_index, statement in enumerate(statements):
            run_logger.on_start_llm_response_fetch(thr_index, len(statements))
            llm_response = self.llm_interface.send_message_wout_history_change(
                message=statement, 
                choices=shots
            )
            run_logger.on_theorem_proof_start()
            with alive_bar(len(llm_response)) as bar:
                for response_index, response in enumerate(llm_response):
                    proof_status, error_msg = self.llm_prompt.verify_proof(statement, response)
                    if proof_status:
                        successfull_proofs += 1
                        run_logger.on_success_attempt(
                            response_index + 1, thr_index + 1, 
                            statement, response
                        )
                        break
                    else:
                        run_logger.on_failed_attempt(
                            response_index + 1, thr_index + 1, 
                            statement, response, error_msg
                        )
                    bar()
            
            run_logger.on_theorem_proof_end(statement)
    
        run_logger.on_evaluation_finish()

        return successfull_proofs / len(statements) if len(statements) != 0 else 0
                    