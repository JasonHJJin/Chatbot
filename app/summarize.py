import os
import glob
from tqdm import tqdm
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("CHATBOT_OPENAI_API_KEY"))

#Baseline extension (including bottlenecks, inefficiencies in the summary)
SUMMARY_PROMPT = """
Analyze the following code file and provide a detailed summary:

Filename: {filename}

```{content}```

Your summary should include:
1. **Functionality**: What is the primary functionality or purpose of this file?
2. **Key Patterns**: Are there any notable patterns, architectures, or design principles used in this file?
3. **Dependencies**: Does this file depend on other files, modules, or external libraries? If so, describe them.
4. **Potential Issues**: Are there any obvious bottlenecks, bugs, or areas for improvement?
5. **Code Quality**: Are there any inconsistencies in coding style, logic, or structure? Provide suggestions for improvement.
6. **Integration**: How does this file integrate with or contribute to the overall project?

Provide your response in a structured format with clear headings for each section.
"""

README_PROMPT = """
Analyze the following README file and provide a detailed summary:

Filename: {filename}

```{content}```

Your summary should include:
1. **Project Purpose**: What is the primary goal or purpose of this repository?
2. **Key Components**: What are the main components or modules of the project?
3. **Usage Instructions**: Are there clear instructions for setting up, running, or using the project? If not, what is missing?
4. **Dependencies**: What dependencies or external tools are required?
5. **Documentation Quality**: Are there any unclear, incomplete, or missing sections in the README? Provide suggestions for improvement.
6. **Additional Notes**: Any other important information or observations about the README.

Provide your response in a structured format with clear headings for each section.
"""

MAIN_FILE_PROMPT = """
Analyze the following main file and provide a detailed summary:

Filename: {filename}

```{content}```

Your summary should include:
1. **Purpose**: What is the primary purpose of this file? Is it an entry point, a core module, or something else?
2. **Key Functionalities**: What are the main functionalities or features implemented in this file?
3. **Project Structure**: How does this file fit into the overall project structure? Does it interact with other files or modules?
4. **Entry Points**: Are there any clear entry points (e.g., `main()` function, API endpoints)? If so, describe them.
5. **Potential Issues**: Are there any obvious bottlenecks, inefficiencies, or areas for optimization?
6. **Code Quality**: Are there any inconsistencies in coding style, logic, or structure? Provide suggestions for improvement.

Provide your response in a structured format with clear headings for each section.
"""

FILE_EXTENSIONS = [
    "*.py", "*.js", "*.java", "*.c", "*.cpp", "*.ts", "*.go", "*.rb", "*.php",
    "*.md", "*.rst", "*.txt", "*.html", "*.css",
    "*.json", "*.yaml", "*.yml", "*.toml"
]

MAX_CONTEXT_TOKENS = 128000
CHUNK_SIZE = 90000  # leaving room for prompt and response

def chunk_text(text, max_length=CHUNK_SIZE):
    return [text[i:i + max_length] for i in range(0, len(text), max_length)]

# COuld do parallel processing but keeping it simple for now
def get_summary(data_path):
    summaries = {}

    # Prioritize README and documentation files
    readme_files = glob.glob(os.path.join(data_path, "**", "README.md"), recursive=True)
    other_files = [file for ext in FILE_EXTENSIONS for file in glob.glob(os.path.join(data_path, "**", ext), recursive=True) if file not in readme_files]

    # Summarize README files first
    for readme_file in readme_files:
        try:
            with open(readme_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": README_PROMPT.format(filename=readme_file, content=content)}],
            )
            summaries[readme_file] = response.choices[0].message.content.strip()

        except Exception as e:
            summaries[readme_file] = f"Error processing file: {str(e)}"

    # Identify and summarize main files
    main_files = [file for file in other_files if "main" in os.path.basename(file).lower() or "app" in os.path.basename(file).lower()]
    for main_file in main_files:
        try:
            with open(main_file, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "system", "content": MAIN_FILE_PROMPT.format(filename=main_file, content=content)}],
            )
            summaries[main_file] = response.choices[0].message.content.strip()

        except Exception as e:
            summaries[main_file] = f"Error processing file: {str(e)}"

    # Summarize remaining files
    for file_path in tqdm(other_files, desc="Summarizing files"):
        if file_path not in main_files and file_path not in readme_files:
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                chunks = chunk_text(content)
                file_summary = []

                for chunk in chunks:
                    response = client.chat.completions.create(
                        model="gpt-4",
                        messages=[{"role": "system", "content": SUMMARY_PROMPT.format(filename=file_path, content=chunk)}],
                    )
                    file_summary.append(response.choices[0].message.content.strip())

                summaries[file_path] = "\n\n".join(file_summary)

            except Exception as e:
                summaries[file_path] = f"Error processing file: {str(e)}"

    return summaries