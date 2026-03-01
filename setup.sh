#!/bin/bash

# Setup script for AI-Powered Web Reading System

set -e

echo "========================================="
echo "AI-Powered Web Reading System Setup"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Detect OS
OS=$(uname -s)
echo "Detected OS: $OS"
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check Python
echo "Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✓${NC} $PYTHON_VERSION"
else
    echo -e "${YELLOW}⚠${NC} Python 3 not found. Please install Python 3.8+"
    exit 1
fi

# Check pip
echo "Checking pip installation..."
if command_exists pip3; then
    PIP_VERSION=$(pip3 --version)
    echo -e "${GREEN}✓${NC} pip installed"
else
    echo -e "${YELLOW}⚠${NC} pip not found. Installing..."
    python3 -m ensurepip --upgrade
fi

echo ""
echo "========================================="
echo "Setting up Webpage Sync Module"
echo "========================================="
cd webpage_sync_module

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create config if not exists
if [ ! -f "config.yaml" ]; then
    echo "Creating config.yaml from example..."
    cp config.yaml.example config.yaml
    echo -e "${YELLOW}⚠${NC} Please edit webpage_sync_module/config.yaml with your SSH settings"
else
    echo -e "${GREEN}✓${NC} config.yaml already exists"
fi

# Create data directories
mkdir -p data/markdown data/metadata
echo -e "${GREEN}✓${NC} Data directories created"

cd ..

echo ""
echo "========================================="
echo "Setting up AI Server Module"
echo "========================================="
cd aiserver_module

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Create config if not exists
if [ ! -f "config.yaml" ]; then
    echo "Creating config.yaml from example..."
    cp config.yaml.example config.yaml
    echo -e "${YELLOW}⚠${NC} Please edit aiserver_module/config.yaml with your LLM API key"
else
    echo -e "${GREEN}✓${NC} config.yaml already exists"
fi

# Create directories
mkdir -p webpages processed output templates
echo -e "${GREEN}✓${NC} Data directories created"

cd ..

echo ""
echo "========================================="
echo "Setting up Chrome Extension"
echo "========================================="
cd chrome_plugin_module

# Create placeholder icons if they don't exist
mkdir -p icons

if [ ! -f "icons/icon16.png" ]; then
    echo "Note: Chrome extension icons need to be created"
    echo "You can:"
    echo "  1. Create your own icons (16x16, 48x48, 128x128)"
    echo "  2. Use online icon generators"
    echo "  3. Extract icons from existing extensions"
    echo ""
    echo "For now, you can load the extension without icons (it will use default)"
fi

cd ..

echo ""
echo "========================================="
echo "Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure SSH connection (MacBook to Desktop):"
echo "   ${YELLOW}ssh-keygen -t ed25519${NC}"
echo "   ${YELLOW}ssh-copy-id -p 9911 username@192.168.59.111${NC}"
echo ""
echo "2. Edit configurations:"
echo "   - webpage_sync_module/config.yaml (SSH settings)"
echo "   - aiserver_module/config.yaml (LLM API key)"
echo ""
echo "3. Start services:"
echo "   Terminal 1 (MacBook):"
echo "   ${YELLOW}cd webpage_sync_module && python3 sync_service.py${NC}"
echo ""
echo "   Terminal 2 (Desktop Server):"
echo "   ${YELLOW}cd aiserver_module && python3 ai_server.py${NC}"
echo ""
echo "4. Install Chrome extension:"
echo "   - Open chrome://extensions/"
echo "   - Enable Developer mode"
echo "   - Click 'Load unpacked'"
echo "   - Select chrome_plugin_module/ directory"
echo ""
echo "5. Access dashboard:"
echo "   ${YELLOW}http://localhost:5000${NC}"
echo ""
echo "========================================="
echo -e "${GREEN}Happy browsing with AI assistance!${NC}"
echo "========================================="
