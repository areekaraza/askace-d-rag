# 🚀 Deploy AskAce: D'RAG on VPS with Ollama

**Complete guide for deploying your chatbot with full privacy and cost control**

## 🎯 Why VPS + Ollama?

✅ **Complete Privacy** - All data stays on your server  
✅ **No Per-Query Costs** - Unlimited usage once deployed  
✅ **Full Control** - Customize everything  
✅ **Use Your Current App** - No code changes needed  

---

## 💰 VPS Provider Options

### **Recommended Providers:**

| Provider | Cost | RAM | Storage | Best For |
|----------|------|-----|---------|----------|
| **DigitalOcean** | $12/month | 2GB | 50GB SSD | Easiest setup |
| **Vultr** | $6/month | 2GB | 55GB SSD | Budget option |
| **Linode** | $12/month | 2GB | 50GB SSD | Great support |
| **Hetzner** | $5/month | 4GB | 40GB SSD | Best value (EU) |

**⚠️ Minimum Requirements:** 2GB RAM, 20GB storage

---

## 🚀 Step 1: Create VPS Server

### **DigitalOcean (Recommended)**
1. Sign up at [digitalocean.com](https://digitalocean.com)
2. Create Droplet:
   - **Image:** Ubuntu 22.04 LTS
   - **Size:** Basic ($12/month, 2GB RAM)
   - **Region:** Closest to you
   - **Authentication:** SSH Key (recommended) or Password

3. Note your server IP address

### **Alternative: Vultr (Budget)**
1. Sign up at [vultr.com](https://vultr.com)
2. Deploy Server:
   - **OS:** Ubuntu 22.04
   - **Size:** Regular Performance ($6/month)

---

## ⚡ Step 2: Server Setup (10 minutes)

### **Connect to Your Server**
```bash
# Replace YOUR_SERVER_IP with actual IP
ssh root@YOUR_SERVER_IP
```

### **Initial Setup**
```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip git nginx certbot python3-certbot-nginx curl

# Create non-root user (recommended)
adduser askace
usermod -aG sudo askace
su askace
cd ~
```

---

## 🤖 Step 3: Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull your preferred model
ollama pull llama3.2:1b  # Fast, small model
# OR
ollama pull llama3.2:3b  # Better quality

# Verify installation
ollama list
```

---

## 📁 Step 4: Deploy Your App

### **Clone Your Repository**
```bash
# If using GitHub
git clone https://github.com/yourusername/askace-drag.git
cd askace-drag

# OR upload files manually
mkdir askace-drag
cd askace-drag
# Use scp or FileZilla to upload your files
```

### **Install Python Dependencies**
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### **Test Your App**
```bash
# Quick test
streamlit run app.py --server.port=8502

# Check if working (from another terminal)
curl http://localhost:8502
```

---

## 🌐 Step 5: Production Setup

### **Install PM2 (Process Manager)**
```bash
# Install Node.js and PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g pm2

# Create start script
cat > start_askace.sh << 'EOF'
#!/bin/bash
cd /home/askace/askace-drag
source .venv/bin/activate
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
EOF

chmod +x start_askace.sh

# Start with PM2
pm2 start start_askace.sh --name askace
pm2 save
pm2 startup

# Check status
pm2 status
```

---

## 🔒 Step 6: Setup Domain & SSL (Optional)

### **Configure Nginx Reverse Proxy**
```bash
sudo nano /etc/nginx/sites-available/askace

# Add this configuration:
```

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/askace /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL (free)
sudo certbot --nginx -d your-domain.com
```

---

## 🎯 Step 7: Access Your Chatbot

### **Option A: Direct IP Access**
```
http://YOUR_SERVER_IP:8501
```

### **Option B: Domain (if configured)**
```
https://your-domain.com
```

---

## 🔧 Maintenance Commands

### **Check Status**
```bash
# App status
pm2 status

# Ollama status  
sudo systemctl status ollama

# Server resources
htop
df -h
```

### **Update App**
```bash
cd ~/askace-drag
git pull  # If using git
pm2 restart askace
```

### **View Logs**
```bash
# App logs
pm2 logs askace

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 🚀 Quick Start Commands (Copy & Paste)

**For Ubuntu 22.04 server:**

```bash
#!/bin/bash
# Complete setup script

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3 python3-pip git curl

# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl start ollama
sudo systemctl enable ollama

# Pull model
ollama pull llama3.2:1b

# Clone your app (replace with your repo)
git clone https://github.com/yourusername/askace-drag.git
cd askace-drag

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Install PM2
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs
npm install -g pm2

# Create and start service
echo '#!/bin/bash
cd /home/'$(whoami)'/askace-drag
source .venv/bin/activate  
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true' > start.sh
chmod +x start.sh

pm2 start start.sh --name askace
pm2 save
pm2 startup

echo "🎉 AskAce deployed! Access at http://$(curl -s ifconfig.me):8501"
```

---

## 💰 Monthly Costs

- **VPS:** $5-12/month  
- **Domain:** $10-15/year (optional)  
- **Total:** ~$6-13/month for unlimited usage

**vs Streamlit Cloud + OpenAI:** $20-100/month depending on usage

---

## 🛟 Troubleshooting

### **App won't start:**
```bash
pm2 logs askace
```

### **Ollama model not found:**
```bash
ollama list
ollama pull llama3.2:1b
pm2 restart askace
```

### **Can't access from browser:**
```bash
# Check if port is open
sudo ufw allow 8501
```

### **Out of memory:**
```bash
# Check resources
free -h
# Consider upgrading to 4GB VPS
```

---

## 🎯 Next Steps

1. **Choose VPS provider** (DigitalOcean recommended)
2. **Create server** with Ubuntu 22.04
3. **Run the setup script** above
4. **Upload your documents** to the `data/` folder
5. **Build index** and start chatting!

**Ready to deploy? The setup takes about 15-20 minutes total!**