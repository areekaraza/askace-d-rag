# 🎓 Deploy AskAce with GitHub Student Developer Pack

**Perfect choice! GitHub Student Pack gives you $200 DigitalOcean credits - that's 16+ months of free hosting!**

## 🎯 Why GitHub Student Pack + DigitalOcean is Perfect

✅ **$200 FREE credits** (16+ months of hosting)  
✅ **Premium DigitalOcean features** included  
✅ **Easy deployment** with excellent documentation  
✅ **Professional setup** for your portfolio  
✅ **Learn real DevOps skills**  

---

## 🚀 Step 1: Activate GitHub Student Pack

### **Get Your Benefits:**
1. **Apply for GitHub Student Pack:**
   - Go to [education.github.com/pack](https://education.github.com/pack)
   - Sign in with your GitHub account
   - Verify student status (upload student ID/email)
   - Approval usually takes 1-7 days

2. **Claim DigitalOcean Credits:**
   - Once approved, find DigitalOcean in your pack
   - Click "Get access to DigitalOcean"
   - Creates account with $200 credit automatically

---

## 🌊 Step 2: Setup DigitalOcean Droplet

### **Create Your Server:**
1. **Go to DigitalOcean Dashboard**
2. **Create Droplet:**
   - **Image:** Ubuntu 22.04 LTS
   - **Plan:** Basic ($12/month, 2GB RAM, 50GB SSD)
   - **Region:** Choose closest to you
   - **Authentication:** 
     - SSH Key (recommended) or Password
     - If SSH Key: Upload your public key or create one
   - **Hostname:** `askace-chatbot`

3. **Note your server IP** (will be assigned after creation)

### **SSH Key Setup (Recommended):**
```bash
# On Windows (Git Bash or WSL)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
cat ~/.ssh/id_rsa.pub  # Copy this key to DigitalOcean
```

---

## 🛠️ Step 3: Prepare Your Code for Deployment

### **1. Push to GitHub (if not already done):**
```bash
# In your rag-chatbot directory
git init
git add .
git commit -m "Initial commit - AskAce chatbot"

# Create repo on GitHub first, then:
git remote add origin https://github.com/yourusername/askace-chatbot.git
git push -u origin main
```

### **2. Create Deployment Branch (Optional):**
```bash
git checkout -b deploy
# Make any deployment-specific changes
git push -u origin deploy
```

---

## 🚀 Step 4: Deploy to Your DigitalOcean Droplet

### **Connect to Your Server:**
```bash
# Replace YOUR_SERVER_IP with actual IP from DigitalOcean
ssh root@YOUR_SERVER_IP
```

### **Quick Setup (One Command):**
```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/yourusername/askace-chatbot/main/setup_vps.sh | bash
```

### **Manual Setup (Step by Step):**
```bash
# 1. Update system
apt update && apt upgrade -y

# 2. Install dependencies
apt install -y python3 python3-pip python3-venv git curl htop

# 3. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
systemctl start ollama
systemctl enable ollama

# 4. Pull AI model (this takes a few minutes)
ollama pull llama3.2:1b

# 5. Clone your repository
cd /root
git clone https://github.com/yourusername/askace-chatbot.git
cd askace-chatbot

# 6. Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 7. Install PM2 for process management
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
npm install -g pm2

# 8. Create startup script
cat > start_askace.sh << 'EOF'
#!/bin/bash
cd /root/askace-chatbot
source .venv/bin/activate
streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true
EOF

chmod +x start_askace.sh

# 9. Start the application
pm2 start start_askace.sh --name askace
pm2 save
pm2 startup

# 10. Configure firewall
ufw allow ssh
ufw allow 8501
ufw --force enable
```

---

## 🌐 Step 5: Access Your Live Chatbot

### **Your chatbot is now live at:**
```
http://YOUR_SERVER_IP:8501
```

### **Test it:**
1. Upload some documents
2. Click "Build Index"
3. Start asking questions!

---

## 🔒 Step 6: Secure with Domain & SSL (Optional)

### **1. Get a Free Domain (Student Benefits):**
- **Namecheap:** 1 year free .me domain (in Student Pack)
- **Name.com:** 1 year free domain (in Student Pack)

### **2. Point Domain to Your Server:**
```bash
# In your domain DNS settings, add:
A record: @ -> YOUR_SERVER_IP
A record: www -> YOUR_SERVER_IP
```

### **3. Setup SSL Certificate:**
```bash
# On your server
apt install -y nginx certbot python3-certbot-nginx

# Configure nginx (use the config from nginx_config file)
nano /etc/nginx/sites-available/askace

# Enable site
ln -s /etc/nginx/sites-available/askace /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Get SSL certificate (replace your-domain.com)
certbot --nginx -d your-domain.com -d www.your-domain.com
```

### **Now access via:** `https://your-domain.com`

---

## 💰 Cost Breakdown

### **With GitHub Student Pack:**
- **DigitalOcean:** $0 for 16+ months (using $200 credit)
- **Domain:** $0 for 1 year (student benefit)
- **SSL:** $0 (Let's Encrypt free)
- **Total First Year:** **$0** 🎉

### **After Credits Expire:**
- **DigitalOcean:** $12/month
- **Domain:** ~$15/year
- **Total:** ~$150/year

---

## 🛠️ Management Commands

### **Check Status:**
```bash
ssh root@YOUR_SERVER_IP
pm2 status          # App status
pm2 logs askace     # View logs
htop                # Server resources
df -h               # Disk space
```

### **Update Your App:**
```bash
cd /root/askace-chatbot
git pull origin main
pm2 restart askace
```

### **Monitor Usage:**
```bash
# DigitalOcean dashboard shows:
# - Bandwidth usage
# - CPU/RAM usage
# - Droplet costs
```

---

## 🎯 Pro Tips for Students

### **1. Document Everything:**
- Take screenshots for your portfolio
- Write blog post about the deployment
- Add to your resume as a full-stack project

### **2. Learn While Building:**
- Understand Linux commands
- Learn about reverse proxies (nginx)
- Practice with SSL certificates
- Monitor server performance

### **3. Expand Your Project:**
- Add user authentication
- Implement chat history
- Add admin dashboard
- Set up monitoring with Grafana

### **4. Save Money:**
- Use monitoring to optimize server size
- Consider smaller droplet if usage is light
- Set up billing alerts

---

## 🚀 Next Steps

1. **Apply for GitHub Student Pack** (if not done already)
2. **Create DigitalOcean account** with student credits
3. **Deploy your chatbot** following this guide
4. **Get a free domain** and set up SSL
5. **Share your live chatbot** with friends and portfolio

**Timeline:** 
- GitHub approval: 1-7 days
- Deployment: 30 minutes
- Domain + SSL: 15 minutes

**Your chatbot will be professionally hosted with zero cost for over a year!**

Need help with any specific step? I can provide more detailed guidance!