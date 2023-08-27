# SuperSummarizeAI

## Description
SuperSummarizeAI is a Python tool that extracts textual content from a provided webpage URL, processes the content through ChatGPT to generate a summary, and then copies the summarized content to the clipboard.

## Installation

1. Ensure you have Python 3 installed.
2. Install the required packages:
```
pip install requests beautifulsoup4 pyperclip openai python-dotenv youtube_transcript_api
```
1. Create a `.env` file in the root directory of your project and add the following line, replacing `YOUR_OPENAI_KEY` with your actual OpenAI key (You can obtain one [here](https://beta.openai.com/).):
```
OPENAI_KEY="YOUR_OPENAI_KEY"
```
Ensure to keep your `.env` file confidential and not share it, as it contains sensitive API credentials.

## Usage
To use SuperSummarizeAI, provide the URL as a command-line argument:

```
python main.py <webpage_url>
```

For example:
```
python main.py https://example.com
```

## Troubleshooting
- **URL Input**: Ensure the URL is correctly formatted and starts with `http://` or `https://`.
- **Dependencies**: Ensure all required dependencies are correctly installed.
- **Command Line Argument**: Always provide a URL when running the script.
- **OpenAI Key**: Ensure your `.env` file contains the correct OpenAI key.

## Contributing
If you'd like to contribute to SuperSummarizeAI, please open an issue first to discuss what you would like to change.

## License
[MIT](https://choosealicense.com/licenses/mit/)