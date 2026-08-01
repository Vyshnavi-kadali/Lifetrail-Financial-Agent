import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 1. Load your OpenAI API Key from a .env file
# Your .env file should contain: OPENAI_API_KEY=your_key_here
load_dotenv()

def run_lifetrail_agent():
    # 2. Initialize the Model (LLM)
    # Using 'gpt-4o-mini' for high accuracy in financial reasoning
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 3. Create a Specialized Prompt Template for 2026 Rules
    # We embed the 2026 fiscal logic directly into the system instructions.
    system_message = """You are LifeTrail, a specialized Financial Advisor for the year 2026.
    
    2026 NEW TAX REGIME RULES:
    - Standard Deduction: ₹75,000.
    - Tax Rebate (Section 87A): No tax if taxable income (Salary - ₹75k) is up to ₹12,00,000.
    - Slabs (on taxable income):
      * Up to ₹4L: 0%
      * ₹4L - ₹8L: 5%
      * ₹8L - ₹12L: 10%
      * ₹12L - ₹16L: 15%
      * ₹16L - ₹20L: 20%
      * ₹20L - ₹24L: 25%
      * Above ₹24L: 30%
    - Health & Education Cess: 4% of the calculated tax.

    2026 OLD TAX REGIME RULES:
    - Standard Deduction: ₹50,000.
    - Tax Rebate: No tax if taxable income is up to ₹5,00,000.
    - Slabs (on taxable income):
      * Up to ₹2.5L: 0%
      * ₹2.5L - ₹5L: 5%
      * ₹5L - ₹10L: 20%
      * Above ₹10L: 30%
    - Health & Education Cess: 4% of the calculated tax.

    2026 INFLATION DATA:
    - Gold: 18% per year.
    - Education: 12% per year.
    - Lifestyle: 8% per year.

    When users ask about tax or savings, use these specific 2026 rules to calculate and explain the results clearly. 
    Always compare the New and Old regimes if it helps the user save money."""

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{user_input}")
    ])

    # 4. Create the Chain (LCEL)
    chain = prompt | llm | StrOutputParser()

    print("--- LifeTrail 2026 Advisor Started ---")
    print("Type 'exit' to quit.\n")

    while True:
        # 5. Get User Input
        user_query = input("You: ").strip()

        if user_query.lower() in ["exit", "quit", "stop"]:
            print("LifeTrail: Goodbye! See you in 2026.")
            break

        if not user_query:
            continue

        # 6. Run the Chain and print the response
        try:
            # The agent will now use the 2026 rules defined in the prompt
            response = chain.invoke({"user_input": user_query})
            print(f"\nLifeTrail: {response}\n")
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_lifetrail_agent()