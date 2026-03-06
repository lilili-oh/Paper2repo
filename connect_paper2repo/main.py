"""
主应用程序 - 论文与代码对齐智能工具
Paper-to-Code Alignment Tool
"""
import streamlit as st
import os
import uuid
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd

# 导入自定义模块
from src.models.text_model import TextDocument
from src.models.code_model import CodeRepository
from src.models.alignment_model import AlignmentResult, AlignmentMatch
from src.processors.text_processor import TextProcessor
from src.processors.code_processor import CodeProcessor
from src.processors.alignment_processor import AlignmentProcessor
from src.services.github_service import GitHubService
from src.services.storage_service import StorageService
from src.visualization.alignment_visualizer import AlignmentVisualizer
from src.visualization.similarity_visualizer import SimilarityVisualizer
from src.visualization.match_visualizer import MatchVisualizer
from config import settings

class PaperCodeAlignmentApp:
    """论文与代码对齐应用主类"""
    
    def __init__(self):
        """初始化应用"""
        self.text_processor = TextProcessor()
        self.code_processor = CodeProcessor()
        self.alignment_processor = AlignmentProcessor()
        self.github_service = GitHubService()
        self.storage_service = StorageService()
        self.alignment_visualizer = AlignmentVisualizer()
        self.similarity_visualizer = SimilarityVisualizer()
        self.match_visualizer = MatchVisualizer()
        
        # 初始化会话状态
        if 'alignment_results' not in st.session_state:
            st.session_state.alignment_results = []
        if 'text_documents' not in st.session_state:
            st.session_state.text_documents = []
        if 'code_repositories' not in st.session_state:
            st.session_state.code_repositories = []
    
    def run(self):
        """运行应用"""
        st.set_page_config(
            page_title="Paper-Code Alignment Tool",
            page_icon="🔗",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # 主标题
        st.title("🔗 Paper-Code Alignment Tool")
        st.markdown("智能论文与代码对齐工具 - 自动分析文本描述与代码仓库的语义对应关系")
        
        # 侧边栏导航
        self._create_sidebar()
        
        # 主内容区域
        page = st.session_state.get('current_page', 'home')
        
        if page == 'home':
            self._show_home_page()
        elif page == 'text_input':
            self._show_text_input_page()
        elif page == 'code_input':
            self._show_code_input_page()
        elif page == 'alignment':
            self._show_alignment_page()
        elif page == 'visualization':
            self._show_visualization_page()
        elif page == 'match_details':
            self._show_match_details_page()
        elif page == 'results':
            self._show_results_page()
        elif page == 'settings':
            self._show_settings_page()
    
    def _create_sidebar(self):
        """创建侧边栏导航"""
        st.sidebar.title("📋 Navigation")
        
        pages = {
            "🏠 Home": "home",
            "📝 Text Input": "text_input", 
            "💻 Code Input": "code_input",
            "🔗 Alignment": "alignment",
            "📊 Visualization": "visualization",
            "🔍 Match Details": "match_details",
            "📋 Results": "results",
            "⚙️ Settings": "settings"
        }
        
        for page_name, page_key in pages.items():
            if st.sidebar.button(page_name, key=f"nav_{page_key}"):
                st.session_state.current_page = page_key
                # st.rerun()
        
        # 显示当前状态
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 📊 Current Status")
        st.sidebar.metric("Text Documents", len(st.session_state.text_documents))
        st.sidebar.metric("Code Repositories", len(st.session_state.code_repositories))
        st.sidebar.metric("Alignment Results", len(st.session_state.alignment_results))
    
    def _show_home_page(self):
        """显示首页"""
        st.header("🏠 Welcome to Paper-Code Alignment Tool")
        
        st.markdown("""
        This tool helps you automatically align text descriptions (papers, documentation) 
        with corresponding code repositories by analyzing semantic similarities.
        
        ### 🚀 Features
        - **Text Processing**: Extract features from papers, documentation, or any text
        - **Code Analysis**: Parse and analyze code repositories from GitHub
        - **Smart Alignment**: Use advanced NLP to find semantic correspondences
        - **Visualization**: Interactive dashboards and similarity analysis
        - **Export Results**: Save and share alignment results
        
        ### 📖 How to Use
        1. **Input Text**: Upload or paste your text content (papers, descriptions)
        2. **Input Code**: Connect to GitHub repositories or upload code files
        3. **Run Alignment**: Let the AI find semantic correspondences
        4. **Visualize**: Explore results with interactive charts
        5. **Export**: Save your findings for further analysis
        """)
        
        # 快速开始按钮
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📝 Start with Text", use_container_width=True):
                st.session_state.current_page = "text_input"
                # st.rerun()
        
        with col2:
            if st.button("💻 Start with Code", use_container_width=True):
                st.session_state.current_page = "code_input"
                # st.rerun()
        
        with col3:
            if st.button("🔗 Quick Alignment", use_container_width=True):
                st.session_state.current_page = "alignment"
                # st.rerun()
        
        # 显示最近的成果
        if st.session_state.alignment_results:
            st.markdown("---")
            st.subheader("📈 Recent Results")
            
            for i, result in enumerate(st.session_state.alignment_results[-3:]):
                with st.expander(f"Alignment Result {i+1} - {result.id[:8]}..."):
                    st.metric("Total Matches", result.total_matches)
                    st.metric("Average Similarity", f"{result.average_similarity:.3f}")
                    st.metric("Processing Time", f"{result.processing_time:.2f}s")
    
    def _show_text_input_page(self):
        """显示文本输入页面"""
        st.header("📝 Text Input")
        
        # 输入方式选择
        input_method = st.radio(
            "Choose input method:",
            ["Upload File", "Paste Text", "Load from URL"]
        )
        
        text_content = ""
        text_title = ""
        
        if input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Upload a text file",
                type=['txt', 'md', 'pdf'],
                help="Supported formats: TXT, MD, PDF"
            )
            
            if uploaded_file:
                if uploaded_file.type == "text/plain":
                    text_content = str(uploaded_file.read(), "utf-8")
                elif uploaded_file.type == "text/markdown":
                    text_content = str(uploaded_file.read(), "utf-8")
                else:
                    st.warning("PDF support coming soon. Please use TXT or MD files.")
                
                text_title = uploaded_file.name
        
        elif input_method == "Paste Text":
            text_content = st.text_area(
                "Paste your text here:",
                height=300,
                placeholder="Enter your paper content, documentation, or any text description..."
            )
            text_title = st.text_input("Document Title:", value="Untitled Document")
        
        elif input_method == "Load from URL":
            url = st.text_input("Enter URL:")
            if url:
                st.info("URL loading feature coming soon. Please use file upload or paste text.")
        
        # 处理文本
        if text_content:
            st.markdown("---")
            st.subheader("📊 Text Preview")
            
            # 显示文本统计
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Characters", len(text_content))
            with col2:
                st.metric("Words", len(text_content.split()))
            with col3:
                st.metric("Lines", len(text_content.split('\n')))
            with col4:
                st.metric("Paragraphs", len([p for p in text_content.split('\n\n') if p.strip()]))
            
            # 显示文本预览
            with st.expander("📖 Text Preview"):
                st.text(text_content[:1000] + "..." if len(text_content) > 1000 else text_content)
            
            # 处理按钮
            if st.button("🔄 Process Text", type="primary"):
                with st.spinner("Processing text..."):
                    # 创建文本文档
                    document = TextDocument(
                        id=str(uuid.uuid4()),
                        title=text_title,
                        content=text_content,
                        source="manual"
                    )
                    
                    # 处理文档
                    print("start process document  1")
                    processed_document = self.text_processor.process_document(document)
                    print("end process document  2")
                    # 保存到会话状态
                    st.session_state.text_documents.append(processed_document)
                    print("append session state  3")
                    # 保存到存储
                    self.storage_service.save_text_document(processed_document)
                    print("process success!!")
                    
                    st.success(f"✅ Text processed successfully! Found {len(processed_document.features)} features.")
                    print("before rerun  4")
                    # st.rerun()
    
    def _show_code_input_page(self):
        """显示代码输入页面"""
        st.header("💻 Code Input")
        
        # 输入方式选择
        input_method = st.radio(
            "Choose input method:",
            ["GitHub Repository", "Upload Files", "Paste Code"]
        )
        
        if input_method == "GitHub Repository":
            st.subheader("🔗 Connect to GitHub Repository")
            
            # GitHub配置
            github_token = st.text_input(
                "GitHub Token (optional):",
                type="password",
                help="Enter your GitHub token for higher rate limits"
            )
            
            if "repo_info" not in st.session_state:
                st.session_state.repo_info = None
                
            if github_token:
                self.github_service = GitHubService(github_token)
            
            # 仓库URL输入
            repo_url = st.text_input(
                "Repository URL:",
                placeholder="https://github.com/owner/repo or owner/repo"
            )
            
            max_files = st.slider("Maximum files to analyze:", 10, 100, 50)
            
            # 按钮1：分析仓库
            if repo_url and st.button("🔍 Analyze Repository", type="primary"):
                with st.spinner("Fetching repository..."):
                    owner, repo_name = self.github_service.parse_repository_url(repo_url)
                    repo_info = self.github_service.get_repository_info(owner, repo_name)
                    st.session_state.repo_info = repo_info  # ✅ 存储在 session_state
                    st.session_state.owner = owner
                    st.session_state.repo_name = repo_name
                    st.success(f"✅ Repository found: {repo_info['full_name']}")

            # 如果已经有 repo_info，则显示仓库信息 + 第二个按钮
            if st.session_state.repo_info:
                repo_info = st.session_state.repo_info
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Stars", repo_info['stars'])
                with col2:
                    st.metric("Forks", repo_info['forks'])
                with col3:
                    st.metric("Size", f"{repo_info['size']} KB")
                with col4:
                    st.metric("Language", repo_info['language'] or "Mixed")

                # 按钮2：处理仓库
                if st.button("🔄 Process Repository", type="primary"):
                    with st.spinner("Processing repository..."):
                        print("start create code repository  0")
                        code_repo = self.github_service.create_code_repository(
                            st.session_state.owner,
                            st.session_state.repo_name,
                            max_files
                        )
                        print("start process code repository  1")
                        st.session_state.code_repositories.append(code_repo)
                        print("append session state  2")
                        self.storage_service.save_code_repository(code_repo)
                        print("process success!!  3")
                        st.success(
                            f"✅ Repository processed! Found {len(code_repo.files)} files with "
                            f"{sum(len(f.features) for f in code_repo.files)} features."
                        )        
        elif input_method == "Upload Files":
            st.subheader("📁 Upload Code Files")
            uploaded_files = st.file_uploader(
                "Upload code files",
                type=['py', 'js', 'java', 'cpp', 'go', 'rs'],
                accept_multiple_files=True,
                help="Supported formats: Python, JavaScript, Java, C++, Go, Rust"
            )
            
            if uploaded_files:
                st.info(f"📁 {len(uploaded_files)} files uploaded")
                
                if st.button("🔄 Process Files", type="primary"):
                    with st.spinner("Processing files..."):
                        # 创建代码仓库
                        code_repo = CodeRepository(
                            id=str(uuid.uuid4()),
                            name="Uploaded Files",
                            owner="user",
                            url="local"
                        )
                        
                        # 处理每个文件
                        for uploaded_file in uploaded_files:
                            content = str(uploaded_file.read(), "utf-8")
                            code_file = self.code_processor.process_file(
                                uploaded_file.name, content
                            )
                            code_repo.files.append(code_file)
                        
                        # 更新统计信息
                        code_repo.total_files = len(code_repo.files)
                        code_repo.total_lines = sum(len(f.content.split('\n')) for f in code_repo.files)
                        code_repo.languages = set(f.language for f in code_repo.files)
                        
                        # 保存到会话状态
                        st.session_state.code_repositories.append(code_repo)
                        
                        # 保存到存储
                        self.storage_service.save_code_repository(code_repo)
                        
                        st.success(f"✅ Files processed! Found {sum(len(f.features) for f in code_repo.files)} features.")
                        # st.rerun()
        
        elif input_method == "Paste Code":
            st.subheader("📝 Paste Code")
            code_content = st.text_area(
                "Paste your code here:",
                height=300,
                placeholder="Enter your code..."
            )
            
            if code_content:
                if st.button("🔄 Process Code", type="primary"):
                    with st.spinner("Processing code..."):
                        # 创建代码文件
                        code_file = self.code_processor.process_file("pasted_code.py", code_content)
                        
                        # 创建代码仓库
                        code_repo = CodeRepository(
                            id=str(uuid.uuid4()),
                            name="Pasted Code",
                            owner="user",
                            url="local"
                        )
                        code_repo.files.append(code_file)
                        code_repo.total_files = 1
                        code_repo.total_lines = len(code_content.split('\n'))
                        code_repo.languages = {code_file.language}
                        
                        # 保存到会话状态
                        st.session_state.code_repositories.append(code_repo)
                        
                        # 保存到存储
                        self.storage_service.save_code_repository(code_repo)
                        
                        st.success(f"✅ Code processed! Found {len(code_file.features)} features.")
                        # st.rerun()
    
    def _show_alignment_page(self):
        """显示对齐页面"""
        st.header("🔗 Text-Code Alignment")
        
        # 检查是否有可用的文本和代码
        if not st.session_state.text_documents:
            st.warning("⚠️ No text documents available. Please add some text first.")
            return
        
        if not st.session_state.code_repositories:
            st.warning("⚠️ No code repositories available. Please add some code first.")
            return
        
        # 选择文本和代码
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📝 Select Text Document")
            text_options = {f"{doc.title} ({len(doc.features)} features)": doc for doc in st.session_state.text_documents}
            selected_text = st.selectbox("Choose text document:", list(text_options.keys()))
            text_document = text_options[selected_text]
        
        with col2:
            st.subheader("💻 Select Code Repository")
            code_options = {f"{repo.name} ({len(repo.files)} files)": repo for repo in st.session_state.code_repositories}
            selected_code = st.selectbox("Choose code repository:", list(code_options.keys()))
            code_repository = code_options[selected_code]
        
        # 对齐配置
        st.subheader("⚙️ Alignment Configuration")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.1,
                max_value=0.9,
                value=settings.similarity_threshold,
                step=0.05
            )
        with col2:
            alignment_method = st.selectbox(
                "Alignment Method",
                ["semantic", "lexical", "hybrid"],
                index=0
            )
        with col3:
            max_matches = st.slider(
                "Maximum Matches",
                min_value=10,
                max_value=1000,
                value=100,
                step=10
            )
        
        # 运行对齐
        if st.button("🚀 Run Alignment", type="primary", use_container_width=True):
            with st.spinner("Running alignment analysis..."):
                # 更新配置
                settings.similarity_threshold = similarity_threshold
                settings.alignment_method = alignment_method
                
                # 运行对齐
                alignment_result = self.alignment_processor.find_alignments(
                    text_document, code_repository
                )
                
                # 保存结果
                st.session_state.alignment_results.append(alignment_result)
                self.storage_service.save_alignment_result(alignment_result)
                
                st.success("✅ Alignment completed!")
                # st.rerun()
        
        # 显示最近的对齐结果
        if st.session_state.alignment_results:
            st.markdown("---")
            st.subheader("📊 Recent Alignment Results")
            
            for i, result in enumerate(st.session_state.alignment_results[-3:]):
                with st.expander(f"Result {i+1} - {result.id[:8]}..."):
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Matches", result.total_matches)
                    with col2:
                        st.metric("Avg Similarity", f"{result.average_similarity:.3f}")
                    with col3:
                        st.metric("Text Coverage", f"{result.text_coverage:.1%}")
                    with col4:
                        st.metric("Processing Time", f"{result.processing_time:.2f}s")
                    
                    if st.button(f"View Details", key=f"view_{i}"):
                        st.session_state.selected_result = result
                        st.session_state.current_page = "visualization"
                        # st.rerun()
    
    def _show_visualization_page(self):
        """显示可视化页面"""
        st.header("📊 Visualization Dashboard")
        
        # 选择要可视化的结果
        if not st.session_state.alignment_results:
            st.warning("⚠️ No alignment results available. Please run alignment first.")
            return
        
        # 选择结果
        result_options = {f"Result {i+1} - {result.id[:8]}...": result for i, result in enumerate(st.session_state.alignment_results)}
        selected_result = st.selectbox("Choose alignment result:", list(result_options.keys()))
        alignment_result = result_options[selected_result]
        
        # 可视化选项
        viz_type = st.radio(
            "Choose visualization type:",
            ["Alignment Dashboard", "Similarity Analysis", "Interactive Dashboard"]
        )
        
        if viz_type == "Alignment Dashboard":
            # 创建对齐仪表板
            self.alignment_visualizer.create_interactive_dashboard(alignment_result)
        
        elif viz_type == "Similarity Analysis":
            # 创建相似度分析
            self.similarity_visualizer.create_interactive_similarity_dashboard(alignment_result)
        
        elif viz_type == "Interactive Dashboard":
            # 创建综合仪表板
            st.subheader("🔗 Comprehensive Analysis")
            
            # 创建标签页
            tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Similarity", "Network", "Statistics"])
            
            with tab1:
                # 概览
                summary = self.alignment_visualizer.create_alignment_summary(alignment_result)
                
                col1, col2 = st.columns(2)
                with col1:
                    for key, value in list(summary.items())[:4]:
                        st.metric(key, value)
                with col2:
                    for key, value in list(summary.items())[4:]:
                        st.metric(key, value)
                
                # 覆盖率图表
                coverage_fig = self.alignment_visualizer.create_coverage_chart(alignment_result)
                st.plotly_chart(coverage_fig, use_container_width=True)
            
            with tab2:
                # 相似度分析
                dist_fig = self.similarity_visualizer.create_similarity_distribution(alignment_result)
                st.plotly_chart(dist_fig, use_container_width=True)
                
                corr_fig = self.similarity_visualizer.create_similarity_correlation(alignment_result)
                st.plotly_chart(corr_fig, use_container_width=True)
            
            with tab3:
                # 网络图
                network_fig = self.alignment_visualizer.create_alignment_network(alignment_result)
                st.plotly_chart(network_fig, use_container_width=True)
            
            with tab4:
                # 统计信息
                stats = self.similarity_visualizer.create_similarity_statistics(alignment_result)
                
                if "error" not in stats:
                    stats_df = pd.DataFrame([
                        {"Metric": k, "Value": f"{v:.3f}" if isinstance(v, float) else str(v)}
                        for k, v in stats.items()
                    ])
                    st.dataframe(stats_df, use_container_width=True)
    
    def _show_match_details_page(self):
        """显示匹配详情页面"""
        st.header("🔍 文字与代码匹配详情")
        
        # 检查是否有对齐结果
        if not st.session_state.alignment_results:
            st.warning("⚠️ 没有对齐结果。请先运行对齐分析。")
            return
        
        # 选择要查看的对齐结果
        result_options = {f"结果 {i+1} - {result.id[:8]}...": result for i, result in enumerate(st.session_state.alignment_results)}
        selected_result = st.selectbox("选择对齐结果:", list(result_options.keys()))
        alignment_result = result_options[selected_result]
        
        # 获取对应的文本和代码数据
        text_document = None
        code_repository = None
        
        # 从会话状态中查找对应的文本和代码
        for doc in st.session_state.text_documents:
            if doc.id == alignment_result.text_document_id:
                text_document = doc
                break
        
        for repo in st.session_state.code_repositories:
            if repo.id == alignment_result.code_repository_id:
                code_repository = repo
                break
        
        if not text_document or not code_repository:
            st.error("❌ 无法找到对应的文本或代码数据")
            return
        
        # 显示匹配详情
        st.markdown("---")
        
        # 创建标签页
        tab1, tab2, tab3 = st.tabs(["详细匹配", "并排对比", "交互式仪表板"])
        
        with tab1:
            self._show_detailed_matches_tab(alignment_result, text_document, code_repository)
        
        with tab2:
            self._show_side_by_side_tab(alignment_result, text_document, code_repository)
        
        with tab3:
            self._show_interactive_dashboard_tab(alignment_result, text_document, code_repository)
    
    def _show_detailed_matches_tab(self, alignment_result: AlignmentResult, 
                                  text_document: TextDocument, 
                                  code_repository: CodeRepository):
        """显示详细匹配标签页"""
        st.subheader("📋 详细匹配列表")
        
        if not alignment_result.matches:
            st.info("没有找到匹配项")
            return
        
        # 创建过滤器
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_similarity = st.slider("最低相似度", 0.0, 1.0, 0.3, 0.05)
        
        with col2:
            max_display = st.slider("显示数量", 5, 50, 20, 5)
        
        with col3:
            sort_by = st.selectbox("排序方式", ["相似度", "置信度", "类型"])
        
        # 过滤和排序
        filtered_matches = [m for m in alignment_result.matches if m.similarity_score.score >= min_similarity]
        
        if sort_by == "相似度":
            filtered_matches.sort(key=lambda x: x.similarity_score.score, reverse=True)
        elif sort_by == "置信度":
            filtered_matches.sort(key=lambda x: x.similarity_score.confidence, reverse=True)
        elif sort_by == "类型":
            filtered_matches.sort(key=lambda x: x.alignment_type.value)
        
        # 显示匹配项
        for i, match in enumerate(filtered_matches[:max_display]):
            with st.expander(f"匹配 {i+1} - 相似度: {match.similarity_score.score:.3f}", expanded=False):
                self._show_single_match_details(match, text_document, code_repository)
    
    def _show_single_match_details(self, match: AlignmentMatch, 
                                  text_document: TextDocument, 
                                  code_repository: CodeRepository):
        """显示单个匹配的详细信息"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📝 文本内容")
            st.markdown("**匹配的文本特征:**")
            
            # 显示文本内容
            text_content = match.text_feature
            if len(text_content) > 300:
                text_content = text_content[:300] + "..."
            
            st.code(text_content, language="text")
            
            # 显示文本元数据
            st.markdown("**文本信息:**")
            st.json({
                "特征类型": "text_feature",
                "位置": match.metadata.get("text_position", "未知"),
                "长度": len(match.text_feature),
                "相似度": f"{match.similarity_score.score:.3f}"
            })
        
        with col2:
            st.subheader("💻 代码内容")
            st.markdown("**匹配的代码特征:**")
            
            # 显示代码内容
            code_content = match.code_feature
            if len(code_content) > 300:
                code_content = code_content[:300] + "..."
            
            st.code(code_content, language="python")
            
            # 显示代码元数据
            st.markdown("**代码信息:**")
            st.json({
                "文件": match.metadata.get("code_file", "未知"),
                "行号": match.metadata.get("code_line", "未知"),
                "长度": len(match.code_feature),
                "置信度": f"{match.similarity_score.confidence:.3f}"
            })
        
        # 显示匹配详情
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("相似度分数", f"{match.similarity_score.score:.3f}")
            st.metric("置信度", f"{match.similarity_score.confidence:.3f}")
        
        with col2:
            st.metric("匹配类型", match.alignment_type.value)
            st.metric("计算方法", match.similarity_score.method)
        
        with col3:
            st.metric("文本长度", len(match.text_feature))
            st.metric("代码长度", len(match.code_feature))
        
        # 显示解释
        if match.explanation:
            st.markdown("**匹配解释:**")
            st.info(match.explanation)
    
    def _show_side_by_side_tab(self, alignment_result: AlignmentResult,
                              text_document: TextDocument,
                              code_repository: CodeRepository):
        """显示并排对比标签页"""
        st.subheader("⚖️ 并排对比")
        
        if not alignment_result.matches:
            st.warning("没有匹配项")
            return
        
        # 选择要查看的匹配
        match_options = {
            f"匹配 {i+1} (相似度: {match.similarity_score.score:.3f})": match 
            for i, match in enumerate(alignment_result.matches)
        }
        
        selected_match = st.selectbox("选择匹配:", list(match_options.keys()))
        
        if selected_match:
            match = match_options[selected_match]
            self._show_side_by_side_match(match, text_document, code_repository)
    
    def _show_side_by_side_match(self, match: AlignmentMatch,
                                text_document: TextDocument,
                                code_repository: CodeRepository):
        """显示并排匹配"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.header("📝 文本内容")
            
            # 显示完整的文本内容
            st.markdown("**匹配的文本段落:**")
            st.markdown(f"```\n{match.text_feature}\n```")
            
            # 显示文本统计
            st.markdown("**文本统计:**")
            st.metric("字符数", len(match.text_feature))
            st.metric("单词数", len(match.text_feature.split()))
            st.metric("行数", len(match.text_feature.split('\n')))
        
        with col2:
            st.header("💻 代码内容")
            
            # 显示完整的代码内容
            st.markdown("**匹配的代码片段:**")
            st.code(match.code_feature, language="python")
            
            # 显示代码统计
            st.markdown("**代码统计:**")
            st.metric("字符数", len(match.code_feature))
            st.metric("行数", len(match.code_feature.split('\n')))
            st.metric("文件", match.metadata.get("code_file", "未知"))
        
        # 显示匹配分析
        st.markdown("---")
        st.header("🔍 匹配分析")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("相似度", f"{match.similarity_score.score:.3f}")
            st.metric("置信度", f"{match.similarity_score.confidence:.3f}")
        
        with col2:
            st.metric("匹配类型", match.alignment_type.value)
            st.metric("计算方法", match.similarity_score.method)
        
        with col3:
            st.metric("文本长度", len(match.text_feature))
            st.metric("代码长度", len(match.code_feature))
        
        # 显示匹配解释
        if match.explanation:
            st.markdown("**匹配解释:**")
            st.success(match.explanation)
    
    def _show_interactive_dashboard_tab(self, alignment_result: AlignmentResult,
                                      text_document: TextDocument,
                                      code_repository: CodeRepository):
        """显示交互式仪表板标签页"""
        st.subheader("🎯 交互式匹配仪表板")
        
        # 创建子标签页
        tab1, tab2, tab3 = st.tabs(["匹配列表", "统计分析", "网络图"])
        
        with tab1:
            self._show_detailed_matches_tab(alignment_result, text_document, code_repository)
        
        with tab2:
            self._show_match_statistics_tab(alignment_result)
        
        with tab3:
            self._show_match_network_tab(alignment_result)
    
    def _show_match_statistics_tab(self, alignment_result: AlignmentResult):
        """显示匹配统计标签页"""
        st.subheader("📊 匹配统计")
        
        # 创建统计图表
        col1, col2 = st.columns(2)
        
        with col1:
            # 相似度分布
            scores = [match.similarity_score.score for match in alignment_result.matches]
            fig = go.Figure(data=[
                go.Histogram(
                    x=scores,
                    nbinsx=20,
                    marker_color='lightblue',
                    opacity=0.7
                )
            ])
            
            fig.update_layout(
                title="相似度分布",
                xaxis_title="相似度分数",
                yaxis_title="匹配数量"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 匹配类型分布
            match_types = [match.alignment_type.value for match in alignment_result.matches]
            type_counts = pd.Series(match_types).value_counts()
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=type_counts.index,
                    values=type_counts.values
                )
            ])
            
            fig.update_layout(title="匹配类型分布")
            st.plotly_chart(fig, use_container_width=True)
    
    def _show_match_network_tab(self, alignment_result: AlignmentResult):
        """显示匹配网络图标签页"""
        st.subheader("🕸️ 匹配网络图")
        
        # 创建网络图
        import networkx as nx
        
        G = nx.Graph()
        
        # 添加节点和边
        for i, match in enumerate(alignment_result.matches[:20]):  # 限制节点数量
            text_node = f"T{i}"
            code_node = f"C{i}"
            
            G.add_node(text_node, type="text", label=f"Text {i+1}")
            G.add_node(code_node, type="code", label=f"Code {i+1}")
            G.add_edge(text_node, code_node, weight=match.similarity_score.score)
        
        # 计算布局
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # 创建网络图
        fig = go.Figure()
        
        # 添加边
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            fig.add_trace(go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(width=2, color='gray'),
                showlegend=False,
                hoverinfo='none'
            ))
        
        # 添加节点
        for node in G.nodes():
            x, y = pos[node]
            node_type = G.nodes[node]['type']
            color = 'lightblue' if node_type == 'text' else 'lightcoral'
            
            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(size=20, color=color),
                text=G.nodes[node]['label'],
                textposition="middle center",
                showlegend=False,
                hoverinfo='text'
            ))
        
        fig.update_layout(
            title="匹配网络图",
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            width=800,
            height=600
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def _show_results_page(self):
        """显示结果页面"""
        st.header("📋 Results Management")
        
        if not st.session_state.alignment_results:
            st.info("No alignment results available.")
            return
        
        # 结果列表
        for i, result in enumerate(st.session_state.alignment_results):
            with st.expander(f"Result {i+1} - {result.id[:8]}...", expanded=False):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Matches", result.total_matches)
                    st.metric("Average Similarity", f"{result.average_similarity:.3f}")
                
                with col2:
                    st.metric("Text Coverage", f"{result.text_coverage:.1%}")
                    st.metric("Code Coverage", f"{result.code_coverage:.1%}")
                
                with col3:
                    st.metric("Processing Time", f"{result.processing_time:.2f}s")
                    st.metric("Created", result.created_at.strftime("%Y-%m-%d %H:%M"))
                
                # 操作按钮
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button(f"View", key=f"view_{i}"):
                        st.session_state.selected_result = result
                        st.session_state.current_page = "visualization"
                        # st.rerun()
                
                with col2:
                    if st.button(f"Export", key=f"export_{i}"):
                        # 导出功能
                        st.info("Export functionality coming soon!")
                
                with col3:
                    if st.button(f"Delete", key=f"delete_{i}"):
                        st.session_state.alignment_results.pop(i)
                        # st.rerun()
    
    def _show_settings_page(self):
        """显示设置页面"""
        st.header("⚙️ Settings")
        
        # 模型配置
        st.subheader("🤖 Model Configuration")
        
        col1, col2 = st.columns(2)
        with col1:
            embedding_model = st.text_input(
                "Embedding Model",
                value=settings.embedding_model,
                help="Sentence transformer model for embeddings"
            )
        
        with col2:
            similarity_threshold = st.slider(
                "Similarity Threshold",
                min_value=0.1,
                max_value=0.9,
                value=settings.similarity_threshold,
                step=0.05
            )
        
        # 文本处理配置
        st.subheader("📝 Text Processing")
        
        col1, col2 = st.columns(2)
        with col1:
            remove_punctuation = st.checkbox(
                "Remove Punctuation",
                value=settings.text_preprocessing.get("remove_punctuation", True)
            )
            lowercase = st.checkbox(
                "Convert to Lowercase",
                value=settings.text_preprocessing.get("lowercase", True)
            )
        
        with col2:
            remove_stopwords = st.checkbox(
                "Remove Stopwords",
                value=settings.text_preprocessing.get("remove_stopwords", True)
            )
            lemmatize = st.checkbox(
                "Lemmatize",
                value=settings.text_preprocessing.get("lemmatize", True)
            )
        
        # 代码分析配置
        st.subheader("💻 Code Analysis")
        
        supported_languages = st.multiselect(
            "Supported Languages",
            options=["python", "javascript", "java", "cpp", "go", "rust"],
            default=settings.supported_languages
        )
        
        # 保存设置
        if st.button("💾 Save Settings", type="primary"):
            # 更新配置
            settings.embedding_model = embedding_model
            settings.similarity_threshold = similarity_threshold
            settings.text_preprocessing = {
                "remove_punctuation": remove_punctuation,
                "lowercase": lowercase,
                "remove_stopwords": remove_stopwords,
                "lemmatize": lemmatize
            }
            settings.supported_languages = supported_languages
            
            st.success("✅ Settings saved!")
        
        # 存储统计
        st.subheader("💾 Storage Statistics")
        stats = self.storage_service.get_storage_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Text Documents", stats.get("text_documents", 0))
        with col2:
            st.metric("Code Repositories", stats.get("code_repositories", 0))
        with col3:
            st.metric("Alignment Results", stats.get("alignment_results", 0))
        with col4:
            st.metric("Total Size", f"{stats.get('total_size', 0) / 1024 / 1024:.2f} MB")

def main():
    """主函数"""
    app = PaperCodeAlignmentApp()
    app.run()

if __name__ == "__main__":
    main()
