import streamlit as st
from dotenv import load_dotenv
load_dotenv()

from ingest.pdf_loader import load_pdf
from ingest.chunker import chunk_documents
from embeddings.embedder import get_embedder
from embeddings.vector_store import VectorStore
from agent.qa_engine import QaEngine
from tools.arxiv_tool import search_arxiv, download_pdf
import os
import time

st.set_page_config(
    page_title="DOC Agent",
    page_icon="📄",
    layout="wide"
)

try:
    if 'vector_store' not in st.session_state:
        embedder = get_embedder()
        st.session_state.vector_store = VectorStore(embedder)

    if 'qa_engine' not in st.session_state:
        st.session_state.qa_engine = QaEngine(st.session_state.vector_store)
    
    if 'initialized' not in st.session_state:
        st.session_state.initialized = True
    
    if 'last_arxiv_search' not in st.session_state:
        st.session_state.last_arxiv_search = 0
        
except Exception as e:
    st.error(f"Initialization failed: {str(e)}")
    st.info("Make sure you have set up your .env file with GOOGLE_API_KEY")
    st.stop()

st.title("Document Q&A AI Agent")

uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)
if uploaded_files:
    success_count = 0
    failed_files = []
    
    for uploaded_file in uploaded_files:
        with st.spinner(f"Processing {uploaded_file.name}..."):
            temp_path = os.path.join(os.getcwd(), f"temp_{uploaded_file.name}")
            try:
                file_size = len(uploaded_file.getvalue())
                if file_size > 50 * 1024 * 1024:
                    failed_files.append((uploaded_file.name, "File too large (max 50MB)"))
                    continue
                
                with open(temp_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                docs = load_pdf(temp_path)
                if not docs:
                    failed_files.append((uploaded_file.name, "No text content extracted"))
                    continue
                
                chunks = chunk_documents(docs)
                if not chunks:
                    failed_files.append((uploaded_file.name, "Failed to create chunks"))
                    continue
                
                st.session_state.vector_store.add_documents(chunks)
                success_count += 1
                
            except Exception as e:
                failed_files.append((uploaded_file.name, str(e)))
            finally:
                try:
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
                except:
                    pass
    
    if success_count > 0:
        st.success(f"{success_count} document(s) processed successfully!")
    if failed_files:
        with st.expander("Failed files", expanded=True):
            for filename, error in failed_files:
                st.error(f"**{filename}**: {error}")

st.header("Search ArXiv")

cooldown_seconds = 15
time_since_last = time.time() - st.session_state.last_arxiv_search
remaining_cooldown = max(0, cooldown_seconds - time_since_last)

if remaining_cooldown > 0:
    st.warning(f"Cooldown active: Wait {int(remaining_cooldown)} seconds before next search to avoid rate limits.")

arxiv_query = st.text_input("Enter search query for ArXiv")

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Search and Add"):
        if arxiv_query:
            time_since_last = time.time() - st.session_state.last_arxiv_search
            if time_since_last < cooldown_seconds:
                remaining = int(cooldown_seconds - time_since_last)
                st.error(f" Please wait {remaining} more seconds. This prevents rate limiting!")
            else:
                st.session_state.last_arxiv_search = time.time()
                
                with st.spinner("Searching ArXiv (this may take 10+ seconds due to rate limiting)..."):
                    results, error = search_arxiv(arxiv_query, max_results=3)
                    
                    if error:
                        st.error(error)
                    elif results:
                        result_titles = [f"{i+1}. {r.title} ({r.published.year})" for i, r in enumerate(results)]
                        selected_idx = 0
                        
                        if len(results) > 1:
                            st.write(f"Found {len(results)} papers:")
                            for i, r in enumerate(results):
                                st.write(f"{i+1}. **{r.title}** ({r.published.year})")
                                st.caption(f"ArXiv ID: {r.get_short_id()} | PDF: {r.pdf_url}")
                            st.info("Adding the first result. Future version will allow selection.")
                        
                        result = results[selected_idx]
                        
                        with st.spinner(f"Downloading: {result.title}..."):
                            pdf_path, dl_error = download_pdf(result)
                            
                            if dl_error:
                                st.error(dl_error)
                            elif pdf_path:
                                try:
                                    with st.spinner("Processing paper..."):
                                        docs = load_pdf(pdf_path)
                                        chunks = chunk_documents(docs)
                                        st.session_state.vector_store.add_documents(chunks)
                                    st.success(f"Paper '{result.title}' added successfully!")
                                except Exception as e:
                                    st.error(f"Failed to process PDF: {str(e)}")
                                finally:
                                    if os.path.exists(pdf_path):
                                        os.remove(pdf_path)
        else:
            st.warning("Please enter a search query.")

with col2:
    st.markdown("**Alternative: Add by URL**")
    pdf_url_input = st.text_input("ArXiv PDF URL (e.g., https://arxiv.org/pdf/2401.12345.pdf)", key="pdf_url")
    if st.button("Add PDF from URL"):
        if pdf_url_input:
            from tools.arxiv_tool import download_pdf_from_url
            with st.spinner("Downloading from URL..."):
                pdf_path, error = download_pdf_from_url(pdf_url_input)
                
                if error:
                    st.error(error)
                elif pdf_path:
                    try:
                        with st.spinner("Processing paper..."):
                            docs = load_pdf(pdf_path)
                            chunks = chunk_documents(docs)
                            st.session_state.vector_store.add_documents(chunks)
                        st.success(f"PDF added successfully!")
                    except Exception as e:
                        st.error(f"Failed to process PDF: {str(e)}")
                    finally:
                        if os.path.exists(pdf_path):
                            os.remove(pdf_path)
        else:
            st.warning("Please enter a PDF URL.")

st.header("Ask a Question")
question = st.text_input("Enter your question")
if st.button("Ask"):
    if question:
        if st.session_state.vector_store.vectorstore is None:
            st.warning("No documents loaded. Please upload PDF files or add papers from ArXiv first.")
        else:
            try:
                with st.spinner("Thinking..."):
                    answer = st.session_state.qa_engine.answer_question(question)
                st.markdown("**Answer:**")
                st.markdown(answer)
            except Exception as e:
                st.error(f"Failed to generate answer: {str(e)}")
                st.info("Tip: Make sure your GOOGLE_API_KEY is correctly set in the .env file.")
    else:
        st.warning("Please enter a question.")