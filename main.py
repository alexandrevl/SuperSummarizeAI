#!python3
import requests
from chatgpt import chatgpt
from teams import send_message
from bs4 import BeautifulSoup
import json
import pyperclip
import sys

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Please provide a URL as a command line argument.")
        sys.exit(1)
        
    print("Extracting text from url:", url)
    text = extract_text_from_url(url)
    print ("Text extracted")
    print("Processing chatGPT")
    chatgpt_result = chatgpt(text)
    print("End of processing chatGPT")
    chatgpt_json = json.loads(chatgpt_result)
    copy_to_clipboard(format_text(url,chatgpt_json))

def format_text(url, text):
    titulo = text.get('titulo', 'Title Not Found')
    resumo = text.get('resumo', 'Summary Not Found')
    # titulo = f"##*{titulo}*"
    formatted_text = f"{titulo}\n\n{resumo}\n\n{url}"
    return formatted_text

def extract_text_from_url(url):
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return

    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([p.get_text() for p in paragraphs])
    return text

def copy_to_clipboard(text):
    pyperclip.copy(text)
    print("-------------------")
    print(text)
    print("-------------------")
    print(f'Copied to clipboard')

if __name__ == "__main__":
    main()
