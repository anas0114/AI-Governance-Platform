# AI Governance Platform - Frontend Setup Guide (Windows PowerShell)

# IMPORTANT: Make sure Node.js 16+ and npm are installed
# Download from https://nodejs.org/ if not installed

# Step 1: Verify Node.js and npm are installed
node --version
npm --version

# Step 2: Navigate to frontend directory
cd frontend

# Step 3: Clean previous installations (if needed)
rm -r node_modules -Force
rm package-lock.json -Force
npm cache clean --force

# Step 4: Install dependencies
npm install

# Step 5: Create .env.local file (if not exists)
if (-not (Test-Path .env.local)) {
  Copy-Item .env.example .env.local
}

# Step 6: Make sure .env.local has the correct API URL
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# Step 7: Clear Next.js cache
rm -r .next -Force

# Step 8: Start development server
npm run dev

# The frontend will be available at http://localhost:3000
