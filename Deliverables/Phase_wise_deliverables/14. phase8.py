import os
import json
import logging
import time
from dotenv import load_dotenv

# LangChain Imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_classic.agents import AgentExecutor, create_openai_tools_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool, create_retriever_tool

# 1. INITIALIZATION
load_dotenv()
logging.basicConfig(filename='lifetrail_final.log', level=logging.INFO, format='%(asctime)s - %(message)s')

PREFS_PATH = "user_preferences.json"

# --- DATA PERSISTENCE HELPERS ---
def load_prefs():
    if os.path.exists(PREFS_PATH):
        try:
            with open(PREFS_PATH, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"style": "default"}

def save_prefs(style):
    with open(PREFS_PATH, 'w') as f:
        json.dump({"style": style}, f)

# SAFETY VALIDATION DATA
RESTRICTED_ACTIONS = [
    "transfer money", "send money", "upi pin", "password", 
    "approve transaction", "bank otp", "otp", "upi id"
]

HIGH_RISK_KEYWORDS = [
    "fraud", "loan default", "suicide", "legal dispute", 
    "money laundering"
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

# --- PHASE 7 ADAPTATION CHECK ---
def check_for_feedback(user_input):
    """
    Checks if the user is giving feedback about the agent's behavior.
    """
    q = user_input.lower()
    if any(word in q for word in ["too long", "shorter", "concise", "brief", "too detailed", "keep it short"]):
        save_prefs("concise")
        return "Understood. I will keep my future responses concise and focused only on the essential data."
    if any(word in q for word in ["more detail", "explain", "longer", "detailed", "too short", "i dont understand"]):
        save_prefs("detailed")
        return "Understood. I will provide more detailed explanations and empathetic context in my future responses."
    return None

# 3. LOAD KNOWLEDGE BASE (RAG Tool)
def load_retriever():
    index_path = "LifeTrail_Combined_Index_Final"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
    return vectorstore.as_retriever(search_kwargs={"k": 10})

# 3. DEFINE STRATEGIC TOOLS (PHASE 1 LOGIC)
@tool
def calculate_2026_tax(salary: float, regime: str) -> str:
    """Calculates the 2026 Indian Income Tax precisely. 'regime' must be 'new' or 'old'."""
    try:
        tax=0
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
    except Exception as e:
        return f"Error in tax calculation: {str(e)}"

@tool
def calculate_goal_feasibility(current_cost: float, years: float, goal_type: str, monthly_income: float) -> str:
    """
    Predictive Tool for 2026 Goals. 
    Inflation: Gold/Jewelry (18%), Education (12%), Lifestyle/Travel (8%).
    Flags 'Unrealistic' goals if monthly savings > 50% of income.
    NOTE: 'years' is a float. If the user says 6 months, pass 0.5.
    """
    try:

        if years <= 0:
            return json.dumps({"error": "Timeline must be greater than zero. Please specify a valid duration in years or months."})

        rates = {"gold": 0.18, "jewelry": 0.18, "education": 0.12, "lifestyle": 0.08, "travel": 0.08}
        rate = rates.get(goal_type.lower(), 0.08)
        
        future_cost = current_cost * ((1 + rate) ** years)
        monthly_savings = future_cost / (years * 12)
        
        status = "Realistic"
        if monthly_savings > (monthly_income * 0.5):
            status = "Unrealistic/High Risk (Exceeds 50% of your take-home pay)"
        
        return json.dumps({
            "future_cost_in_2026": round(future_cost, 2),
            "required_monthly_savings": round(monthly_savings, 2),
            "feasibility_status": status,
            "inflation_applied": f"{int(rate*100)}%"
        })
    except Exception as e:
        return f"Error in goal calculation: {str(e)}"

@tool
def guilt_to_guidance_course_correction(splurge_amount: float, remaining_months: int) -> str:
    """
    Calculates how to adjust a savings plan after a 'guilt spend' (splurge).
    Redistributes the splurge amount over the remaining months.
    """
    if remaining_months <= 0:
        return json.dumps({"error": "Remaining months must be at least 1."})

    extra_per_month = splurge_amount / remaining_months
    return json.dumps({
        "course_correction": f"Increase your monthly savings by ₹{round(extra_per_month, 2)} for the next {remaining_months} months to stay on track."
    })

# 4. AGENT RUNNER
def run_lifetrail_agent():
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    # Graceful failure handling on initialization
    try:
        retriever_tool = create_retriever_tool(
            load_retriever(), 
            "search_financial_docs", 
            "Access 2026 facts on tax, HRA, 80C, 80D, and India Post rules."
        )
    except Exception as e:
        logging.critical(f"Deployment Failed: {e}")
        print("FATAL: Could not initialize knowledge base. Check logs.")
        return
    
    tools = [retriever_tool, calculate_2026_tax, calculate_goal_feasibility, guilt_to_guidance_course_correction]
    chat_history = []

    print("\n" + "="*45)
    print("\n=== LifeTrail: Your 2026 Lifecycle Companion Online ===")
    print(" LIFE-TRAIL 2026 DEPLOYMENT READY ".center(45))
    print("="*45)
    print("Tracing: lifetrail_production.log | Persistence: ON\n")

    
    
    while True:
        # RELOAD PREFERENCES AND REBUILD AGENT EVERY TURN TO ENSURE ADAPTATION
        prefs = load_prefs()
        style_instruction = ""
        if prefs['style'] == "concise":
            style_instruction = "User prefers CONCISE answers. Skip introductory fluff. Provide only essential data and results without long explanations."
        elif prefs['style'] == "detailed":
            style_instruction = "User prefers DETAILED and LONG answers. Always provide full context, empathetic reasoning, and step-by-step breakdowns of all math or advice."

        system_message = f"""You are LifeTrail, a Predictive & Empathetic Financial Companion for 2026.
        {style_instruction}
        
        STRICT FINANCIAL ADVISOR RULE: You are ONLY allowed to discuss finances, taxes, and savings goals. 
        Do NOT suggest restaurants, food (like Biryani), travel spots, or entertainment. 
        If a user asks about non-financial topics, you MUST say: 'I'm sorry, my current 2026 knowledge base doesn't have specific details on that.'
        Use Tools for ALL math
        
        YOUR CORE LOGIC:
        1. MANDATORY TOOL CALL: If a user asks about a goal with a 0-year, 0-month, or 'immediate' timeline, you are FORBIDDEN from answering with text reasoning. You MUST call 'calculate_goal_feasibility' with years=0.0 to receive the official system error message.
        2. PREDICTIVE: Always use the goal tool and tax tool for calculations. Convert months to years (e.g., 6 months = 0.5 years).
        3. EMPATHETIC: If a user mentions 'guilt' or a 'splurge', use the 'course_correction' tool.
        4. STRATEGIC: If a goal is 'Unrealistic' (more than 50% of income), warn the user.
        5. GROUNDED: Use 'search_financial_docs' for all tax/savings facts.
        6. DEBT PRIORITIZATION: Advise paying off high-interest debt (like bike loans) before low-return savings.
        """

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{user_input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])

        agent = create_openai_tools_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False, max_iterations=5, handle_parsing_errors=True)

        user_query = input("You: ").strip()
        if user_query.lower() in ["exit", "quit"]: break
        if not user_query: continue

        # PHASE 6: Memory Reset Behavior
        if user_query.lower() == "reset":
            chat_history = []
            print("\nLifeTrail: Conversation history has been reset. How can I help you afresh?\n")
            continue
        
        # Safety Check
        safety = safety_check(user_query)
        if not safety["safe"]:
            print(f"\n[BLOCKED]\n{safety['message']}\n"); continue

        # Check for Adaptation Signal
        feedback_msg = check_for_feedback(user_query)
        if feedback_msg:
            print(f"\nLifeTrail (Learning): {feedback_msg}\n")
            continue

        try:
            start_time = time.time()
            
            res = agent_executor.invoke({"user_input": user_query, "chat_history": chat_history})
            latency = round(time.time() - start_time, 2)
            print(f"\nLifeTrail: {res['output']}\n")
            print(f"--- [Tracing: Latency {latency}s] ---")
            
            chat_history.append(("human", user_query))
            chat_history.append(("ai", res['output']))
            logging.info(f"Query: {user_query[:50]}... | Latency: {latency}s | Status: SUCCESS")
            
        except Exception as e:
            # Graceful Failure Handling
            logging.error(f"Error: {e}")
            print(f"\nLifeTrail: I encountered a technical issue. Please ensure your query includes clear numbers.\n")
            

if __name__ == "__main__":
    run_lifetrail_agent()