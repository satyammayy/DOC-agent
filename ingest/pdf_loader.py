from langchain_community.document_loaders import PyMuPDFLoader

def load_pdf(file_path):
    """
    Load a PDF file and return a list of Document objects with page content and metadata.
    """
    loader = PyMuPDFLoader(file_path)
    documents = loader.load()
    return documents