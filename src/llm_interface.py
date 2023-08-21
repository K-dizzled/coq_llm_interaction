from typing import List, Dict
from .llm_prompt_interface import LLMPromptInterface

class LLMInterface:
    def __init__(self, api_key: str)  -> None:
        """
        Constructs a new LLMInterface object. Initializes the LLM 
        with a given system_message.append(message_history). 

        :param prompt: The initial system_message to configure the LLM. 
        :param api_key: The API key for the LLM. 
        :param message_history: A list of messages comprising the conversation so far.
            By default it is empty.
        """
        pass 

    def init_history(self, llm_prompt: LLMPromptInterface) -> None:
        """
        Initializes the message history of the LLM. 
        This function should be called after the LLM is initialized. 

        :param llm_prompt: The LLM prompt to use to initialize the message history. 
        """
        pass

    def send_message_for_response(self, message: str, choices: int = 1) -> List[str]: 
        """
        Sends a message to the LLM and returns the response. 

        :param message: The message to send to the LLM.
        :param choices: The number of choices to return. Defaults to 1.
        :return: A list of choices. 
        """
        pass

    def send_message_wout_history_change(self, message: str, choices: int = 1) -> List[str]: 
        """
        Sends a message to the LLM and returns the response. 
        But garantees that the message history after the call 
        remains the same as before the call.

        :param message: The message to send to the LLM.
        :param choices: The number of choices to return. Defaults to 1.
        :return: A list of choices. 
        """
        pass