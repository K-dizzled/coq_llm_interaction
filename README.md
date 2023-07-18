# Coq-LLM interaction
An environment for convenient evaluation of the performance of different LLMs with various configurations and prompts to solve the problem of generating proofs for theorems, written in Coq. 

## Installation
Create the `.env` file in the root directory and place your openai api key there: 
```
OPENAI_API_KEY="{your key here}"
```

To install the required packages: 
```
python3 -r requirements.txt
```

To update the underlying submodule with coq-lsp-client: 
```
git submodule update --remote coqpylspclient
```

## Usage
This package provides a set of convenient interfaces and tools for evaluating the performance of LLMs on the task of generating proofs for theorems. Evaluation is configured with an instance of the `LLMPromptInterface` class and a given LLM, e.g. `GPT35`. 

The two key methods of the `LLMPromptInterface` are: 
```python
def get_system_message(self) -> str: 
    pass 

def get_msg_history(self) -> List[Dict[str, str]]:
    pass
```

If one wants to evaluate the performance of gpt, for example, with respect to a given way of prompting it, e.g. single shot / k-shot (passing gpt a number of theorems+proofs to learn from) / k-shot with context embedded into proofs, etc., one needs to implement the `LLMPromptInterface` interface.

Basic implementation of the `LLMPromptInterface` is presented as `CoqPromptKShot` which takes a coq file and two lists of strings as input. Theorems with names from the first list are looked up in the file and are preprocessed to a form of messages history: 
```json
{
    "role": "user",
    "content": "Theorem ...",
},
{
    "role": "assistant",
    "content": "Proof ...",
}, 
```
And theorems from the second list are given to the assistants to evaluate performance. *VERY important:* 
theorems from both list *MUST* be ordered in the same way as they are in the file.

To run a basic check of how things work, take a look at the `__main__` file in `src`:
```
python3 -m src
``` 

To run the interactor which evaluates the performance, configure it and run `run`. You can also set the amount of attempts LLM has to generate a proof for a given theorem. Each time we try to check the proof via coq-lsp and either continue the process or move on to the next theorem.

Logs are stored in the `logs` directory and each log file is of the following format: 

```coq
(*
 Date: ...
 Strat: ...
*)

(* Start context *)
(* ... *)
(* End context *)

(* Attempt i for theorem j *)
Theorem test : forall (A : Prop), A -> A. (* some theorem *)
Proof.
    auto. (* some proof *)
Qed.
(* Attempt i for theorem j successful / unsuccessful *)
```