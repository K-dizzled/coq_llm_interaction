from . import Interactor
from . import GPT35
import dotenv
from . import CoqPromptSolveAdmitted
import os 
import sys

coq_file = sys.argv[1]
root_dir = sys.argv[2]

llm_prompt = CoqPromptSolveAdmitted(coq_file, root_dir)

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_interface = GPT35(OPENAI_API_KEY)
interactor = Interactor(llm_prompt, llm_interface, is_silent=True)

llm_prompt.stop()