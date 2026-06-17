from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from livekit.agents import function_tool

# ── LOAD VECTOR STORE ONCE ────────────────────────────────────────────────────
# We load this once when the file is imported
# So it doesn't reload every time the tool is called
# This makes responses much faster
print("⏳ Loading knowledge base...")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma(
    persist_directory="chroma_db",    # same folder ingest.py created
    embedding_function=embeddings
)

print("✅ Knowledge base loaded!")


# ── KNOWLEDGE SEARCH TOOL ─────────────────────────────────────────────────────
# When user asks something related to expository writing
# LLM calls this tool with the user's question as the query
# We find the 3 most relevant chunks from the slides
# Return them as context for the LLM to answer from
@function_tool
async def search_knowledge_base(query: str) -> str:
    """Search the course slides knowledge base ONLY for questions about:
    - Academic writing (expository writing, proposal writing, abstract, executive summary)
    - CMAPP analysis
    - Brainstorming strategies
    - Graphics in writing
    Do NOT use this tool for general knowledge, sports, weather, or current events."""
    try:
        # similarity_search finds the most relevant chunks
        # k=3 means return top 3 most relevant chunks
        results = vectorstore.similarity_search(query, k=3)

        if not results:
            return "No relevant information found in the course slides."

        # Combine the chunks into one response
        combined = ""
        for i, doc in enumerate(results):
            source = doc.metadata.get("source", "unknown")
            slide = doc.metadata.get("slide", "?")
            combined += f"[From {source}, Slide {slide}]:\n{doc.page_content}\n\n"

        return f"Here is relevant information from your course slides:\n\n{combined}"

    except Exception as e:
        return f"Could not search knowledge base: {str(e)}"