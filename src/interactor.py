from .llm_interface import LLMInterface
from .llm_prompt_interface import LLMPromptInterface, ProofViewError
from .eval_logger import EvalLogger
import time
from typing import Tuple

class Interactor: 
    def __init__(
        self, 
        llm_prompt: LLMPromptInterface, 
        llm_interface: LLMInterface, 
        is_silent: bool = False
    ) -> None: 
        self.llm_prompt = llm_prompt
        self.llm_interface = llm_interface
        self.llm_interface.init_history(llm_prompt)
        self.log_f_path = None
        self.contents = None
        self.contents_pointer = 0
        self.timeout = 20
        self.silent_mode = is_silent
    
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
        run_logger = EvalLogger(
            self.llm_prompt.coq_file, self.llm_prompt.prompt_strategy, 
            shots, self.llm_prompt.statements_to_ranges, silent_mode=self.silent_mode
        )

        statements = self.llm_prompt.get_theorems_for_evaluation()
        successfull_proofs = 0
        for thr_index, statement in enumerate(statements):
            # run_logger.log("Await to not bump into the tocken limit")
            # time.sleep(self.timeout)
            run_logger.on_start_llm_response_fetch(thr_index, len(statements))
            llm_response = self.llm_interface.send_message_wout_history_change(
                message=statement, 
                choices=shots
            )
            run_logger.on_end_llm_response_fetch()
            run_logger.on_theorem_proof_start()

            verify_proofs_attempts = 3
            proof_check_result = []
            while verify_proofs_attempts > 0:
                try: 
                    proof_check_result = self.llm_prompt.verify_proofs(statement, llm_response)
                    break
                except ProofViewError as e:
                    verify_proofs_attempts -= 1
                    run_logger.on_proof_check_fail(e.message)
                    run_logger.on_start_llm_response_fetch(thr_index, len(statements))
                    llm_response = self.llm_interface.send_message_wout_history_change(
                        message=statement, 
                        choices=shots
                    )
                    run_logger.on_end_llm_response_fetch()
                    run_logger.log(llm_response)
                    if verify_proofs_attempts == 0: 
                        raise e
                    else: 
                        continue
                except Exception as e:
                    run_logger.on_attempt_exception(0, thr_index + 1, str(e))
                    run_logger.on_start_llm_response_fetch(thr_index, len(statements))
                    llm_response = self.llm_interface.send_message_wout_history_change(
                        message=statement, 
                        choices=shots
                    )
                    run_logger.on_end_llm_response_fetch()
                    run_logger.log(llm_response)
                    self.llm_prompt.restart_proof_view()

            for i, (proof_status, error_msg) in enumerate(proof_check_result):
                if proof_status: 
                    successfull_proofs += 1
                    run_logger.on_success_attempt(
                        i + 1, thr_index + 1, 
                        statement, llm_response[i]
                    )
                else: 
                    run_logger.on_failed_attempt(
                        i + 1, thr_index + 1, 
                        statement, llm_response[i], error_msg
                    )
            
            run_logger.on_theorem_proof_end(statement, self.llm_prompt.correct_proofs[statement])
    
        run_logger.on_evaluation_finish()

        return successfull_proofs / len(statements) if len(statements) != 0 else 0
                    