import openai
from config import Config

class OpenAIService:
    """
    A service class to handle OpenAI API interactions.
    """
    @staticmethod
    def generate_completion(prompt: str, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Generate a completion for the given prompt using the OpenAI API.

        Args:
            prompt (str): The input prompt.
            max_tokens (int): The maximum number of tokens to include in the completion.
            temperature (float): Sampling temperature to control randomness (0.0 to 1.0).

        Returns:
            str: The generated text completion.
        """
        try:
            openai.api_key = Config.OPENAI_API_KEY
            model = Config.OPENAI_API_MODEL
            response = openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise

    @staticmethod
    def generate_completion_message(messages: list, max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Generate a completion for the given message using the OpenAI API.

        Args:
            messages (list): The input messages.
            max_tokens (int): The maximum number of tokens to include in the completion.
            temperature (float): Sampling temperature to control randomness (0.0 to 1.0).

        Returns:
            str: The generated text completion.
        """
        try:
            openai.api_key = Config.OPENAI_API_KEY
            model = Config.OPENAI_API_MODEL
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise



if __name__ == '__main__':
    openai_service = OpenAIService()
    
    # Example usage of generate_completion
    prompt = "Hello, how are you?"
    completion = openai_service.generate_completion(prompt)
    print(f"Generated completion: {completion}")
    
    # Example usage of generate_completion_message
    messages = [{"role": "user", "content": "Hello, how are you?"}]
    completion_message = openai_service.generate_completion_message(messages)
    print(f"Generated message: {completion_message}")