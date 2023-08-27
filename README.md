
# SuperSummarizeAI

## Description
SuperSummarizeAI is a versatile Python tool designed to extract and summarize textual content. Whether it's from a provided webpage URL or a YouTube video link, this tool processes the content through ChatGPT to generate an insightful summary. Once the summary is ready, the tool copies the content directly to your clipboard for quick access and sharing. Additionally, with its multilingual capabilities, SuperSummarizeAI can cater to a global audience, generating summaries in various languages.

## Installation

1. Ensure you have Python 3 installed on your system.
2. Install the required packages using pip:
```
pip install requests beautifulsoup4 pyperclip openai python-dotenv youtube_transcript_api argparse
```
3. Create a `.env` file in the root directory of your project. Inside this file, add the following line. Remember to replace `YOUR_OPENAI_KEY` with your actual OpenAI key (You can get one [here](https://beta.openai.com/)):
```
OPENAI_KEY="YOUR_OPENAI_KEY"
```
For security reasons, always ensure that your `.env` file remains confidential. Do not share or expose it as it contains sensitive API credentials.

## Usage
To employ SuperSummarizeAI, simply provide the desired URL (webpage or YouTube video) as a command-line argument:

```
python main.py <URL>
```

For instance:
```
python main.py https://example.com
```

For multilingual summaries, specify your desired language using the `--lang` option (default is 'brazilian portuguese'):
```
python main.py <URL> --lang <desired_language_code>
```

## Troubleshooting

- **URL Input**: Make sure the URL you input is correctly formatted and always begins with `http://` or `https://`.
- **Dependencies**: Double-check to ensure all required dependencies are correctly installed.
- **Command Line Argument**: Always provide a URL when executing the script.
- **OpenAI Key**: Make sure your `.env` file contains the correct and valid OpenAI key.

## Contributing
Interested in contributing to SuperSummarizeAI? We'd love to collaborate! Please initiate by opening an issue to discuss the changes you'd like to make.

## License
Licensed under [MIT](https://choosealicense.com/licenses/mit/).
