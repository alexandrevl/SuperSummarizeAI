#!python
import requests
from bs4 import BeautifulSoup
import json
import pyperclip
import sys
import subprocess
import urllib3
import tiktoken

import openai
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def encoding_getter(encoding_type: str):
    """
    Returns the appropriate encoding based on the given encoding type (either an encoding string or a model name).
    """
    if "k_base" in encoding_type:
        return tiktoken.get_encoding(encoding_type)
    else:
        return tiktoken.encoding_for_model(encoding_type)

def tokenizer(string: str, encoding_type: str) -> list:
    """
    Returns the tokens in a text string using the specified encoding.
    """
    encoding = encoding_getter(encoding_type)
    tokens = encoding.encode(string)
    return tokens

def token_counter(string: str, encoding_type: str) -> int:
    """
    Returns the number of tokens in a text string using the specified encoding.
    """
    num_tokens = len(tokenizer(string, encoding_type))
    return num_tokens

def truncate_to_max_tokens(text: str, max_tokens: int = 8180, encoding_type: str = "cl100k_base") -> str:
    """
    Truncates the text to a specified number of tokens.
    """
    tokens = tokenizer(text, encoding_type)
    if len(tokens) <= max_tokens:
        return text
    
    # Convert tokens back to text
    reconstructed_text = encoding_getter(encoding_type).decode(tokens)
    
    # Re-tokenize and truncate the text iteratively until it fits within the max_tokens limit
    while len(tokenizer(reconstructed_text, encoding_type)) > max_tokens:
        reconstructed_text = reconstructed_text[:-1]
    
    return reconstructed_text



def chatgpt(text, source):
    try:
        openai.api_key = os.getenv("OPENAI_KEY")
        # To get the tokeniser corresponding to a specific model in the OpenAI API:

        if source == "youtube":
            system_text = """
    The data below is a transcript from a YouTube video. Please summarize this data in brazilian portuguese. Return the result as a JSON in the following format:
    {
        title: "Title of your summary",
        summary: "Summary of the video"
    }
            """
        else:
            system_text = """
    The data below was extracted from a website. Please summarize this data in brazilian portuguese. Return the result as a JSON in the following format:
    {
        title: "Title of your summary",
        summary: "Summary of the article"
    }
            """
        # print(len(tokenizer(system_text + text,"cl100k_base")))
        # print("Adjusting text to max tokens")
        # text = truncate_to_max_tokens(system_text + text)
        # print(len(tokenizer(text,"cl100k_base")))
        # print("Adjusting text to max tokens")
        text_to_chatgpt = system_text + text
        response_openai = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{"role": "user", "content": text_to_chatgpt}], 
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
        
    print("Extracting data from url:", url)

    # Check if the URL is a YouTube URL
    if "youtube.com" in url or "youtu.be" in url:
        text = extract_transcript(url)
        source = "youtube"
    else:
        text = extract_text_from_url(url)
        source = "website"

    if text is None:
        print("Failed to extract data from url:", url)
        sys.exit(1)
    print ("Text extracted ("+source+")")
    print("Processing chatGPT")
    chatgpt_result = chatgpt(text, source)
    print("End of processing chatGPT")
    try:
        chatgpt_json = json.loads(chatgpt_result)
    except Exception as e:
        print("Error: ", e)
        chatgpt_json = {
            "title": "Error",
            "summary": chatgpt_result
        }
    title = chatgpt_json.get('title', 'Title Not Found')
    copy_to_clipboard(format_text(url,chatgpt_json))


def format_text(url, text):
    title = text.get('title', 'Title Not Found')
    summary = text.get('summary', 'Summary Not Found')
    formatted_text = f"{title}\n\n{summary}\n\n{url}"
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
