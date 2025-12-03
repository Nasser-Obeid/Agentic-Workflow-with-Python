"""Configuration settings for the application"""

# Ollama Configuration
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"

# Flask Configuration
FLASK_HOST = "0.0.0.0"
FLASK_PORT = 5000
FLASK_DEBUG = True

# Tool Configuration
ENABLE_WEB_SEARCH = True
ENABLE_CALCULATOR = True
ENABLE_FILE_OPS = True