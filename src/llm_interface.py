from typing import List, Dict

class LLMInterface:
    def __init__(self, prompt: str, api_key: str, message_history: List[Dict[str, str]] = []) -> None:
        """
        Constructs a new LLMInterface object. Initializes the LLM 
        with a given system_message.append(message_history). 

        :param prompt: The initial system_message to configure the LLM. 
        :param api_key: The API key for the LLM. 
        :param message_history: A list of messages comprising the conversation so far.
            By default it is empty.
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