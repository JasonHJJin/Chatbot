import os
from tqdm import tqdm
from openai import OpenAI

client = OpenAI(api_key=os.getenv("CHATBOT_OPENAI_API_KEY"))

def get_embeddings(df_chunks):

    # Ensure 'chunk' is treated as a string and drop rows where 'chunk' is empty or invalid
    df_chunks = df_chunks[df_chunks['chunk'].astype(str) != "0"].copy()

    def get_embedding(row):
        query = row['chunk']
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=[query]
        )
        return response.data[0].embedding, response.usage.total_tokens

    #progress bar
    tqdm.pandas()
    df_chunks[['embedding', 'totalTokens']] = df_chunks.progress_apply(get_embedding, axis=1, result_type='expand')

    df_chunks.to_json("./Embeddings_850.json", orient="records", indent=4)

    return df_chunks
