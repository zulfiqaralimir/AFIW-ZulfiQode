"""
Visualizes key metrics for dashboards.
"""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Optional


def render_integrity_trend(dataframe: pd.DataFrame):
    """
    Render Temporal Integrity Trend (CII & TIT) line chart.
    
    Args:
        dataframe: DataFrame with 'date', 'CII', 'TIT' columns
        
    Returns:
        Plotly figure
    """
    fig = px.line(
        dataframe,
        x="date",
        y=["CII", "TIT"],
        title="Temporal Integrity Trend (CII & TIT)",
        markers=True,
        template="plotly_dark"
    )
    fig.update_traces(line=dict(width=3))
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Score",
        height=400
    )
    return fig


def render_ethics_risk_heatmap(dataframe: pd.DataFrame):
    """
    Render Ethics–Risk Matrix heatmap.
    
    Args:
        dataframe: DataFrame with 'EthicsScore', 'RiskScore' columns
        
    Returns:
        Plotly figure
    """
    fig = px.density_heatmap(
        dataframe,
        x="EthicsScore",
        y="RiskScore",
        color_continuous_scale="RdYlGn_r",
        title="Ethics–Risk Matrix"
    )
    fig.update_layout(height=400)
    return fig


def render_metrics_gauge(value: float, title: str, min_val: float = 0, max_val: float = 100):
    """
    Render a gauge chart for a single metric.
    
    Args:
        value: Current value
        title: Chart title
        min_val: Minimum value
        max_val: Maximum value
        
    Returns:
        Plotly figure
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_val, max_val * 0.5], 'color': "lightgray"},
                {'range': [max_val * 0.5, max_val * 0.75], 'color': "gray"},
                {'range': [max_val * 0.75, max_val], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': max_val * 0.9
            }
        }
    ))
    fig.update_layout(height=300)
    return fig


def render_comparison_bar(dataframe: pd.DataFrame, x_col: str, y_col: str, title: str):
    """
    Render a comparison bar chart.
    
    Args:
        dataframe: DataFrame with data
        x_col: Column name for x-axis
        y_col: Column name for y-axis
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = px.bar(
        dataframe,
        x=x_col,
        y=y_col,
        title=title,
        color=y_col,
        color_continuous_scale="RdYlGn",
        template="plotly_dark"
    )
    fig.update_layout(height=400)
    return fig


def render_timeline(dataframe: pd.DataFrame, date_col: str, value_cols: list, title: str):
    """
    Render a timeline chart with multiple values.
    
    Args:
        dataframe: DataFrame with date and value columns
        date_col: Column name for dates
        value_cols: List of column names for values
        title: Chart title
        
    Returns:
        Plotly figure
    """
    fig = px.line(
        dataframe,
        x=date_col,
        y=value_cols,
        title=title,
        markers=True,
        template="plotly_dark"
    )
    fig.update_traces(line=dict(width=2))
    fig.update_layout(height=400)
    return fig

