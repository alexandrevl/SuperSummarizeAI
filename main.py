#!python
import requests
from bs4 import BeautifulSoup
import json
import pyperclip
import sys
import subprocess
import urllib3
import argparse
from pathlib import Path

import openai
from dotenv import load_dotenv
import os
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
import openai

def parse_arguments():
    parser = argparse.ArgumentParser(description='Summarize a URL using ChatGPT.')
    
    # Making the URL argument positional
    parser.add_argument('url', type=str, help='The URL to be summarized.')
    parser.add_argument('--lang', type=str, default='brazilian portuguese', help='Target language for the summary.', dest='language')
    
    args = parser.parse_args()

    if args.url is None:
        print("No URL specified. Use <URL to be summarized>")
        exit(1)

    return args

def main():
    args = parse_arguments()

    url = args.url
    target_language = args.language
    
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
        exit(1)
    print ("Data extracted ("+source+")")
    print(f"Creating ChatGPT summary in {target_language}. This may take a while...")
    chatgpt_result = chatgpt(text, source, target_language)
    print("ChatGPT summary done")
    try:
        chatgpt_json = json.loads(chatgpt_result)
    except Exception as e:
        print("Error: ", e)
        chatgpt_json = {
            "title": "Error",
            "summary": chatgpt_result
        }
    title = chatgpt_json.get('title', 'Title Not Found')
    copy_to_clipboard(format_text(url, chatgpt_json))

def chatgpt(text, source, target_language="brazilian portuguese"):
    try:
        openai.api_key = os.getenv("OPENAI_KEY")
        
        if source == "youtube":
            system_text = f"""
    The data below is a transcript from a YouTube video. Please summarize this data in {target_language}. Return the result as a JSON in the following format:
    {{
        title: "Title of your summary",
        summary: "Summary of the video"
    }}
            """
        else:
            system_text = f"""
    The data below was extracted from a website. Please summarize this data in {target_language}. Return the result as a JSON in the following format:
    {{
        title: "Title of your summary",
        summary: "Summary of the article"
    }}
            """
        
        text_to_chatgpt = system_text + text
        text_to_chatgpt = text_to_chatgpt[:20000]
        
        response_openai = openai.ChatCompletion.create(
            model='gpt-4',
            messages=[{"role": "user", "content": text_to_chatgpt}], 
        )
        response_message = response_openai.choices[0].message.content
    except Exception as e:
        response_message = "Error: " + str(e)
    return response_message

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
