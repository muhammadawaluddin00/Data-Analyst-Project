# 📊 Indodana BI Analyst Portfolio Project

A complete Business Intelligence portfolio project for the **Indodana BI Analyst** role, covering:
- Synthetic lending dataset (5,000 loans + 19,000 repayment records)
- 8 production-quality SQL analysis queries
- Interactive Streamlit dashboard (Indodana branded)
- Full interview prep documentation

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Generate synthetic data
python generate_data.py

# 3. Launch dashboard
streamlit run dashboard.py
```

## 📁 Project Structure

```
indodana_bi_project/
├── dashboard.py              # Streamlit BI dashboard
├── generate_data.py          # Synthetic data generator
├── requirements.txt          # Python dependencies
├── data/
│   ├── loan_applications.csv # 5,000 loan records (2022–2024)
│   └── repayments.csv        # ~19,000 repayment installments
├── sql/
│   └── analysis_queries.sql  # 8 SQL analysis queries
└── docs/
    └── PROJECT_DOCUMENTATION.md  # Full project + interview guide
```

## 📊 Dashboard Tabs

| Tab | Content |
|-----|---------|
| Portfolio Trend | Monthly disbursement, approval rates by product & channel |
| Geographic | Province-level KPIs, approval vs NPL scatter |
| Credit Risk | NPL by credit tier, score distribution, DTI analysis |
| Repayment Health | DPD buckets, monthly repayment status |
| Segmentation | Income segment analysis, employment × product heatmap |

## 🎯 Key Metrics Tracked
- Approval Rate | NPL Rate | Portfolio Value | Avg Ticket Size
- DPD Buckets (OJK regulatory format)
- Vintage / Cohort Analysis
- Province & Channel Performance
