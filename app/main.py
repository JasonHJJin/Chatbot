from app.summarize import get_summary
from app.chunks import get_chunks
from app.embeddings import get_embeddings
from app.search import search_chunks

import os
from openai import OpenAI

#for simple animation...
import time
import threading
import sys

client = OpenAI(api_key=os.getenv("CHATBOT_OPENAI_API_KEY"))

def openai_chatgpt(query, context):
    prompt = f"""
    You are a knowledgeable assistant. Use the following context to answer the question.
    Context: {context}
    Question: {query}
    Answer:
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "You are a helpful AI assistant."},
                  {"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()

def animate_processing():
    # Simple animation using dots
    while not animation_done:
        for i in range(4):
            sys.stdout.write("\r[CHATBOT] Processing" + "." * i + "   ")
            sys.stdout.flush()
            time.sleep(0.5)
        sys.stdout.write("\r" + " " * 30 + "\r")  # Clear the line

def main():
    global animation_done
    data_path = "./data"

    # Get Summary
    print("[INFO] Summarizing...")
    summary = get_summary(data_path)

    # Create Knowledge Base
    print("[INFO] Creating Knowledge Base...")
    chunks = get_chunks(data_path, summary)
    embeddings = get_embeddings(chunks)
    print("[INFO] Knowledge Base Created!\n", "-" * 38)

    # Chatbot
    print("\n[CHATBOT] Ready. Type your query or 'exit' to quit.")
    while True:
        user_query = input("\n[YOU]: ")
        if user_query.lower() == "exit":
            print("[INFO] Shutting down...")
            break

        # Start the animation
        animation_done = False
        animation_thread = threading.Thread(target=animate_processing)
        animation_thread.start()

        # Process the query
        relevant_texts = search_chunks(user_query, embeddings)
        response = openai_chatgpt(user_query, relevant_texts)

        # Stop the animation
        animation_done = True
        animation_thread.join()

        # Print the response
        print("\r[CHATBOT]:", response)

if __name__ == "__main__":
    main()