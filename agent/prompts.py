DOCUMENT_SUMMARY_PROMPT = """
You are an AI document analyst. The user wants a high-level overview of this document.

Using the provided context, produce:
- A concise high-level summary (3-4 sentences max)
- Explain the purpose and main points of the document
- Do NOT repeat the context verbatim
- Do NOT list page numbers or chunks
- Use plain, professional language

Context:
{context}

Provide a clear summary:
"""

QA_PROMPT = """
You are an AI research assistant analyzing documents.

User Question: {question}

Using the provided context, answer the question directly and concisely:
- Provide a SHORT, DIRECT answer to the specific question asked
- If it's a simple factual question (like "what is X?"), answer in 1-2 sentences
- If it's asking for a specific value or metric, just provide that value with minimal context
- Do NOT extract or list all metrics unless explicitly asked
- If the context lacks the specific information, state that clearly

Context:
{context}

Answer:
"""

METRIC_EXTRACTION_PROMPT = """
You are extracting research metrics from a document.

The user has requested a comprehensive extraction of ALL metrics from the document.

Extract all metrics such as:
- Accuracy, F1-score, Precision, Recall
- Performance benchmarks
- Statistical results
- Model scores and rankings

Provide them in a clear, structured format (use tables or organized lists).

Context:
{context}

Metrics:
"""