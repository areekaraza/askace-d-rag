# Upload Your AskAce App to VPS

## 📁 Method 1: Using SCP (Secure Copy)

### From your local machine (Windows):

```powershell
# Navigate to your app directory
cd C:\Users\hello\rag-chatbot

# Copy all files to VPS (replace YOUR_SERVER_IP with actual IP)
scp -r app.py rag/ requirements.txt data/ root@YOUR_SERVER_IP:/home/askace/askace/

# Alternative: Copy as tar file
tar -czf askace.tar.gz app.py rag/ requirements.txt data/
scp askace.tar.gz root@YOUR_SERVER_IP:/home/askace/
```

### On your VPS server:
```bash
cd /home/askace/askace
# If you uploaded tar file:
tar -xzf ../askace.tar.gz
rm ../askace.tar.gz
```

---

## 📁 Method 2: Using FileZilla (GUI)

1. **Download FileZilla:** [filezilla-project.org](https://filezilla-project.org)
2. **Connect to server:**
   - Host: `sftp://YOUR_SERVER_IP`
   - Username: `root` (or your username)
   - Password: Your server password
   - Port: `22`
3. **Upload files:**
   - Local: `C:\Users\hello\rag-chatbot\*`
   - Remote: `/home/askace/askace/`

---

## 📁 Method 3: Git Repository

### If your code is on GitHub:

```bash
# On VPS server
cd /home/askace
git clone https://github.com/yourusername/askace-drag.git askace
cd askace
```

---

## 🚀 Start Your App

### Once files are uploaded:

```bash
# Connect to VPS
ssh root@YOUR_SERVER_IP

# Go to app directory
cd /home/askace/askace

# Activate virtual environment
source .venv/bin/activate

# Test the app
streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# If working, start with PM2
pm2 start start_askace.sh --name askace
pm2 save
pm2 startup
```

### Check if running:
```bash
pm2 status
pm2 logs askace
```

### Access your chatbot:
```
http://YOUR_SERVER_IP:8501
```

---

## 🎯 Complete File Structure

Your VPS should have:
```
/home/askace/askace/
├── app.py
├── rag/
│   ├── __init__.py
│   ├── llm_client.py
│   ├── rag_core.py
│   └── ingest.py
├── data/                 # Your documents
├── storage/             # Generated index files
├── requirements.txt
├── start_askace.sh
└── .venv/
```

---

## 🛟 Quick Troubleshooting

### **Files not found:**
```bash
ls -la /home/askace/askace/
# Make sure all files are there
```

### **Permission issues:**
```bash
sudo chown -R askace:askace /home/askace/askace/
chmod +x start_askace.sh
```

### **App won't start:**
```bash
cd /home/askace/askace
source .venv/bin/activate
python -c "import streamlit; print('Streamlit OK')"
python -c "import faiss; print('FAISS OK')"
```

### **Can't access from browser:**
```bash
# Check if app is running on port
sudo netstat -tlnp | grep 8501

# Check firewall
sudo ufw status
```