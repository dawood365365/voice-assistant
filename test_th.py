from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# ── LOAD THE SAME VECTOR STORE YOUR AGENT USES ────────────────────────────────
print("⏳ Loading knowledge base...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorstore = Chroma(
    persist_directory="chroma_db",
    embedding_function=embeddings
)
print("✅ Knowledge base loaded!\n")

# ── TEST QUERIES ───────────────────────────────────────────────────────────────
test_queries = [
    # Relevant — should score LOW (close match)
    "when not to use graphics in expository writting",
    "Difference of abstract and an executive summary",
    "what is CMAPP Analysis",

    # Irrelevant — should score HIGH (far match)
    "Ronaldo vs Messi , who scored more goals",
    "what is the weather today",
    "how to cook biryani",
]

# ── RUN EACH QUERY AND PRINT SCORES ───────────────────────────────────────────
for query in test_queries:
    results = vectorstore.similarity_search_with_score(query, k=1)

    if results:
        doc, score = results[0]
        print(f"Query: '{query}'")
        print(f"  Score: {score:.4f}")
        print(f"  Matched chunk: {doc.page_content[:80]}...")
        print()
    else:
        print(f"Query: '{query}' — No results found\n")