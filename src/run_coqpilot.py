from .interactor import Interactor
from .gpt35 import GPT35
from .coq_llm_prompt import CoqPromptSingleTheorem
from ..coqpylspclient.coqlspclient.progress_bar import StdoutProgressBar
from .eval_logger import StdoutLoggingSetup
import sys
from typing import List

"""
Path to the coq file from the editor and path to the workspace folder
with the _CoqProject.
"""
path_to_coq_file: str = sys.argv[1]
path_to_root_dir: str = sys.argv[2]

"""
The key of the OpenAI API  and the number of attempts to solve a single theorem.
"""
openai_api_key = sys.argv[3]
number_of_shots = int(sys.argv[4])

"""
Name of the theorem to solve and a list of theorems to use as train theorems.
Train theorems must be separated by a comma (without spaces).
"""
theorem_to_solve: str = sys.argv[5]
# If equal to "EMPTY", then empty list is used.
train_theorems: List[str] = sys.argv[6].split(",") if sys.argv[6] != "EMPTY" else []

"""
System messages to parse the logs. 
"""
progress_indicator_start_msg: str = sys.argv[7]
progress_indicator_end_msg: str = sys.argv[8]
progress_update_msg: str = sys.argv[9]
progress_log_every_n_percent: int = int(sys.argv[10])

"""
System messages to identify when the return data of the script starts and ends.
"""
return_start_msg: str = sys.argv[11]
return_end_msg: str = sys.argv[12]
return_failure_msg: str = sys.argv[13]

progress_bar = StdoutProgressBar(
    progress_indicator_start_msg, progress_indicator_end_msg, 
    progress_update_msg, progress_log_every_n_percent
)

llm_prompt = CoqPromptSingleTheorem(
    path_to_coq_file, path_to_root_dir, 
    train_theorems, theorem_to_solve, 
    progress_bar=progress_bar
)

logging_setup = StdoutLoggingSetup(
    return_start_msg, return_end_msg, return_failure_msg
)

llm_interface = GPT35(openai_api_key)
interactor = Interactor(
    llm_prompt, llm_interface, 
    is_silent=True, logging_setup=logging_setup
)

interactor.run(shots=number_of_shots)

llm_prompt.stop()