#!python
import requests
from bs4 import BeautifulSoup
import json
import pyperclip
import sys
import subprocess
import urllib3

import openai
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def chatgpt(text, source):
    try:
        openai.api_key = os.getenv("OPENAI_KEY")

        if source == "youtube":
            system_text = """
    Os dados abaixo são a transcrição de um vídeo do YouTube. Faça um resumo desses dados em português do brasil. Devolva como um JSON no seguinte formato:
    {
        titulo: "Titulo do seu resumo",
        resumo: "Resumo do vídeo"
    }
            """
        else:
            system_text = """
    Os dados abaixo foram extraidos de um site da internet. Faça um resumo desses dados em português do brasil. Devolva como um JSON no seguinte formato:
    {
        titulo: "Titulo do seu resumo",
        resumo: "Resumo do artigo"
    }
            """

        response_openai = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{"role": "user", "content": system_text + text}], 
        )
        response_message = response_openai.choices[0].message.content
    except Exception as e:
        response_message = "Error: " + str(e)
    return response_message

def main():
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        print("Please provide a URL as a command line argument.")
        sys.exit(1)
        
    print("Extracting text from url:", url)

    # Check if the URL is a YouTube URL
    if "youtube.com" in url or "youtu.be" in url:
        text = extract_transcript(url)
        source = "youtube"
    else:
        text = extract_text_from_url(url)
        source = "website"

    if text is None:
        print("Failed to extract text from url:", url)
        sys.exit(1)
    print ("Text extracted")
    print("Processing chatGPT")
    chatgpt_result = chatgpt(text, source)
    print("End of processing chatGPT")
    try:
        chatgpt_json = json.loads(chatgpt_result)
    except Exception as e:
        print("Error: ", e)
        chatgpt_json = {
            "titulo": "Error",
            "resumo": chatgpt_result
        }
    title = chatgpt_json.get('titulo', 'Title Not Found')
    copy_to_clipboard(format_text(url,chatgpt_json))


def format_text(url, text):
    title = text.get('titulo', 'Title Not Found')
    resume = text.get('resumo', 'Summary Not Found')
    # titulo = f"##*{titulo}*"
    formatted_text = f"{title}\n\n{resume}\n\n{url}"
    return formatted_text

def extract_text_from_url(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }

    response = requests.get(url, headers=headers, verify=False)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return
    soup = BeautifulSoup(response.content, 'html.parser')
    paragraphs = soup.find_all('p')
    text = ' '.join([p.get_text() for p in paragraphs])
    return text

def extract_transcript(video_url):
    video_id = video_url.split("v=")[1].split("&")[0]
    text = ""  # This will hold the transcript text
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcripts = list(transcript_list)

        # Try to get the English transcript
        try:
            transcript = transcript_list.find_transcript(['en'])
        except:
            # If English transcript is not available, get the first transcript in the list
            transcript = transcripts[0]

        fetched_transcript = transcript.fetch()
        for entry in fetched_transcript:
            text += f"{round(entry['start'],2)} - {round((entry['start'] + entry['duration']),2)}: {entry['text']}\n"
    except Exception as e:
        print(f"An error occurred: {e}")
    return text

def copy_to_clipboard(text):
    pyperclip.copy(text)
    print("-------------------")
    print(text)
    print("-------------------")
    print(f'Copied to clipboard')

def notify(title, text):
    """Send a macOS notification."""
    applescript = f'display notification "{text}" with title "{title}"'
    subprocess.run(["osascript", "-e", applescript])

if __name__ == "__main__":
    main()
