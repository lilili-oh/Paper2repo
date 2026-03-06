"""
对齐结果数据模型
"""
from typing import List, Optional, Dict, Any, Tuple
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class AlignmentType(str, Enum):
    """对齐类型"""
    SEMANTIC = "semantic"  # 语义对齐
    LEXICAL = "lexical"    # 词汇对齐
    STRUCTURAL = "structural"  # 结构对齐
    HYBRID = "hybrid"      # 混合对齐

class SimilarityScore(BaseModel):
    """相似度分数"""
    score: float = Field(..., ge=0.0, le=1.0, description="相似度分数 (0-1)")
    method: str = Field(..., description="计算方法")
    confidence: float = Field(..., ge=0.0, le=1.0, description="置信度")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="计算元数据")

class AlignmentMatch(BaseModel):
    """对齐匹配项"""
    text_feature: str = Field(..., description="文本特征ID")
    code_feature: str = Field(..., description="代码特征ID")
    similarity_score: SimilarityScore = Field(..., description="相似度分数")
    alignment_type: AlignmentType = Field(..., description="对齐类型")
    explanation: Optional[str] = Field(None, description="对齐解释")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="匹配元数据")

class AlignmentResult(BaseModel):
    """对齐结果"""
    id: str = Field(..., description="对齐结果唯一标识")
    text_document_id: str = Field(..., description="文本文档ID")
    code_repository_id: str = Field(..., description="代码仓库ID")
    
    # 对齐结果
    matches: List[AlignmentMatch] = Field(default_factory=list, description="匹配列表")
    total_matches: int = Field(default=0, description="总匹配数")
    average_similarity: float = Field(default=0.0, description="平均相似度")
    best_matches: List[AlignmentMatch] = Field(default_factory=list, description="最佳匹配")
    
    # 统计信息
    alignment_coverage: float = Field(default=0.0, description="对齐覆盖率")
    text_coverage: float = Field(default=0.0, description="文本覆盖率")
    code_coverage: float = Field(default=0.0, description="代码覆盖率")
    
    # 元数据
    created_at: datetime = Field(default_factory=datetime.now)
    processing_time: float = Field(default=0.0, description="处理时间（秒）")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="结果元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
