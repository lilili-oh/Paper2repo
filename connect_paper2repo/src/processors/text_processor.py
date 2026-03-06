"""
文本处理器 - 负责文本预处理和特征提取
"""
import re
import string
from typing import List, Dict, Any, Optional
import nltk
import spacy
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
import torch

from ..models.text_model import TextDocument, TextFeature
from config import settings

class TextProcessor:
    """文本处理器类"""
    
    def __init__(self):
        """初始化文本处理器"""
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.embedding_model = SentenceTransformer(settings.embedding_model,device=device)
        self.nlp = None
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self._initialize_nlp()
        self._download_nltk_data()
    
    def _initialize_nlp(self):
        """初始化spaCy模型"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
        except (OSError, ImportError):
            print("spaCy not available. Using NLTK fallback.")
            self.nlp = None
    
    def _download_nltk_data(self):
        """下载必要的NLTK数据"""
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            nltk.download('wordnet', quiet=True)
        except Exception as e:
            print(f"Error downloading NLTK data: {e}")
    
    def preprocess_text(self, text: str) -> str:
        """文本预处理"""
        # 移除多余的空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 移除特殊字符（保留基本标点）
        if settings.text_preprocessing.get("remove_punctuation", True):
            text = re.sub(r'[^\w\s\.\,\!\?\;\:]', '', text)
        
        # 转换为小写
        if settings.text_preprocessing.get("lowercase", True):
            text = text.lower()
        
        return text
    
    def extract_sentences(self, text: str) -> List[str]:
        """提取句子"""
        if self.nlp:
            doc = self.nlp(text)
            sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 10]
        else:
            # 使用NLTK作为备选
            try:
                sentences = nltk.sent_tokenize(text)
                sentences = [sent.strip() for sent in sentences if len(sent.strip()) > 10]
            except:
                # 简单的句子分割作为最后备选
                sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        
        return sentences
    
    def extract_paragraphs(self, text: str) -> List[str]:
        """提取段落"""
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
        return paragraphs
    
    def extract_formulas(self, text: str) -> List[str]:
        """提取数学公式（简单实现）"""
        # 匹配LaTeX格式的公式
        latex_pattern = r'\$([^$]+)\$|\\\[([^\]]+)\\\]|\\\(([^)]+)\\\)'
        formulas = re.findall(latex_pattern, text)
        
        # 匹配简单的数学表达式
        math_pattern = r'[a-zA-Z]\s*[=<>]\s*[a-zA-Z0-9\+\-\*/\(\)]+'
        math_expressions = re.findall(math_pattern, text)
        
        all_formulas = []
        for formula_group in formulas:
            all_formulas.extend([f for f in formula_group if f.strip()])
        all_formulas.extend(math_expressions)
        
        return [f.strip() for f in all_formulas if len(f.strip()) > 2]
    
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        if self.nlp:
            doc = self.nlp(text)
            keywords = []
            
            # 提取名词短语
            for chunk in doc.noun_chunks:
                if len(chunk.text.split()) >= 2:
                    keywords.append(chunk.text.lower())
            
            # 提取命名实体
            for ent in doc.ents:
                if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']:
                    keywords.append(ent.text.lower())
            
            return list(set(keywords))
        else:
            # 简单的关键词提取作为备选
            import re
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            # 简单的频率统计
            from collections import Counter
            word_freq = Counter(words)
            # 返回最常见的词
            return [word for word, freq in word_freq.most_common(10)]
    
    def extract_features(self, text: str) -> List[TextFeature]:
        """提取文本特征"""
        features = []
        
        # 提取句子特征
        sentences = self.extract_sentences(text)
        for i, sentence in enumerate(sentences):
            feature = TextFeature(
                feature_type="sentence",
                content=sentence,
                position=i,
                metadata={"length": len(sentence)}
            )
            features.append(feature)
        
        # 提取段落特征
        paragraphs = self.extract_paragraphs(text)
        for i, paragraph in enumerate(paragraphs):
            feature = TextFeature(
                feature_type="paragraph",
                content=paragraph,
                position=i,
                metadata={"length": len(paragraph)}
            )
            features.append(feature)
        
        # 提取公式特征
        formulas = self.extract_formulas(text)
        for i, formula in enumerate(formulas):
            feature = TextFeature(
                feature_type="formula",
                content=formula,
                position=i,
                metadata={"type": "mathematical"}
            )
            features.append(feature)
        
        # 提取关键词特征
        keywords = self.extract_keywords(text)
        for i, keyword in enumerate(keywords):
            feature = TextFeature(
                feature_type="keyword",
                content=keyword,
                position=i,
                metadata={"type": "semantic"}
            )
            features.append(feature)
        
        return features
    
    def generate_embeddings(self, features: List[TextFeature]) -> List[TextFeature]:
        """为特征生成嵌入向量"""
        texts = [feature.content for feature in features]
        if not texts:
            return features
        
        # 生成嵌入向量
        embeddings = self.embedding_model.encode(texts)
        
        # 更新特征
        for i, feature in enumerate(features):
            feature.embedding = embeddings[i].tolist()
        
        return features
    
    def process_document(self, document: TextDocument) -> TextDocument:
        """处理文本文档"""
        # 预处理文本
        processed_content = self.preprocess_text(document.content)
        
        # 提取句子和段落
        sentences = self.extract_sentences(processed_content)
        paragraphs = self.extract_paragraphs(processed_content)
        
        # 更新文档
        document.content = processed_content
        document.sentences = sentences
        document.paragraphs = paragraphs
        
        # 提取特征
        features = self.extract_features(processed_content)
        
        # 生成嵌入向量
        features = self.generate_embeddings(features)
        
        # 更新文档特征
        document.features = features
        
        return document
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        embeddings = self.embedding_model.encode([text1, text2])
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        return float(similarity)
