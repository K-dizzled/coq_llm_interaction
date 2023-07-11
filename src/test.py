import sys
import os

sys.path.insert(1, '../coqpylspclient')

from coqlspclient.proof_view import ProofView

sys.path.pop()

# Create an instance of a coq-lsp client and initialize it.
file_path = os.path.join("../coqpylspclient/tests/resources", "aux.v")
pv = ProofView(file_path)

print(pv.all_theorem_names())

pv.exit()

