"""
Plotly Visualizations for Lawyer-AI Dashboard
Comprehensive data visualization using Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, Any, Optional, List
import json


def create_cii_gauge(cii_score: float, company_name: str = "") -> go.Figure:
    """
    Create a gauge chart for CII Score.
    
    Args:
        cii_score: CII Score value (0-100)
        company_name: Company name for title
        
    Returns:
        Plotly figure
    """
    # Convert string score to float if needed
    if isinstance(cii_score, str):
        try:
            cii_score = float(cii_score.split('/')[0])
        except:
            cii_score = 0.0
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=cii_score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"CII Score{(' - ' + company_name) if company_name else ''}"},
        delta={'reference': 50},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 40], 'color': "lightgray"},
                {'range': [40, 70], 'color': "yellow"},
                {'range': [70, 100], 'color': "lightgreen"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        paper_bgcolor="white",
        font={'color': "darkblue", 'family': "Arial"}
    )
    return fig


def create_risk_distribution(risk_level: str, risk_data: Optional[Dict] = None) -> go.Figure:
    """
    Create a risk level distribution chart.
    
    Args:
        risk_level: Risk level (Low/Medium/High)
        risk_data: Optional risk data dictionary
        
    Returns:
        Plotly figure
    """
    # Risk level mapping
    risk_map = {"Low": 1, "Medium": 2, "High": 3, "low": 1, "medium": 2, "high": 3}
    risk_value = risk_map.get(risk_level, 2)
    
    # Create data
    risk_levels = ["Low", "Medium", "High"]
    values = [0, 0, 0]
    values[risk_value - 1] = 100
    
    colors = ["green", "yellow", "red"]
    
    fig = go.Figure(data=[
        go.Bar(
            x=risk_levels,
            y=values,
            marker_color=colors,
            text=[f"{v}%" if v > 0 else "" for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Risk Level Distribution",
        xaxis_title="Risk Level",
        yaxis_title="Score",
        height=300,
        showlegend=False,
        paper_bgcolor="white"
    )
    
    return fig


def create_technical_indicators(rsi: str, ma200: str, trend: str) -> go.Figure:
    """
    Create a technical indicators dashboard.
    
    Args:
        rsi: RSI value
        ma200: MA-200 value
        trend: Trend value (bullish/bearish/neutral)
        
    Returns:
        Plotly figure with subplots
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("RSI Indicator", "MA-200", "Trend Analysis", "Combined View"),
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # RSI Gauge
    rsi_value = 50  # Default
    if isinstance(rsi, str) and rsi.replace('.', '').isdigit():
        rsi_value = float(rsi)
    elif isinstance(rsi, (int, float)):
        rsi_value = float(rsi)
    
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=rsi_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "RSI"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 30], 'color': "lightgreen"},
                    {'range': [30, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70
                }
            }
        ),
        row=1, col=1
    )
    
    # MA-200 Indicator
    ma_value = 0
    if isinstance(ma200, str) and ma200.replace('.', '').replace('-', '').isdigit():
        ma_value = float(ma200)
    elif isinstance(ma200, (int, float)):
        ma_value = float(ma200)
    
    fig.add_trace(
        go.Indicator(
            mode="number",
            value=ma_value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "MA-200"}
        ),
        row=1, col=2
    )
    
    # Trend Bar Chart
    trend_map = {"bullish": 1, "bearish": -1, "neutral": 0, "Bullish": 1, "Bearish": -1, "Neutral": 0}
    trend_value = trend_map.get(trend, 0)
    trend_labels = ["Bearish", "Neutral", "Bullish"]
    trend_values = [0, 0, 0]
    trend_values[trend_value + 1] = 100
    
    fig.add_trace(
        go.Bar(
            x=trend_labels,
            y=trend_values,
            marker_color=["red", "yellow", "green"],
            text=[f"{v}%" if v > 0 else "" for v in trend_values],
            textposition='auto',
        ),
        row=2, col=1
    )
    
    # Combined View (scatter)
    fig.add_trace(
        go.Scatter(
            x=["RSI", "MA-200", "Trend"],
            y=[rsi_value, ma_value if ma_value > 0 else 50, trend_value * 50 + 50],
            mode='lines+markers',
            name="Technical Indicators",
            line=dict(color='blue', width=2),
            marker=dict(size=10)
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=600,
        showlegend=False,
        paper_bgcolor="white",
        title_text="Technical Indicators Dashboard"
    )
    
    return fig


def create_ethics_risk_matrix(ethical_flag: str, risk_level: str) -> go.Figure:
    """
    Create an ethics-risk matrix heatmap.
    
    Args:
        ethical_flag: Ethical flag (Ethical/Unethical/Questionable)
        risk_level: Risk level (Low/Medium/High)
        
    Returns:
        Plotly figure
    """
    # Map values
    ethics_map = {"Ethical": 3, "Unethical": 1, "Questionable": 2, 
                  "ethical": 3, "unethical": 1, "questionable": 2}
    risk_map = {"Low": 1, "Medium": 2, "High": 3,
                "low": 1, "medium": 2, "high": 3}
    
    ethics_value = ethics_map.get(ethical_flag, 2)
    risk_value = risk_map.get(risk_level, 2)
    
    # Create matrix data
    ethics_levels = ["Unethical", "Questionable", "Ethical"]
    risk_levels = ["Low", "Medium", "High"]
    
    matrix_data = [[0 for _ in range(3)] for _ in range(3)]
    matrix_data[ethics_value - 1][risk_value - 1] = 100
    
    fig = go.Figure(data=go.Heatmap(
        z=matrix_data,
        x=risk_levels,
        y=ethics_levels,
        colorscale='RdYlGn',
        text=[[f"{v}%" if v > 0 else "" for v in row] for row in matrix_data],
        texttemplate="%{text}",
        textfont={"size": 12}
    ))
    
    fig.update_layout(
        title="Ethics-Risk Matrix",
        xaxis_title="Risk Level",
        yaxis_title="Ethical Flag",
        height=400,
        paper_bgcolor="white"
    )
    
    return fig


def create_metrics_dashboard(result: Dict[str, Any], company_name: str = "") -> go.Figure:
    """
    Create a comprehensive metrics dashboard.
    
    Args:
        result: Analysis result dictionary
        company_name: Company name for title
        
    Returns:
        Plotly figure with subplots
    """
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=("CII Score", "Risk Distribution", "Ethics-Risk Matrix", "Technical Overview"),
        specs=[[{"type": "indicator"}, {"type": "bar"}],
               [{"type": "heatmap"}, {"type": "scatter"}]]
    )
    
    # Extract values
    cii_score = result.get("CII_Score", 0)
    if isinstance(cii_score, str):
        try:
            cii_score = float(cii_score.split('/')[0])
        except:
            cii_score = 0.0
    
    risk_level = result.get("Risk_Level", "Medium")
    ethical_flag = result.get("Ethical_Flag", "Questionable")
    rsi = result.get("RSI", "50")
    ma200 = result.get("MA200", "0")
    trend = result.get("Trend", "neutral")
    
    # CII Score Gauge
    fig.add_trace(
        go.Indicator(
            mode="gauge+number",
            value=cii_score,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "CII Score"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 40], 'color': "lightgray"},
                    {'range': [40, 70], 'color': "yellow"},
                    {'range': [70, 100], 'color': "lightgreen"}
                ]
            }
        ),
        row=1, col=1
    )
    
    # Risk Distribution
    risk_map = {"Low": 1, "Medium": 2, "High": 3, "low": 1, "medium": 2, "high": 3}
    risk_value = risk_map.get(risk_level, 2)
    risk_levels = ["Low", "Medium", "High"]
    risk_values = [0, 0, 0]
    risk_values[risk_value - 1] = 100
    
    fig.add_trace(
        go.Bar(
            x=risk_levels,
            y=risk_values,
            marker_color=["green", "yellow", "red"],
            text=[f"{v}%" if v > 0 else "" for v in risk_values],
            textposition='auto',
        ),
        row=1, col=2
    )
    
    # Ethics-Risk Matrix
    ethics_map = {"Ethical": 3, "Unethical": 1, "Questionable": 2,
                  "ethical": 3, "unethical": 1, "questionable": 2}
    ethics_value = ethics_map.get(ethical_flag, 2)
    risk_value = risk_map.get(risk_level, 2)
    
    matrix_data = [[0 for _ in range(3)] for _ in range(3)]
    matrix_data[ethics_value - 1][risk_value - 1] = 100
    
    fig.add_trace(
        go.Heatmap(
            z=matrix_data,
            x=["Low", "Medium", "High"],
            y=["Unethical", "Questionable", "Ethical"],
            colorscale='RdYlGn',
            showscale=False
        ),
        row=2, col=1
    )
    
    # Technical Overview
    rsi_value = 50
    if isinstance(rsi, str) and rsi.replace('.', '').isdigit():
        rsi_value = float(rsi)
    elif isinstance(rsi, (int, float)):
        rsi_value = float(rsi)
    
    ma_value = 0
    if isinstance(ma200, str) and ma200.replace('.', '').replace('-', '').isdigit():
        ma_value = float(ma200)
    elif isinstance(ma200, (int, float)):
        ma_value = float(ma200)
    
    trend_map = {"bullish": 1, "bearish": -1, "neutral": 0,
                 "Bullish": 1, "Bearish": -1, "Neutral": 0}
    trend_value = trend_map.get(trend, 0)
    
    fig.add_trace(
        go.Scatter(
            x=["RSI", "MA-200", "Trend"],
            y=[rsi_value, ma_value if ma_value > 0 else 50, trend_value * 50 + 50],
            mode='lines+markers',
            name="Technical",
            line=dict(color='blue', width=2),
            marker=dict(size=10)
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        height=800,
        showlegend=False,
        paper_bgcolor="white",
        title_text=f"Comprehensive Metrics Dashboard{(' - ' + company_name) if company_name else ''}"
    )
    
    return fig


def create_summary_chart(result: Dict[str, Any]) -> go.Figure:
    """
    Create a summary bar chart of all key metrics.
    
    Args:
        result: Analysis result dictionary
        
    Returns:
        Plotly figure
    """
    # Extract and normalize values
    metrics = []
    values = []
    colors = []
    
    # CII Score
    cii_score = result.get("CII_Score", 0)
    if isinstance(cii_score, str):
        try:
            cii_score = float(cii_score.split('/')[0])
        except:
            cii_score = 0.0
    metrics.append("CII Score")
    values.append(cii_score)
    colors.append("blue" if cii_score > 70 else "orange" if cii_score > 40 else "red")
    
    # RSI
    rsi = result.get("RSI", "50")
    rsi_value = 50
    if isinstance(rsi, str) and rsi.replace('.', '').isdigit():
        rsi_value = float(rsi)
    elif isinstance(rsi, (int, float)):
        rsi_value = float(rsi)
    metrics.append("RSI")
    values.append(rsi_value)
    colors.append("green" if 30 < rsi_value < 70 else "red")
    
    # Risk Level (mapped to 0-100)
    risk_level = result.get("Risk_Level", "Medium")
    risk_map = {"Low": 30, "Medium": 60, "High": 90, "low": 30, "medium": 60, "high": 90}
    risk_value = risk_map.get(risk_level, 60)
    metrics.append("Risk Level")
    values.append(risk_value)
    colors.append("green" if risk_value < 40 else "orange" if risk_value < 70 else "red")
    
    # Ethics (mapped to 0-100)
    ethical_flag = result.get("Ethical_Flag", "Questionable")
    ethics_map = {"Ethical": 90, "Unethical": 10, "Questionable": 50,
                  "ethical": 90, "unethical": 10, "questionable": 50}
    ethics_value = ethics_map.get(ethical_flag, 50)
    metrics.append("Ethics")
    values.append(ethics_value)
    colors.append("green" if ethics_value > 70 else "orange" if ethics_value > 40 else "red")
    
    fig = go.Figure(data=[
        go.Bar(
            x=metrics,
            y=values,
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Key Metrics Summary",
        xaxis_title="Metrics",
        yaxis_title="Score (0-100)",
        height=400,
        paper_bgcolor="white",
        showlegend=False
    )
    
    return fig

