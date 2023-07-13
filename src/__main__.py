from src.interactor import Interactor
from src.gpt35 import GPT35
import dotenv
from src.coq_llm_prompt import CoqPromptBasic
import os 

evaluation_file = os.path.join("../coqpylspclient/tests/resources", "aux.v")
llm_prompt = CoqPromptBasic(evaluation_file)

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_interface = GPT35(OPENAI_API_KEY, llm_prompt)
interactor = Interactor(llm_prompt, llm_interface)

print(interactor.run(shots=1, log_attempts=True))

llm_prompt.stop()