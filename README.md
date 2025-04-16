# VerdeMuse Intelligent Customer Support Virtual Assistant

## Overview

VerdeMuse is an intelligent customer support virtual assistant designed to provide instant support for sustainable plant products. The application leverages FastAPI for the backend, Streamlit for the frontend, and incorporates Mistral LLM via LangChain for intelligent responses.

## Features

- Live chat interface for customer inquiries
- AI-powered responses based on product knowledge base
- Context-aware conversations with memory
- Semantic search across product information
- Source citations for transparent answers

## Project Structure

The project follows a domain-driven design architecture:

```
├── config/               # Configuration files
├── data/                 # Knowledge base and vector embeddings
├── docs/                 # Documentation
├── src/                  # Source code
│   ├── api/              # FastAPI backend
│   ├── domain/           # Business logic and models
│   ├── infrastructure/   # External dependencies (LLM, vector store)
│   └── presentation/     # User interface (Streamlit)
├── scripts/              # Utility scripts
└── tests/                # Test suite
```

## Getting Started

### Prerequisites

- Python 3.10 or higher
- Docker (optional for containerized deployment)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/verdemuse.git
   cd verdemuse
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables by copying `.env.example` to `.env` and filling in your API keys.

5. Generate the knowledge base:
   ```
   python scripts/generate_knowledge_base.py
   ```

### Running the Application

#### Development Mode

1. Start the FastAPI backend:
   ```
   uvicorn src.api.main:app --reload
   ```

2. In a separate terminal, start the Streamlit frontend:
   ```
   streamlit run src/presentation/streamlit/app.py
   ```

3. Access the application:
   - API: http://localhost:8000
   - API docs: http://localhost:8000/docs
   - Streamlit UI: http://localhost:8501

#### Using Docker

```
docker-compose up
```

## Testing

Run the test suite:

```
pytest
```

## License

[MIT License](LICENSE)

## Acknowledgements

- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [LangChain](https://langchain.readthedocs.io/)
- [Mistral AI](https://mistral.ai/)