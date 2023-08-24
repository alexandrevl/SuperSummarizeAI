import openai
from dotenv import load_dotenv
import os

load_dotenv()

def chatgpt(text):
    try:
        openai.api_key = os.getenv("OPENAI_KEY")
        system_text = """
    Os dados abaixo foram extraidos de um site da internet. Faça um resumo desses dados em PT-BR. Devolva como um JSON no seguinte formato:
    {
        titulo: "Titulo do artigo",
        resumo: "Resumo do artigo"
    }
        """
        response_openai = openai.ChatCompletion.create(
            model='gpt-4',
            # model='gpt-3.5-turbo-16k',
            # model='gpt-4-32k', 
            messages=[{"role": "user", "content": system_text + text}], 
        )
        response_message = response_openai.choices[0].message.content
    except Exception as e:
        # print("Error: ", e)
        response_message = "Error: " + str(e)
    return response_message



