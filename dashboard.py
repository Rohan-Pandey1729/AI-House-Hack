import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Seattle Customer Service Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .metric-card {
        background-color: #1e1e1e;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .stMetric {
        background-color: #1e1e1e;
        padding: 15px;
        border-radius: 8px;
    }
    .stMetric label {
        color: #aaaaaa !important;
    }
    .stMetric [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    .stMetric [data-testid="stMetricDelta"] {
        color: #4da6ff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Title
st.title("🏙️ Seattle Customer Service Requests Dashboard")
st.markdown("**Interactive analytics for Seattle's customer service data (2024-2025)**")

# Data loading with caching
@st.cache_data
def load_data():
    """Load and prepare the customer service requests data."""
    try:
        with open('seattle_requests_2024_2025.json', 'r') as f:
            data = json.load(f)

        # Extract the data array from the JSON object
        df = pd.DataFrame(data['data'])

        # Convert date strings to datetime
        df['date'] = pd.to_datetime(df['date'])

        # Add derived columns
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        df['week'] = df['date'].dt.isocalendar().week

        # Clean up community names (handle None/null values)
        df['community'] = df['community'].fillna('Unknown')

        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# Load data
with st.spinner("Loading customer service requests data..."):
    df = load_data()

if df.empty:
    st.error("Failed to load data. Please ensure 'seattle_requests_2024_2025.json' exists.")
    st.stop()

st.success(f"✅ Loaded {len(df):,} customer service requests")

# Sidebar filters
st.sidebar.header("🔍 Filters")

# Date range filter
min_date = df['date'].min().date()
max_date = df['date'].max().date()

date_range = st.sidebar.date_input(
    "Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Convert date_range to proper format
if len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date = end_date = date_range[0]

# Department filter
departments = sorted(df['department'].unique().tolist())
selected_departments = st.sidebar.multiselect(
    "Departments",
    options=departments,
    default=departments
)

# Status filter
statuses = sorted(df['status'].unique().tolist())
selected_statuses = st.sidebar.multiselect(
    "Status",
    options=statuses,
    default=statuses
)

# Request type filter
request_types = sorted(df['type'].unique().tolist())
selected_types = st.sidebar.multiselect(
    "Request Types",
    options=request_types,
    default=request_types[:10] if len(request_types) > 10 else request_types,
    help="Select request types to include"
)

# Community filter
communities = sorted([c for c in df['community'].unique().tolist() if c != 'Unknown'])
selected_communities = st.sidebar.multiselect(
    "Communities/Neighborhoods",
    options=communities,
    default=communities,
    help="Filter by specific neighborhoods"
)

# Apply filters
filtered_df = df[
    (df['date'].dt.date >= start_date) &
    (df['date'].dt.date <= end_date) &
    (df['department'].isin(selected_departments)) &
    (df['status'].isin(selected_statuses)) &
    (df['type'].isin(selected_types)) &
    ((df['community'].isin(selected_communities)) | (df['community'] == 'Unknown'))
]

st.sidebar.markdown(f"**Filtered Records:** {len(filtered_df):,} / {len(df):,}")

# KPI Metrics
st.markdown("---")
st.subheader("📊 Key Metrics")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Total Requests",
        value=f"{len(filtered_df):,}"
    )

with col2:
    closed_count = len(filtered_df[filtered_df['status'].str.contains('Closed', case=False, na=False)])
    closed_pct = (closed_count / len(filtered_df) * 100) if len(filtered_df) > 0 else 0
    st.metric(
        label="Closed Requests",
        value=f"{closed_count:,}",
        delta=f"{closed_pct:.1f}%"
    )

with col3:
    open_count = len(filtered_df[~filtered_df['status'].str.contains('Closed', case=False, na=False)])
    st.metric(
        label="Open/Reported",
        value=f"{open_count:,}"
    )

with col4:
    unique_types = filtered_df['type'].nunique()
    st.metric(
        label="Request Types",
        value=f"{unique_types}"
    )

with col5:
    unique_depts = filtered_df['department'].nunique()
    st.metric(
        label="Departments",
        value=f"{unique_depts}"
    )

# Time Series Analysis
st.markdown("---")
st.subheader("📈 Requests Over Time")

# Time granularity selector
time_granularity = st.radio(
    "Time Granularity",
    options=["Daily", "Weekly", "Monthly"],
    horizontal=True,
    index=1
)

# Prepare time series data
if time_granularity == "Daily":
    time_series = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index(name='count')
    time_series.columns = ['date', 'count']
    time_series['date'] = pd.to_datetime(time_series['date'])
elif time_granularity == "Weekly":
    temp_df = filtered_df.copy()
    temp_df['year'] = temp_df['date'].dt.year
    temp_df['week'] = temp_df['date'].dt.isocalendar().week
    time_series = temp_df.groupby(['year', 'week']).size().reset_index(name='count')
    time_series['date'] = pd.to_datetime(time_series['year'].astype(str) + '-W' + time_series['week'].astype(str) + '-1', format='%Y-W%W-%w')
else:  # Monthly
    temp_df = filtered_df.copy()
    temp_df['year'] = temp_df['date'].dt.year
    temp_df['month'] = temp_df['date'].dt.month
    time_series = temp_df.groupby(['year', 'month']).size().reset_index(name='count')
    time_series['date'] = pd.to_datetime(time_series[['year', 'month']].assign(day=1))

# Create time series chart
fig_time = px.line(
    time_series,
    x='date',
    y='count',
    title=f'Customer Service Requests - {time_granularity} Trend',
    labels={'date': 'Date', 'count': 'Number of Requests'},
    template='plotly_white'
)

fig_time.update_traces(line_color='#1f77b4', line_width=2)
fig_time.update_layout(
    hovermode='x unified',
    height=400,
    showlegend=False
)

st.plotly_chart(fig_time, use_container_width=True)

# Department and Status Analysis
st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🏢 Requests by Department")

    dept_counts = filtered_df['department'].value_counts().reset_index()
    dept_counts.columns = ['department', 'count']
    dept_counts['percentage'] = (dept_counts['count'] / dept_counts['count'].sum() * 100).round(1)

    fig_dept = px.bar(
        dept_counts.head(10),
        x='count',
        y='department',
        orientation='h',
        title='Top 10 Departments by Request Volume',
        labels={'count': 'Number of Requests', 'department': 'Department'},
        template='plotly_white',
        color='count',
        color_continuous_scale='Blues'
    )

    fig_dept.update_layout(
        height=400,
        showlegend=False,
        yaxis={'categoryorder': 'total ascending'}
    )

    st.plotly_chart(fig_dept, use_container_width=True)

with col_right:
    st.subheader("📋 Status Distribution")

    status_counts = filtered_df['status'].value_counts().reset_index()
    status_counts.columns = ['status', 'count']

    fig_status = px.pie(
        status_counts,
        values='count',
        names='status',
        title='Request Status Breakdown',
        template='plotly_white',
        hole=0.4
    )

    fig_status.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Count: %{value:,}<br>Percentage: %{percent}<extra></extra>'
    )

    fig_status.update_layout(height=400)

    st.plotly_chart(fig_status, use_container_width=True)

# Request Type Analysis
st.markdown("---")
st.subheader("📝 Request Type Analysis")

type_counts = filtered_df['type'].value_counts().head(15).reset_index()
type_counts.columns = ['type', 'count']

fig_types = px.bar(
    type_counts,
    x='count',
    y='type',
    orientation='h',
    title='Top 15 Request Types',
    labels={'count': 'Number of Requests', 'type': 'Request Type'},
    template='plotly_white',
    color='count',
    color_continuous_scale='Viridis'
)

fig_types.update_layout(
    height=500,
    showlegend=False,
    yaxis={'categoryorder': 'total ascending'}
)

st.plotly_chart(fig_types, use_container_width=True)

# Map Visualization
st.markdown("---")
st.subheader("🗺️ Interactive Heatmap")
st.markdown("**3D density heatmap with interactive controls showing request concentrations across Seattle**")

# Load and embed the visualization.html with inline filtered data
with open('visualization.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

# Convert filtered dataframe to the format expected by visualization.html
map_data = filtered_df[['lat', 'lon', 'type', 'department', 'date', 'status', 'community']].copy()
map_data['date'] = map_data['date'].dt.strftime('%Y-%m-%d')

# Create the JSON structure with data and stats
json_structure = {
    "data": map_data.to_dict('records'),
    "stats": {
        "total_records": len(map_data),
        "date_range": {
            "start": map_data['date'].min(),
            "end": map_data['date'].max()
        },
        "top_request_types": filtered_df['type'].value_counts().head(10).to_dict(),
        "top_departments": filtered_df['department'].value_counts().head(5).to_dict()
    }
}

json_data = json.dumps(json_structure)

# Replace the fetch call with inline data
old_fetch = """fetch('seattle_requests_2024_2025.json')
      .then(response => response.json())
      .then(json => {"""

new_fetch = f"""Promise.resolve({json_data}).then(json => {{"""

html_content = html_content.replace(old_fetch, new_fetch)

components.html(html_content, height=800, scrolling=False)

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 20px;'>
    <p>Seattle Customer Service Requests Dashboard | Data: 2024-2025</p>
    <p>Built with Streamlit 🎈 | Visualizations by Plotly, Deck.gl & Mapbox</p>
    </div>
    """, unsafe_allow_html=True)
