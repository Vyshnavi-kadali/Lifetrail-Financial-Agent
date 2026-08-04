# LifeTrail: 2026 Lifecycle Financial Companion

LifeTrail is an Agentic AI system designed to bridge the **"Planning Gap"** for young professionals. It helps users move from financial guilt to informed decision-making by providing predictive, grounded, and empathetic financial guidance tailored to the 2026 economic landscape.

---

## Core Capabilities

### Safe Spend & Tax Optimization
Calculates personalized lifestyle budgets after considering 2026 income tax regulations and financial goal commitments using grounded RAG data.

### Goal Conflict Mapping
Analyzes the opportunity cost of financial decisions (e.g., how purchasing a car impacts a future house-buying goal).

### Course Correction
Mathematically adjusts monthly savings plans to help users recover from unexpected lifestyle expenses.

### Safety Guardrails
Locally pre-processes user input to intercept sensitive information such as OTPs and passwords with near-zero latency.

---

## Technical Highlights

### RAG-Grounded Intelligence
Uses a FAISS vector index built from 2026 financial and regulatory documents to provide accurate and up-to-date financial guidance.

### Deterministic Tools
Python-based mathematical tools perform tax and financial calculations, reducing LLM hallucinations for numerical operations.

### Stateful Persistence
Remembers user interaction preferences (Concise vs. Detailed) across sessions.

### Agentic Reasoning
Uses LangChain's **AgentExecutor** to perform multi-step reasoning and coordinate tool usage for complex financial planning tasks.

---

# Architecture

```text
User Query
      ↓
Agent Reasoning Loop (GPT-4o-mini)
      ↓
Tool Selection / FAISS Retrieval
      ↓
Deterministic Math Execution (Python)
      ↓
Context-Aware Response Generation
```

---

## Tech Stack

- **Python**
- **OpenAI API**
  - `gpt-4o-mini` (Chat Model)
  - `text-embedding-3-small` (Embedding Model)
- **LangChain**
- **FAISS** (Vector Database)
- **PyPDF** (PDF Ingestion)

---

## Project Structure

```text
LifeTrail_Project/
│
├── documents/                           # Source PDF files for RAG ingestion
│   ├── House Rent Allowance.pdf
│   ├── Income Tax Slabs FY 2025.pdf
│   ├── INDIA_POST_SAVINGS.txt
│   ├── Leave Travel Allowance.pdf
│   ├── Section 80C of Income Tax Act.pdf
│   └── Sovereign Gold Bond.pdf
│
├── RAG_ingestion.py                     # PDF ingestion and FAISS indexing
├── LifeTrailAgent.py                    # Main Agentic AI application
├── LifeTrail_Combined_Index_Final/      # Generated FAISS vector database
│
├── user_preferences.json                # Stores user response preferences
├── chat_history.json                    # Stores conversation history
├── lifetrail_final.log                  # Logs latency, tracing, and execution details
│
├── .env                                 # Environment variables
├── requirements.txt                     # Python dependencies
└── README.md                            # Project documentation
```

---

# Setup Instructions

## 1. Project Setup

Ensure the following files are present in the same project directory:

- `.env`
- `documents/`
- `RAG_ingestion.py`
- `LifeTrailAgent.py`
- `requirements.txt`

---

## 2. Configure Environment Variables

Create a `.env` file and add your OpenAI API key.

```env
OPENAI_API_KEY=your_openai_api_key
```

---

## 3. Create a Virtual Environment

```bash
python -m venv .venv
```

---

## 4. Activate the Virtual Environment

### Windows

```bash
.venv\Scripts\activate
```

---

## 5. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# PDF Ingestion (One-Time Step)

Run the ingestion script to process all financial documents and generate the FAISS vector database.

```bash
python RAG_ingestion.py
```

This process:

- Loads all documents from the `documents/` folder
- Splits documents into semantic chunks
- Generates embeddings using OpenAI
- Stores vectors locally using FAISS

---

# Running the Agent

```bash
python LifeTrailAgent.py
```

---

# Example Queries

1. I earn ₹36 Lakhs. I am saving ₹40,000 monthly for a house and ₹10,000 for my kid's school. After 2026 taxes, what is my Safe Spend limit for my daily lifestyle so I don't feel guilty?

2. I just spent ₹15,000 on a weekend trip. How does this affect my Safe Spend limit for the rest of the month? Use the course correction logic.

3. I want to buy a ₹20 Lakh car in 2 years and a ₹1 Crore house in 7 years. I earn ₹45 Lakhs. If I buy the car, how much will it delay or affect my house goal? Show me a feasibility map for both.

4. I have a bike loan of ₹2 Lakhs. I also want to start an SIP for a ₹5 Lakh international trip next year. Which one should I prioritize to stay in the "Realistic" zone?

5. I earn ₹14 Lakhs. Since the Section 87A rebate stops at ₹12.75 Lakhs (Gross), I am just above the limit. Suggest a tax optimization strategy using Sections 80C or 80D to bring my taxable income below the rebate threshold.

6. I earn ₹25 Lakhs and have a home loan interest of ₹2 Lakhs. Show me a personalized comparison. Is the New Tax Regime's ₹75,000 standard deduction better for me than the Old Tax Regime's 80C and Section 24(b) benefits?

---

# Public Data Sources

- **Income Tax Slabs FY 2025:** https://cleartax.in/s/income-tax-slabs#h22
- **Section 80C of Income Tax Act:** https://cleartax.in/s/80c-80-deductions
- **Sovereign Gold Bond:** https://cleartax.in/s/sovereign-gold-bonds
- **India Post Savings:** https://www.indiapost.gov.in/banking-services/savings
- **House Rent Allowance:** https://cleartax.in/s/hra-house-rent-allowance
- **Leave Travel Allowance:** https://cleartax.in/s/lta-leave-travel-allowance
