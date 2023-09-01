#!python
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import openai
import PyPDF2
import pyperclip
import requests
import urllib3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Summarize a URL, PDF and Youtube Video using ChatGPT.')
    
    # Making the TARGET argument positional
    parser.add_argument('target', type=str, help='The URL, PDF or Youtube Video URL to be summarized.')
    parser.add_argument('--lang', type=str, default='brazilian portuguese', help='Target language for the summary.', dest='lang')
    parser.add_argument('--context', type=str, default=None, help='Add context to the summary', dest='context')
    parser.add_argument('--p', type=int, default=1, help='Number of paragraphs for the summary.', dest='paragraphs')
    
    args = parser.parse_args()

    if args.target is None:
        print("No TARGET specified. Use <TARGET to be summarized>")
        exit(1)

    return args

def main():
    args = parse_arguments()

    target = args.target
    is_url_valid = is_url(target)
    target_language = args.lang
    target_paragraphs = args.paragraphs
    context = args.context

    print("Extracting data from:", target)
    if not is_url_valid:
        text = extract_text_from_pdf(target)
        source = "pdf"
        if text is None:
            print("Failed to extract data from pdf:", target)
            exit(1)
    else:

        # Check if the URL is a YouTube URL
        if "youtube.com" in target or "youtu.be" in target:
            text = extract_transcript(target)
            source = "youtube"
        else:
            text = extract_text_from_url(target)
            source = "website"

        if text is None:
            print("Failed to extract data from:", target)
            exit(1)

    print ("Data extracted ("+source+")")
    # print(f"Creating ChatGPT summary in {target_language} in {target_paragraphs} paragraphs. This may take a while...")
    if context is not None:
        print("Context:", context)
    print(f"Creating ChatGPT summary in {target_language}. This may take a while...")
    chatgpt_result = chatgpt(text, source, target_language, target_paragraphs, context)
    print("ChatGPT summary done")
    try:
        chatgpt_result = chatgpt_result.strip()
        chatgpt_json = json.loads(chatgpt_result)
    except Exception as e:
        print("Error: ", e)
        chatgpt_json = {
            "title": "Error",
            "summary": chatgpt_result
        }
    title = chatgpt_json.get('title', 'Title Not Found')
    copy_to_clipboard(format_text(target, chatgpt_json))

def chatgpt(text, source, target_language="brazilian portuguese", target_paragraphs=1, context=None):
    try:
        additional_context = ""
        if context is not None:
            additional_context = "Additional context: " + context
        openai.api_key = os.getenv("OPENAI_KEY")
        if source == "youtube":
            system_text = f"""
    The data below is a transcript from a YouTube video. Generate an insightful summary of this data in this language: {target_language}. {additional_context}. Use \\n to break line, if needed. Return the result as a JSON in the following format:
    {{
        title: "Title of your summary",
        summary: "Summary of the video"
    }}
            """
        else:
            system_text = f"""
    The data below was extracted from a {source}. Generate an insightful summary of this data in this language: {target_language}. {additional_context}. Use \\n to break line, if needed. Return the result as a JSON in the following format:
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

def extract_text_from_pdf(file_path):
    # Open the PDF file
    with open(file_path, 'rb') as pdf_file:
        # Initialize PDF reader
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Extract text from each page
        text = ''
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
            
    return text

def is_url(string):
    try:
        result = urlparse(string)
        # Ensure the string has a scheme (e.g., "http") and a network location (e.g., "www.google.com")
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

if __name__ == "__main__":
    main()
