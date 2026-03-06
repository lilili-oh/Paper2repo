"""
文本数据模型
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class TextFeature(BaseModel):
    """文本特征"""
    feature_type: str = Field(..., description="特征类型：sentence, paragraph, formula, keyword")
    content: str = Field(..., description="特征内容")
    position: int = Field(..., description="在文档中的位置")
    embedding: Optional[List[float]] = Field(None, description="特征向量")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class TextDocument(BaseModel):
    """文本文档模型"""
    id: str = Field(..., description="文档唯一标识")
    title: str = Field(..., description="文档标题")
    content: str = Field(..., description="文档内容")
    source: str = Field(..., description="文档来源：paper, description, manual")
    language: str = Field(default="en", description="文档语言")
    
    # 处理后的特征
    features: List[TextFeature] = Field(default_factory=list, description="提取的特征")
    sentences: List[str] = Field(default_factory=list, description="句子列表")
    paragraphs: List[str] = Field(default_factory=list, description="段落列表")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文档元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
