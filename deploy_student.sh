#!/bin/bash
# AskAce: D'RAG - GitHub Student Pack Deployment
# Optimized for DigitalOcean with student credits

set -e

echo "🎓 Welcome to AskAce GitHub Student Pack Deployment!"
echo "This will set up your chatbot on DigitalOcean with free credits"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root: sudo ./deploy_student.sh"
    exit 1
fi

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}==>${NC} $1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Update system
print_step "Updating system packages..."
apt update && apt upgrade -y
print_success "System updated"

# Install system dependencies
print_step "Installing system dependencies..."
apt install -y python3 python3-pip python3-venv git curl htop nginx ufw fail2ban
print_success "Dependencies installed"

# Install Ollama
print_step "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh
systemctl start ollama
systemctl enable ollama
print_success "Ollama installed and started"

# Wait for Ollama to start
print_step "Waiting for Ollama to initialize..."
sleep 10

# Pull AI model
print_step "Downloading AI model (this may take several minutes)..."
ollama pull llama3.2:1b
print_success "AI model downloaded"

# Verify Ollama
print_step "Verifying Ollama installation..."
ollama list
print_success "Ollama verification complete"

# Setup application directory
APP_DIR="/opt/askace"
print_step "Setting up application directory: $APP_DIR"
mkdir -p $APP_DIR
cd $APP_DIR

# Get repository URL from user
echo ""
echo -e "${YELLOW}📋 Please provide your GitHub repository details:${NC}"
read -p "Enter your GitHub username: " GITHUB_USER
read -p "Enter your repository name (e.g., askace-chatbot): " REPO_NAME

REPO_URL="https://github.com/$GITHUB_USER/$REPO_NAME.git"

# Clone repository
print_step "Cloning repository: $REPO_URL"
git clone $REPO_URL .
print_success "Repository cloned"

# Setup Python environment
print_step "Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
print_success "Virtual environment created"

# Install Python dependencies
print_step "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt
print_success "Dependencies installed"

# Install Node.js and PM2
print_step "Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
npm install -g pm2
print_success "PM2 installed"

# Create startup script
print_step "Creating startup script..."
cat > start_askace.sh << EOF
#!/bin/bash
cd $APP_DIR
source .venv/bin/activate
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --server.fileWatcherType=none
EOF

chmod +x start_askace.sh
print_success "Startup script created"

# Create systemd service (alternative to PM2)
print_step "Creating systemd service..."
cat > /etc/systemd/system/askace.service << EOF
[Unit]
Description=AskAce RAG Chatbot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/start_askace.sh
Restart=always
RestartSec=3
Environment=PATH=/usr/local/bin:/usr/bin:/bin
Environment=NODE_ENV=production

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable askace
print_success "Systemd service created"

# Configure firewall
print_step "Configuring firewall..."
ufw --force enable
ufw allow ssh
ufw allow 8501
ufw allow 80
ufw allow 443
print_success "Firewall configured"

# Setup fail2ban for security
print_step "Configuring security..."
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
systemctl enable fail2ban
systemctl start fail2ban
print_success "Security configured"

# Start the application
print_step "Starting AskAce application..."
systemctl start askace

# Also start with PM2 as backup
pm2 start start_askace.sh --name askace
pm2 save
pm2 startup --user root --hp /root > /dev/null 2>&1
print_success "Application started"

# Get server IP
SERVER_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "Unable to detect")

# Final setup summary
echo ""
echo "🎉 AskAce deployment complete!"
echo ""
echo -e "${GREEN}📋 Deployment Summary:${NC}"
echo "├─ Server IP: $SERVER_IP"
echo "├─ App URL: http://$SERVER_IP:8501"
echo "├─ App Directory: $APP_DIR"
echo "├─ AI Model: llama3.2:1b"
echo "└─ GitHub Repo: $REPO_URL"
echo ""
echo -e "${YELLOW}🛠️  Management Commands:${NC}"
echo "├─ Check status: systemctl status askace"
echo "├─ View logs: journalctl -u askace -f"
echo "├─ Restart app: systemctl restart askace"
echo "├─ Update code: cd $APP_DIR && git pull"
echo "└─ PM2 status: pm2 status"
echo ""
echo -e "${BLUE}🔒 Next Steps (Optional):${NC}"
echo "1. Get free domain from Namecheap (GitHub Student Pack)"
echo "2. Point domain to $SERVER_IP"
echo "3. Setup SSL with: certbot --nginx -d yourdomain.com"
echo ""
echo -e "${GREEN}✨ Your AskAce chatbot is now live at: http://$SERVER_IP:8501${NC}"

# Create quick info file
cat > /root/askace_info.txt << EOF
AskAce Deployment Info
=====================
Date: $(date)
Server IP: $SERVER_IP
App URL: http://$SERVER_IP:8501
App Directory: $APP_DIR
GitHub Repo: $REPO_URL

Management Commands:
- systemctl status askace
- journalctl -u askace -f  
- systemctl restart askace
- cd $APP_DIR && git pull && systemctl restart askace

To setup domain:
1. Point DNS A record to $SERVER_IP
2. Run: certbot --nginx -d yourdomain.com
EOF

print_success "Deployment info saved to /root/askace_info.txt"