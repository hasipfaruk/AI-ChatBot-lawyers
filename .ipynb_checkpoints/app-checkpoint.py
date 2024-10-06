import gradio as gr
from qdrant_utils import get_retriever
from groq_utils import initialize_groq
from custom_prompt_template import prompt_template

# Initialize components
retriever = get_retriever()  # Retrieve the Qdrant retriever
llm = initialize_groq()       # Initialize the Groq LLM

def format_docs(docs):
    formatted_docs = []
    for doc in docs:
        metadata_str = ", ".join(f"{key}: {value}" for key, value in doc.metadata.items())
        doc_str = f"{doc.page_content}\nMetadata: {metadata_str}"
        formatted_docs.append(doc_str)
    return "\n\n".join(formatted_docs)

def chatbot_response(history, query):
    print(f"Received query: {query}")
    
    try:
        # Retrieve relevant documents from Qdrant
        docs = retriever.invoke(query)

        # Handle case when no documents are retrieved
        if not docs:
            formatted_context = "No relevant documents found."
        else:
            formatted_context = "\n".join([doc.page_content for doc in docs])
        
        # Create the prompt
        formatted_prompt = prompt_template.format(context=formatted_context, question=query)
        messages = [{"role": "user", "content": formatted_prompt}]
        
        # Get LLM response
        response_data = llm.invoke(messages)
        
        # Log response to inspect the structure
        print(f"LLM Response: {response_data}")

        # Ensure the response is correctly accessed
        if isinstance(response_data, dict):
            response_text = response_data['content']  # If it's a dict
        elif hasattr(response_data, "content"):
            response_text = response_data.content  # If it's an object with an attribute
        else:
            response_text = str(response_data)  # Fallback to string format

        # Add history for chat context
        history.append(("User", query))
        history.append(("Legal Assistant", response_text))
        
        return history, history  # Return history for both input and output

    except Exception as e:
        print(f"Error: {e}")
        history.append(("Legal Assistant", "An error occurred. Please try again."))
        return history, history

# Define the Gradio Interface with Custom Styling
css = """
.chatbox {
    background-color: #f7f7f8;
    font-family: 'Arial', sans-serif;
}
.chat-message {
    border-radius: 10px;
    padding: 10px;
    margin: 10px 0;
}
.chat-message.user {
    background-color: #cef;
    text-align: right;
}
.chat-message.assistant {
    background-color: #f1f1f1;
    text-align: left;
}
"""

iface = gr.Interface(
    fn=chatbot_response, 
    inputs=[
        gr.State([]),  # To maintain chat history
        gr.Textbox(label="Enter your query", placeholder="Ask about legal guidance...")
    ],
    outputs=[
        gr.Chatbot(label="Legal Guide PK Chatbot", elem_classes="chatbox"),  # Chatbot component
        gr.State([])  # To maintain chat history as output
    ],
    title="Legal Guide PK - Chatbot",
    description="This chatbot provides legal guidance on various topics. Simply enter your query below and get assistance.",
    css=css
)

# Launch the Gradio app
if __name__ == "__main__":
    iface.launch()
