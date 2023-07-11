from typing import List, Dict

class LLMPromptInterface:
    def get_system_message(self) -> str: 
        """
        Gets the system message for the LLM. 
        """
        pass

    def get_msg_history(self) -> List[Dict[str, str]]:
        """
        Gets the message history for the LLM. 
        """
        pass