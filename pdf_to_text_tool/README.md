# PDF to Text Tool

This tool utilizes a multimodal Ollama model to convert PDF files to txt files in markdown. The prompt outputs the text and tables in the PDF file only. Since it utilizes Ollama, it's recommended that you use the tool on your machine without Docker abstraction unless you have a lot of resources dedicated to Docker.

## Installation

1. [Install Ollama](https://ollama.com/download)
2. Pull a model that has vision. This one used "llama3.2-vision"
   `ollama pull llama3.2-vision`
3. Create a virtual Python environment and activate it
   There are multiple ways to do this, but I am beginning to use [uv](https://github.com/astral-sh/uv)
4. Install the requirements
5. Drop all your PDFs into the inputs folder
6. From the pdf_to_text_tool directory, run the following command:
   `python ollama_text_convert.py
