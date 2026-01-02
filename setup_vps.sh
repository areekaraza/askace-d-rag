#!/bin/bash
# AskAce: D'RAG - Complete VPS Deployment Script
# Run this on a fresh Ubuntu 22.04 server

set -e

echo "🚀 Starting AskAce deployment..."

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
echo "🔧 Installing system dependencies..."
sudo apt install -y python3 python3-pip python3-venv git curl htop nginx

# Install Ollama
echo "🤖 Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

# Start and enable Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Wait for Ollama to start
echo "⏳ Waiting for Ollama to start..."
sleep 5

# Pull the LLM model
echo "📥 Downloading language model (this may take a few minutes)..."
ollama pull llama3.2:1b

# Verify Ollama installation
echo "✅ Verifying Ollama installation..."
ollama list

# Setup application directory
APP_DIR="/home/$(whoami)/askace"
echo "📁 Setting up application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Download application files (you'll need to customize this)
echo "📂 Setting up application files..."
# Create basic app structure
mkdir -p {data,storage,rag}

# Install Node.js and PM2
echo "🟢 Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g pm2

# Setup Python virtual environment
echo "🐍 Setting up Python environment..."
python3 -m venv .venv
source .venv/bin/activate

# Create requirements file
cat > requirements.txt << 'EOF'
streamlit==1.41.1
faiss-cpu==1.9.0.post1
numpy==2.2.1
requests==2.32.3
sentence-transformers==5.1.1
pypdf==5.1.0
python-docx==1.1.2
EOF

# Install Python dependencies
pip install -r requirements.txt

# Create startup script
cat > start_askace.sh << 'EOF'
#!/bin/bash
cd /home/$(whoami)/askace
source .venv/bin/activate
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --server.fileWatcherType=none
EOF

chmod +x start_askace.sh

# Note: You'll need to copy your app files here
echo "📋 IMPORTANT: Copy your AskAce application files to $APP_DIR"
echo "   - Copy app.py, rag/ folder, and other files from your local machine"

# Setup firewall
echo "🔥 Configuring firewall..."
sudo ufw allow ssh
sudo ufw allow 8501
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

# Get server IP
SERVER_IP=$(curl -s ifconfig.me)

echo ""
echo "🎉 AskAce deployment setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Copy your app files to: $APP_DIR"
echo "   scp -r app.py rag/ user@$SERVER_IP:$APP_DIR/"
echo ""
echo "2. Start the application:"
echo "   cd $APP_DIR"
echo "   pm2 start start_askace.sh --name askace"
echo "   pm2 save"
echo "   pm2 startup"
echo ""
echo "3. Access your chatbot at: http://$SERVER_IP:8501"
echo ""
echo "🛠️  Useful commands:"
echo "   pm2 status          - Check app status"
echo "   pm2 logs askace     - View app logs"
echo "   pm2 restart askace  - Restart app"
echo "   ollama list         - Check available models"
echo ""