import os
import json
import logging
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool, create_retriever_tool

# 1. INITIALIZATION
load_dotenv()
logging.basicConfig(filename='lifetrail_final.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# SAFETY VALIDATION DATA
RESTRICTED_ACTIONS = [
    "transfer money", "send money", "upi pin", "password", 
    "approve transaction", "bank otp", "otp", "upi id"
]

HIGH_RISK_KEYWORDS = [
    "fraud", "loan default", "suicide", "legal dispute", 
    "money laundering", "end my life", "depression", "attempt suicide"
]

EMERGENCY_KEYWORDS=["suicide", "end my life", "depression", "i dont want this life", "kill", "i'm going to kill somebody"]

# 2. SAFETY CHECK FUNCTION (Phase 5 Guardrail)
def safety_check(user_input):
    """
    Blocks restricted actions and routes high-risk queries to professional help with a visual helpline box.
    """
    q = user_input.lower()

    for keyword in RESTRICTED_ACTIONS:
        if keyword in q:
            return {
                "safe": False,
                "message": "I cannot process financial transactions or sensitive credentials."
            }

    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in q:
            return {
                "safe": False,
                "message": "I'm really sorry to hear that you're feeling this way. This situation may require assistance from a certified professional. Please reach out to emergency services or a trusted mental health professional immediately."
            }
        
    for keyword in EMERGENCY_KEYWORDS:
        if keyword in q:
            # Formatted Helpline Box for terminal output
            helpline_box = (
                "\n" + "="*50 + "\n"
                "               🆘 HELPLINE ACCESS 🆘\n" +
                "="*50 + "\n"
                " AASRA (24/7)            : +91-9820466726\n"
                " Vandrevala Foundation   : 1860 2662 345\n"
                " iCall                   : +91-9152987821\n"
                " Emergency Services      : 112\n" +
                "="*50 + "\n"
            )
            
            return {
                "safe": False,
                "message": (
                    "I'm really sorry to hear that you're feeling this way. Please know that you are not alone "
                    "and help is available immediately." + helpline_box +
                    "Please reach out to one of these services or a trusted professional right now."
                )
            }

    return {"safe": True, "message": "Safe"}

# 3. LOAD KNOWLEDGE BASE (RAG Tool)
def load_retriever():
    index_path = "LifeTrail_Combined_Index_Final"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore.as_retriever(search_kwargs={"k": 10})

# 4. DEFINE PRECISION MATH TOOLS
@tool
def calculate_2026_tax(salary: float, regime: str) -> str:
    """Calculates the 2026 Indian Income Tax precisely. 'regime' must be 'new' or 'old'."""
    if regime.lower() == "new":
        sd = 75000
        taxable = max(0, salary - sd)
        if taxable <= 1200000: tax = 0
        else:
            tax = 0
            if taxable > 400000: tax += min(taxable - 400000, 400000) * 0.05
            if taxable > 800000: tax += min(taxable - 800000, 400000) * 0.10
            if taxable > 1200000: tax += min(taxable - 1200000, 400000) * 0.15
            if taxable > 1600000: tax += min(taxable - 1600000, 400000) * 0.20
            if taxable > 2000000: tax += min(taxable - 2000000, 400000) * 0.25
            if taxable > 2400000: tax += (taxable - 2400000) * 0.30
    else:
        sd = 50000
        taxable = max(0, salary - sd)
        if taxable <= 500000: tax = 0
        else:
            tax = 0
            if taxable > 250000: tax += min(taxable - 250000, 250000) * 0.05
            if taxable > 500000: tax += min(taxable - 500000, 500000) * 0.20
            if taxable > 1000000: tax += (taxable - 1000000) * 0.30
    
    final_tax = round(tax * 1.04, 2)
    return json.dumps({"regime": regime, "tax_payable": final_tax, "SD": sd})

@tool
def calculate_goal_savings(current_cost: float, years: int, goal_type: str) -> str:
    """Calculates future cost for 'gold' (18%), 'education' (12%), or 'lifestyle' (8%)."""
    rates = {"gold": 0.18, "education": 0.12, "lifestyle": 0.08}
    rate = rates.get(goal_type.lower(), 0.08)
    future_cost = current_cost * ((1 + rate) ** years)
    monthly_needed = future_cost / (years * 12)
    return json.dumps({"future_cost": round(future_cost, 2), "monthly_savings": round(monthly_needed, 2)})

# 5. AGENT INTERFACE
def run_lifetrail_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    retriever_tool = create_retriever_tool(
        load_retriever(), 
        "search_financial_docs", 
        "Use this for any factual question about HRA, LTA, 80C, 80D, SGB, or India Post rules."
    )
    
    tools = [retriever_tool, calculate_2026_tax, calculate_goal_savings]

    # Note: chat_history placeholder removed for Phase 5 to demonstrate lack of memory
    system_message = """You are LifeTrail, a specialized Financial Advisor for the year 2026.
    
    Your goal is to provide advice based ONLY on the provided 'search_financial_docs' tool and your Math Tools.
    
    STRICT GROUNDING RULES:
    1. If the user asks for a FACT (e.g., "What is the 80D limit?"), you MUST use 'search_financial_docs'.
    2. FALLBACK: If the search tool does not return the specific answer, you MUST say: "I'm sorry, my current 2026 knowledge base doesn't have specific details on that."
    3. NO EXTERNAL DATA: Do not use your own training data for tax rates or prices (e.g., Cryptocurrency or restaurant suggestions).
    4. MATH: For any tax or savings calculation, ALWAYS use the specific math tools ('calculate_2026_tax' or 'calculate_goal_savings').NEVER guess a number. If a parameter (like price of gold) is missing, ask the user for it. Show the math step-by-step.
    5. CITATION: Always mention which document or rule you found in the search (e.g., "According to the HRA rules...").
    6. REBATE VS DEDUCTION: Note that a 'Rebate' (like 87A) reduces the total tax bill, while a 'Deduction' (like 80C/80D) reduces the taxable income.
    7. Do not use USD.
    8. Use INR.
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{user_input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_openai_tools_agent(llm, tools, prompt)
    
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=False, 
        handle_parsing_errors=True,
        max_iterations=5 
    )

    print("\n=== LifeTrail 2026: Phase 5 Agent Online (Stateless) ===")
    
    while True:
        user_query = input("You: ").strip()
        if user_query.lower() in ["exit", "quit"]: break
        if not user_query: continue

        # --- STEP 1: SAFETY CHECK ---
        safety_status = safety_check(user_query)
        if not safety_status["safe"]:
            # Highlight blocked message in terminal
            print(f"\n[ALERT/BLOCKED]\n{safety_status['message']}\n")
            continue

        # --- STEP 2: AGENT EXECUTION ---
        try:
            # Memory removed here to demonstrate Turn-2 failures in Phase 5
            res = agent_executor.invoke({"user_input": user_query})
            print(f"\nLifeTrail: {res['output']}\n")
        except Exception as e: 
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_lifetrail_agent()