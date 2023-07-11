from llm_prompt_interface import LLMPromptInterface
from typing import List, Dict

class CoqPromptBasic(LLMPromptInterface): 
    def __init__(self, path_to_coq_file: str) -> None: 
        self.coq_file = path_to_coq_file

    def get_system_message(self) -> str: 
        return ('Generate proof of the theorem from user input in Coq. '
                'You should only generate proofs in Coq.'
               )

    def get_msg_history(self) -> List[Dict[str, str]]:
        return []