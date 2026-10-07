# Vigilance.AI 🛡️

**The Operating System for Agentic Pharmacovigilance.**

Vigilance.AI is a next-generation platform that unifies real-time social listening, FDA regulatory data, and agentic AI to detect safety signals, automate compliance, and optimize pharmacy operations.

![Status](https://img.shields.io/badge/Status-Live-green) ![AI](https://img.shields.io/badge/AI-Agentic%20RAG-purple) ![Data](https://img.shields.io/badge/Data-OpenFDA%20%2B%20Social-blue)

## 🚀 Key Features

### 1. 📱 Live Social Intelligence Feed
*   **Real-time Monitoring**: Aggregates signals from "Simulated" Reddit, Twitter, and PubMed streams.
*   **Signal Detection**: AI automatically flags posts with potential adverse events (e.g., "Hair Shedding" on Wegovy).
*   **Thread Analysis**: Groups conversations into parent posts and threaded replies to analyze sentiment context.

### 2. 🤖 Agentic Drug Copilot (Hybrid RAG)
*   **Dual-Brain Architecture**: Combines official **FDA Label Data** (fetched live from `openfda.gov`) with **Live Social Stats**.
*   **Demographic Reasoning**: Answers complex queries like *"What are the side effects for women under 30?"* by filtering the live data stream.
*   **Gap Analysis**: Highlights discrepancies between the official label and real-world patient reports.

### 3. 👨‍⚕️ Doctor Prescribing Portal
*   **Safety Score**: Real-time risk assessment for drugs before prescribing.
*   **Regulatory Automation**: One-click generation of **FDA MedWatch 3500** forms for adverse events.
*   **Peer Surveillance**: Shows alerts from other doctors and pharmacists in the network.

### 4. 🏥 Pharmacy Command Center
*   **Demand Radar**: Visualizes "Viral Velocity" (social hype) vs. "Stock Remaining".
*   **Smart Inventory**: Auto-recommends restocks to prevent shortages of high-demand GLP-1s (Wegovy, Zepbound).

---

## 🛠️ Technical Architecture

The system uses a **Hybrid Data Implementation**:

*   **Real-World Data**: The `fetch_fda.py` module connects to the **OpenFDA API** to retrieve live labeling and black-box warnings.
*   **Simulation Engine**: The `mock_stream.py` script acts as a high-fidelity data generator, simulating thousands of patient and doctor interactions to demonstrate "Big Data" capabilities without expensive licenses.
*   **Agentic Core**: `utils.py` orchestrates the logic, routing user queries to the appropriate data source and synthesizing answers via LLM (GPT-4o).

## 📦 Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/YourUsername/VigilanceAI.git
    cd VigilanceAI
    ```

2.  **Install Dependencies**
    ```bash
    pip install streamlit pandas plotly openai python-dotenv requests faker
    ```

3.  **Configure Environment**
    Create a `.env` file in the root directory:
    ```ini
    OPENAI_API_KEY=sk-your-key-here
    ```

4.  **Run the Simulation Engine** (Terminal 1)
    ```bash
    python mock_stream.py
    ```

5.  **Launch the Dashboard** (Terminal 2)
    ```bash
    python -m streamlit run app.py
    ```

## 👥 Contributors

*   **Sanjeev M** - *Lead Architect & AI Logic*
*   **Harish Balaji** - *AI Engineer*

---
*Built for the Future of Drug Safety.*
