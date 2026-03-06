"""
配置文件 - 定义项目的核心配置参数
"""
import os
from typing import Dict, List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """应用配置类"""
    
    # GitHub API配置
    github_token: Optional[str] = None
    github_api_base_url: str = "https://api.github.com"
    
    # 模型配置
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    similarity_threshold: float = 0.3
    max_text_length: int = 512
    max_code_length: int = 1024
    
    # 数据库配置
    chroma_persist_directory: str = "./data/chroma_db"
    
    # 文本处理配置
    supported_languages: List[str] = ["python", "javascript", "java", "cpp", "go"]
    text_preprocessing: Dict[str, bool] = {
        "remove_punctuation": True,
        "lowercase": True,
        "remove_stopwords": True,
        "lemmatize": True
    }
    
    # 代码分析配置
    code_features: List[str] = [
        "function_names",
        "variable_names", 
        "comments",
        "imports",
        "class_names",
        "method_names"
    ]
    
    # 对齐算法配置
    alignment_method: str = "semantic"  # semantic, lexical, hybrid
    similarity_metrics: List[str] = ["cosine", "euclidean", "manhattan"]
    
    # 可视化配置
    max_display_items: int = 50
    similarity_color_map: str = "viridis"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# 全局配置实例
settings = Settings()
