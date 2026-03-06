#!/usr/bin/env python3
"""
演示脚本 - 展示论文与代码对齐工具的核心功能
"""
import sys
import os
import uuid
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_text_processing():
    """演示文本处理功能"""
    print("📝 文本处理演示")
    print("-" * 30)
    
    # 示例文本
    sample_text = """
    This paper presents a novel approach to machine learning using neural networks.
    The proposed method achieves state-of-the-art performance on several benchmarks.
    
    The algorithm works by:
    1. Preprocessing the input data
    2. Training a deep neural network
    3. Evaluating the model performance
    
    Our experiments show that the method achieves 95% accuracy on the test set.
    The loss function is defined as: L = -log(p) where p is the predicted probability.
    """
    
    print(f"📄 原始文本长度: {len(sample_text)} 字符")
    
    # 简单的文本处理
    sentences = [s.strip() for s in sample_text.split('.') if len(s.strip()) > 10]
    paragraphs = [p.strip() for p in sample_text.split('\n\n') if len(p.strip()) > 20]
    
    print(f"📊 提取到 {len(sentences)} 个句子")
    print(f"📊 提取到 {len(paragraphs)} 个段落")
    
    # 显示第一个句子
    if sentences:
        print(f"🔤 第一个句子: {sentences[0][:50]}...")
    
    return sample_text, sentences, paragraphs

def demo_code_processing():
    """演示代码处理功能"""
    print("\n💻 代码处理演示")
    print("-" * 30)
    
    # 示例Python代码
    sample_code = '''
def train_neural_network(X, y, epochs=100):
    """
    Train a neural network model
    
    Args:
        X: Input features
        y: Target labels
        epochs: Number of training epochs
    
    Returns:
        Trained model
    """
    model = create_model()
    
    for epoch in range(epochs):
        loss = model.train_step(X, y)
        if epoch % 10 == 0:
            print(f"Epoch {epoch}, Loss: {loss}")
    
    return model

class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.weights = self.initialize_weights()
    
    def initialize_weights(self):
        """Initialize network weights"""
        return np.random.randn(self.input_size, self.hidden_size)
    
    def forward(self, x):
        """Forward propagation"""
        return np.dot(x, self.weights)
'''
    
    print(f"📄 代码长度: {len(sample_code)} 字符")
    
    # 简单的代码分析
    lines = sample_code.split('\n')
    functions = []
    classes = []
    comments = []
    
    for i, line in enumerate(lines):
        line = line.strip()
        if line.startswith('def '):
            func_name = line.split('(')[0].replace('def ', '')
            functions.append((i+1, func_name))
        elif line.startswith('class '):
            class_name = line.split(':')[0].replace('class ', '').split('(')[0].strip()
            classes.append((i+1, class_name))
        elif line.startswith('#') or line.startswith('"""'):
            comments.append((i+1, line[:50]))
    
    print(f"📊 找到 {len(functions)} 个函数")
    print(f"📊 找到 {len(classes)} 个类")
    print(f"📊 找到 {len(comments)} 个注释")
    
    if functions:
        print(f"🔧 第一个函数: {functions[0][1]} (行 {functions[0][0]})")
    if classes:
        print(f"🏗️ 第一个类: {classes[0][1]} (行 {classes[0][0]})")
    
    return sample_code, functions, classes, comments

def demo_alignment():
    """演示对齐功能"""
    print("\n🔗 对齐演示")
    print("-" * 30)
    
    # 模拟文本特征
    text_features = [
        "neural network training",
        "machine learning algorithm", 
        "model performance evaluation",
        "loss function definition"
    ]
    
    # 模拟代码特征
    code_features = [
        "train_neural_network function",
        "NeuralNetwork class",
        "forward propagation method",
        "initialize_weights method"
    ]
    
    print(f"📝 文本特征: {len(text_features)} 个")
    print(f"💻 代码特征: {len(code_features)} 个")
    
    # 简单的相似度计算（基于关键词匹配）
    matches = []
    for i, text_feature in enumerate(text_features):
        for j, code_feature in enumerate(code_features):
            # 简单的关键词匹配
            text_words = set(text_feature.lower().split())
            code_words = set(code_feature.lower().split())
            
            # 计算Jaccard相似度
            intersection = len(text_words.intersection(code_words))
            union = len(text_words.union(code_words))
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0.1:  # 简单的阈值
                matches.append({
                    'text': text_feature,
                    'code': code_feature,
                    'similarity': similarity
                })
    
    print(f"🔗 找到 {len(matches)} 个匹配")
    
    # 显示最佳匹配
    if matches:
        best_match = max(matches, key=lambda x: x['similarity'])
        print(f"🏆 最佳匹配:")
        print(f"   文本: {best_match['text']}")
        print(f"   代码: {best_match['code']}")
        print(f"   相似度: {best_match['similarity']:.3f}")
    
    return matches

def demo_visualization():
    """演示可视化功能"""
    print("\n📊 可视化演示")
    print("-" * 30)
    
    # 模拟相似度数据
    similarities = [0.85, 0.72, 0.68, 0.45, 0.38, 0.32, 0.28, 0.15]
    
    print(f"📈 相似度分布:")
    print(f"   最高: {max(similarities):.3f}")
    print(f"   最低: {min(similarities):.3f}")
    print(f"   平均: {sum(similarities)/len(similarities):.3f}")
    
    # 简单的直方图
    print("\n📊 相似度分布图:")
    for i, sim in enumerate(similarities):
        bar_length = int(sim * 20)  # 缩放到20个字符
        bar = "█" * bar_length
        print(f"   {i+1:2d}: {bar} {sim:.3f}")
    
    return similarities

def main():
    """主演示函数"""
    print("🔗 Paper-Code Alignment Tool - 功能演示")
    print("=" * 50)
    
    # 运行各个演示
    text_content, sentences, paragraphs = demo_text_processing()
    code_content, functions, classes, comments = demo_code_processing()
    matches = demo_alignment()
    similarities = demo_visualization()
    
    # 总结
    print("\n📋 演示总结")
    print("=" * 50)
    print(f"✅ 文本处理: 提取了 {len(sentences)} 个句子和 {len(paragraphs)} 个段落")
    print(f"✅ 代码分析: 找到了 {len(functions)} 个函数和 {len(classes)} 个类")
    print(f"✅ 智能对齐: 发现了 {len(matches)} 个文本-代码对应关系")
    print(f"✅ 可视化: 分析了 {len(similarities)} 个相似度分数")
    
    print("\n🚀 完整功能需要安装依赖:")
    print("   pip install -r requirements.txt")
    print("   python -m spacy download en_core_web_sm")
    print("\n🎯 启动完整应用:")
    print("   streamlit run main.py")

if __name__ == "__main__":
    main()
