# 论文文本与 GitHub 代码语义对齐工具 

## 项目简介

本项目旨在解决科研论文与 GitHub 代码仓库之间的“信息脱节”问题。用户输入论文片段或文档描述，系统会自动在指定仓库中查找与之语义最相关的代码片段，并展示相似度和可视化对齐结果。该工具帮助开发者和科研人员：

- 快速找到论文算法对应的代码实现；
- 提高科研复现和开源项目理解效率；
- 为文档补充、PR生成等后续扩展提供基础接口。

**核心 AI 功能**：
1. 文本与代码向量化（Embedding）
2. 语义检索和相似度匹配
3. 可选：生成自然语言对齐说明与修改建议

## 功能特点

- 🔹 **论文片段与代码对齐**：输入论文文本，返回最相关代码片段
- 🔹 **相似度计算**：提供语义相似度评分
- 🔹 **可视化展示**：高亮显示论文片段与对应代码，支持前端查看
- 🔹 **跨语言支持**：目前支持 Python，后续可扩展到 C++、Java 等
- 🔹 **开源可扩展**：提供 API 接口，方便集成到其他工具或服务

## 技术架构

```
用户输入文本 (论文描述) ─────┐
                           │
                           v
                   [文本向量编码模块]  ←  AI
                             │
GitHub 仓库拉取与分片 ───→ [代码向量索引库构建]  ←  AI
                             │
                             v
                     FAISS 相似度检索  ←  AI
                             │
                             v
                     可视化展示模块（高亮 + 相似度）  ←  工程实现
```

**说明**：
- AI 部分：文本与代码向量化、语义检索、可选 LLM 生成对齐说明
- 工程实现：仓库拉取、分片、前端展示、API服务（FastAPI/Streamlit）

## 安装指南

### 1. 克隆仓库
```bash
git clone https://github.com/your-username/paper-code-align.git
cd paper-code-align
```

### 2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```
依赖示例：
- `sentence-transformers`：文本和代码向量化
- `faiss-cpu`：向量检索
- `PyGithub`：仓库拉取
- `Streamlit` 或 `FastAPI`：前端展示或 API

## 使用方法

### 命令行示例
```bash
python main.py --repo https://github.com/example/repo --text "论文描述片段"
```
输出：
- Top-K 匹配代码片段
- 相似度评分
- 可选择生成对齐解释文本

### Web 前端（Streamlit）
```bash
streamlit run app.py
```
在浏览器中打开本地地址，输入论文文本和 GitHub 仓库链接即可查看可视化结果。

## 示例截图

![示例截图](docs/example.png)  
*论文文本与代码片段匹配可视化示意*

## 项目结构

```
paper-code-align/
├── main.py          # 程序入口
├── app.py           # Streamlit 前端示例
├── aligner/         # AI 核心模块（向量化 + 检索）
│   └── __init__.py
├── utils/           # 工具函数（GitHub 拉取、代码分片）
│   └── __init__.py
├── docs/            # 文档、示例截图
├── README.md        # 项目说明
└── requirements.txt # 依赖
```

## 贡献指南

欢迎贡献！请遵循以下步骤：

1. Fork 仓库
2. 创建新分支：`git checkout -b feature/新功能`
3. 提交修改：`git commit -m "描述功能"`
4. Push 分支：`git push origin feature/新功能`
5. 提交 Pull Request

请确保代码风格一致，并在提交前通过单元测试。

## 许可证

本项目采用 **MIT License**，详情见 [LICENSE](LICENSE)。

## 联系方式

- 作者：你的名字  
- GitHub: [https://github.com/your-username/paper-code-align](https://github.com/your-username/paper-code-align)
