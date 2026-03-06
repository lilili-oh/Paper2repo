#!/usr/bin/env python3
"""
简单启动脚本 - 论文与代码对齐工具
"""
import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import streamlit
        import transformers
        import torch
        import sentence_transformers
        import spacy
        import nltk
        import plotly
        import pandas
        import numpy
        import sklearn
        import chromadb
        print("[OK] All dependencies are installed")
        return True
    except ImportError as e:
        print(f"[ERROR] Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_models():
    """检查NLP模型是否下载"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("[OK] spaCy English model is available")
    except OSError:
        print("[ERROR] spaCy English model not found")
        print("Please run: python -m spacy download en_core_web_sm")
        return False
    
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/wordnet')
        print("[OK] NLTK data is available")
    except LookupError:
        print("[ERROR] NLTK data not found")
        print("Please run: python -c \"import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')\"")
        return False
    
    return True

def create_directories():
    """创建必要的目录"""
    directories = [
        "data",
        "data/chroma_db",
        "data/text_documents",
        "data/code_repositories", 
        "data/alignment_results"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"[OK] Created directory: {directory}")

def main():
    # """主函数"""
    print("Paper-Code Alignment Tool")
    print("=" * 50)
    
    # # 检查依赖
    # print("\nChecking dependencies...")
    # if not check_dependencies():
    #     sys.exit(1)
    
    # # 检查模型
    # print("\nChecking NLP models...")
    # if not check_models():
    #     sys.exit(1)
    
    # # 创建目录
    # print("\nCreating directories...")
    # create_directories()
    
    # 启动应用
    print("\nStarting application...")
    print("=" * 50)
    
    try:
        # 使用streamlit运行主应用
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"\nError starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
