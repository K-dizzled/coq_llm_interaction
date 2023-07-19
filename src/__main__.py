from src.interactor import Interactor
from src.gpt35 import GPT35
import dotenv
from src.coq_llm_prompt import CoqPromptKShot
import os 

coq_file = os.path.join("coqpylspclient/tests/resources", "test_basic_sf.v")
train_thrs = [
    'plus_O_n', "plus_O_n'", "plus_O_n''", 'plus_1_l', 'mult_0_l', 
    'plus_id_example', 'plus_id_exercise', 'mult_n_0_m_0', 
    'mult_n_1', 'plus_1_neq_0_firsttry', 'plus_1_neq_0', 
    'negb_involutive', 'andb_commutative', "andb_commutative'", 
    'andb3_exchange'
]
test_thrs = [
    'andb_true_elim2', "plus_1_neq_0'", 
    "andb_commutative''", 'zero_nbeq_plus_1', 'identity_fn_applied_twice', 
    'negation_fn_applied_twice', 'andb_eq_orb'
]
# coq_file = os.path.join("coqpylspclient/tests/resources", "aux.v")
llm_prompt = CoqPromptKShot(coq_file, train_thrs, test_thrs)

dotenv.load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

llm_interface = GPT35(OPENAI_API_KEY)
interactor = Interactor(llm_prompt, llm_interface)

print(interactor.run(shots=10))

llm_prompt.stop()