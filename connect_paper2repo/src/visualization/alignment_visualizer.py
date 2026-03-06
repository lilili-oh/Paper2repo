"""
对齐可视化器 - 负责对齐结果的可视化展示
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
import networkx as nx
from datetime import datetime

from ..models.alignment_model import AlignmentResult, AlignmentMatch
from ..models.text_model import TextDocument
from ..models.code_model import CodeRepository
from config import settings

class AlignmentVisualizer:
    """对齐可视化器类"""
    
    def __init__(self):
        """初始化可视化器"""
        self.color_map = settings.similarity_color_map
    
    def create_similarity_heatmap(self, alignment_result: AlignmentResult, max_items: int = 20) -> go.Figure:
        """创建相似度热力图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 准备数据
        matches = alignment_result.matches[:max_items]
        
        # 创建矩阵数据
        similarity_matrix = []
        text_labels = []
        code_labels = []
        
        for i, match in enumerate(matches):
            similarity_matrix.append([match.similarity_score.score])
            text_labels.append(f"Text {i+1}")
            code_labels.append(f"Code {i+1}")
        
        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            x=code_labels,
            y=text_labels,
            colorscale=self.color_map,
            showscale=True,
            colorbar=dict(title="Similarity Score")
        ))
        
        fig.update_layout(
            title="Text-Code Similarity Heatmap",
            xaxis_title="Code Features",
            yaxis_title="Text Features",
            width=800,
            height=600
        )
        
        return fig
    
    def create_similarity_distribution(self, alignment_result: AlignmentResult) -> go.Figure:
        """创建相似度分布图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 提取相似度分数
        scores = [match.similarity_score.score for match in alignment_result.matches]
        
        # 创建直方图
        fig = go.Figure(data=[
            go.Histogram(
                x=scores,
                nbinsx=20,
                marker_color='lightblue',
                opacity=0.7
            )
        ])
        
        # 添加统计信息
        mean_score = np.mean(scores)
        median_score = np.median(scores)
        
        fig.add_vline(
            x=mean_score,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Mean: {mean_score:.3f}"
        )
        
        fig.add_vline(
            x=median_score,
            line_dash="dot",
            line_color="green",
            annotation_text=f"Median: {median_score:.3f}"
        )
        
        fig.update_layout(
            title="Similarity Score Distribution",
            xaxis_title="Similarity Score",
            yaxis_title="Count",
            width=800,
            height=400
        )
        
        return fig
    
    def create_alignment_network(self, alignment_result: AlignmentResult, max_nodes: int = 30) -> go.Figure:
        """创建对齐网络图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 创建网络图
        G = nx.Graph()
        
        # 添加节点和边
        matches = alignment_result.matches[:max_nodes]
        
        for i, match in enumerate(matches):
            text_node = f"T{i}"
            code_node = f"C{i}"
            
            G.add_node(text_node, type="text", label=f"Text {i+1}")
            G.add_node(code_node, type="code", label=f"Code {i+1}")
            G.add_edge(text_node, code_node, weight=match.similarity_score.score)
        
        # 计算布局
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # 提取边信息
        edge_x = []
        edge_y = []
        edge_info = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            
            weight = G[edge[0]][edge[1]]['weight']
            edge_info.append(f"Similarity: {weight:.3f}")
        
        # 创建边轨迹
        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=2, color='gray'),
            hoverinfo='none',
            mode='lines'
        )
        
        # 提取节点信息
        node_x = []
        node_y = []
        node_text = []
        node_colors = []
        
        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            
            node_type = G.nodes[node]['type']
            node_label = G.nodes[node]['label']
            node_text.append(node_label)
            
            if node_type == "text":
                node_colors.append('lightblue')
            else:
                node_colors.append('lightcoral')
        
        # 创建节点轨迹
        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle center",
            marker=dict(
                size=20,
                color=node_colors,
                line=dict(width=2, color='black')
            )
        )
        
        # 创建图形
        fig = go.Figure(data=[edge_trace, node_trace],
                       layout=go.Layout(
                           title="Text-Code Alignment Network",
                           titlefont_size=16,
                           showlegend=False,
                           hovermode='closest',
                           margin=dict(b=20,l=5,r=5,t=40),
                           annotations=[ dict(
                               text="Blue nodes: Text features, Red nodes: Code features",
                               showarrow=False,
                               xref="paper", yref="paper",
                               x=0.005, y=-0.002,
                               xanchor='left', yanchor='bottom',
                               font=dict(color="black", size=12)
                           )],
                           xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                           width=800,
                           height=600
                       ))
        
        return fig
    
    def create_coverage_chart(self, alignment_result: AlignmentResult) -> go.Figure:
        """创建覆盖率图表"""
        # 准备数据
        coverage_data = {
            'Alignment Coverage': alignment_result.alignment_coverage,
            'Text Coverage': alignment_result.text_coverage,
            'Code Coverage': alignment_result.code_coverage
        }
        
        # 创建条形图
        fig = go.Figure(data=[
            go.Bar(
                x=list(coverage_data.keys()),
                y=list(coverage_data.values()),
                marker_color=['lightblue', 'lightgreen', 'lightcoral'],
                text=[f"{v:.1%}" for v in coverage_data.values()],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Alignment Coverage Metrics",
            xaxis_title="Coverage Type",
            yaxis_title="Coverage Percentage",
            yaxis=dict(tickformat='.0%'),
            width=600,
            height=400
        )
        
        return fig
    
    def create_top_matches_table(self, alignment_result: AlignmentResult, max_matches: int = 10) -> pd.DataFrame:
        """创建最佳匹配表格"""
        if not alignment_result.matches:
            return pd.DataFrame()
        
        # 准备数据
        matches_data = []
        for i, match in enumerate(alignment_result.matches[:max_matches]):
            matches_data.append({
                'Rank': i + 1,
                'Text Feature': match.text_feature[:50] + "..." if len(match.text_feature) > 50 else match.text_feature,
                'Code Feature': match.code_feature[:50] + "..." if len(match.code_feature) > 50 else match.code_feature,
                'Similarity Score': f"{match.similarity_score.score:.3f}",
                'Confidence': f"{match.similarity_score.confidence:.3f}",
                'Type': match.alignment_type.value,
                'Explanation': match.explanation
            })
        
        return pd.DataFrame(matches_data)
    
    def create_alignment_summary(self, alignment_result: AlignmentResult) -> Dict[str, Any]:
        """创建对齐摘要"""
        summary = {
            "Total Matches": alignment_result.total_matches,
            "Average Similarity": f"{alignment_result.average_similarity:.3f}",
            "Best Match Score": f"{max(m.similarity_score.score for m in alignment_result.matches):.3f}" if alignment_result.matches else "N/A",
            "Alignment Coverage": f"{alignment_result.alignment_coverage:.1%}",
            "Text Coverage": f"{alignment_result.text_coverage:.1%}",
            "Code Coverage": f"{alignment_result.code_coverage:.1%}",
            "Processing Time": f"{alignment_result.processing_time:.2f}s",
            "Created At": alignment_result.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return summary
    
    def create_feature_type_distribution(self, alignment_result: AlignmentResult) -> go.Figure:
        """创建特征类型分布图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 统计特征类型
        text_types = {}
        code_types = {}
        
        for match in alignment_result.matches:
            # 这里需要从metadata中获取特征类型
            # 简化实现，假设可以从explanation中提取
            if "sentence" in match.explanation.lower():
                text_types["sentence"] = text_types.get("sentence", 0) + 1
            elif "paragraph" in match.explanation.lower():
                text_types["paragraph"] = text_types.get("paragraph", 0) + 1
            elif "formula" in match.explanation.lower():
                text_types["formula"] = text_types.get("formula", 0) + 1
            else:
                text_types["other"] = text_types.get("other", 0) + 1
            
            if "function" in match.explanation.lower():
                code_types["function"] = code_types.get("function", 0) + 1
            elif "class" in match.explanation.lower():
                code_types["class"] = code_types.get("class", 0) + 1
            elif "comment" in match.explanation.lower():
                code_types["comment"] = code_types.get("comment", 0) + 1
            else:
                code_types["other"] = code_types.get("other", 0) + 1
        
        # 创建子图
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=("Text Feature Types", "Code Feature Types"),
            specs=[[{"type": "pie"}, {"type": "pie"}]]
        )
        
        # 添加文本特征饼图
        if text_types:
            fig.add_trace(
                go.Pie(
                    labels=list(text_types.keys()),
                    values=list(text_types.values()),
                    name="Text Features"
                ),
                row=1, col=1
            )
        
        # 添加代码特征饼图
        if code_types:
            fig.add_trace(
                go.Pie(
                    labels=list(code_types.keys()),
                    values=list(code_types.values()),
                    name="Code Features"
                ),
                row=1, col=2
            )
        
        fig.update_layout(
            title="Feature Type Distribution",
            width=800,
            height=400
        )
        
        return fig
    
    def _create_empty_plot(self, message: str) -> go.Figure:
        """创建空图表"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5,
            showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(
            xaxis=dict(showgrid=False, showticklabels=False),
            yaxis=dict(showgrid=False, showticklabels=False),
            width=400,
            height=300
        )
        return fig
    
    def create_interactive_dashboard(self, alignment_result: AlignmentResult) -> None:
        """创建交互式仪表板"""
        st.set_page_config(
            page_title="Paper-Code Alignment Dashboard",
            page_icon="🔗",
            layout="wide"
        )
        
        st.title("🔗 Paper-Code Alignment Dashboard")
        
        # 摘要信息
        st.header("📊 Alignment Summary")
        summary = self.create_alignment_summary(alignment_result)
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Matches", summary["Total Matches"])
        with col2:
            st.metric("Average Similarity", summary["Average Similarity"])
        with col3:
            st.metric("Alignment Coverage", summary["Alignment Coverage"])
        with col4:
            st.metric("Processing Time", summary["Processing Time"])
        
        # 主要图表
        st.header("📈 Visualization")
        
        tab1, tab2, tab3, tab4 = st.tabs(["Similarity Heatmap", "Distribution", "Network", "Coverage"])
        
        with tab1:
            heatmap_fig = self.create_similarity_heatmap(alignment_result)
            st.plotly_chart(heatmap_fig, use_container_width=True)
        
        with tab2:
            dist_fig = self.create_similarity_distribution(alignment_result)
            st.plotly_chart(dist_fig, use_container_width=True)
        
        with tab3:
            network_fig = self.create_alignment_network(alignment_result)
            st.plotly_chart(network_fig, use_container_width=True)
        
        with tab4:
            coverage_fig = self.create_coverage_chart(alignment_result)
            st.plotly_chart(coverage_fig, use_container_width=True)
        
        # 最佳匹配表格
        st.header("🏆 Top Matches")
        matches_df = self.create_top_matches_table(alignment_result)
        if not matches_df.empty:
            st.dataframe(matches_df, use_container_width=True)
        else:
            st.info("No matches found")
        
        # 特征类型分布
        st.header("📊 Feature Type Distribution")
        feature_fig = self.create_feature_type_distribution(alignment_result)
        st.plotly_chart(feature_fig, use_container_width=True)


