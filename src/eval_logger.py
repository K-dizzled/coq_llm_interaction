from datetime import datetime
import plotly.graph_objects as go
from abc import abstractmethod
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EvalLogger")


class EvalLoggerException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class EvalLogger: 
    def __init__(self, coq_file_path: str, run_strategy: str, shots: int) -> None: 
        self.coq_file = coq_file_path
        date_time_now = datetime.now().strftime("%d_%m__%H_%M_%S")        
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        self.log_f_path = f"logs/log_{date_time_now}.v"
        self.log_pie_path = f"logs/pie_{date_time_now}.pdf"
        with open(self.log_f_path, "w") as log_file:
            log_file.write(f"(*\n Date: {date_time_now}\n Strat: {run_strategy}\n*)\n\n")
            with open(self.coq_file, "r") as coq_file:
                self.contents = coq_file.read()

        self.labels = []
        self.values = []
        for i in range(shots): 
            self.labels.append(f"Success on attempt {i + 1}")
            self.values.append(0)
        self.labels.append("Failure")
        self.values.append(0)
        self.pull = [0] * (shots + 1)
        self.pull[-1] = 0.2
        self.in_proof = False
        self.proof_log = ""
        self.proof_complete = None
        self.contents_pointer = 0

    def __log(self, text: str) -> None: 
        with open(self.log_f_path, "a") as f:
            f.write(text)

    @abstractmethod
    def __l2r_search(self, text: str, pattern: str, start: int = 0) -> int:
        for i in range(start, len(text)):
            if text[i] == pattern[0]:
                if text[i:i+len(pattern)] == pattern:
                    return i
        
        return len(text)

    def __update_proof_contents_with_new_text(self, statement: str, text: str) -> None:
        statement_index = self.__l2r_search(self.contents, statement, self.contents_pointer)
        qed_index = self.__l2r_search(self.contents, "Qed.", statement_index)
        admitted_index = self.__l2r_search(self.contents, "Admitted.", statement_index)
        
        indent = 4
        if admitted_index < qed_index:
            qed_index = admitted_index
            indent = 9
        self.contents_pointer = statement_index
        
        # Erase the old proof (contents between 
        # statement_finish_index and qed_index)
        # Then insert the new proof
        updated_contents = self.contents[:statement_index] + \
                           text + \
                           self.contents[qed_index + indent:]
        self.contents = updated_contents
        
    def on_start_llm_response_fetch(self, thr_index: int, am_theorems: int) -> None: 
        logger.info(f"Fetching potential proofs for theorem {thr_index + 1}/{am_theorems}")

    def on_theorem_proof_start(self) -> None:
        if self.in_proof: 
            raise EvalLoggerException("Already in proof")
        self.in_proof = True
        self.proof_complete = False
        self.proof_log = "(* {THEOREM PROOF LOG START} *)\n"

    def on_success_attempt(
        self, attempt_ind: int, 
        thr_ind: int, statement: str, 
        proof: str
    ) -> None:
        if not self.in_proof: 
            raise EvalLoggerException("Not in proof")
        self.proof_log += f"(* Attempt {attempt_ind} for theorem {thr_ind} *)\n"
        self.proof_log += f"{statement}\n{proof}\n"
        
        self.proof_log += f"(* Attempt {attempt_ind} for theorem {thr_ind} successful *)\n\n"
        self.proof_log += "(* {THEOREM PROOF LOG END} *)"
        logger.info(f"Attempt {attempt_ind} for theorem {thr_ind} successful")
        self.values[attempt_ind - 1] += 1
        self.proof_complete = True
    
    def on_failed_attempt(
        self, attempt_ind: int, 
        thr_ind: int, statement: str, 
        proof: str, error_msg: str
    ) -> None: 
        if not self.in_proof: 
            raise EvalLoggerException("Not in proof")
        self.proof_log += f"(* Attempt {attempt_ind} for theorem {thr_ind} *)\n"
        self.proof_log += f"(*\n{statement}\n{proof}\n*)\n"
        
        self.proof_log += f"(* Attempt {attempt_ind} for theorem {thr_ind} unsuccessful *)\n"
        self.proof_log += f"(* ERROR message: {error_msg} *)\n\n"

    def on_theorem_proof_end(self, statement: str) -> None: 
        if not self.in_proof: 
            raise EvalLoggerException("Not in proof")
        if not self.proof_complete: 
            self.values[-1] += 1
            self.proof_log += "(* {THEOREM PROOF LOG END} *)"
            
        self.in_proof = False
        self.__update_proof_contents_with_new_text(statement, self.proof_log)

    def on_evaluation_finish(self) -> None: 
        fig = go.Figure(data=[go.Pie(labels=self.labels, values=self.values, pull=self.pull)])
        fig.write_image(self.log_pie_path)
        self.__log(self.contents)
