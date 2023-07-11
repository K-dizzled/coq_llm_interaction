from src.llm_interface import LLMInterface
from src.llm_prompt_interface import LLMPromptInterface

class Interactor: 
    def __init__(
        self, 
        llm_model: LLMPromptInterface, 
        llm_interface: LLMInterface
    ) -> None: 
        self.llm_model = llm_model
        self.llm_interface = llm_interface