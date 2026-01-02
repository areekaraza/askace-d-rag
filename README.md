# AskAce: D'RAG 🎯

**Ultra-fast RAG chatbot for document Q&A**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)


## ✨ Features

🔒 **Complete Privacy** - All processing happens locally  
⚡ **Lightning Fast** - 2-second startup, 1-3 second responses  
📚 **Multi-Format** - PDF, DOCX, TXT, MD support  
🎯 **Smart Retrieval** - FAISS vector search with citations  
🚀 **Easy Deployment** - One-click cloud deployment  
💰 **Zero API Costs** - Uses local Ollama LLMs  
🌐 **Web Version** - Static HTML/CSS/JS for GitHub Pages

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Ollama
```bash
# Install from https://ollama.com
ollama pull llama3.2:1b  # Fast model
# OR
ollama pull llama3.2:3b  # Better quality
```

### 4. Add Your Documents
- Drop files into `data/` folder
- Click "🚀 Build Index" 
- Start asking questions!

## ⚡ Performance Optimizations

- **Smart Caching** - Index and models cached in memory
- **Lazy Loading** - Components load only when needed  
- **Batch Processing** - Embeddings generated in efficient batches
- **Optimized Chunking** - 500-char chunks with minimal overlap
- **Fast Models** - Prioritized smaller, faster LLMs

## 🏗️ Architecture

```
Documents → Chunking → Embeddings → FAISS Index
     ↓
User Query → Embedding → Similarity Search → Context → LLM → Answer
```

## 📊 Benchmarks

| Metric | Performance |
|--------|------------|
| **Cold Start** | ~2 seconds |
| **Query Response** | 1-3 seconds |
| **Index Building** | ~100 chunks/second |
| **Memory Usage** | 200-500 MB |
| **Supported Docs** | Unlimited |

## 🛠️ Tech Stack

- **🎨 Frontend**: Streamlit + HTML/CSS/JS
- **🔤 Embeddings**: SentenceTransformers (local)
- **🗂️ Vector DB**: FAISS
- **🤖 LLM**: Ollama (local) / OpenAI (cloud)
- **📄 Documents**: PyPDF, python-docx

## 🔧 Configuration

### Models
- **Fast**: `llama3.2:1b` (~1.5GB)
- **Balanced**: `phi3:mini` (~2.2GB)  
- **Quality**: `llama3.2:3b` (~2.0GB)

### Embeddings  
- **Default**: `all-MiniLM-L6-v2` (22MB, 384 dims)
- **Alternative**: `paraphrase-MiniLM-L6-v2` (22MB, 384 dims)

## 📁 Project Structure

```
askace-drag/
├── index.html             # 🌐 Static web version
├── app.py                 # 🐍 Main Streamlit app
├── app_cloud.py           # ☁️ Cloud version
├── start.py               # 🚀 Optimized launcher
├── rag/
│   ├── llm_client.py     # 🤖 Optimized LLM & embeddings
│   ├── rag_core.py       # 🧠 RAG pipeline with caching  
│   └── ingest.py         # 📄 Fast document processing
├── data/                  # 📂 Your documents
├── storage/              # 💾 Generated indices
├── requirements.txt      # 📦 Dependencies
├── WEB_VERSION.md        # 🌐 Web deployment guide
└── deployment guides/    # 📚 Hosting instructions
```

## 🚀 Getting Started

### Local Development
```bash
git clone https://github.com/areekaraza/askace-d-rag.git
cd askace-d-rag
pip install -r requirements.txt
ollama pull llama3.2:1b
python start.py
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.com) - Local LLM serving
- [FAISS](https://github.com/facebookresearch/faiss) - Efficient similarity search
- [SentenceTransformers](https://www.sbert.net) - Semantic embeddings
- [Streamlit](https://streamlit.io) - Rapid web app development

## 💡 Support

- **Documentation**: Check the deployment guides in this repo
- **Issues**: [GitHub Issues](https://github.com/areekaraza/askace-d-rag/issues)
- **Discussions**: [GitHub Discussions](https://github.com/areekaraza/askace-d-rag/discussions)

---

**🌟 Star this repo if it helped you build an awesome RAG chatbot!**
