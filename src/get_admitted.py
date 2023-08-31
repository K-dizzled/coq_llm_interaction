from ..coqpylspclient import ProofView 
from ..coqpylspclient.coqlspclient.coq_lsp_structs import Theorem
from ..coqpylspclient.coqlspclient.progress_bar import StdoutProgressBar
import sys
import re
import random
from typing import List

"""
Path to the coq file from the editor and path to the workspace folder
with the _CoqProject.
"""
path_to_coq_file: str = sys.argv[1]
path_to_root_dir: str = sys.argv[2]

"""
The number of tokens that gpt can process in a single request.
"""
gpt_token_limit: str = sys.argv[3]

"""
System messages to parse the logs. 
"""
progress_indicator_start_msg: str = sys.argv[4]
progress_indicator_end_msg: str = sys.argv[5]
progress_update_msg: str = sys.argv[6]
progress_log_every_n_percent: int = int(sys.argv[7])

"""
System messages to identify when the return data of the script starts and ends.
"""
return_start_msg: str = sys.argv[8]
return_end_msg: str = sys.argv[9]

progress_bar = StdoutProgressBar(
    progress_indicator_start_msg, progress_indicator_end_msg, 
    progress_update_msg, progress_log_every_n_percent
)

proof_view = ProofView(path_to_coq_file, path_to_root_dir, prog_bar=progress_bar)
all_theorems = proof_view.parse_file()

admitted_theorems: List[str] = []
rest_theorems_aux: List[Theorem] = []

"""
When we send a request to gpt, it has an upper limit on the number of tokens.
Number of tokens in our case, as we make a request for a single theorem not continuing the 
chat, will be system_message.size + all_theorems_statements_with_proofs.size + new_statement.size

When working with huge files, we cannot send all the solved theorems from the 
file as "train" theorems, because we will reach the token limit. This is why we need to 
heuristically choose the train theorems. For now we will choose theorems randomly. 
"""
admitted_theorems_max_tokens: int = 0
theorems_tokens_sum: int = 0

for theorem in all_theorems:
    if theorem.proof is None:
        continue

    if theorem.proof.is_incomplete:
        admitted_theorems_max_tokens = max(
            admitted_theorems_max_tokens, 
            len(re.findall(r'\s', theorem.statement))
        )
        admitted_theorems.append(theorem.name)
    else:
        # Count the number of tokens using the \s regex that counts all 
        # whitespace symbols (spaces, tabs, newlines)
        theorems_tokens_sum += len(
            re.findall(r'\s', theorem.statement + theorem.proof.only_text())
        )
        rest_theorems_aux.append(theorem)

"""
We collected all the solved theorems from the file to an auxiliary list, we 
shuffle it and then pop theorems from it until the sum of their tokens + maximum
possible statement.size is greater than the token limit.
"""

theorems_tokens_sum += admitted_theorems_max_tokens
random.shuffle(rest_theorems_aux)
while theorems_tokens_sum > 0.9 * int(gpt_token_limit) and len(rest_theorems_aux) > 0:
    theorem = rest_theorems_aux.pop()
    if theorem.proof is None:
        continue

    theorems_tokens_sum -= len(
        re.findall(r'\s', theorem.statement + theorem.proof.only_text())
    )

rest_theorems = [theorem.name for theorem in rest_theorems_aux]

# Return block: 
print(return_start_msg)
for theorem in admitted_theorems:
    print(theorem)
print(return_end_msg)
print(return_start_msg)
for theorem in rest_theorems:
    print(theorem)
print(return_end_msg)

# Post processing block:
proof_view.exit()