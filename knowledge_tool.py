from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from livekit.agents import function_tool

# ── LOAD VECTOR STORE ONCE ────────────────────────────────────────────────────

print("⏳ Loading knowledge base...")

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

vectorstore = Chroma(
    persist_directory="chroma_db",    
    embedding_function=embeddings
)

# print("✅ Knowledge base loaded!")


# ── KNOWLEDGE SEARCH TOOL ─────────────────────────────────────────────────────
# When user asks something related to expository writing
# LLM calls this tool with the user's question as the query
# We find the 3 most relevant chunks from the slides
# Return them as context for the LLM to answer from
@function_tool
async def search_knowledge_base(query: str) -> str:
    """Search the course slides knowledge base. ONLY use this for questions about 
    expository writing, essay structure, or academic writing course content. 
    If this tool returns NOT_RELEVANT, you MUST immediately call the general_knowledge 
    tool next — do not answer the user yet, do not say you don't know."""

    try:
        results = vectorstore.similarity_search_with_score(query, k=3)

        #Set based on the testing result
        RELEVANCE_THRESHOLD = 1.1

        if not results or results[0][1] > RELEVANCE_THRESHOLD:
            return "NOT_RELEVANT: This question is not related to the course slides. You must now call the general_knowledge tool."

        combined = ""
        for doc, score in results:
            if score <= RELEVANCE_THRESHOLD:
                source = doc.metadata.get("source", "unknown")
                slide = doc.metadata.get("slide", "?")
                combined += f"[From {source}, Slide {slide}]:\n{doc.page_content}\n\n"

        return f"Here is relevant information from your course slides:\n\n{combined}"

    except Exception as e:
        return f"Could not search knowledge base: {str(e)}"