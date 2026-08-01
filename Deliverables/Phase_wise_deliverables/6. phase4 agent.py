import os
import logging
from dotenv import load_dotenv

# LangChain Imports for RAG
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. INITIALIZATION
load_dotenv()

# Setup logging
logging.basicConfig(
    filename='lifetrail_rag.log', 
    level=logging.INFO, 
    format='%(asctime)s - %(message)s'
)

def load_knowledge_base(index_path="LifeTrail_Combined_Index_Final"):
    """
    Loads the existing FAISS index that was created during the ingestion phase.
    """
    print(f"LifeTrail: Connecting to local knowledge base at '{index_path}'...")
    
    # Use the same embedding model used during ingestion for consistency
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    
    # Load the local index (allow_dangerous_deserialization is required for loading local FAISS files)
    vectorstore = FAISS.load_local(
        index_path, 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    
    print("LifeTrail: Knowledge base connected and ready for queries.")
    return vectorstore.as_retriever(search_kwargs={"k": 3})

def run_lifetrail_agent():
    # 2. Setup the Retriever (Loading the saved index)
    try:
        retriever = load_knowledge_base("LifeTrail_Combined_Index_Final")
    except Exception as e:
        print(f"Error loading Knowledge Base: {e}")
        print("Please ensure the 'LifeTrail_Combined_Index_Final' folder is in your project directory.")
        return

    # 3. Initialize the Model
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 4. Create a RAG-specific Prompt
    system_message = """You are LifeTrail, a specialized Financial Advisor for the year 2026.
    
    Use the provided context from our official financial documents to answer the user's question.
    
    RULES:
    1. If the context contains tax slabs or interest rates, use them for calculations.
    2. If the user asks for a calculation, show your work step-by-step.
    3. If the answer is not in the provided context, say: "I'm sorry, my current 2026 knowledge base doesn't have specific details on that. Let me look at the general rules instead."
    4. Always maintain a professional, empathetic, and clear tone.

    CONTEXT:
    {context}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_message),
        ("human", "{user_input}")
    ])

    # 5. Create the RAG Chain
    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
        {"context": retriever | format_docs, "user_input": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    print("\n=== LifeTrail Phase 4: RAG-Enabled Advisor Online ===")
    print("I am now using your pre-indexed knowledge base.")
    print("Type 'exit' to quit.\n")

    while True:
        user_query = input("You: ").strip()

        if user_query.lower() in ["exit", "quit", "stop"]:
            print("LifeTrail: Goodbye! See you in 2026.")
            break

        if not user_query:
            continue

        try:
            # The chain retrieves the relevant chunks from your FAISS index and answers
            response = rag_chain.invoke(user_query)
            print(f"\nLifeTrail: {response}\n")
            logging.info(f"User: {user_query} | AI (RAG): {response}")

        except Exception as e:
            print(f"An error occurred: {e}")
            logging.error(f"Error: {e}")

if __name__ == "__main__":
    run_lifetrail_agent()