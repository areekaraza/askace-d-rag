# 🌐 Streamlit Cloud Deployment

**Deploy your AskAce chatbot to Streamlit Cloud for FREE hosting!**

## ⚠️ Important: Cloud vs Local Versions

### Your app has 2 versions:
- **`app.py`** - Local version (uses Ollama)
- **`app_cloud.py`** - Cloud version (uses OpenAI API)

**For Streamlit Cloud, we need to use the cloud version because:**
- ❌ Streamlit Cloud can't run Ollama (local LLM)
- ✅ Streamlit Cloud can use OpenAI API

---

## 🚀 Quick Cloud Deployment

### 1. Prepare Cloud Version
```bash
# Copy cloud version to main app
cp app_cloud.py app.py
git add app.py
git commit -m "☁️ Switch to cloud version for Streamlit hosting"
git push
```

### 2. Deploy to Streamlit Cloud
1. **Go to**: [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with GitHub
3. **Click**: "New app"
4. **Repository**: `yourusername/askace-drag`
5. **Branch**: `main`
6. **Main file**: `app.py`
7. **Click**: "Deploy!"

### 3. Add OpenAI API Key
1. **In Streamlit Cloud**, go to app settings
2. **Secrets tab**, add:
```toml
OPENAI_API_KEY = "your-openai-api-key-here"
```
3. **Get API key** from [platform.openai.com](https://platform.openai.com)

### 4. Your App is Live! 🎉
```
https://yourusername-askace-drag-app-xxxxx.streamlit.app
```

---

## 💰 Costs

- **Hosting**: FREE (Streamlit Cloud)
- **OpenAI API**: ~$0.01-0.05 per query
- **Total**: ~$1-5/month depending on usage

---

## 🔄 Alternative: Keep Both Versions

### Option 1: Separate Branches
```bash
# Create cloud branch
git checkout -b cloud-deployment
cp app_cloud.py app.py
git add app.py
git commit -m "☁️ Cloud deployment version"
git push -u origin cloud-deployment

# Deploy from 'cloud-deployment' branch on Streamlit Cloud
```

### Option 2: Environment Detection
Edit `app.py` to auto-detect environment:

```python
import os

# Detect if running on Streamlit Cloud
if "streamlit" in os.environ.get("HOSTNAME", "").lower():
    # Use OpenAI (cloud version)
    from llm_client_cloud import chat_answer, embed_texts
else:
    # Use Ollama (local version)  
    from rag.llm_client import chat_answer, embed_texts
```

---

## 🎯 Recommended Approach

### **For Portfolio/Demo**: Use Streamlit Cloud
1. Switch `app.py` to cloud version
2. Deploy to Streamlit Cloud
3. Add live demo link to README

### **For Privacy/Development**: Keep local version
1. Use `app.py` with Ollama locally
2. Deploy to VPS with student credits

---

## 📝 Update Your README

After deployment, update your README:

```markdown
## 🌐 Live Demo
**[Try AskAce Live →](https://yourusername-askace-drag-app.streamlit.app)**

*Note: Live demo uses OpenAI API for cloud compatibility. Download for local Ollama version.*
```

---

## 🛠️ Troubleshooting

### App won't start?
- ✅ Check you copied `app_cloud.py` to `app.py`
- ✅ Verify OpenAI API key is set in secrets
- ✅ Check requirements.txt includes `openai`

### Costs too high?
- ✅ Use cheaper model: `gpt-3.5-turbo` instead of `gpt-4o-mini`
- ✅ Reduce context length in the app
- ✅ Consider VPS deployment for unlimited usage

**Ready to deploy? Follow the steps above and your chatbot will be live in 10 minutes!**