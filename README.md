# Seattle Customer Service Requests Dashboard

An interactive Streamlit dashboard for analyzing and visualizing Seattle's customer service requests data from 2024-2025.

## Features

### 📊 Analytics & Visualizations

- **Key Performance Indicators (KPIs)**
  - Total request count
  - Closed vs. open requests with percentages
  - Unique request types and departments

- **Time Series Analysis**
  - Requests trend over time
  - Configurable granularity: Daily, Weekly, or Monthly
  - Interactive hover details

- **Department Breakdown**
  - Top 10 departments by request volume
  - Horizontal bar chart with color gradient
  - Request counts and rankings

- **Status Distribution**
  - Pie chart showing status breakdown
  - Closed, Reported, Transferred, and other statuses
  - Percentage and count displays

- **Request Type Analysis**
  - Top 15 most common request types
  - Color-coded visualization
  - Sortable by frequency

### 🗺️ Interactive Maps

- **3D Heatmap**
  - Density visualization showing request concentrations
  - Interactive 3D view with adjustable pitch and bearing
  - Dark theme for better contrast

- **Choropleth by Community**
  - 3D column visualization by neighborhood
  - Color gradient from blue (low) to red (high)
  - Hover tooltips showing community name and request count
  - Top 10 communities table

### 🔍 Dynamic Filters

All visualizations update dynamically based on:
- **Date Range**: Select start and end dates
- **Departments**: Multi-select filter (SPD, SDOT, SPU, etc.)
- **Status**: Filter by request status
- **Request Types**: Choose specific types to analyze
- **Communities**: Filter by Seattle neighborhoods

## Data Source

- **Dataset**: Seattle Customer Service Requests (2024-2025)
- **Records**: ~581,000 requests
- **File**: `seattle_requests_2024_2025.json`
- **Original CSV**: `Customer_Service_Requests_20251104.csv` (2.2M records dating back to 2013)

### Data Fields

Each request includes:
- `lat`, `lon`: Geographic coordinates
- `type`: Request category (e.g., Abandoned Vehicle, Pothole)
- `department`: City department handling the request
- `date`: Request creation date
- `status`: Current status (Closed, Reported, etc.)
- `community`: Neighborhood/area name

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or navigate to the project directory**
   ```bash
   cd /path/to/customer_service_hackathon
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install packages individually:
   ```bash
   pip install streamlit pandas plotly pydeck numpy python-dateutil
   ```

3. **Verify data file exists**
   Make sure `seattle_requests_2024_2025.json` is in the project directory.

## Usage

### Running the Dashboard

Start the Streamlit app:
```bash
streamlit run dashboard.py
```

The dashboard will automatically open in your default web browser at `http://localhost:8501`.

### Alternative: Using the Original Visualization

The project also includes a standalone HTML visualization:
```bash
python serve.py
```

This will start a local server and open `index.html` with the 3D heatmap.

## Dashboard Navigation

1. **Sidebar Filters (Left)**
   - Adjust date range with date picker
   - Select departments, statuses, types, and communities
   - View filtered record count

2. **Main Dashboard (Center/Right)**
   - Scroll through KPI metrics at the top
   - Explore time series trends
   - Analyze department and status distributions
   - Review top request types
   - Interact with the map visualization

3. **Map Views**
   - Toggle between "3D Heatmap" and "Choropleth by Community"
   - Click and drag to pan
   - Scroll to zoom
   - Hover over choropleth columns for details

## Project Structure

```
customer_service_hackathon/
├── dashboard.py                              # Streamlit dashboard (new)
├── requirements.txt                          # Python dependencies (new)
├── README.md                                 # This file (new)
├── index.html                                 # Standalone Deck.gl map (GitHub Pages friendly)
├── prepare_data.py                           # Data preprocessing script
├── serve.py                                  # Local HTTP server
├── seattle_requests_2024_2025.json           # Processed data (581K records)
└── Customer_Service_Requests_20251104.csv    # Raw data (2.2M records)
```

## Deploying to GitHub Pages

1. **Commit the static assets**
   - Ensure `index.html` and `seattle_requests_2024_2025.json` live at the repo root (already configured).
   - Commit and push changes to your `main` branch.

2. **Enable Pages**
   - In GitHub, go to **Settings → Pages**.
   - Under *Build and deployment*, choose `Deploy from a branch`.
   - Select `main` and the `/ (root)` folder, then click **Save**.

3. **Visit the site**
   - After GitHub finishes the build (usually <1 minute), the heatmap is available at  
     `https://<username>.github.io/<repo-name>/`.
   - The Deck.gl view fetches the JSON relative to the page, so no extra configuration is required.

4. **Optional: Custom domain**
   - Add a `CNAME` file with your domain and update DNS per GitHub’s docs if you want vanity hosting.

Whenever you rerun `prepare_data.py`, commit both the refreshed JSON and any HTML tweaks so Pages serves the latest state.

## Data Preprocessing

To regenerate the JSON file from the CSV:
```bash
python prepare_data.py
```

This script:
- Loads the full CSV dataset (2.2M records)
- Filters to 2024-2025 data
- Removes records without valid GPS coordinates
- Outputs `seattle_requests_2024_2025.json`
- Prints statistics about the data

## Technology Stack

- **Streamlit**: Dashboard framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive charts and graphs
- **PyDeck**: 3D map visualizations (deck.gl integration)
- **NumPy**: Numerical operations
- **Python-dateutil**: Date parsing and manipulation

## Performance Notes

- Data is cached using `@st.cache_data` for fast reload
- Initial load may take 5-10 seconds for 581K records
- Subsequent interactions are near-instantaneous
- Filters update all visualizations dynamically

## Troubleshooting

### Dashboard won't start
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)

### Data file not found
- Verify `seattle_requests_2024_2025.json` exists in the project directory
- Run `python prepare_data.py` to regenerate from CSV

### Map not rendering
- PyDeck requires a stable internet connection for base maps
- Try switching between heatmap and choropleth views

### Slow performance
- Reduce the date range or apply more filters
- Close other browser tabs
- Ensure you have sufficient RAM (4GB+ recommended)

## Future Enhancements

- [ ] Add response time analysis (time from created to closed)
- [ ] Implement geofencing for custom area analysis
- [ ] Export filtered data to CSV
- [ ] Add forecast models for request trends
- [ ] Integration with real-time Seattle Open Data API
- [ ] Mobile-responsive design improvements

## Credits

**Data Source**: City of Seattle Open Data Portal

**Dashboard**: Built for the Customer Service Hackathon

**Technologies**: Streamlit, Plotly, PyDeck, Pandas

---

*Last updated: November 2025*
