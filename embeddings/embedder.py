from langchain_huggingface import HuggingFaceEmbeddings

def get_embedder():
    """
    Return a local HuggingFace embeddings instance (offline, no API needed).
    Uses 'all-MiniLM-L6-v2' - a small, fast model.
    """
    return HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )