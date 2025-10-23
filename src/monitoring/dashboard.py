import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path
import mlflow
import json

def load_model_metrics():
    """Load latest model metrics from MLflow."""
    try:
        client = mlflow.tracking.MlflowClient()
        experiments = client.search_experiments()
        
        if experiments:
            latest_run = client.search_runs(
                experiment_ids=[experiments[0].experiment_id],
                order_by=["start_time DESC"],
                max_results=1
            )
            
            if latest_run:
                metrics = latest_run[0].data.metrics
                return metrics
    except Exception as e:
        st.error(f"Error loading MLflow metrics: {e}")
    
    return {}

def load_prediction_data():
    """Load latest prediction results."""
    pred_dir = Path("data/predictions")
    if pred_dir.exists():
        pred_files = list(pred_dir.glob("*.parquet"))
        if pred_files:
            latest_file = max(pred_files, key=lambda x: x.stat().st_mtime)
            return pd.read_parquet(latest_file)
    return pd.DataFrame()

def create_model_performance_chart(metrics):
    """Create model performance visualization."""
    if not metrics:
        return go.Figure()
    
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('AUC Score', 'Precision', 'Recall', 'F1 Score'),
        specs=[[{"type": "indicator"}, {"type": "indicator"}],
               [{"type": "indicator"}, {"type": "indicator"}]]
    )
    
    # AUC
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.get('auc', 0),
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "AUC"},
        gauge={'axis': {'range': [None, 1]},
               'bar': {'color': "darkblue"},
               'steps': [{'range': [0, 0.5], 'color': "lightgray"},
                        {'range': [0.5, 0.8], 'color': "yellow"},
                        {'range': [0.8, 1], 'color': "green"}],
               'threshold': {'line': {'color': "red", 'width': 4},
                           'thickness': 0.75, 'value': 0.9}}
    ), row=1, col=1)
    
    # Precision
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.get('precision', 0),
        title={'text': "Precision"},
        gauge={'axis': {'range': [None, 1]},
               'bar': {'color': "darkgreen"}}
    ), row=1, col=2)
    
    # Recall
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.get('recall', 0),
        title={'text': "Recall"},
        gauge={'axis': {'range': [None, 1]},
               'bar': {'color': "darkorange"}}
    ), row=2, col=1)
    
    # F1 Score
    fig.add_trace(go.Indicator(
        mode="gauge+number",
        value=metrics.get('f1_score', 0),
        title={'text': "F1 Score"},
        gauge={'axis': {'range': [None, 1]},
               'bar': {'color': "darkred"}}
    ), row=2, col=2)
    
    fig.update_layout(height=600, title="Model Performance Metrics")
    return fig

def create_prediction_distribution(df):
    """Create prediction distribution chart."""
    if df.empty:
        return go.Figure()
    
    fig = px.histogram(
        df, x='fraud_prediction',
        title='Prediction Distribution',
        labels={'fraud_prediction': 'Prediction', 'count': 'Count'}
    )
    return fig

def create_fraud_probability_dist(df):
    """Create fraud probability distribution."""
    if df.empty or 'fraud_probability' not in df.columns:
        return go.Figure()
    
    fig = px.histogram(
        df, x='fraud_probability',
        title='Fraud Probability Distribution',
        nbins=50,
        labels={'fraud_probability': 'Fraud Probability', 'count': 'Count'}
    )
    return fig

def main():
    """Main dashboard function."""
    st.set_page_config(
        page_title="Fraud Detection Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("🔍 Fraud Detection Monitoring Dashboard")
    
    # Sidebar
    st.sidebar.header("Dashboard Controls")
    refresh_data = st.sidebar.button("Refresh Data")
    
    # Load data
    metrics = load_model_metrics()
    predictions_df = load_prediction_data()
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model AUC", f"{metrics.get('auc', 0):.3f}")
    
    with col2:
        st.metric("Precision", f"{metrics.get('precision', 0):.3f}")
    
    with col3:
        st.metric("Recall", f"{metrics.get('recall', 0):.3f}")
    
    with col4:
        st.metric("F1 Score", f"{metrics.get('f1_score', 0):.3f}")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.plotly_chart(
            create_model_performance_chart(metrics),
            use_container_width=True
        )
    
    with col2:
        st.plotly_chart(
            create_prediction_distribution(predictions_df),
            use_container_width=True
        )
    
    # Fraud probability distribution
    st.plotly_chart(
        create_fraud_probability_dist(predictions_df),
        use_container_width=True
    )
    
    # Recent predictions table
    if not predictions_df.empty:
        st.subheader("Recent Predictions")
        st.dataframe(
            predictions_df.head(100),
            use_container_width=True
        )
    
    # Model info
    st.subheader("Model Information")
    if metrics:
        st.json(metrics)
    else:
        st.info("No model metrics available. Run the training pipeline first.")

if __name__ == "__main__":
    main()