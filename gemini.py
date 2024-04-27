"""
At the command line, only need to run once to install the package via pip:

$ pip install google-generativeai
"""
import google.generativeai as genai

class gmini_ai:
    def __init__(self, api_key: str):
        self.genai = genai
        self.api_key = api_key
        self.genai.configure(api_key=self.api_key)
    # Set up the model
        self.generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 0,
        "max_output_tokens": 8192,
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

        self.model = self.genai.GenerativeModel(model_name="gemini-1.5-pro-latest",
                                    generation_config=self.generation_config,
                                    safety_settings=self.safety_settings)

        self.convo = self.model.start_chat(history=[
        ])
    
    def send_message(self, msg: str) -> str:
        """Send a message and return the response in one line."""
        self.convo.send_message(msg)
        # print(self.convo)
        return self.convo.last.text

# input = input("Input: ")
# import os
# from dotenv import load_dotenv
# load_dotenv()
# ap = os.getenv("GEMINI")
# print(gmini_ai(api_key=ap).send_message(input))