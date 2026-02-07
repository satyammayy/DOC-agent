from langchain_community.vectorstores import FAISS
import numpy as np

class VectorStore:
    def __init__(self, embedder):
        self.embedder = embedder
        self.vectorstore = None

    def add_documents(self, documents):
        """
        Add documents to the vector store.
        """
        if not documents:
            return
            
        if self.vectorstore is None:
            self.vectorstore = FAISS.from_documents(documents, self.embedder)
        else:
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            self.vectorstore.add_texts(texts, metadatas=metadatas)

    def similarity_search(self, query, k=5):
        """
        Search for similar documents.
        """
        if self.vectorstore is None:
            return []
        return self.vectorstore.similarity_search(query, k=k)