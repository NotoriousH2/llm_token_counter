# LLM Token Counter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) 


Upload your content or paste text to calculate the token count across various Large Language Models (LLMs).

**[🚀 (Live Demo Link)](http://notolab.64bit.kr/tokenizer/)**

![image](https://github.com/user-attachments/assets/21cc8ace-2ccd-4109-afbe-e954c82eaaf9)



## Overview

This tool provides a simple web interface to determine the number of tokens a given text or document file represents for different LLMs. Understanding token counts is crucial for estimating API costs, managing context window limits, and optimizing prompts.

## Features

* **Wide Model Support**: Calculate tokens for:
    * **Commercial Models**: GPT series (OpenAI), Claude series (Anthropic), Gemini series (Google).
    * **Hugging Face Models**: Any tokenizer available on the Hugging Face Hub.
* **Flexible Input**:
    * Paste text directly into the interface.
    * Upload files (`.pdf`, `.docx`, `.txt`, `.md`).
* **Easy Model Selection**:
    * Choose from pre-populated lists of popular models.
    * Directly input any specific model ID (for commercial models) or Hugging Face model identifier (`username/model-name`).
* **User-Friendly Interface**: Built with Gradio for a simple and interactive web UI.
* **Calculation History**: View a list of your recent token count calculations.
* **Multi-language Support**: Switch the interface between English and Korean.
* **Caching**: Efficiently caches loaded Hugging Face tokenizers and parsed file content.

## What is a Tokenizer?

A tokenizer is a component that breaks down raw text (like "Hello, world!") into smaller units called **tokens**, which LLMs can understand. Tokens can be words, parts of words (subwords), punctuation marks, or special symbols.

For example, the sentence "tokenizer is important" might be tokenized as:
`["token", "izer", " is", " important"]`

Different models use different tokenizers, so the same text can result in a different number and sequence of tokens depending on the model.

## Why is Tokenization Important?

Tokenization plays a critical role in how LLMs work:

1.  **Model Input Processing**: LLMs don't process raw text directly. They process sequences of token IDs (numbers representing each token). Tokenizers perform the crucial first step of converting human-readable text into this numerical format.
2.  **Performance and Efficiency**: How text is tokenized can impact model training efficiency and overall performance. Effective tokenizers can represent information compactly, potentially reducing computation.
3.  **Cost and Context Limits**:
    * **Cost**: Many LLM APIs charge based on the number of tokens processed (both input and output).
    * **Context Window**: Models have a maximum limit on the number of tokens they can handle in a single input/output interaction (the "context window").
    * Knowing the token count helps you estimate costs accurately and ensure your input fits within the model's limits.

This `llm_token_counter` helps you easily find the token count for your text using various models, allowing you to plan your LLM usage more effectively.

## Installation & Setup

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/YourUsername/llm-token-counter.git](https://github.com/YourUsername/llm-token-counter.git) # Replace YourUsername
    cd llm-token-counter
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3.  **Install Dependencies:**
    *(Ensure you have a `requirements.txt` file in your project root)*
    ```bash
    pip install -r requirements.txt
    ```
    *(If you don't have one yet, you can create it using `pip freeze > requirements.txt` after installing necessary packages like `gradio`, `transformers`, `pdfplumber`, `python-docx`, `tiktoken`, `google-generativeai`, `anthropic`, `huggingface_hub`, `python-dotenv`, `pydantic-settings`)*

4.  **Set Up API Keys (Optional but Recommended):**
    * Create a file named `.env` in the project root directory.
    * Add your API keys for the services you intend to use:
        ```dotenv
        # .env file
        OPENAI_API_KEY="your_openai_api_key"
        GOOGLE_API_KEY="your_google_api_key"
        ANTHROPIC_API_KEY="your_anthropic_api_key"
        HUGGINGFACE_HUB_TOKEN="your_huggingface_read_token" # Needed for gated/private HF models
        ```
    * These keys are used for calculating tokens for respective commercial models and accessing private/gated models on Hugging Face Hub.

## Usage

1.  **Run the Server:**
    ```bash
    python src/server.py
    ```

2.  **Access the Interface:**
    * Open your web browser and navigate to the URL provided (usually `http://127.0.0.1:7860` or `http://0.0.0.0:7860`).

3.  **Calculate Tokens:**
    * Select the **Model Type** (Commercial or Huggingface).
    * Choose the **Model Input Method** (Select from List or Direct Input).
        * If "Select from List", choose a model from the dropdown.
        * If "Direct Input", type the specific model ID.
    * Select the **Input Method** (Text Input or File Upload).
        * If "Text Input", paste your text into the textbox.
        * If "File Upload", upload your `.pdf`, `.docx`, `.txt`, or `.md` file.
    * Click the **Calculate Tokens** button.
    * View the processing status and the final token count in the results section. Your calculation will also appear in the history table.

## Supported Models

* **Commercial**: Tested with common models from OpenAI (GPT series), Anthropic (Claude series), and Google (Gemini series). You can add others by directly inputting their model ID recognized by their respective token counting libraries (`tiktoken`, `anthropic`, `genai`). Newly used models are added to the dropdown list.
* **Hugging Face**: Supports any model identifier available on the Hugging Face Hub (e.g., `meta-llama/Llama-2-7b-chat-hf`). Requires an internet connection to download the tokenizer on first use. A `HUGGINGFACE_HUB_TOKEN` in your `.env` file might be needed for gated or private models. Newly used models are added to the dropdown list.
* Model lists are managed in `src/utils/models.json` and updated automatically.

## Supported File Types

* PDF (`.pdf`)
* Word Documents (`.docx`)
* Text Files (`.txt`)
* Markdown Files (`.md`)

## Configuration

Configuration options can be managed via environment variables or a `.env` file. Key settings include:

* `ANTHROPIC_API_KEY`: Your Anthropic API key.
* `OPENAI_API_KEY`: Your OpenAI API key.
* `GOOGLE_API_KEY`: Your Google API key.
* `HUGGINGFACE_HUB_TOKEN`: Your Hugging Face Hub token (read access usually sufficient).
* `CACHE_DIR`: Directory to cache Hugging Face models/tokenizers (Defaults to `~/.cache/huggingface`).
* `PORT`: Port to run the Gradio server on (Defaults to `7860`).
* `HOST`: Host address for the server (Defaults to `0.0.0.0`).
* `LANGUAGE`: Default interface language (`kor` or `eng`, defaults to `kor`).

See `src/utils/config.py` for more details.

## Multi-language Support

The user interface supports both English and Korean. You can toggle the language using the button in the top-right corner of the application.

## License

This project is licensed under the [MIT License](LICENSE). ```
