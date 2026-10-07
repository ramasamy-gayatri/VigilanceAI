
import pathway as pw
import os
from dotenv import load_dotenv
load_dotenv()

from pathway.xpacks.llm.question_answering import SummaryQuestionAnswerer, BaseRAGQuestionAnswerer
from pathway.xpacks.llm.servers import QASummaryRestServer
from pathway.xpacks.llm import llms, embedders, splitters, parsers
from pathway.stdlib.indexing import UsearchKnnFactory

# --- CONFIGURATION ---
DATA_DIR = "./data"
RESULTS_DIR = "./results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# API Keys (Set these in .env or environment)
# For demo, we assume they are set or we use a free key if available, but here we expect OPENAI_API_KEY
# pw.set_license_key("YOUR_KEY") # Optional for free features

# --- PART 1: ANALYTICS PIPELINE (DASHBOARD) ---
sales = pw.io.csv.read(
    os.path.join(DATA_DIR, "sales_stream.csv"),
    mode="streaming",
    schema=pw.schema_from_csv(os.path.join(DATA_DIR, "sales_stream.csv"))
)

rx = pw.io.csv.read(
    os.path.join(DATA_DIR, "prescriptions_stream.csv"),
    mode="streaming",
    schema=pw.schema_from_csv(os.path.join(DATA_DIR, "prescriptions_stream.csv"))
)

# Aggregations
sales_stats = sales.groupby(sales.drug_name).reduce(
    total_sold=pw.reducers.sum(sales.quantity_sold),
    last_location=pw.reducers.max(sales.location)
)

rx_stats = rx.groupby(rx.drug_name).reduce(
    total_prescribed=pw.reducers.count(),
    avg_dosage=pw.reducers.avg(rx.dosage_mg)
)

# Join for Dashboard
dashboard_stats = sales_stats.join(
    rx_stats, on=sales_stats.id == rx_stats.id, how="outer"
).select(
    drug_name=sales_stats.id,
    total_sold=pw.coalesce(sales_stats.total_sold, 0),
    total_prescribed=pw.coalesce(rx_stats.total_prescribed, 0),
    avg_dosage=pw.coalesce(rx_stats.avg_dosage, 0.0)
)

# Risk Score Calculation
dashboard_stats = dashboard_stats.select(
    *dashboard_stats,
    risk_score=(dashboard_stats.total_sold * 0.5) + (dashboard_stats.total_prescribed * 1.2)
)

# Output to CSV for Streamlit
pw.io.csv.write(
    dashboard_stats,
    os.path.join(RESULTS_DIR, "live_stats.csv")
)

# --- PART 2: RAG PIPELINE (CHATBOT) ---

# 1. Input: Social Stream (Text)
documents = pw.io.csv.read(
    os.path.join(DATA_DIR, "social_stream.csv"),
    mode="streaming",
    schema=pw.schema_from_csv(os.path.join(DATA_DIR, "social_stream.csv")),
    with_metadata=True
)

# 2. Components
# We use OpenAI by default (requires OPENAI_API_KEY env var)
# If unavailable, one could swap with LiteLLMChat and a local Ollama.
llm_model = llms.OpenAIChat(model="gpt-3.5-turbo", temperature=0.0)
embedder = embedders.OpenAIEmbedder()

# 3. RAG App
# AdaptiveRAGQuestionAnswerer is a high-level pack
rag_app = BaseRAGQuestionAnswerer(
    llm=llm_model,
    indexer=pw.xpacks.llm.document_store.DocumentStore(
        docs=documents,
        splitter=splitters.TokenCountSplitter(max_tokens=200),
        retriever_factory=UsearchKnnFactory(
            embedder=embedder,
            dimensions=1536 # OpenAI embedding size
        ),
        parser=parsers.ParseUnstructured() # Simple parser
    ),
    short_prompt_template="Answer the question based on the context: {context}\nQuestion: {question}"
)

# 4. Expose as HTTP API
# This will run on localhost:8000/v1/pw_ai_answer
host = "0.0.0.0"
port = 8000
rag_server = QASummaryRestServer(host, port, rag_app)

# --- EXECUTION ---
if __name__ == "__main__":
    print(f"Starting Pathway Backend...")
    print(f" - Dashboard Stats writing into {RESULTS_DIR}")
    print(f" - Chatbot API listening on {host}:{port}")
    pw.run()
