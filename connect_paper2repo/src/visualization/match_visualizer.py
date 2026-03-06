"""
匹配可视化器 - 展示具体的文字与代码匹配关系
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import re
from datetime import datetime

from ..models.alignment_model import AlignmentResult, AlignmentMatch
from ..models.text_model import TextDocument, TextFeature
from ..models.code_model import CodeRepository, CodeFile, CodeFeature

class MatchVisualizer:
    """匹配可视化器类"""
    
    def __init__(self):
        """初始化匹配可视化器"""
        self.color_map = "viridis"
    
    def create_detailed_match_view(self, alignment_result: AlignmentResult, 
                                 text_document: TextDocument, 
                                 code_repository: CodeRepository) -> None:
        """创建详细的匹配视图"""
        st.set_page_config(
            page_title="Text-Code Match Visualization",
            page_icon="🔍",
            layout="wide"
        )
        
        st.title("🔍 文字与代码匹配详情")
        st.markdown("展示具体的文字段落与代码片段的对应关系")
        
        if not alignment_result.matches:
            st.warning("⚠️ 没有找到匹配项")
            return
        
        # 创建侧边栏过滤器
        self._create_sidebar_filters(alignment_result)
        
        # 显示匹配概览
        self._show_match_overview(alignment_result)
        
        # 显示详细匹配列表
        self._show_detailed_matches(alignment_result, text_document, code_repository)
        
        # 显示匹配统计
        self._show_match_statistics(alignment_result)
    
    def _create_sidebar_filters(self, alignment_result: AlignmentResult):
        """创建侧边栏过滤器"""
        st.sidebar.title("🔧 过滤器")
        
        # 相似度阈值过滤
        min_similarity = st.sidebar.slider(
            "最低相似度",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05
        )
        
        # 匹配类型过滤
        match_types = list(set(match.alignment_type.value for match in alignment_result.matches))
        selected_types = st.sidebar.multiselect(
            "匹配类型",
            options=match_types,
            default=match_types
        )
        
        # 最大显示数量
        max_display = st.sidebar.slider(
            "最大显示数量",
            min_value=5,
            max_value=50,
            value=20,
            step=5
        )
        
        # 保存过滤条件到会话状态
        st.session_state.min_similarity = min_similarity
        st.session_state.selected_types = selected_types
        st.session_state.max_display = max_display
    
    def _show_match_overview(self, alignment_result: AlignmentResult):
        """显示匹配概览"""
        st.header("📊 匹配概览")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("总匹配数", alignment_result.total_matches)
        
        with col2:
            st.metric("平均相似度", f"{alignment_result.average_similarity:.3f}")
        
        with col3:
            st.metric("最高相似度", f"{max(m.similarity_score.score for m in alignment_result.matches):.3f}")
        
        with col4:
            st.metric("处理时间", f"{alignment_result.processing_time:.2f}s")
    
    def _show_detailed_matches(self, alignment_result: AlignmentResult, 
                              text_document: TextDocument, 
                              code_repository: CodeRepository):
        """显示详细匹配列表"""
        st.header("🔗 详细匹配列表")
        
        # 应用过滤器
        filtered_matches = self._apply_filters(alignment_result.matches)
        
        if not filtered_matches:
            st.info("没有符合过滤条件的匹配项")
            return
        
        # 按相似度排序
        filtered_matches.sort(key=lambda x: x.similarity_score.score, reverse=True)
        
        # 显示匹配项
        for i, match in enumerate(filtered_matches[:st.session_state.get('max_display', 20)]):
            with st.expander(f"匹配 {i+1} - 相似度: {match.similarity_score.score:.3f}", expanded=False):
                self._show_single_match(match, text_document, code_repository)
    
    def _show_single_match(self, match: AlignmentMatch, 
                          text_document: TextDocument, 
                          code_repository: CodeRepository):
        """显示单个匹配项"""
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📝 文本内容")
            st.markdown("**匹配的文本特征:**")
            
            # 显示文本内容
            text_content = match.text_feature
            if len(text_content) > 200:
                text_content = text_content[:200] + "..."
            
            st.code(text_content, language="text")
            
            # 显示文本元数据
            st.markdown("**文本信息:**")
            st.json({
                "特征类型": "text_feature",
                "位置": match.metadata.get("text_position", "未知"),
                "长度": len(match.text_feature)
            })
        
        with col2:
            st.subheader("💻 代码内容")
            st.markdown("**匹配的代码特征:**")
            
            # 显示代码内容
            code_content = match.code_feature
            if len(code_content) > 200:
                code_content = code_content[:200] + "..."
            
            st.code(code_content, language="python")
            
            # 显示代码元数据
            st.markdown("**代码信息:**")
            st.json({
                "文件": match.metadata.get("code_file", "未知"),
                "行号": match.metadata.get("code_line", "未知"),
                "长度": len(match.code_feature)
            })
        
        # 显示匹配详情
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("相似度分数", f"{match.similarity_score.score:.3f}")
        
        with col2:
            st.metric("置信度", f"{match.similarity_score.confidence:.3f}")
        
        with col3:
            st.metric("匹配类型", match.alignment_type.value)
        
        # 显示解释
        if match.explanation:
            st.markdown("**匹配解释:**")
            st.info(match.explanation)
    
    def _show_match_statistics(self, alignment_result: AlignmentResult):
        """显示匹配统计"""
        st.header("📈 匹配统计")
        
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
                yaxis_title="匹配数量",
                width=400,
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 匹配类型分布
            match_types = [match.alignment_type.value for match in alignment_result.matches]
            type_counts = pd.Series(match_types).value_counts()
            
            fig = go.Figure(data=[
                go.Pie(
                    labels=type_counts.index,
                    values=type_counts.values,
                    marker_colors=px.colors.qualitative.Set3[:len(type_counts)]
                )
            ])
            
            fig.update_layout(
                title="匹配类型分布",
                width=400,
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    def _apply_filters(self, matches: List[AlignmentMatch]) -> List[AlignmentMatch]:
        """应用过滤器"""
        filtered = matches
        
        # 相似度过滤
        min_sim = st.session_state.get('min_similarity', 0.0)
        filtered = [m for m in filtered if m.similarity_score.score >= min_sim]
        
        # 类型过滤
        selected_types = st.session_state.get('selected_types', [])
        if selected_types:
            filtered = [m for m in filtered if m.alignment_type.value in selected_types]
        
        return filtered
    
    def create_side_by_side_view(self, alignment_result: AlignmentResult,
                                text_document: TextDocument,
                                code_repository: CodeRepository) -> None:
        """创建并排对比视图"""
        st.set_page_config(
            page_title="Side-by-Side Match View",
            page_icon="⚖️",
            layout="wide"
        )
        
        st.title("⚖️ 文字与代码并排对比")
        
        if not alignment_result.matches:
            st.warning("⚠️ 没有找到匹配项")
            return
        
        # 选择要显示的匹配
        match_options = {
            f"匹配 {i+1} (相似度: {match.similarity_score.score:.3f})": match 
            for i, match in enumerate(alignment_result.matches)
        }
        
        selected_match = st.selectbox(
            "选择要查看的匹配:",
            list(match_options.keys())
        )
        
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
            
            # 显示文本上下文
            st.markdown("**文本上下文:**")
            # 这里可以添加更多上下文信息
            st.info("显示文本的更多上下文信息...")
        
        with col2:
            st.header("💻 代码内容")
            
            # 显示完整的代码内容
            st.markdown("**匹配的代码片段:**")
            st.code(match.code_feature, language="python")
            
            # 显示代码上下文
            st.markdown("**代码上下文:**")
            # 这里可以添加更多上下文信息
            st.info("显示代码的更多上下文信息...")
        
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
    
    def create_interactive_match_dashboard(self, alignment_result: AlignmentResult,
                                         text_document: TextDocument,
                                         code_repository: CodeRepository) -> None:
        """创建交互式匹配仪表板"""
        st.set_page_config(
            page_title="Interactive Match Dashboard",
            page_icon="🎯",
            layout="wide"
        )
        
        st.title("🎯 交互式匹配仪表板")
        
        # 创建标签页
        tab1, tab2, tab3, tab4 = st.tabs(["匹配列表", "并排对比", "统计分析", "网络图"])
        
        with tab1:
            self._show_match_list_tab(alignment_result, text_document, code_repository)
        
        with tab2:
            self._show_side_by_side_tab(alignment_result, text_document, code_repository)
        
        with tab3:
            self._show_statistics_tab(alignment_result)
        
        with tab4:
            self._show_network_tab(alignment_result)
    
    def _show_match_list_tab(self, alignment_result: AlignmentResult,
                           text_document: TextDocument,
                           code_repository: CodeRepository):
        """显示匹配列表标签页"""
        st.header("📋 匹配列表")
        
        # 创建过滤器
        col1, col2, col3 = st.columns(3)
        
        with col1:
            min_sim = st.slider("最低相似度", 0.0, 1.0, 0.3, 0.05)
        
        with col2:
            max_display = st.slider("显示数量", 5, 50, 20, 5)
        
        with col3:
            sort_by = st.selectbox("排序方式", ["相似度", "置信度", "类型"])
        
        # 过滤和排序匹配
        filtered_matches = [m for m in alignment_result.matches if m.similarity_score.score >= min_sim]
        
        if sort_by == "相似度":
            filtered_matches.sort(key=lambda x: x.similarity_score.score, reverse=True)
        elif sort_by == "置信度":
            filtered_matches.sort(key=lambda x: x.similarity_score.confidence, reverse=True)
        elif sort_by == "类型":
            filtered_matches.sort(key=lambda x: x.alignment_type.value)
        
        # 显示匹配列表
        for i, match in enumerate(filtered_matches[:max_display]):
            with st.expander(f"匹配 {i+1} - {match.similarity_score.score:.3f}", expanded=False):
                self._show_single_match(match, text_document, code_repository)
    
    def _show_side_by_side_tab(self, alignment_result: AlignmentResult,
                              text_document: TextDocument,
                              code_repository: CodeRepository):
        """显示并排对比标签页"""
        st.header("⚖️ 并排对比")
        
        if not alignment_result.matches:
            st.warning("没有匹配项")
            return
        
        # 选择匹配
        match_options = {
            f"匹配 {i+1} (相似度: {match.similarity_score.score:.3f})": match 
            for i, match in enumerate(alignment_result.matches)
        }
        
        selected_match = st.selectbox("选择匹配:", list(match_options.keys()))
        
        if selected_match:
            match = match_options[selected_match]
            self._show_side_by_side_match(match, text_document, code_repository)
    
    def _show_statistics_tab(self, alignment_result: AlignmentResult):
        """显示统计标签页"""
        st.header("📊 统计分析")
        
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
    
    def _show_network_tab(self, alignment_result: AlignmentResult):
        """显示网络图标签页"""
        st.header("🕸️ 匹配网络图")
        
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


