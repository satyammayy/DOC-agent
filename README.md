# Document Q&A AI Agent

A production-ready RAG-based AI agent for answering questions from research papers with intelligent intent detection and ArXiv integration.

## Features

- 📄 **PDF Upload**: Batch upload and process multiple PDF documents with validation
- 🔍 **ArXiv Integration**: Search and automatically add papers from ArXiv with rate limiting
- 🤖 **Smart Q&A**: Intent-aware question answering (specific queries, summaries, metrics extraction)
- 🧠 **Local Embeddings**: Offline vector embeddings using HuggingFace models
- 🎯 **Context-Aware**: Multi-document support with source citations
- 🛡️ **Production-Ready**: Comprehensive error handling, retry logic, and user feedback

## Architecture

```
document-qa-agent/
├── app.py                  # Streamlit UI with error handling
├── agent/
│   ├── qa_engine.py       # Intent detection & RAG pipeline
│   └── prompts.py         # Optimized LLM prompts
├── embeddings/
│   ├── embedder.py        # HuggingFace embeddings
│   └── vector_store.py    # FAISS vector storage
├── ingest/
│   ├── pdf_loader.py      # PDF parsing
│   └── chunker.py         # Document chunking
└── tools/
    └── arxiv_tool.py      # ArXiv search with rate limiting
```

## Setup

### Prerequisites
- Python 3.8+
- Google Gemini API key

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd document-qa-agent
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys:**
   Create a `.env` file in the project root:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Usage

### Upload PDFs
- Drag and drop PDF files (max 50MB each)
- Supports batch upload with individual file validation
- Automatic text extraction and chunking

### Search ArXiv
- Enter search queries like "large language models" or "RAG systems"
- Shows top 3 results with publication years
- Automatically downloads and processes selected papers
- **Rate Limiting**: Built-in delays to respect ArXiv API limits

### Ask Questions

**Simple Questions:**
```
Q: "What is the GPT-4o elo score?"
A: The GPT-4o Elo score is 980 (Rank #3).
```

**Document Summaries:**
```
Q: "What is this about?"
A: [Concise 3-4 sentence summary of the document]
```

**Comprehensive Metrics:**
```
Q: "Extract all metrics"
A: [Structured list of all performance metrics]
```

**Multi-Document Queries:**
```
Q: "Compare both documents"
A: [Separate summaries for each document]
```

## Production Deployment

### Environment Variables
Ensure these are set in production:
- `GOOGLE_API_KEY`: Gemini API key for LLM

### Error Handling
The application handles:
- ✅ ArXiv rate limits (HTTP 429) with helpful messages
- ✅ PDF parsing failures with detailed errors
- ✅ Large file validation (50MB limit)
- ✅ Network timeouts with retries
- ✅ Missing API keys with clear instructions
- ✅ Empty or invalid documents

### Rate Limiting
- ArXiv: 3-second delay between requests
- Exponential backoff on failures
- User-friendly error messages for rate limits

### Scaling Considerations
- Consider using Redis for vector store caching
- Implement document deduplication
- Add authentication for multi-user deployments
- Use async processing for large batches

## API Rate Limits

**ArXiv API:**
- Limit: ~1 request per 3 seconds
- Built-in delays: ✅ Implemented
- Retry logic: ✅ 3 attempts with exponential backoff

**Google Gemini API:**
- Depends on your API tier
- Free tier: 60 requests per minute
- Errors handled with clear messages

## Troubleshooting

### "ArXiv rate limit reached"
**Solution:** Wait 3-5 minutes before searching again. The API has built-in delays but repeated searches may still trigger limits.

### "Failed to process PDF"
**Solutions:**
- Check if PDF is text-based (not scanned images)
- Verify file size is under 50MB
- Ensure PDF is not password-protected

### "Error generating answer"
**Solutions:**
- Verify `GOOGLE_API_KEY` in `.env` file
- Check internet connection
- Ensure you have API quota remaining

### Empty or No Results
**Solutions:**
- Upload more relevant documents
- Try different search terms
- Check that PDFs contain extractable text

## Development

### Running Tests
```bash
pytest tests/
```

### Code Style
```bash
black .
flake8 .
```

## Tech Stack

- **UI**: Streamlit
- **LLM**: Google Gemini 2.5 Flash
- **Embeddings**: HuggingFace sentence-transformers
- **Vector Store**: FAISS
- **PDF Processing**: PyPDF
- **ArXiv Integration**: arxiv Python library

## License

MIT License

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Submit a pull request

## Support

For issues or questions, please open a GitHub issue with:
- Error messages and stack traces
- Steps to reproduce
- Python version and OS