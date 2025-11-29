import os
import json
from dotenv import load_dotenv

from langchain_chroma import Chroma
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- Configuration ---
load_dotenv()
# Use the correct, standardized environment variable
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
DB_PATH = "backend/chroma_db"
LLM_MODEL = "gemini-2.5-flash"  # The model for chat responses

# This is the prompt template that tells the LLM its role and provides context
RAG_PROMPT_TEMPLATE = """
You are an expert on HMRC regulations and a helpful AI assistant. 
Answer the user's question based *only* on the provided context below.
If the context does not contain the answer, politely state that the information is not available in the source documents.

Context:
{context}

Question: {question}
"""


def handler(event, context):
    """
    Vercel Serverless function handler.
    Processes a POST request containing a user query.
    """
    if not GOOGLE_API_KEY:
        return {
            'statusCode': 500,
            'body': json.dumps({"error": "GOOGLE_API_KEY not configured."})
        }

    # 1. Parse Input Query from Vercel Event
    try:
        # Vercel wraps the request body in the 'event' dictionary
        body = json.loads(event['body'])
        user_query = body.get("query")
    except Exception:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Invalid JSON body or missing 'query'."})
        }

    if not user_query:
        return {
            'statusCode': 400,
            'body': json.dumps({"error": "Missing 'query' parameter."})
        }

    try:
        # 2. Setup RAG Chain Components

        # Initialize Embeddings for retriever
        embeddings = GoogleGenerativeAIEmbeddings(
            model="text-embedding-004",
            api_key=GOOGLE_API_KEY
        )

        # Load the saved Chroma DB
        vector_store = Chroma(
            persist_directory=DB_PATH,
            embedding_function=embeddings
        )

        # Create a Retriever component
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        # Initialize the Chat LLM
        llm = ChatGoogleGenerativeAI(
            model=LLM_MODEL,
            temperature=0.1,
            api_key=GOOGLE_API_KEY
        )

        # Create the prompt structure
        prompt = ChatPromptTemplate.from_template(RAG_PROMPT_TEMPLATE)

        # 3. Define the RAG Chain
        # The chain handles the flow: Retrieve -> Format Context -> Prompt LLM -> Output
        rag_chain = (
                {"context": retriever, "question": RunnablePassthrough()}
                | prompt
                | llm
                | StrOutputParser()
        )

        # 4. Run the Chain
        print(f"Executing RAG chain for query: {user_query}")
        response = rag_chain.invoke(user_query)

        # 5. Return Response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'  # Important for Vercel/CORS
            },
            'body': json.dumps({"response": response})
        }

    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({"error": f"Internal server error: {str(e)}"})
        }


# This allows for local testing if needed, though Vercel uses handler(event, context)
if __name__ == "__main__":
    print("--- Running Local Test of RAG Chain ---")

    # 1. Simulate the request body that Vercel would send
    test_event = {
        'body': json.dumps(
            {"query": "What is the small profits rate for corporation tax and what is the deadline for filing?"})
    }

    # 2. Call the handler function directly
    result = handler(test_event, None)

    # 3. Print the successful response body
    print("--- Test Result (Should contain the answer) ---")
    # Decode the JSON response body for clean viewing
    response_body = json.loads(result['body'])
    print(response_body['response'])