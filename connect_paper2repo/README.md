# 🔗 Paper-Code Alignment Tool

智能论文与代码对齐工具 - 自动分析文本描述与代码仓库的语义对应关系

## 🚀 功能特性

- **📝 文本处理**: 从论文、文档或任何文本中提取语义特征
- **💻 代码分析**: 解析和分析GitHub代码仓库，提取代码特征
- **🔗 智能对齐**: 使用先进的NLP技术找到语义对应关系
- **📊 可视化**: 交互式仪表板和相似度分析
- **💾 结果导出**: 保存和分享对齐结果

## 🛠️ 技术架构

### 核心模块

1. **文本处理器** (`src/processors/text_processor.py`)
   - 文本预处理和清洗
   - 句子、段落、公式提取
   - 关键词和命名实体识别
   - 语义嵌入向量生成

2. **代码处理器** (`src/processors/code_processor.py`)
   - 多语言代码解析 (Python, JavaScript, Java, C++, Go, Rust)
   - 函数、类、变量、注释提取
   - 代码结构分析
   - 语义嵌入向量生成

3. **对齐处理器** (`src/processors/alignment_processor.py`)
   - 语义相似度计算
   - 词汇相似度分析
   - 结构相似度匹配
   - 混合对齐算法

4. **GitHub服务** (`src/services/github_service.py`)
   - GitHub API集成
   - 仓库信息获取
   - 代码文件下载
   - 仓库搜索功能

5. **存储服务** (`src/services/storage_service.py`)
   - ChromaDB向量数据库
   - 文件系统备份
   - 数据持久化

6. **可视化器** (`src/visualization/`)
   - 对齐结果可视化
   - 相似度分析图表
   - 交互式仪表板

## 📦 安装和配置

### 1. 环境要求

- Python 3.8+
- 8GB+ RAM (推荐)
- 2GB+ 磁盘空间

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 下载NLP模型

```bash
# 下载spaCy英文模型
python -m spacy download en_core_web_sm

# 下载NLTK数据
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet')"
```

### 4. 配置环境变量

复制 `env_example.txt` 为 `.env` 并配置：

```bash
cp env_example.txt .env
```

编辑 `.env` 文件，设置你的GitHub token（可选，用于提高API限制）：

```
GITHUB_TOKEN=your_github_token_here
```

## 🚀 使用方法
### 运行演示
、、、bash
python demo.py 
# or
python demo_matches.py
、、、

### 启动应用

```bash
streamlit run main.py
```

### 基本工作流程

1. **📝 输入文本**
   - 上传文件 (TXT, MD, PDF)
   - 粘贴文本内容
   - 从URL加载

2. **💻 输入代码**
   - 连接GitHub仓库
   - 上传代码文件
   - 粘贴代码内容

3. **🔗 运行对齐**
   - 选择文本和代码
   - 配置对齐参数
   - 相似度阈值
   - 对齐方法
   - 最大匹配数

4. **📊 可视化结果**
   - 对齐仪表板
   - 相似度分析
   - 网络图
   - 统计信息

## 📊 可视化功能

### 对齐仪表板
- 相似度热力图
- 覆盖率分析
- 特征类型分布
- 最佳匹配表格

### 相似度分析
- 分布直方图
- 趋势分析
- 聚类分析
- 相关性分析

### 网络可视化
- 文本-代码对应关系图
- 特征连接网络
- 交互式探索

## 🔧 配置选项

### 模型配置
- 嵌入模型选择
- 相似度阈值调整
- 对齐方法选择

### 文本处理
- 标点符号处理
- 大小写转换
- 停用词过滤
- 词形还原

### 代码分析
- 支持语言选择
- 特征提取配置
- 解析深度设置

## 📈 性能优化

### 内存优化
- 分批处理大文件
- 向量缓存机制
- 增量更新

### 计算优化
- 并行处理
- 向量化计算
- 模型缓存

### 存储优化
- 压缩存储
- 索引优化
- 增量备份

## 🔍 使用案例

### 1. 论文与实现对齐
- 上传研究论文
- 连接相关GitHub仓库
- 找到论文描述与代码实现的对应关系

### 2. 文档与代码同步
- 分析技术文档
- 匹配对应的代码实现
- 识别文档与代码的差异

### 3. 代码理解辅助
- 输入代码描述
- 找到最相关的代码片段
- 辅助代码理解和维护

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

MIT License

## 🙏 致谢

- [Sentence Transformers](https://www.sbert.net/)
- [spaCy](https://spacy.io/)
- [Tree-sitter](https://tree-sitter.github.io/)
- [ChromaDB](https://www.trychroma.com/)
- [Streamlit](https://streamlit.io/)
- [Plotly](https://plotly.com/)

## 📞 支持

如有问题或建议，请：
- 创建Issue
- 发送邮件
- 参与讨论

---

**🔗 Paper-Code Alignment Tool** - 让文本与代码的对应关系一目了然！
