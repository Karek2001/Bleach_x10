#!/bin/bash
# setup_server_envs.sh - Helper script to create server-specific .env files

echo "================================================"
echo "Server-Specific .env File Setup"
echo "================================================"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "Please create .env first using .env.example as template"
    exit 1
fi

# Create .env1, .env2, .env3 if they don't exist
for i in 1 2 3; do
    if [ ! -f ".env$i" ]; then
        echo "📝 Creating .env$i from .env..."
        cp .env ".env$i"
        echo "✅ Created .env$i (RDP#$i)"
    else
        echo "⚠️  .env$i already exists, skipping..."
    fi
done

echo ""
echo "================================================"
echo "✅ Setup Complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "1. Edit .env1, .env2, .env3 with server-specific credentials"
echo "2. Run: python project_sync.py"
echo ""
echo "The sync script will automatically:"
echo "  • Sync .env1 to RDP#1 as .env"
echo "  • Sync .env2 to RDP#2 as .env"
echo "  • Sync .env3 to RDP#3 as .env"
echo ""
