#!/bin/bash

echo "🚀 Market Regime Detection App - Setup Script"
echo "=============================================="
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    exit 1
fi

echo "✓ Node.js $(node --version) found"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.9+ first."
    exit 1
fi

echo "✓ Python $(python3 --version) found"
echo ""

# Frontend setup
echo "📦 Installing frontend dependencies..."
npm install
echo "✓ Frontend dependencies installed"
echo ""

# Backend setup
echo "📦 Setting up Python virtual environment..."
cd api
python3 -m venv venv

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    source venv/Scripts/activate
fi

echo "📦 Installing Python dependencies..."
pip install -r requirements.txt
echo "✓ Backend dependencies installed"
echo ""

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the application:"
echo ""
echo "Terminal 1 (Backend):"
echo "  cd api"
echo "  source venv/bin/activate"
echo "  uvicorn main:app --reload --port 8000"
echo ""
echo "Terminal 2 (Frontend):"
echo "  npm run dev"
echo ""
echo "Then open: http://localhost:3000"
