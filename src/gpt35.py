from llm_interface import LLMInterface
from typing import List, Dict
import openai

class GPT35(LLMInterface):
    def __init__(self, prompt: str, api_key: str, message_history: List[Dict[str, str]] = []) -> None:
        self.history = []
        self.history.append( {"role": "system", "content": prompt} )
        self.history.extend(message_history)
        self.model = "gpt-3.5-turbo-0301"
        openai.api_key = api_key

    def __accept_message(self, message: str) -> None:
        self.history.append({"role": "user", "content": message})

    def __get_next_responses(self, choices: int = 1) -> List[str]:
        completion = openai.ChatCompletion.create(
            model=self.model, 
            messages=self.history,
            n=choices
        )

        best_response = completion['choices'][0]['message']['content']
        self.history.append({"role": "assistant", "content": best_response})

        return [choice['message']['content'] for choice in completion["choices"]]


    def send_message_for_response(self, message: str, choices: int = 1) -> List[str]:
        self.__accept_message(message)
        return self.__get_next_responses(choices=choices)