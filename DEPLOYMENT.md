# 🚀 Deploy AskAce: D'RAG to the Web

## Quick Deployment Options

### 🌟 Option 1: Streamlit Community Cloud (Easiest & Free)

**Step 1: Prepare for GitHub**
```bash
# Initialize git repository
git init
git add .
git commit -m "Initial AskAce deployment"

# Push to GitHub (create repo first at github.com)
git remote add origin https://github.com/yourusername/askace-drag.git
git push -u origin main
```

**Step 2: Deploy to Streamlit Cloud**
1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with GitHub
3. Click "New app" 
4. Select your repository
5. Main file: `app_cloud.py` (I'll create this for you)
6. Add secrets: `OPENAI_API_KEY = your_openai_key`
7. Click "Deploy!"

**Step 3: Get OpenAI API Key**
1. Go to [platform.openai.com](https://platform.openai.com)
2. Create account → API Keys → Create new key
3. Copy the key (starts with `sk-`)

---

### 🐳 Option 2: Docker Deployment (Full Control)

**Works on:** Railway, Render, DigitalOcean, Google Cloud

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

---

### 💻 Option 3: VPS Deployment (Advanced)

**For:** DigitalOcean ($5/month), Vultr, Linode

```bash
# Server setup
sudo apt update && sudo apt install python3-pip git nginx
git clone https://github.com/yourusername/askace-drag.git
cd askace-drag
pip install -r requirements.txt

# Install Ollama (if keeping local LLM)
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.2:1b

# Run with PM2
npm install -g pm2
pm2 start "streamlit run app.py --server.port=8501" --name askace
```

---

## 🔧 Which Version Should You Deploy?

### **Cloud Version (app_cloud.py)**
✅ **Pros:** Fast, reliable, scales automatically  
❌ **Cons:** ~$0.01-0.05 per query (OpenAI costs)

### **Local LLM Version (app.py)** 
✅ **Pros:** Free queries, private  
❌ **Cons:** Requires VPS ($5/month), more setup

---

## 🚀 Recommended: Streamlit Cloud + OpenAI

**Why this is best for most users:**
- ✅ **Free hosting** (Streamlit Community Cloud)
- ✅ **Zero server management** 
- ✅ **Fast responses** (OpenAI GPT-4o-mini)
- ✅ **Auto-scaling** (handles traffic spikes)
- ✅ **HTTPS included** (secure by default)

**Cost:** ~$1-5/month depending on usage

**Ready to deploy? I can create the cloud version for you!**