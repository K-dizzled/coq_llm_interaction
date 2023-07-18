from src.interactor import Interactor
from src.gpt35 import GPT35
import dotenv
from src.coq_llm_prompt import CoqPromptBasic, CoqPromptKShot
import os 

training_file = os.path.join("resources", "sf_train.v")
evaluation_file = os.path.join("resources", "sf_test.v")
llm_prompt = CoqPromptKShot(training_file, evaluation_file)

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_interface = GPT35(OPENAI_API_KEY)
interactor = Interactor(llm_prompt, llm_interface)

print(interactor.run(shots=10, log_attempts=True))

llm_prompt.stop()