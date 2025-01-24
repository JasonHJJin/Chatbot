# Chatbot Project

This chatbot allows users to ask questions about a given code repository ("data" folder), referencing actual code segments when relevant. It can analyze individual files or the entire repository to provide meaningful insights.

## Setup

# 1. Clone the repository
```sh
git clone https://github.com/your-username/Chatbot.git
cd Chatbot
```

# 2. Set up a virtual environment

# For Windows:
```sh
python -m venv venv
venv\Scripts\activate
```

# For macOS/Linux:
```sh
python3 -m venv venv
source venv/bin/activate
```

# 3. Install dependencies
```sh
pip install -r requirements.txt
```

# 4. Configure the Repository for Analysis
Replace the contents of the data/ folder (located in the root directory) with the repository you want the chatbot to analyze.

# 5. Run the chatbot
```sh
python run.py
```

# 5. Deactivate the virtual environment (when done)
```sh
deactivate
```
