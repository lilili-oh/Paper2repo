"""
对齐处理器 - 负责文本与代码的对齐算法和相似度计算
"""
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity, euclidean_distances
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import pdist, squareform
import time

from ..models.text_model import TextDocument, TextFeature
from ..models.code_model import CodeRepository, CodeFile, CodeFeature
from ..models.alignment_model import AlignmentResult, AlignmentMatch, SimilarityScore, AlignmentType
from config import settings

class AlignmentProcessor:
    """对齐处理器类"""
    
    def __init__(self):
        """初始化对齐处理器"""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
    
    def calculate_semantic_similarity(self, text_feature: TextFeature, code_feature: CodeFeature) -> float:
        """计算语义相似度"""
        if not text_feature.embedding or not code_feature.embedding:
            return 0.0
        
        # 使用余弦相似度
        text_emb = np.array(text_feature.embedding).reshape(1, -1)
        code_emb = np.array(code_feature.embedding).reshape(1, -1)
        
        similarity = cosine_similarity(text_emb, code_emb)[0][0]
        return float(similarity)
    
    def calculate_lexical_similarity(self, text_feature: TextFeature, code_feature: CodeFeature) -> float:
        """计算词汇相似度"""
        text_content = text_feature.content.lower()
        code_content = code_feature.content.lower()
        
        # 提取词汇
        text_words = set(text_content.split())
        code_words = set(code_content.split())
        
        if not text_words or not code_words:
            return 0.0
        
        # 计算Jaccard相似度
        intersection = len(text_words.intersection(code_words))
        union = len(text_words.union(code_words))
        
        jaccard_sim = intersection / union if union > 0 else 0.0
        
        # 计算词汇重叠度
        overlap_ratio = intersection / min(len(text_words), len(code_words))
        
        # 组合相似度
        lexical_sim = (jaccard_sim + overlap_ratio) / 2
        
        return float(lexical_sim)
    
    def calculate_structural_similarity(self, text_feature: TextFeature, code_feature: CodeFeature) -> float:
        """计算结构相似度"""
        text_content = text_feature.content
        code_content = code_feature.content
        
        # 长度相似度
        len_sim = 1 - abs(len(text_content) - len(code_content)) / max(len(text_content), len(code_content))
        
        # 关键词匹配
        text_keywords = self._extract_keywords(text_content)
        code_keywords = self._extract_keywords(code_content)
        
        keyword_sim = 0.0
        if text_keywords and code_keywords:
            intersection = len(set(text_keywords).intersection(set(code_keywords)))
            union = len(set(text_keywords).union(set(code_keywords)))
            keyword_sim = intersection / union if union > 0 else 0.0
        
        # 结构模式匹配
        pattern_sim = self._calculate_pattern_similarity(text_content, code_content)
        
        # 组合结构相似度
        structural_sim = (len_sim + keyword_sim + pattern_sim) / 3
        
        return float(structural_sim)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        import re
        # 简单的关键词提取
        words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
        return words
    
    def _calculate_pattern_similarity(self, text: str, code: str) -> float:
        """计算模式相似度"""
        # 检查是否包含相似的模式
        patterns = [
            r'\b\w+\s*=\s*\w+',  # 赋值模式
            r'\b\w+\s*\(\s*\w*\s*\)',  # 函数调用模式
            r'\b\w+\s*:\s*\w+',  # 键值对模式
        ]
        
        text_patterns = []
        code_patterns = []
        
        for pattern in patterns:
            text_matches = len(re.findall(pattern, text))
            code_matches = len(re.findall(pattern, code))
            text_patterns.append(text_matches)
            code_patterns.append(code_matches)
        
        if not any(text_patterns) and not any(code_patterns):
            return 0.0
        
        # 计算模式相似度
        text_patterns = np.array(text_patterns)
        code_patterns = np.array(code_patterns)
        
        similarity = 1 - np.linalg.norm(text_patterns - code_patterns) / (
            np.linalg.norm(text_patterns) + np.linalg.norm(code_patterns) + 1e-8
        )
        
        return float(max(0, similarity))
    
    def calculate_hybrid_similarity(self, text_feature: TextFeature, code_feature: CodeFeature) -> Tuple[float, Dict[str, float]]:
        """计算混合相似度"""
        # 计算各种相似度
        semantic_sim = self.calculate_semantic_similarity(text_feature, code_feature)
        lexical_sim = self.calculate_lexical_similarity(text_feature, code_feature)
        structural_sim = self.calculate_structural_similarity(text_feature, code_feature)
        
        # 权重组合
        weights = {
            'semantic': 0.5,
            'lexical': 0.3,
            'structural': 0.2
        }
        
        hybrid_sim = (
            weights['semantic'] * semantic_sim +
            weights['lexical'] * lexical_sim +
            weights['structural'] * structural_sim
        )
        
        similarity_breakdown = {
            'semantic': semantic_sim,
            'lexical': lexical_sim,
            'structural': structural_sim
        }
        
        return float(hybrid_sim), similarity_breakdown
    
    def find_alignments(self, text_document: TextDocument, code_repository: CodeRepository) -> AlignmentResult:
        """查找文本与代码的对齐"""
        start_time = time.time()
        
        # 创建对齐结果
        alignment_id = f"align_{hash(text_document.id)}_{hash(code_repository.id)}"
        alignment_result = AlignmentResult(
            id=alignment_id,
            text_document_id=text_document.id,
            code_repository_id=code_repository.id
        )
        
        matches = []
        all_text_features = text_document.features
        all_code_features = []
        
        # 收集所有代码特征
        for code_file in code_repository.files:
            all_code_features.extend(code_file.features)
        
        # 计算所有特征对之间的相似度
        for text_feature in all_text_features:
            for code_feature in all_code_features:
                # 计算相似度
                if settings.alignment_method == "semantic":
                    similarity_score = self.calculate_semantic_similarity(text_feature, code_feature)
                    alignment_type = AlignmentType.SEMANTIC
                elif settings.alignment_method == "lexical":
                    similarity_score = self.calculate_lexical_similarity(text_feature, code_feature)
                    alignment_type = AlignmentType.LEXICAL
                elif settings.alignment_method == "hybrid":
                    similarity_score, breakdown = self.calculate_hybrid_similarity(text_feature, code_feature)
                    alignment_type = AlignmentType.HYBRID
                else:
                    similarity_score = self.calculate_semantic_similarity(text_feature, code_feature)
                    alignment_type = AlignmentType.SEMANTIC
                
                # 只保留超过阈值的匹配
                if similarity_score >= settings.similarity_threshold:
                    similarity_score_obj = SimilarityScore(
                        score=similarity_score,
                        method=settings.alignment_method,
                        confidence=min(similarity_score * 1.2, 1.0),
                        metadata={"threshold": settings.similarity_threshold}
                    )
                    
                    match = AlignmentMatch(
                        text_feature=text_feature.content[:100],  # 截断用于显示
                        code_feature=code_feature.content[:100],
                        similarity_score=similarity_score_obj,
                        alignment_type=alignment_type,
                        explanation=f"Text: {text_feature.feature_type} -> Code: {code_feature.feature_type}",
                        metadata={
                            "text_position": text_feature.position,
                            "code_file": code_feature.metadata.get("file", "unknown"),
                            "code_line": f"{code_feature.line_start}-{code_feature.line_end}"
                        }
                    )
                    matches.append(match)
        
        # 按相似度排序
        matches.sort(key=lambda x: x.similarity_score.score, reverse=True)
        
        # 更新对齐结果
        alignment_result.matches = matches
        alignment_result.total_matches = len(matches)
        alignment_result.best_matches = matches[:10]  # 前10个最佳匹配
        
        if matches:
            alignment_result.average_similarity = sum(m.similarity_score.score for m in matches) / len(matches)
        
        # 计算覆盖率
        alignment_result.alignment_coverage = len(matches) / max(len(all_text_features), 1)
        alignment_result.text_coverage = len(set(m.text_feature for m in matches)) / max(len(all_text_features), 1)
        alignment_result.code_coverage = len(set(m.code_feature for m in matches)) / max(len(all_code_features), 1)
        
        # 计算处理时间
        alignment_result.processing_time = time.time() - start_time
        
        return alignment_result
    
    def find_similar_code_snippets(self, text: str, code_repository: CodeRepository, top_k: int = 5) -> List[Tuple[CodeFeature, float]]:
        """查找与给定文本最相似的代码片段"""
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer(settings.embedding_model)
        text_embedding = model.encode([text])
        
        similarities = []
        
        for code_file in code_repository.files:
            for feature in code_file.features:
                if feature.embedding:
                    code_embedding = np.array(feature.embedding).reshape(1, -1)
                    similarity = cosine_similarity(text_embedding, code_embedding)[0][0]
                    similarities.append((feature, float(similarity)))
        
        # 按相似度排序并返回前k个
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]
    
    def analyze_alignment_quality(self, alignment_result: AlignmentResult) -> Dict[str, Any]:
        """分析对齐质量"""
        if not alignment_result.matches:
            return {"quality": "poor", "score": 0.0, "issues": ["No matches found"]}
        
        issues = []
        quality_score = 0.0
        
        # 检查匹配数量
        if alignment_result.total_matches < 5:
            issues.append("Very few matches found")
            quality_score -= 0.2
        elif alignment_result.total_matches > 100:
            issues.append("Too many matches, may indicate low precision")
            quality_score -= 0.1
        
        # 检查平均相似度
        if alignment_result.average_similarity < 0.3:
            issues.append("Low average similarity")
            quality_score -= 0.3
        elif alignment_result.average_similarity > 0.8:
            quality_score += 0.2
        
        # 检查覆盖率
        if alignment_result.text_coverage < 0.1:
            issues.append("Low text coverage")
            quality_score -= 0.2
        
        if alignment_result.code_coverage < 0.1:
            issues.append("Low code coverage")
            quality_score -= 0.2
        
        # 确定质量等级
        if quality_score >= 0.7:
            quality = "excellent"
        elif quality_score >= 0.4:
            quality = "good"
        elif quality_score >= 0.1:
            quality = "fair"
        else:
            quality = "poor"
        
        return {
            "quality": quality,
            "score": max(0, min(1, quality_score)),
            "issues": issues,
            "recommendations": self._generate_recommendations(alignment_result, issues)
        }
    
    def _generate_recommendations(self, alignment_result: AlignmentResult, issues: List[str]) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if "No matches found" in issues:
            recommendations.append("Try lowering the similarity threshold")
            recommendations.append("Check if text and code are in the same domain")
        
        if "Low average similarity" in issues:
            recommendations.append("Consider using different embedding models")
            recommendations.append("Try preprocessing text and code differently")
        
        if "Low text coverage" in issues:
            recommendations.append("Extract more diverse text features")
            recommendations.append("Consider using different text segmentation")
        
        if "Low code coverage" in issues:
            recommendations.append("Extract more code features")
            recommendations.append("Consider different code parsing strategies")
        
        return recommendations


