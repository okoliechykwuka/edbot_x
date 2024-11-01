# Theoriq Documentation Assistant

A specialized Retrieval-Augmented Generation (RAG) agent built on the Theoriq framework, designed to help users understand and implement Theoriq's AI platform by leveraging official documentation and blog posts.

## Features

- 🔍 RAG-powered responses using Embedchain technology
- 📚 Multi-source knowledge integration (web pages, PDFs, JSON)
- 📝 Comprehensive logging system
- 💰 Transparent cost tracking
- 🔄 Flask-based API implementation
- ⚡ Theoriq protocol integration

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- Access to Theoriq platform

## Installation

1. Clone the repository:
```bash
git clone <your-repository-url>
cd theoriq-doc-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root:
```env
THEORIQ_API_KEY=your_api_key
THEORIQ_AGENT_ID=your_agent_id
```

2. Prepare your data sources:
   - Create `url.txt` with Theoriq documentation URLs (one per line)
   - Place your Theoriq documentation PDF in the root as `litepaper.pdf`
   - Create `img_data.json` for any additional structured data
   - Configure `config.yaml` for Embedchain settings

## Project Structure

```
theoriq-doc-assistant/
├── .env                  # Environment variables
├── app.log              # Application logs
├── config.yaml          # Embedchain configuration
├── url.txt              # List of web sources
├── litepaper.pdf        # PDF documentation
├── img_data.json        # Additional data
└── main.py             # Main application file
```

## Usage

1. Start the Flask server:
```bash
python main.py
```

2. The server will start on `http://localhost:8000` by default


```

## Logging

Logs are written to both console and `app.log` file, including:
- Query processing
- Response generation
- Error tracking
- Cost information

## Error Handling

The agent includes comprehensive error handling for:
- Invalid requests
- Failed data source loading
- Query processing errors
- Response generation issues

## Cost Structure

- Fixed cost of 1.0 USDC per query
- Cost tracking per request
- Transparent pricing model
