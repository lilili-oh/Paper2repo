"""
相似度可视化器 - 负责相似度分析的可视化展示
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns

from ..models.alignment_model import AlignmentResult, AlignmentMatch
from config import settings

class SimilarityVisualizer:
    """相似度可视化器类"""
    
    def __init__(self):
        """初始化相似度可视化器"""
        self.color_map = settings.similarity_color_map
    
    def create_similarity_matrix(self, alignment_result: AlignmentResult, max_features: int = 20) -> go.Figure:
        """创建相似度矩阵图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 准备数据
        matches = alignment_result.matches[:max_features]
        
        # 创建相似度矩阵
        similarity_matrix = np.zeros((len(matches), len(matches)))
        
        for i, match1 in enumerate(matches):
            for j, match2 in enumerate(matches):
                if i == j:
                    similarity_matrix[i][j] = match1.similarity_score.score
                else:
                    # 计算特征之间的相似度（简化实现）
                    similarity_matrix[i][j] = abs(match1.similarity_score.score - match2.similarity_score.score)
        
        # 创建热力图
        fig = go.Figure(data=go.Heatmap(
            z=similarity_matrix,
            colorscale=self.color_map,
            showscale=True,
            colorbar=dict(title="Similarity")
        ))
        
        fig.update_layout(
            title="Feature Similarity Matrix",
            xaxis_title="Features",
            yaxis_title="Features",
            width=600,
            height=600
        )
        
        return fig
    
    def create_similarity_trend(self, alignment_result: AlignmentResult) -> go.Figure:
        """创建相似度趋势图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 准备数据
        scores = [match.similarity_score.score for match in alignment_result.matches]
        indices = list(range(len(scores)))
        
        # 创建趋势图
        fig = go.Figure()
        
        # 添加原始数据点
        fig.add_trace(go.Scatter(
            x=indices,
            y=scores,
            mode='markers',
            name='Individual Scores',
            marker=dict(size=8, color='lightblue')
        ))
        
        # 添加移动平均线
        if len(scores) > 5:
            window_size = min(5, len(scores) // 3)
            moving_avg = pd.Series(scores).rolling(window=window_size).mean()
            
            fig.add_trace(go.Scatter(
                x=indices,
                y=moving_avg,
                mode='lines',
                name=f'Moving Average (window={window_size})',
                line=dict(color='red', width=2)
            ))
        
        # 添加平均线
        mean_score = np.mean(scores)
        fig.add_hline(
            y=mean_score,
            line_dash="dash",
            line_color="green",
            annotation_text=f"Mean: {mean_score:.3f}"
        )
        
        fig.update_layout(
            title="Similarity Score Trend",
            xaxis_title="Match Index",
            yaxis_title="Similarity Score",
            width=800,
            height=400
        )
        
        return fig
    
    def create_similarity_clusters(self, alignment_result: AlignmentResult, n_clusters: int = 3) -> go.Figure:
        """创建相似度聚类图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 准备数据
        scores = [match.similarity_score.score for match in alignment_result.matches]
        
        if len(scores) < n_clusters:
            return self._create_empty_plot("Not enough data for clustering")
        
        # 使用K-means聚类
        from sklearn.cluster import KMeans
        
        # 重塑数据
        X = np.array(scores).reshape(-1, 1)
        
        # 执行聚类
        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(X)
        
        # 创建散点图
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set1[:n_clusters]
        
        for i in range(n_clusters):
            cluster_mask = cluster_labels == i
            cluster_scores = np.array(scores)[cluster_mask]
            cluster_indices = np.where(cluster_mask)[0]
            
            fig.add_trace(go.Scatter(
                x=cluster_indices,
                y=cluster_scores,
                mode='markers',
                name=f'Cluster {i+1}',
                marker=dict(size=10, color=colors[i])
            ))
        
        # 添加聚类中心
        centers = kmeans.cluster_centers_.flatten()
        fig.add_trace(go.Scatter(
            x=list(range(len(centers))),
            y=centers,
            mode='markers',
            name='Cluster Centers',
            marker=dict(size=15, color='black', symbol='x')
        ))
        
        fig.update_layout(
            title=f"Similarity Score Clusters (k={n_clusters})",
            xaxis_title="Match Index",
            yaxis_title="Similarity Score",
            width=800,
            height=500
        )
        
        return fig
    
    def create_similarity_boxplot(self, alignment_result: AlignmentResult) -> go.Figure:
        """创建相似度箱线图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 准备数据
        scores = [match.similarity_score.score for match in alignment_result.matches]
        
        # 创建箱线图
        fig = go.Figure(data=go.Box(
            y=scores,
            name="Similarity Scores",
            boxpoints='outliers',
            jitter=0.3,
            pointpos=-1.8
        ))
        
        # 添加统计信息
        mean_score = np.mean(scores)
        median_score = np.median(scores)
        std_score = np.std(scores)
        
        fig.add_annotation(
            text=f"Mean: {mean_score:.3f}<br>Median: {median_score:.3f}<br>Std: {std_score:.3f}",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        )
        
        fig.update_layout(
            title="Similarity Score Distribution (Box Plot)",
            yaxis_title="Similarity Score",
            width=600,
            height=500
        )
        
        return fig
    
    def create_similarity_histogram(self, alignment_result: AlignmentResult, bins: int = 20) -> go.Figure:
        """创建相似度直方图"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 准备数据
        scores = [match.similarity_score.score for match in alignment_result.matches]
        
        # 创建直方图
        fig = go.Figure(data=[
            go.Histogram(
                x=scores,
                nbinsx=bins,
                marker_color='lightblue',
                opacity=0.7,
                name="Similarity Scores"
            )
        ])
        
        # 添加统计线
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
        
        # 添加正态分布拟合
        from scipy import stats
        mu, sigma = stats.norm.fit(scores)
        x = np.linspace(min(scores), max(scores), 100)
        y = stats.norm.pdf(x, mu, sigma) * len(scores) * (max(scores) - min(scores)) / bins
        
        fig.add_trace(go.Scatter(
            x=x,
            y=y,
            mode='lines',
            name='Normal Fit',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="Similarity Score Histogram with Normal Fit",
            xaxis_title="Similarity Score",
            yaxis_title="Frequency",
            width=800,
            height=500
        )
        
        return fig
    
    def create_similarity_correlation(self, alignment_result: AlignmentResult) -> go.Figure:
        """创建相似度相关性分析"""
        if not alignment_result.matches:
            return self._create_empty_plot("No matches found")
        
        # 准备数据
        scores = [match.similarity_score.score for match in alignment_result.matches]
        confidences = [match.similarity_score.confidence for match in alignment_result.matches]
        
        # 创建散点图
        fig = go.Figure(data=go.Scatter(
            x=scores,
            y=confidences,
            mode='markers',
            marker=dict(
                size=10,
                color=scores,
                colorscale=self.color_map,
                showscale=True,
                colorbar=dict(title="Similarity Score")
            ),
            text=[f"Match {i+1}" for i in range(len(scores))],
            hovertemplate="<b>%{text}</b><br>Similarity: %{x:.3f}<br>Confidence: %{y:.3f}<extra></extra>"
        ))
        
        # 添加趋势线
        if len(scores) > 1:
            z = np.polyfit(scores, confidences, 1)
            p = np.poly1d(z)
            x_trend = np.linspace(min(scores), max(scores), 100)
            y_trend = p(x_trend)
            
            fig.add_trace(go.Scatter(
                x=x_trend,
                y=y_trend,
                mode='lines',
                name='Trend Line',
                line=dict(color='red', width=2)
            ))
        
        # 计算相关系数
        correlation = np.corrcoef(scores, confidences)[0, 1]
        
        fig.add_annotation(
            text=f"Correlation: {correlation:.3f}",
            xref="paper", yref="paper",
            x=0.02, y=0.98,
            showarrow=False,
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="black",
            borderwidth=1
        )
        
        fig.update_layout(
            title="Similarity vs Confidence Correlation",
            xaxis_title="Similarity Score",
            yaxis_title="Confidence Score",
            width=800,
            height=600
        )
        
        return fig
    
    def create_similarity_statistics(self, alignment_result: AlignmentResult) -> Dict[str, Any]:
        """创建相似度统计信息"""
        if not alignment_result.matches:
            return {"error": "No matches found"}
        
        scores = [match.similarity_score.score for match in alignment_result.matches]
        confidences = [match.similarity_score.confidence for match in alignment_result.matches]
        
        stats = {
            "count": len(scores),
            "mean": float(np.mean(scores)),
            "median": float(np.median(scores)),
            "std": float(np.std(scores)),
            "min": float(np.min(scores)),
            "max": float(np.max(scores)),
            "q25": float(np.percentile(scores, 25)),
            "q75": float(np.percentile(scores, 75)),
            "confidence_mean": float(np.mean(confidences)),
            "confidence_std": float(np.std(confidences)),
            "correlation": float(np.corrcoef(scores, confidences)[0, 1]) if len(scores) > 1 else 0.0
        }
        
        return stats
    
    def create_interactive_similarity_dashboard(self, alignment_result: AlignmentResult) -> None:
        """创建交互式相似度仪表板"""
        st.set_page_config(
            page_title="Similarity Analysis Dashboard",
            page_icon="📊",
            layout="wide"
        )
        
        st.title("📊 Similarity Analysis Dashboard")
        
        # 统计信息
        st.header("📈 Statistics")
        stats = self.create_similarity_statistics(alignment_result)
        
        if "error" in stats:
            st.error(stats["error"])
            return
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Count", stats["count"])
        with col2:
            st.metric("Mean", f"{stats['mean']:.3f}")
        with col3:
            st.metric("Std Dev", f"{stats['std']:.3f}")
        with col4:
            st.metric("Correlation", f"{stats['correlation']:.3f}")
        
        # 详细统计表格
        st.subheader("📋 Detailed Statistics")
        stats_df = pd.DataFrame([
            {"Metric": "Mean", "Value": f"{stats['mean']:.3f}"},
            {"Metric": "Median", "Value": f"{stats['median']:.3f}"},
            {"Metric": "Standard Deviation", "Value": f"{stats['std']:.3f}"},
            {"Metric": "Minimum", "Value": f"{stats['min']:.3f}"},
            {"Metric": "Maximum", "Value": f"{stats['max']:.3f}"},
            {"Metric": "Q25", "Value": f"{stats['q25']:.3f}"},
            {"Metric": "Q75", "Value": f"{stats['q75']:.3f}"},
            {"Metric": "Confidence Mean", "Value": f"{stats['confidence_mean']:.3f}"},
            {"Metric": "Confidence Std", "Value": f"{stats['confidence_std']:.3f}"}
        ])
        st.dataframe(stats_df, use_container_width=True)
        
        # 可视化图表
        st.header("📊 Visualizations")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "Distribution", "Trend", "Clusters", "Box Plot", "Correlation"
        ])
        
        with tab1:
            hist_fig = self.create_similarity_histogram(alignment_result)
            st.plotly_chart(hist_fig, use_container_width=True)
        
        with tab2:
            trend_fig = self.create_similarity_trend(alignment_result)
            st.plotly_chart(trend_fig, use_container_width=True)
        
        with tab3:
            n_clusters = st.slider("Number of Clusters", 2, 5, 3)
            cluster_fig = self.create_similarity_clusters(alignment_result, n_clusters)
            st.plotly_chart(cluster_fig, use_container_width=True)
        
        with tab4:
            box_fig = self.create_similarity_boxplot(alignment_result)
            st.plotly_chart(box_fig, use_container_width=True)
        
        with tab5:
            corr_fig = self.create_similarity_correlation(alignment_result)
            st.plotly_chart(corr_fig, use_container_width=True)
    
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


