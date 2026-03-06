# 📁 项目结构

```
connect_paper2repo/
├── 📄 main.py                          # 主应用程序入口
├── 📄 run.py                           # 启动脚本
├── 📄 test_basic.py                    # 基本功能测试
├── 📄 config.py                        # 配置文件
├── 📄 requirements.txt                 # 依赖列表
├── 📄 env_example.txt                  # 环境变量示例
├── 📄 README.md                        # 项目说明
├── 📄 PROJECT_STRUCTURE.md             # 项目结构说明
│
├── 📁 src/                             # 源代码目录
│   ├── 📄 __init__.py                  # 包初始化
│   │
│   ├── 📁 models/                      # 数据模型
│   │   ├── 📄 __init__.py
│   │   ├── 📄 text_model.py            # 文本数据模型
│   │   ├── 📄 code_model.py            # 代码数据模型
│   │   └── 📄 alignment_model.py       # 对齐结果模型
│   │
│   ├── 📁 processors/                  # 处理器模块
│   │   ├── 📄 __init__.py
│   │   ├── 📄 text_processor.py        # 文本处理器
│   │   ├── 📄 code_processor.py       # 代码处理器
│   │   └── 📄 alignment_processor.py   # 对齐处理器
│   │
│   ├── 📁 services/                    # 服务模块
│   │   ├── 📄 __init__.py
│   │   ├── 📄 github_service.py        # GitHub API服务
│   │   └── 📄 storage_service.py      # 存储服务
│   │
│   └── 📁 visualization/              # 可视化模块
│       ├── 📄 __init__.py
│       ├── 📄 alignment_visualizer.py   # 对齐可视化器
│       └── 📄 similarity_visualizer.py # 相似度可视化器
│
└── 📁 data/                           # 数据目录（运行时创建）
    ├── 📁 chroma_db/                  # ChromaDB向量数据库
    ├── 📁 text_documents/             # 文本文档存储
    ├── 📁 code_repositories/           # 代码仓库存储
    └── 📁 alignment_results/          # 对齐结果存储
```

## 🏗️ 架构说明

### 核心组件

1. **📊 数据模型层** (`src/models/`)
   - `TextDocument`: 文本文档模型
   - `CodeFile`: 代码文件模型
   - `CodeRepository`: 代码仓库模型
   - `AlignmentResult`: 对齐结果模型

2. **⚙️ 处理器层** (`src/processors/`)
   - `TextProcessor`: 文本预处理和特征提取
   - `CodeProcessor`: 代码解析和特征提取
   - `AlignmentProcessor`: 对齐算法和相似度计算

3. **🔌 服务层** (`src/services/`)
   - `GitHubService`: GitHub API集成
   - `StorageService`: 数据持久化

4. **📊 可视化层** (`src/visualization/`)
   - `AlignmentVisualizer`: 对齐结果可视化
   - `SimilarityVisualizer`: 相似度分析可视化

### 数据流

```
📝 文本输入 → TextProcessor → 文本特征 → 嵌入向量
💻 代码输入 → CodeProcessor → 代码特征 → 嵌入向量
🔗 对齐处理 → AlignmentProcessor → 相似度计算 → 对齐结果
📊 可视化 → Visualizers → 交互式图表 → 用户界面
💾 存储 → StorageService → ChromaDB/文件系统 → 持久化
```

### 技术栈

- **前端**: Streamlit (Web界面)
- **后端**: Python 3.8+
- **NLP**: spaCy, NLTK, Sentence Transformers
- **ML**: scikit-learn, PyTorch
- **数据库**: ChromaDB (向量数据库)
- **可视化**: Plotly, NetworkX
- **API**: GitHub API, PyGithub
- **解析**: Tree-sitter

### 关键特性

1. **🔍 智能特征提取**
   - 文本: 句子、段落、公式、关键词
   - 代码: 函数、类、变量、注释

2. **🧠 语义对齐算法**
   - 语义相似度 (Sentence Transformers)
   - 词汇相似度 (TF-IDF, Jaccard)
   - 结构相似度 (模式匹配)

3. **📊 丰富可视化**
   - 相似度热力图
   - 对齐网络图
   - 分布分析
   - 交互式仪表板

4. **💾 数据持久化**
   - 向量数据库存储
   - 文件系统备份
   - 增量更新

### 扩展性

- **模块化设计**: 易于添加新的处理器
- **插件架构**: 支持自定义可视化器
- **配置驱动**: 灵活的参数调整
- **API友好**: 支持程序化调用


