#!/usr/bin/env python3
"""
启动脚本 - 论文与代码对齐工具
"""
import os
import sys
import subprocess
from pathlib import Path
# import nltk

# nltk_data_path = r"C:\Users\SF\AppData\Roaming\nltk_data"
# os.environ['NLTK_DATA'] = nltk_data_path
# if nltk_data_path not in nltk.data.path:
#     nltk.data.path.append(nltk_data_path)
import nltk
import os
nltk.data.path.append(os.path.join(os.environ['CONDA_PREFIX'], 'nltk_data'))
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
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_models():
    """检查NLP模型是否下载"""
    try:
        import spacy
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy English model is available")
    except OSError:
        print("❌ spaCy English model not found")
        print("Please run: python -m spacy download en_core_web_sm")
        return False
    
    try:
        import nltk
        nltk.data.find('tokenizers/punkt')
        nltk.data.find('corpora/stopwords')
        nltk.data.find('corpora/wordnet')
        print("✅ NLTK data is available")
    except LookupError:
        print("❌ NLTK data not found")
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
        print(f"✅ Created directory: {directory}")

def main():
    """主函数"""
    print("Paper-Code Alignment Tool")
    print("=" * 50)
    
    # 检查依赖
    print("\nChecking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    # 检查模型
    print("\nChecking NLP models...")
    if not check_models():
        sys.exit(1)
    
    # 创建目录
    print("\nCreating directories...")
    create_directories()
    
    # 启动应用
    print("\nStarting application...")
    print("=" * 50)
    
    # try:
    #     # 使用streamlit运行主应用
    #     result = subprocess.Popen([
    #         sys.executable, "-m", "streamlit", "run", "main.py",
    #         "--server.port", "8501",
    #         "--server.address", "localhost",
    #         "--browser.gatherUsageStats", "false"
    #     ])
    #     process.communicate()
    # except KeyboardInterrupt:
    #     print("\n👋 Application stopped by user")
    #     process.terminate()
    result = subprocess.run([
        sys.executable, "-m", "streamlit", "run", "main.py",
        "--server.port", "8501",
        "--server.address", "localhost",
        "--server.runOnSave", "false",
        "--browser.gatherUsageStats", "false"
    ], capture_output=True, text=True)

    print(result.stdout)
    print(result.stderr)

if __name__ == "__main__":
    main()


