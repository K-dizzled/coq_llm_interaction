from ..coqpylspclient import ProofView 
from ..coqpylspclient.coqlspclient.coq_lsp_structs import Theorem
import sys
import re
import random
from typing import List

path_to_coq_file: str = sys.argv[1]
path_to_root_dir: str = sys.argv[2]
gpt_token_limit: str = sys.argv[3]

progress_indicator_msg_prefix: str = sys.argv[4]
return_start_msg: str = sys.argv[5]
return_end_msg: str = sys.argv[6]

proof_view = ProofView(path_to_coq_file, path_to_root_dir)
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