# 🌐 AskAce: D'RAG - Web Version

**Static web version of AskAce for easy GitHub Pages hosting!**

## 🎯 What's Different?

This is a **pure HTML/CSS/JavaScript** version that can be hosted directly on GitHub Pages without any server requirements.

### **Web Version Features:**
✅ **Pure HTML/CSS/JS** - No Python required  
✅ **GitHub Pages compatible** - Static hosting  
✅ **OpenAI API integration** - Cloud-based processing  
✅ **Drag & drop file upload** - Easy document management  
✅ **Responsive design** - Works on mobile  
✅ **Real-time chat interface** - Beautiful UI  

## 🚀 Quick Deploy to GitHub Pages

### **Step 1: Enable GitHub Pages**
1. Go to your repository: `https://github.com/areekaraza/askace-d-rag`
2. Click **Settings** → **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main**
5. Folder: **/ (root)**
6. Click **Save**

### **Step 2: Your site will be live at:**
```
https://areekaraza.github.io/askace-d-rag
```

## 📁 File Structure

```
your-repo/
├── index.html          # Main web app (created)
├── README.md           # This file
├── app.py             # Original Python version
├── app_cloud.py       # Streamlit cloud version
└── web-version/       # Web assets (if needed)
```

## 🔧 How It Works

### **Frontend (Static):**
- **HTML/CSS/JS** - Runs entirely in browser
- **File Upload** - Drag & drop interface
- **OpenAI API** - Direct browser-to-API calls
- **No Server** - Pure client-side processing

### **Backend (API):**
- **OpenAI API** - For embeddings and chat
- **Browser Storage** - For uploaded files
- **Local Processing** - JavaScript-based text chunking

## 💰 Cost Comparison

| Version | Hosting | Processing | Total Cost |
|---------|---------|------------|------------|
| **Web Version** | FREE (GitHub Pages) | ~$0.01-0.05/query | $1-5/month |
| **Python Local** | FREE (local) | FREE (Ollama) | $0/month |
| **Streamlit Cloud** | FREE | ~$0.01-0.05/query | $1-5/month |

## 🔑 Setup Instructions

### **1. Get OpenAI API Key**
1. Visit [platform.openai.com](https://platform.openai.com)
2. Create account → API Keys → Create new key
3. Copy the key (starts with `sk-`)

### **2. First Visit**
1. Go to your live site
2. Enter OpenAI API key when prompted
3. Key is stored securely in your browser

### **3. Upload Documents**
1. Drag & drop files or click to browse
2. Supports: PDF, DOCX, TXT, MD
3. Click "Build Index"
4. Start chatting!

## 🌟 Advantages of Web Version

### **✅ Pros:**
- **Zero setup** - Just visit the URL
- **Cross-platform** - Works anywhere
- **No installation** - Pure web app
- **Easy sharing** - Send URL to anyone
- **Mobile friendly** - Responsive design
- **GitHub Pages** - Free hosting forever

### **❌ Limitations:**
- **Requires API key** - Not completely free
- **Internet required** - Can't work offline
- **Limited file processing** - Basic text extraction
- **No local LLM** - Depends on OpenAI

## 🚀 Deployment Steps

### **Option A: Replace main app (Simple)**
```bash
# Replace app.py with web version
mv index.html app.html
git add app.html
git commit -m "🌐 Add web version for GitHub Pages"
git push
```

### **Option B: Keep both versions (Recommended)**
```bash
# Keep both Python and Web versions
git add index.html
git commit -m "🌐 Add static web version for GitHub Pages hosting"
git push
```

### **Option C: Web-only repository**
Create a new repository specifically for the web version:
1. Create new repo: `askace-web`
2. Upload only `index.html`
3. Enable GitHub Pages

## 📱 Features

### **Modern UI:**
- **Gradient design** - Beautiful visual appeal
- **Responsive layout** - Mobile & desktop
- **Real-time chat** - Smooth animations
- **Drag & drop** - Intuitive file upload
- **Status indicators** - Clear system feedback

### **Smart Features:**
- **Auto-save settings** - Remembers preferences
- **Error handling** - User-friendly messages
- **Progress indicators** - Visual feedback
- **File validation** - Supported formats only

## 🎯 Next Steps

1. **Deploy** using the steps above
2. **Test** with sample documents
3. **Share** your live demo URL
4. **Add to portfolio** as a web development project

## 💡 Customization

The web version is easily customizable:
- **Colors**: Modify CSS variables
- **Layout**: Adjust grid structure
- **Features**: Add new functionality
- **Branding**: Change titles and icons

**Your AskAce chatbot is now ready for the modern web! 🌐✨**