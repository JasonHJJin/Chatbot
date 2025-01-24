import os
import glob
import pandas as pd
import tiktoken
from tqdm import tqdm
from langchain.text_splitter import CharacterTextSplitter

# Configuration
CHUNK_SIZE = 850  # Number of tokens per chunk
CHUNK_OVERLAP = 150  # Token overlap between chunks
LANGUAGE_MAPPING = {
    ".py": "Python",
    ".js": "JavaScript",
    ".java": "Java",
    ".c": "C",
    ".cpp": "C++",
    ".ts": "TypeScript",
    ".go": "Go",
    ".rb": "Ruby",
    ".php": "PHP"
}

def get_num_tokens(text, model="text-davinci-003"):
    """Calculate the number of tokens in a text string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

def get_language(file_path):
    """Determine the programming language based on the file extension."""
    _, ext = os.path.splitext(file_path)
    return LANGUAGE_MAPPING.get(ext, "Unknown")

def get_chunks(data_path, summaries):
    
    file_extensions = ["*.py", "*.js", "*.java", "*.c", "*.cpp", "*.ts", "*.go", "*.rb", "*.php"]
    
    file_paths = [file for ext in file_extensions for file in glob.glob(os.path.join(data_path, "**", ext), recursive=True)]
    
    if not file_paths:
        raise ValueError("No files found. Check the data path and file extensions.")
    
    docs = []
    for file_path in tqdm(file_paths, desc="Loading files"):
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading file {file_path}: {e}")
            continue
        
        # Use precomputed summary
        summary = summaries.get(file_path, "No summary available.")
        
        # Combine summary with content
        combined_content = f"Summary:\n{summary}\n\nCode:\n{content}"
        
        docs.append({"filename": file_path, "content": combined_content})
    
    df = pd.DataFrame(docs)
    df["tokens"] = df["content"].apply(get_num_tokens)
    
    # Chunking
    text_splitter = CharacterTextSplitter(
        separator="\n", chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
        length_function=lambda text: len(tiktoken.encoding_for_model("text-davinci-003").encode(text))
    )
    
    df_chunks = []
    for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Chunking files"):
        chunks = text_splitter.create_documents([row['content']])
        for j, chunk in enumerate(chunks):
            df_chunks.append({
                "filename": row["filename"],
                "chunk_num": j,
                "chunk": chunk.page_content,
                "chunk_tokens": get_num_tokens(chunk.page_content)
            })
    
    df_chunks = pd.DataFrame(df_chunks)
    chunks_json = f"./Chunks_{CHUNK_SIZE}.json"
    df_chunks.to_json(chunks_json, indent=4)

    return df_chunks