"""
代码数据模型
"""
from typing import List, Optional, Dict, Any, Set
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class CodeLanguage(str, Enum):
    """支持的编程语言"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    GO = "go"
    RUST = "rust"
    TYPESCRIPT = "typescript"

class CodeFeature(BaseModel):
    """代码特征"""
    feature_type: str = Field(..., description="特征类型：function, class, variable, comment, import")
    name: str = Field(..., description="特征名称")
    content: str = Field(..., description="特征内容")
    line_start: int = Field(..., description="起始行号")
    line_end: int = Field(..., description="结束行号")
    embedding: Optional[List[float]] = Field(None, description="特征向量")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")

class CodeFile(BaseModel):
    """代码文件模型"""
    id: str = Field(..., description="文件唯一标识")
    filename: str = Field(..., description="文件名")
    filepath: str = Field(..., description="文件路径")
    language: CodeLanguage = Field(..., description="编程语言")
    content: str = Field(..., description="文件内容")
    size: int = Field(..., description="文件大小（字节）")
    
    # 解析后的特征
    features: List[CodeFeature] = Field(default_factory=list, description="提取的特征")
    functions: List[CodeFeature] = Field(default_factory=list, description="函数列表")
    classes: List[CodeFeature] = Field(default_factory=list, description="类列表")
    imports: List[CodeFeature] = Field(default_factory=list, description="导入列表")
    comments: List[CodeFeature] = Field(default_factory=list, description="注释列表")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="文件元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class CodeRepository(BaseModel):
    """代码仓库模型"""
    id: str = Field(..., description="仓库唯一标识")
    name: str = Field(..., description="仓库名称")
    owner: str = Field(..., description="仓库所有者")
    url: str = Field(..., description="仓库URL")
    description: Optional[str] = Field(None, description="仓库描述")
    
    # 仓库内容
    files: List[CodeFile] = Field(default_factory=list, description="文件列表")
    languages: Set[CodeLanguage] = Field(default_factory=set, description="使用的编程语言")
    total_files: int = Field(default=0, description="总文件数")
    total_lines: int = Field(default=0, description="总行数")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict, description="仓库元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
