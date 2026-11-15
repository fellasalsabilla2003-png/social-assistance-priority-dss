# Social Assistance Prioritization Decision Support System

A decision support system that ranks 38 regencies/cities in East Java by
social assistance priority, using K-Means clustering and TOPSIS, with an
interactive Streamlit dashboard.

**Live demo:** [Open the dashboard](https://social-assistance-priority-dss-bvhdcpmfapd3sedzam9eys.streamlit.app/)

## Problem

Social assistance should reach the regions that need it most. This project
helps prioritize regions using official socio-economic indicators.

## Data

- Source: Statistics Indonesia (BPS), 2019-2025
- 8 indicators: poverty rate, Human Development Index, unemployment rate,
  economic growth, and others
- 38 regencies/cities in East Java

## Method

1. Data cleaning and exploratory data analysis (EDA)
2. K-Means clustering on 7 standardized indicators (k = 2, silhouette ≈ 0.397)
3. PCA for cluster visualization
4. TOPSIS priority score using 4 equally weighted criteria
5. Priority categories (quartiles) and dominant indicators per region
6. Rule-based recommendations with IQR-based alerts
7. Streamlit dashboard

## Results

- Highest priority: Bangkalan (TOPSIS score 0.759)
- Lowest priority: Batu City (score 0.249)
- 8-page interactive dashboard

## How to run

pip install -r requirements.txt
streamlit run dashboard/app.py

## Limitations

- Equal criteria weights were not validated with a sensitivity analysis
- Clustering found only two groups

## Tech stack

Python, Pandas, NumPy, Scikit-learn, SciPy, Plotly, Streamlit
