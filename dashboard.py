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

# SeaBot (floating chatbot)
seabot_widget = """
<script>
(function() {
  const parentDoc = window.parent?.document;
  if (!parentDoc || parentDoc.getElementById('seabot-launcher')) {
    return;
  }

  const style = parentDoc.createElement('style');
  style.id = 'seabot-style';
  style.textContent = `
    :root {
      --seabot-primary: #1e75ff;
      --seabot-secondary: #4da6ff;
      --seabot-bg: rgba(7, 11, 22, 0.94);
    }
    #seabot-launcher {
      position: fixed;
      right: 28px;
      bottom: 28px;
      background: linear-gradient(135deg, var(--seabot-primary), var(--seabot-secondary));
      color: #fff;
      border: none;
      border-radius: 18px;
      padding: 14px 22px;
      min-width: 200px;
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 600;
      font-size: 15px;
      letter-spacing: 0.3px;
      box-shadow: 0 25px 50px rgba(0, 0, 0, 0.35);
      cursor: pointer;
      z-index: 9999;
      animation: seabotFloat 4s ease-in-out infinite;
    }
    #seabot-launcher .seabot-icon {
      font-size: 22px;
    }
    #seabot-launcher .seabot-label {
      display: flex;
      flex-direction: column;
      line-height: 1.1;
      text-align: left;
    }
    #seabot-panel {
      position: fixed;
      right: 40px;
      bottom: 110px;
      width: 380px;
      max-height: 72vh;
      background: var(--seabot-bg);
      border-radius: 22px;
      border: 1px solid rgba(255, 255, 255, 0.12);
      box-shadow: 0 35px 70px rgba(0, 0, 0, 0.6);
      display: flex;
      flex-direction: column;
      overflow: hidden;
      opacity: 0;
      transform: translateY(12px);
      pointer-events: none;
      transition: opacity 0.25s ease, transform 0.25s ease;
      z-index: 10000;
    }
    #seabot-panel.open {
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }
    #seabot-panel * {
      box-sizing: border-box;
    }
    .seabot-header {
      padding: 18px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .seabot-header h2 {
      margin: 0;
      color: #fff;
      font-size: 16px;
    }
    .seabot-header p {
      margin: 4px 0 0;
      font-size: 12px;
      color: #9cb0ff;
    }
    #seabot-close {
      background: transparent;
      border: none;
      color: #9cb0ff;
      font-size: 20px;
      cursor: pointer;
    }
    #seabot-messages {
      flex: 1;
      padding: 18px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .seabot-message {
      padding: 12px 14px;
      border-radius: 14px;
      font-size: 14px;
      line-height: 1.45;
      color: #f7f8ff;
      max-width: 90%;
    }
    .seabot-message.bot {
      align-self: flex-start;
      background: rgba(255, 255, 255, 0.08);
    }
    .seabot-message.user {
      align-self: flex-end;
      background: linear-gradient(135deg, var(--seabot-secondary), var(--seabot-primary));
    }
    .seabot-suggestions {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      padding: 0 18px 12px;
    }
    .seabot-suggestions button {
      flex: 1 1 45%;
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 999px;
      color: #fff;
      font-size: 12px;
      padding: 6px 10px;
      cursor: pointer;
    }
    #seabot-form {
      display: flex;
      gap: 10px;
      padding: 16px 18px 20px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
    }
    #seabot-input {
      flex: 1;
      border-radius: 14px;
      border: 1px solid rgba(255, 255, 255, 0.2);
      background: rgba(255, 255, 255, 0.05);
      color: #fff;
      padding: 10px 12px;
      font-size: 14px;
    }
    #seabot-send {
      background: var(--seabot-secondary);
      border: none;
      color: #fff;
      border-radius: 12px;
      padding: 0 18px;
      font-weight: 600;
      cursor: pointer;
    }
    @keyframes seabotFloat {
      0% { transform: translateY(0); }
      50% { transform: translateY(-6px); }
      100% { transform: translateY(0); }
    }
    @media (max-width: 640px) {
      #seabot-launcher {
        right: 16px;
        bottom: 16px;
        min-width: 170px;
      }
      #seabot-panel {
        right: 14px;
        left: 14px;
        width: auto;
        bottom: 90px;
        max-height: 65vh;
      }
    }
  `;
  parentDoc.head.appendChild(style);

  const root = parentDoc.createElement('div');
  root.id = 'seabot-root';
  root.innerHTML = `
    <button id="seabot-launcher" aria-haspopup="dialog" aria-expanded="false">
      <span class="seabot-icon">🤖</span>
      <span class="seabot-label">
        <strong>SeaBot</strong>
        <small>City Services Assistant</small>
      </span>
    </button>
    <section id="seabot-panel" role="dialog" aria-label="SeaBot assistant">
      <div class="seabot-header">
        <div>
          <h2>SeaBot</h2>
          <p>Need help with City services?</p>
        </div>
        <button id="seabot-close" aria-label="Close SeaBot">&times;</button>
      </div>
      <div id="seabot-messages" role="log" aria-live="polite"></div>
      <div class="seabot-suggestions">
        <button type="button" data-message="How do I report a pothole in Seattle?">Report pothole</button>
        <button type="button" data-message="Where do I submit graffiti cleanup?">Graffiti cleanup</button>
        <button type="button" data-message="How can I check the status of a city request?">Check status</button>
        <button type="button" data-message="What filters can I use on the heatmap?">Heatmap tips</button>
      </div>
      <form id="seabot-form">
        <input id="seabot-input" type="text" placeholder="Ask SeaBot anything about city services…" autocomplete="off">
        <button id="seabot-send" type="submit">Send</button>
      </form>
    </section>
  `;
  parentDoc.body.appendChild(root);

  const launcher = parentDoc.getElementById('seabot-launcher');
  const panel = parentDoc.getElementById('seabot-panel');
  const closeBtn = parentDoc.getElementById('seabot-close');
  const form = parentDoc.getElementById('seabot-form');
  const input = parentDoc.getElementById('seabot-input');
  const messages = parentDoc.getElementById('seabot-messages');
  const suggestionButtons = panel.querySelectorAll('.seabot-suggestions button');
  let greeted = false;

  const resourceGuides = [
    {
      keywords: ['pothole', 'street', 'road', 'asphalt'],
      response: 'For potholes or street damage, submit a Find It, Fix It request (https://www.seattle.gov/customer-service-bureau/find-it-fix-it-mobile-app). Share cross streets or the block you spotted in the dashboard so SDOT crews can route faster.'
    },
    {
      keywords: ['graffiti', 'tag', 'paint'],
      response: 'Graffiti cleanup reports go to Seattle Public Utilities at https://my.seattle.gov/services/graffiti-report or call 206-684-7587 for private property assistance.'
    },
    {
      keywords: ['trash', 'garbage', 'missed', 'recycling', 'compost'],
      response: 'Missed garbage, recycling, or compost pickups can be rescheduled at https://myutilities.seattle.gov or by calling 206-684-3000. Reference the neighborhood concentration you see on the map to help routing.'
    },
    {
      keywords: ['light', 'streetlight', 'lamp'],
      response: 'Seattle City Light handles streetlight outages. File a report at https://citylight.seattle.gov/outages/report-streetlight-issue and drop a pin that matches the coordinates you reviewed.'
    },
    {
      keywords: ['dump', 'illegal dumping', 'debris', 'tires'],
      response: 'Report illegal dumping through Seattle Public Utilities: https://www.seattle.gov/utilities/protecting-our-environment/report-a-problem. Photos and nearby intersections from the dashboard help inspectors.'
    }
  ];

  function addMessage(text, sender = 'bot') {
    const bubble = parentDoc.createElement('div');
    bubble.className = `seabot-message ${sender}`;
    bubble.textContent = text;
    messages.appendChild(bubble);
    messages.scrollTop = messages.scrollHeight;
  }

  function greetIfNeeded() {
    if (greeted) return;
    greeted = true;
    addMessage("Hi there! I'm SeaBot. I can point you to City of Seattle tools, request forms, and tips for using this dashboard.", 'bot');
    addMessage('Ask me how to submit a service request or tap one of the quick suggestions below.', 'bot');
  }

  function togglePanel(forceOpen = null) {
    const open = forceOpen !== null ? forceOpen : !panel.classList.contains('open');
    panel.classList.toggle('open', open);
    launcher.setAttribute('aria-expanded', open ? 'true' : 'false');
    if (open) {
      greetIfNeeded();
      input.focus();
    }
  }

  function getBotResponse(message) {
    const normalized = message.toLowerCase();
    const match = resourceGuides.find(guide =>
      guide.keywords.some(keyword => normalized.includes(keyword))
    );
    if (match) {
      return match.response;
    }
    if (normalized.includes('status') || normalized.includes('track')) {
      return 'Track existing service requests in the Seattle Customer Service Portal (https://srhub.seattle.gov) or call the Service Bureau at 206-684-2489.';
    }
    if (normalized.includes('filter') || normalized.includes('map') || normalized.includes('heatmap')) {
      return 'Use the dashboard filters (date, department, status, type, neighborhood) to narrow the dataset. The embedded heatmap updates automatically so you can zoom to precise hotspots before submitting a request.';
    }
    if (normalized.includes('submit') || normalized.includes('request') || normalized.includes('help')) {
      return 'Identify the request type from the charts, then open the Find It, Fix It portal or call 206-684-2489. Include the cross streets you discovered in this dashboard for faster triage.';
    }
    if (normalized.includes('data') || normalized.includes('download') || normalized.includes('csv')) {
      return 'Regenerate the dataset locally with `python3 prepare_data.py` and download `seattle_requests_2024_2025.json` from your Streamlit server if you need raw data.';
    }
    return 'SeaBot can help with potholes, graffiti, trash, lighting, illegal dumping, status tracking, and dashboard tips. Try asking something more specific about the service you need.';
  }

  function handleUserMessage(message) {
    const trimmed = message.trim();
    if (!trimmed) return;
    addMessage(trimmed, 'user');
    input.value = '';
    setTimeout(() => {
      addMessage(getBotResponse(trimmed), 'bot');
    }, 220);
  }

  launcher.addEventListener('click', () => togglePanel());
  closeBtn.addEventListener('click', () => togglePanel(false));

  form.addEventListener('submit', event => {
    event.preventDefault();
    handleUserMessage(input.value);
  });

  suggestionButtons.forEach(button => {
    button.addEventListener('click', () => {
      togglePanel(true);
      handleUserMessage(button.dataset.message || button.textContent);
    });
  });
})();
</script>
"""

components.html(seabot_widget, height=0, width=0, scrolling=False)
