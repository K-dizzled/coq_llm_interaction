from .interactor import Interactor
from .gpt35 import GPT35
import dotenv
from .coq_llm_prompt import CoqPromptSolveAdmitted
import os 
import sys

coq_file = sys.argv[1]
root_dir = sys.argv[2]
openai_api_key = sys.argv[3]
number_of_shots = int(sys.argv[4])

llm_prompt = CoqPromptSolveAdmitted(coq_file, root_dir)

llm_interface = GPT35(openai_api_key)
interactor = Interactor(llm_prompt, llm_interface, is_silent=True)

interactor.run(shots=number_of_shots)

llm_prompt.stop()