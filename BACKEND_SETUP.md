# AI Governance Platform - Backend Setup Guide (Windows PowerShell)

# IMPORTANT: Make sure Python 3.10+ is installed and in your PATH
# Download from https://www.python.org/downloads/ if not installed

# Step 1: Verify Python is installed
python --version

# Step 2: Navigate to backend directory (if not already there)
# From AI-Governance-Platform root:
cd backend

# Step 3: Create virtual environment
python -m venv venv

# Step 4: Activate virtual environment
venv\Scripts\Activate.ps1

# If you get an execution policy error, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Step 5: Upgrade pip
python -m pip install --upgrade pip

# Step 6: Install dependencies
pip install -r requirements.txt

# On Windows, use the included workaround instead of the command above:
# pip install -r requirements-windows.txt
# pip install chroma-hnswlib==0.7.5
# pip install chromadb==0.5.11 langchain-chroma==0.1.4 --no-deps

# Step 7: Create .env file from example
Copy-Item .env.example .env

# Step 8: Update .env with your settings:
# - OPENAI_API_KEY (required)
# - DATABASE_URL (if not using default)
# - CHROMA_HOST/CHROMA_PORT (if running separately)

# Step 9: Run database migrations (if needed)
# cd ..
# alembic upgrade head

# Step 10: Start the backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
