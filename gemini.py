"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""
import os
import google.generativeai as genai

class gmini_ai:
    """
    Initializes an instance of the class with the provided API key and AI model.

    Args:
        api_key (str): The API key for accessing the generative AI service.
        ai_model (str): The name of the AI model to be used for generating responses.

    Initializes the following instance variables:
        - genai: The Google Generative AI library.
        - api_key: The provided API key.
        - generation_config: A dictionary containing the configuration for response generation.
        - safety_settings: A list of dictionaries specifying the safety settings for the AI model.
        - model: An instance of the GenerativeModel class from the Google Generative AI library.
        - chat_session: A chat session object for interacting with the AI model.

    Note:
        - The `generation_config` dictionary specifies the temperature, top_p, top_k, max_output_tokens, and response_mime_type for response generation.
        - The `safety_settings` list specifies the categories and thresholds for safety settings.
        - The `model` is initialized with the provided AI model name, generation configuration, and safety settings.
        - The `chat_session` is started with an empty history.

    """
    def __init__(self, api_key: str, ai_model:str):
        self.genai = genai
        self.api_key = api_key
        self.genai.configure(api_key=self.api_key)
    # Set up the model
        self.generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        # "top_k": 0,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
        }

        self.safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_MEDIUM_AND_ABOVE"
        },
        ]

        self.model = self.genai.GenerativeModel(model_name=ai_model,
                                    generation_config=self.generation_config,
                                    safety_settings=self.safety_settings)
        # self.model = self.genai.GenerativeModel(model_name="gemini-1.5-flash-latest",
        #                             generation_config=self.generation_config,
        #                             safety_settings=self.safety_settings)

        self.chat_session = self.model.start_chat(history=[
        ])
    
    def send_message(self, msg: str) -> str:
        """Send a message and return the response in one line."""
        response = self.chat_session.send_message(msg)
        # print(self.convo)
        # return self.convo.last.text
        return response.text

# input = input("Input: ")
# import os
# from dotenv import load_dotenv
# load_dotenv()
# ap = os.getenv("GEMINI")
# print(gmini_ai(api_key=ap).send_message(input))