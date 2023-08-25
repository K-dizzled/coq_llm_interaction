from datetime import datetime
import plotly.graph_objects as go
from abc import abstractmethod
from .llm_prompt_interface import Range, Position
from typing import Dict, List, Tuple
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EvalLogger")


class EvalLoggerException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message


class EvalLogger: 
    def __init__(
        self, 
        coq_file_path: str, 
        run_strategy: str, 
        shots: int, 
        statements2ranges: Dict[str, Range], 
        silent_mode: bool = False
    ) -> None: 
        self.coq_file = coq_file_path
        date_time_now = datetime.now().strftime("%d_%m__%H_%M_%S")      
        if not silent_mode:  
            if not os.path.exists("logs"):
                os.makedirs("logs")
            
            self.log_f_path = f"logs/log_{date_time_now}.v"
            self.log_pie_path = f"logs/pie_{date_time_now}.pdf"
            with open(self.log_f_path, "w") as log_file:
                log_file.write(f"(*\n Date: {date_time_now}\n Strat: {run_strategy}\n*)\n\n")
        with open(self.coq_file, "r") as coq_file:
            self.contents = coq_file.read().split('\n')

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
        self.statements_to_ranges = statements2ranges
        self.ranges_to_text = {}
        self.silent_mode = silent_mode

    def __log(self, text: str) -> None: 
        with open(self.log_f_path, "a") as f:
            f.write(text)

    def log(self, text: str) -> None: 
        logger.info(text)

    def __get_text_in_range(
        self, 
        start: Position, 
        end: Position, 
        preserve_line_breaks: bool = True
    ) -> str:
        if start.line == end.line: 
            return self.contents[start.line][start.character:end.character]
        else: 
            text = self.contents[start.line][start.character:]
            for i in range(start.line + 1, end.line):
                if preserve_line_breaks: 
                    text += '\n'
                text += self.contents[i]
            if preserve_line_breaks:
                text += '\n'
            text += self.contents[end.line][:end.character]

            return text

    def __substitute_text_pieces(self) -> str: 
        """
        Iterates over self.contents and substitutes
        the ranges from self.ranges_to_text with 
        the corresponding text. 
        """
        new_text = ""
        ranges_text_pairs: List[Tuple[Range, str]] = list(self.ranges_to_text.items())
        ranges_text_pairs.sort(key=lambda x: (x[0].start.line, x[0].start.character))
        last_range_end_pos = Position(0, 0)
        for (range_, text_piece) in ranges_text_pairs:
            # Add the text between the last range and the start of the current range
            new_text += self.__get_text_in_range(last_range_end_pos, range_.start)
            # Add the text of the current range
            new_text += text_piece
            last_range_end_pos = range_.end

        # Add the text after the last range
        new_text += self.__get_text_in_range(
            last_range_end_pos, 
            Position(len(self.contents) - 1, len(self.contents[-1]))
        )
        return new_text
        
    def on_start_llm_response_fetch(self, thr_index: int, am_theorems: int) -> None: 
        logger.info(f"Fetching potential proofs for theorem {thr_index + 1}/{am_theorems}")

    def on_end_llm_response_fetch(self) -> None:
        logger.info("Fetching potential proofs finished")

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

        if self.silent_mode:
            needed_range = self.statements_to_ranges[statement]
            self.ranges_to_text[needed_range] = f"{statement}\n{proof}"
    
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
    
    def on_attempt_exception(self, attempt_ind: int, thr_ind: int, error_msg: str) -> None:
        if not self.in_proof: 
            raise EvalLoggerException("Not in proof")
        self.proof_log += f"(* Attempt {attempt_ind} for theorem {thr_ind} failed with an exception*)\n"
        self.proof_log += f"(* EXCEPTION message: {error_msg} *)\n\n"
        logger.info(f"Attempt {attempt_ind} for theorem {thr_ind} failed with an exception")

    def on_proof_check_fail(self, error_msg: str) -> None:
        if not self.in_proof: 
            raise EvalLoggerException("Not in proof")
        self.proof_log += f"(* ProofView responded with an error: {error_msg} *)\n"

    def on_theorem_proof_end(self, statement: str, correct_proof: str) -> None: 
        if not self.in_proof: 
            raise EvalLoggerException("Not in proof")
        if not self.proof_complete: 
            self.values[-1] += 1
            self.proof_log += f"(* Correct proof was not found. Here is the one from original file. *)\n"
            self.proof_log += f"{statement}\n{correct_proof}\n"
            self.proof_log += "(* {THEOREM PROOF LOG END} *)"
            
        self.in_proof = False

        if not self.silent_mode: 
            needed_range = self.statements_to_ranges[statement]
            self.ranges_to_text[needed_range] = self.proof_log

    def on_evaluation_finish(self) -> None: 
        new_text = self.__substitute_text_pieces()

        if not self.silent_mode: 
            fig = go.Figure(data=[go.Pie(labels=self.labels, values=self.values, pull=self.pull)])
            fig.write_image(self.log_pie_path)
            self.__log(new_text)
        else: 
            print("&start&return&message&")
            print(new_text)
            print(("failure" if self.values[:-1] == [0] * len(self.values[:-1]) else "success"))
            print("&end&return&message&")