# LifeTrail: 2026 Lifecycle Financial Companion
LifeTrail is an Agentic AI designed to bridge the "Planning Gap" for young professionals. It moves users from financial guilt to guidance by providing predictive, grounded, and empathetic strategy for the 2026 economic landscape.

## Core Capabilities:
Safe Spend & Tax Optimization: Calculates lifestyle budgets after 2026 taxes and goal commitments using grounded RAG data.
Goal Conflict Mapping: Analyzes the "opportunity cost" of purchases (e.g., how a car purchase affects house-buying timelines).
Course Correction: Mathematically adjusts monthly savings plans to recover from lifestyle splurges.
Safety Guardrails: Local pre-processing intercepts sensitive data (OTPs/Passwords) at 0.0s latency.

## Technical Highlights:
RAG-Grounded Intelligence: Uses a FAISS index of 2026 regulatory data to prevent outdated advice.
Deterministic Tools: Python-based math tools eliminate LLM "hallucinations" for tax and inflation.
Stateful Persistence: Remembers user style preferences (Concise vs. Detailed) across sessions.
Agentic Reasoning: Leverages LangChain’s AgentExecutor for complex, multi-step financial problem-solving.

# Architecture
User Query
      ↓
Agent Reasoning Loop (GPT-4o-mini)
      ↓
Tool Selection / FAISS Retrieval
      ↓
Deterministic Math Execution (Python)
      ↓
Context-Aware Response Generation

## Tech Stack
* **Python**
* **OpenAI API**

  * `gpt-4o-mini` (chat model)
  * `text-embedding-3-small` (embedding model)
* **LangChain**
* **FAISS** (vector database)
* **PyPDF** (PDF ingestion)

## Project Structure
LifeTrail_Project/
│
├─ documents/                        # Source PDF files for RAG ingestion
│    ├─ House Rent Allowance.pdf
│    ├─ Income Tax Slabs FY 2025.pdf
│    ├─ INDIA_POST_SAVINGS.txt
│    ├─ Leave Travel Allowance.pdf
│    ├─ Section 80C of Income Tax Act.pdf
│    ├─ Sovereign Gold Bond.pdf
│    
├─ RAG_ingestion.py                         # Ingestion + indexing script (PDF to FAISS)
├─ LifeTrailAgent.py                         # Primary Agentic Chatbot Script
├─ LifeTrail_Combined_Index_Final/   # Generated FAISS Vector Database
│
├─ user_preferences.json              # Persists style (Concise/Detailed)
├─ chat_history.json                 # Persists long-term conversational context
├─ lifetrail_final.log               # Latency, tracing, and success logs
│
├─ .env                              # API credentials
├─ requirements.txt                  # All Python dependencies
└─ README.md                         # Project documentation and setup guide

## Setup Instructions and Run instructions
### 1. 
Make sure .env file, documents, RAG_ingestion.py, LifeTrailAgent.py, requirements.txt are under the same folder
### 2. Configure Environment Variables
in  `.env` file:
```
OPENAI_API_KEY=your_openai_api_key
```
### 3. create virtual environment
create a virtual environment under that folder using the command: python -m venv .env
### 3. Activate environment
Activate the virtual environment: .venv\Script\activate
### 4. Install Dependencies in that virtual environment
```bash
pip install -r requirements.txt
```

## PDF Ingestion (One-Time Step)

```bash
python RAG_ingestion.py
```

What this does:
* Loads all PDFs from `documents/`
* Splits them into semantic chunks
* Generates embeddings using OpenAI
* Stores vectors locally using FAISS
---

## Running the agent
```bash
python LifeTrailAgent.py
```
## Example queries
1. I earn ₹36 Lakhs. I am saving ₹40,000 monthly for a house and ₹10,000 for my kid's school. After 2026 taxes, what is my Safe Spend limit for my daily lifestyle so I don't feel guilty?
2. I just spent ₹15,000 on a weekend trip. How does this affect my Safe Spend limit for the rest of the month? Use the course correction logic."
3. I want to buy a ₹20 Lakh car in 2 years and a ₹1 Crore house in 7 years. I earn ₹45 Lakhs. If I buy the car, how much will it delay or affect my house goal? Show me a feasibility map for both
4. I have a bike loan of ₹2 Lakhs. I also want to start an SIP for a ₹5 Lakh international trip next year. Which one should I prioritize to stay in the 'Realistic' zone?"
5. I earn ₹14 Lakhs. Since the 87A rebate stops at ₹12.75L (Gross), I am just over the limit. Suggest a Tax Optimization strategy using 80C or 80D to bring my taxable income back under the rebate threshold
6. I earn ₹25 Lakhs and have a home loan interest of ₹2 Lakhs. Show me a personalized comparison. Is the New Regime's ₹75k deduction better for me than the Old Regime's 80C/24b combo?"

# Public data source links
Income Tax Slabs FY 2025: https://cleartax.in/s/income-tax-slabs#h22
Section 80C of Income Tax Act: https://cleartax.in/s/80c-80-deductions
Sovereign Gold Bond: https://cleartax.in/s/sovereign-gold-bonds
INDIA_POST_SAVINGS: https://www.indiapost.gov.in/banking-services/savings
House Rent Allowance: https://cleartax.in/s/hra-house-rent-allowance
Leave Travel Allowance: https://cleartax.in/s/lta-leave-travel-allowance