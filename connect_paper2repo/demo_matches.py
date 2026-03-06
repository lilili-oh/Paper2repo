#!/usr/bin/env python3
"""
匹配可视化演示脚本 - 展示文字与代码的具体匹配关系
"""
import sys
import os
import uuid
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def create_sample_data():
    """创建示例数据"""
    print("📝 创建示例数据...")
    
    # 示例文本内容
    sample_text = """
    This paper presents a novel machine learning approach for image classification.
    The proposed method uses a deep convolutional neural network architecture.
    
    The algorithm consists of three main steps:
    1. Data preprocessing and augmentation
    2. Model training with backpropagation
    3. Performance evaluation on test dataset
    
    Our experiments show that the method achieves 95% accuracy on the CIFAR-10 dataset.
    The loss function is defined as: L = -log(p) where p is the predicted probability.
    
    The network architecture includes:
    - Input layer: 32x32x3 RGB images
    - Convolutional layers: 3 layers with ReLU activation
    - Pooling layers: Max pooling for dimensionality reduction
    - Fully connected layers: 2 layers with dropout regularization
    - Output layer: 10 classes with softmax activation
    """
    
    # 示例代码内容
    sample_code = '''
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torchvision.transforms as transforms

class CNNClassifier(nn.Module):
    """
    Convolutional Neural Network for image classification
    """
    def __init__(self, num_classes=10):
        super(CNNClassifier, self).__init__()
        
        # Convolutional layers
        self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
        
        # Pooling layer
        self.pool = nn.MaxPool2d(2, 2)
        
        # Fully connected layers
        self.fc1 = nn.Linear(128 * 4 * 4, 512)
        self.fc2 = nn.Linear(512, num_classes)
        self.dropout = nn.Dropout(0.5)
        
    def forward(self, x):
        """Forward propagation"""
        # Convolutional layers with ReLU activation
        x = torch.relu(self.conv1(x))
        x = self.pool(x)
        
        x = torch.relu(self.conv2(x))
        x = self.pool(x)
        
        x = torch.relu(self.conv3(x))
        x = self.pool(x)
        
        # Flatten for fully connected layers
        x = x.view(-1, 128 * 4 * 4)
        
        # Fully connected layers with dropout
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        return x

def train_model(model, train_loader, criterion, optimizer, epochs=10):
    """
    Train the CNN model using backpropagation
    """
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for i, (inputs, labels) in enumerate(train_loader):
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        print(f'Epoch {epoch+1}, Loss: {running_loss/len(train_loader):.3f}')

def evaluate_model(model, test_loader):
    """
    Evaluate model performance on test dataset
    """
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            outputs = model(inputs)
            _, predicted = torch.max(outputs.data, 1)
            total += labels.size(0)
            correct += (predicted == labels).sum().item()
    
    accuracy = 100 * correct / total
    print(f'Test Accuracy: {accuracy:.2f}%')
    return accuracy

# Loss function definition
def cross_entropy_loss(outputs, labels):
    """
    Cross-entropy loss function: L = -log(p)
    """
    return nn.CrossEntropyLoss()(outputs, labels)
'''
    
    return sample_text, sample_code

def create_mock_alignment_result():
    """创建模拟的对齐结果"""
    print("🔗 创建模拟对齐结果...")
    
    # 模拟匹配项
    matches = [
        {
            "text": "deep convolutional neural network architecture",
            "code": "class CNNClassifier(nn.Module):",
            "similarity": 0.85,
            "type": "semantic",
            "explanation": "文本描述神经网络架构与代码中的CNN类定义匹配"
        },
        {
            "text": "Data preprocessing and augmentation",
            "code": "import torchvision.transforms as transforms",
            "similarity": 0.72,
            "type": "semantic", 
            "explanation": "文本提到数据预处理与代码中的数据变换导入匹配"
        },
        {
            "text": "Model training with backpropagation",
            "code": "def train_model(model, train_loader, criterion, optimizer, epochs=10):",
            "similarity": 0.88,
            "type": "semantic",
            "explanation": "文本描述模型训练与代码中的训练函数匹配"
        },
        {
            "text": "Performance evaluation on test dataset",
            "code": "def evaluate_model(model, test_loader):",
            "similarity": 0.79,
            "type": "semantic",
            "explanation": "文本提到性能评估与代码中的评估函数匹配"
        },
        {
            "text": "The loss function is defined as: L = -log(p)",
            "code": "def cross_entropy_loss(outputs, labels):",
            "similarity": 0.91,
            "type": "semantic",
            "explanation": "文本中的损失函数定义与代码中的交叉熵损失函数匹配"
        },
        {
            "text": "Convolutional layers: 3 layers with ReLU activation",
            "code": "self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)",
            "similarity": 0.76,
            "type": "structural",
            "explanation": "文本描述卷积层与代码中的卷积层定义匹配"
        },
        {
            "text": "Pooling layers: Max pooling for dimensionality reduction",
            "code": "self.pool = nn.MaxPool2d(2, 2)",
            "similarity": 0.83,
            "type": "structural",
            "explanation": "文本提到最大池化与代码中的池化层定义匹配"
        },
        {
            "text": "Fully connected layers: 2 layers with dropout regularization",
            "code": "self.fc1 = nn.Linear(128 * 4 * 4, 512)",
            "similarity": 0.74,
            "type": "structural",
            "explanation": "文本描述全连接层与代码中的线性层定义匹配"
        }
    ]
    
    return matches

