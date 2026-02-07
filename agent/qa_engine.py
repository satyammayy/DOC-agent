from langchain_google_genai import ChatGoogleGenerativeAI
from .prompts import QA_PROMPT, DOCUMENT_SUMMARY_PROMPT, METRIC_EXTRACTION_PROMPT
import os

class QaEngine:
    def __init__(self, vector_store):
        self.vector_store = vector_store
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            convert_system_message_to_human=True
        )
    
    def _get_clean_doc_name(self, source_path):
        """Extract clean document name from full path, removing temp_ prefix."""
        filename = os.path.basename(source_path)
        if filename.startswith('temp_'):
            filename = filename[5:]
        return filename

    def _detect_intent(self, question):
        """Detect the type of query from user input."""
        q_lower = question.lower().strip()
        
        multi_doc_keywords = ["both", "two docs", "two documents", "all docs", "all documents",
                              "both files", "both pdfs", "what are the", "compare"]
        if any(kw in q_lower for kw in multi_doc_keywords):
            return "multi_doc_summary"
        
        summary_keywords = ["what is this about", "summary", "summarize", "overview", 
                           "what's this", "explain this document", "what is this document"]
        if any(kw in q_lower for kw in summary_keywords):
            return "summary"
        
        comprehensive_keywords = ["all metrics", "extract metrics", "list all", "all results",
                                 "all performance", "extract all", "show all metrics",
                                 "give me all", "comprehensive metrics"]
        if any(kw in q_lower for kw in comprehensive_keywords):
            return "metrics"
        
        return "qa"

    def _deduplicate_chunks(self, docs):
        """Remove duplicate chunks from same page, but keep diversity across documents."""
        seen = set()
        unique_docs = []
        doc_sources = {}
        
        for doc in docs:
            source = doc.metadata.get('source', 'unknown')
            page = doc.metadata.get('page', 0)
            key = f"{source}_{page}"
            
            if source not in doc_sources:
                doc_sources[source] = 0
            
            if key not in seen:
                seen.add(key)
                unique_docs.append(doc)
                doc_sources[source] += 1
        
        return unique_docs, doc_sources

    def answer_question(self, question):
        """
        Answer a question using RAG with Gemini LLM.
        Includes intent detection and proper response synthesis.
        """
        if self.vector_store.vectorstore is None:
            return "No documents loaded. Please upload PDF files first."
        
        intent = self._detect_intent(question)
        
        if intent == "multi_doc_summary":
            docs = self._get_diverse_chunks(k_per_doc=5)
        else:
            k = 8 if intent == "summary" else 5
            docs = self.vector_store.similarity_search(question, k=k)
        
        docs, doc_sources = self._deduplicate_chunks(docs)
        
        if not docs:
            return "No relevant information found in the documents."
        
        if intent == "multi_doc_summary":
            context_parts = []
            current_source = None
            for doc in docs:
                source = doc.metadata.get('source', 'Unknown')
                if source != current_source:
                    clean_name = self._get_clean_doc_name(source)
                    context_parts.append(f"\n--- Document: {clean_name} ---\n")
                    current_source = source
                context_parts.append(doc.page_content)
            context = "\n\n".join(context_parts)
        else:
            context = "\n\n".join([doc.page_content for doc in docs])
        
        if intent == "multi_doc_summary":
            prompt = f"""You are analyzing multiple documents. The user asked: "{question}"

Based on the context below from different documents, provide a clear summary of EACH document separately.

Format your answer like:
**Document 1: [filename]**
- Brief summary (2-3 sentences)

**Document 2: [filename]**
- Brief summary (2-3 sentences)

Context from multiple documents:
{context}

Provide summaries for all unique documents found:"""
        elif intent == "summary":
            prompt = DOCUMENT_SUMMARY_PROMPT.format(context=context)
        elif intent == "metrics":
            prompt = METRIC_EXTRACTION_PROMPT.format(context=context)
        else:
            prompt = QA_PROMPT.format(context=context, question=question)
        
        try:
            response = self.llm.invoke(prompt)
            answer = response.content if hasattr(response, 'content') else str(response)
            
            sources = self._format_sources(docs)
            doc_count = len(doc_sources)
            return f"{answer}\n\n---\n**{doc_count} document(s) referenced:** {sources}"
        except Exception as e:
            return f"Error generating answer: {str(e)}. Please check your GOOGLE_API_KEY in .env file."
    
    def _get_diverse_chunks(self, k_per_doc=5):
        """Get chunks from all documents in the vector store for comprehensive coverage."""
        all_docs = self.vector_store.similarity_search("document overview summary", k=50)
        
        docs_by_source = {}
        for doc in all_docs:
            source = doc.metadata.get('source', 'unknown')
            if source not in docs_by_source:
                docs_by_source[source] = []
            docs_by_source[source].append(doc)
        
        diverse_docs = []
        for source, docs in docs_by_source.items():
            diverse_docs.extend(docs[:k_per_doc])
        
        return diverse_docs
    
    def _format_sources(self, docs):
        """Format source references showing all unique documents."""
        source_refs = {}
        for doc in docs:
            source = doc.metadata.get('source', 'Unknown')
            page = doc.metadata.get('page', 'N/A')
            if source not in source_refs:
                source_refs[source] = []
            if page not in source_refs[source]:
                source_refs[source].append(page)
        
        formatted = []
        for source, pages in source_refs.items():
            clean_name = self._get_clean_doc_name(source)
            pages_str = ", ".join([str(p) for p in sorted(pages)[:3]])
            formatted.append(f"{clean_name} (Pages: {pages_str})")
        
        return "; ".join(formatted)