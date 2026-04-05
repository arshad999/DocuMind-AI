# DocuMind-AI

DocuMind-AI is a modular, scalable SaaS-style document generation system that uses OpenAI APIs to ingest company documents, build user-specific vector embeddings, and generate grounded documents in Word and PDF formats.

## Features

- Local username/password authentication
- Upload and ingest PDF and DOCX files
- Intelligent chunking and embeddings for RAG
- FAISS vector store per user for data isolation
- Streamlit UI with document library and generation workflow
- Download generated output as DOCX and PDF

## Project Structure

- `auth/` - Local authentication logic
- `ingestion/` - Document loading, chunking, and embedding pipeline
- `rag/` - Retrieval and generation logic
- `llm/` - OpenAI API client and prompt engineering
- `storage/` - SQLite metadata and FAISS vector storage
- `ui/` - Streamlit application
- `utils/` - Helper utilities for file handling and output generation

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment

Set your OpenAI API key:

```bash
set OPENAI_API_KEY=your_api_key_here
```

## Run Locally

Start the Streamlit app from the project root:

```bash
streamlit run ui/app.py
```

## Example Prompts

- "Create an employment agreement for India using our company tone."
- "Draft a client services contract for a SaaS advisory engagement."
- "Generate an employee handbook introduction page with HR policy sections."

## Sample Test

Run the sample sanity test file:

```bash
python tests/sample_test_case.py
```

## Notes

- The app uses SQLite to store users, documents, and chunk metadata.
- FAISS indexes are stored under `data/vector_store/{user_id}`.
- Generated DOCX and PDF files are saved under `data/outputs/`.