def display_matches(matches):
    """显示匹配结果"""
    print("\n🔍 文字与代码匹配详情")
    print("=" * 60)
    
    for i, match in enumerate(matches, 1):
        print(f"\n📋 匹配 {i}:")
        print(f"   相似度: {match['similarity']:.3f}")
        print(f"   类型: {match['type']}")
        print(f"   解释: {match['explanation']}")
        
        print(f"\n📝 文本内容:")
        print(f"   {match['text']}")
        
        print(f"\n💻 代码内容:")
        print(f"   {match['code']}")
        
        print("-" * 60)

def display_side_by_side(matches):
    """显示并排对比"""
    print("\n⚖️ 并排对比视图")
    print("=" * 80)
    
    for i, match in enumerate(matches[:3], 1):  # 只显示前3个
        print(f"\n🔗 匹配 {i} - 相似度: {match['similarity']:.3f}")
        print("=" * 80)
        
        # 并排显示
        text_lines = match['text'].split('\n')
        code_lines = match['code'].split('\n')
        
        max_lines = max(len(text_lines), len(code_lines))
        
        print(f"{'📝 文本内容':<40} | {'💻 代码内容':<40}")
        print("-" * 80)
        
        for j in range(max_lines):
            text_line = text_lines[j] if j < len(text_lines) else ""
            code_line = code_lines[j] if j < len(code_lines) else ""
            
            # 截断过长的行
            text_display = text_line[:38] + ".." if len(text_line) > 38 else text_line
            code_display = code_line[:38] + ".." if len(code_line) > 38 else code_line
            
            print(f"{text_display:<40} | {code_display:<40}")
        
        print(f"\n💡 匹配解释: {match['explanation']}")
        print("-" * 80)

def display_statistics(matches):
    """显示匹配统计"""
    print("\n📊 匹配统计信息")
    print("=" * 40)
    
    # 基本统计
    similarities = [match['similarity'] for match in matches]
    types = [match['type'] for match in matches]
    
    print(f"总匹配数: {len(matches)}")
    print(f"平均相似度: {sum(similarities)/len(similarities):.3f}")
    print(f"最高相似度: {max(similarities):.3f}")
    print(f"最低相似度: {min(similarities):.3f}")
    
    # 类型分布
    from collections import Counter
    type_counts = Counter(types)
    print(f"\n匹配类型分布:")
    for match_type, count in type_counts.items():
        print(f"  {match_type}: {count} 个")
    
    # 相似度分布
    print(f"\n相似度分布:")
    high_sim = len([s for s in similarities if s >= 0.8])
    medium_sim = len([s for s in similarities if 0.6 <= s < 0.8])
    low_sim = len([s for s in similarities if s < 0.6])
    
    print(f"  高相似度 (≥0.8): {high_sim} 个")
    print(f"  中等相似度 (0.6-0.8): {medium_sim} 个")
    print(f"  低相似度 (<0.6): {low_sim} 个")

def display_network_view(matches):
    """显示网络视图"""
    print("\n🕸️ 匹配网络图")
    print("=" * 50)
    
    # 简化的网络图表示
    print("文本节点 -> 代码节点 (相似度)")
    print("-" * 50)
    
    for i, match in enumerate(matches[:10], 1):  # 只显示前10个
        text_node = f"T{i}"
        code_node = f"C{i}"
        similarity = match['similarity']
        
        # 用字符表示相似度强度
        strength = int(similarity * 10)
        bar = "█" * strength + "░" * (10 - strength)
        
        print(f"{text_node} -> {code_node} [{bar}] {similarity:.3f}")

def main():
    """主演示函数"""
    print("🔍 文字与代码匹配可视化演示")
    print("=" * 50)
    
    # 创建示例数据
    sample_text, sample_code = create_sample_data()
    matches = create_mock_alignment_result()
    
    print(f"📄 示例文本长度: {len(sample_text)} 字符")
    print(f"💻 示例代码长度: {len(sample_code)} 字符")
    print(f"🔗 找到匹配: {len(matches)} 个")
    
    # 显示不同类型的视图
    display_matches(matches)
    display_side_by_side(matches)
    display_statistics(matches)
    display_network_view(matches)
    
    print("\n🎯 完整功能需要运行:")
    print("   streamlit run main.py")
    print("   然后选择 '🔍 Match Details' 页面查看详细的可视化界面")

if __name__ == "__main__":
    main()
