# Indodana BI Analyst Portfolio Project
## Lending Analytics Dashboard — Project Documentation & Interview Prep Guide

---

## 📋 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Dataset Description](#2-dataset-description)
3. [SQL Analysis — Query Explanations](#3-sql-analysis--query-explanations)
4. [Dashboard Guide](#4-dashboard-guide)
5. [Key Business Insights & Findings](#5-key-business-insights--findings)
6. [Interview Q&A Preparation](#6-interview-qa-preparation)
7. [Glossary of Fintech/Lending Terms](#7-glossary-of-fintechlending-terms)
8. [Technical Stack](#8-technical-stack)

---

## 1. Project Overview

### What is this project?
This is a **Business Intelligence portfolio project** built to demonstrate data analysis, SQL, visualization, and business insight capabilities relevant to the **BI Analyst role at Indodana**.

Indodana is a leading Indonesian fintech lending platform (est. 2017, OJK-licensed since 2020) offering PayLater, personal loans, business loans, and education loans. This dashboard simulates the type of analytics a BI Analyst would build internally.

### Business Objective
> *"Present information in a way that drives fact-based decision making."*

The dashboard answers five core business questions:
- **Portfolio Trend** — How is our lending volume and disbursement growing over time?
- **Geographic** — Which provinces generate the most value and risk?
- **Credit Risk** — What is our NPL exposure by credit tier?
- **Repayment Health** — What is the DPD (Days Past Due) distribution across the portfolio?
- **Segmentation** — Which customer segments are most creditworthy?

---

## 2. Dataset Description

### Tables Created

#### `loan_applications.csv` — 5,000 rows
| Column | Type | Description |
|---|---|---|
| `loan_id` | String | Unique loan identifier (LN000001) |
| `customer_id` | String | Customer identifier (some customers have multiple loans) |
| `application_date` | Date | Date loan was applied for (2022–2024) |
| `disbursement_date` | Date | Date funds were released (NULL if not Approved) |
| `product_type` | String | PayLater / KTA / Business Loan / Education Loan |
| `channel` | String | Mobile App / Web / Partner API / Agent |
| `province` | String | 10 Indonesian provinces |
| `age` | Int | Applicant age (18–65) |
| `employment_type` | String | Employed / Self-Employed / Business Owner / Freelancer / Student |
| `monthly_income_idr` | Int | Monthly income in IDR (log-normal distribution) |
| `loan_amount_idr` | Int | Requested loan amount (varies by product) |
| `tenor_months` | Int | Repayment period: 1, 3, 6, 12, 18, 24, or 36 months |
| `interest_rate_pct` | Float | Monthly interest rate (%) |
| `credit_score` | Int | Score 300–850 (higher = lower risk) |
| `dti_ratio` | Float | Debt-to-income ratio (%) |
| `status` | String | Approved / Rejected / Pending |

**Data Distribution:**
- ~30% Approved, ~22% Rejected, ~47% Pending (realistic for Indonesia fintech)
- Approval is modeled via logistic function of credit score and DTI ratio

#### `repayments.csv` — ~19,000 rows
| Column | Type | Description |
|---|---|---|
| `repayment_id` | String | Unique installment ID |
| `loan_id` | String | Foreign key → loan_applications |
| `customer_id` | String | Customer reference |
| `installment_no` | Int | Which installment (1, 2, 3...) |
| `due_date` | Date | When payment was due |
| `paid_date` | Date | When payment was actually made |
| `monthly_payment_idr` | Int | Amount to pay each month |
| `delay_days` | Int | Days between due and paid date |
| `repayment_status` | String | On Time / Late / Overdue |

**Status Logic:**
- `On Time`: `delay_days = 0`
- `Late`: `delay_days` 1–30 (also called "30 DPD")
- `Overdue`: `delay_days > 30` (NPL candidate, OJK reporting required)

---

## 3. SQL Analysis — Query Explanations

### Query 1: Loan Application Funnel
**Business question:** Which products have highest conversion?
**Technique:** Conditional aggregation (`SUM CASE WHEN`)
**Insight to discuss:** PayLater typically has the lowest average ticket but highest volume. Business loans have lowest approval rates due to stricter DTI requirements.

### Query 2: Monthly Disbursement Trend
**Business question:** Is our portfolio growing?
**Technique:** `DATE_FORMAT` / `DATE_TRUNC` with `GROUP BY` time period
**Insight to discuss:** Look for seasonal patterns (Ramadan, year-end). Declining trend may indicate tightened credit policy, not declining demand.

### Query 3: Credit Risk Segmentation (NPL by Tier)
**Business question:** Where is our risk concentrated?
**Technique:** Common Table Expressions (CTEs), window functions, `CASE WHEN` binning
**Insight to discuss:** Sub-prime borrowers (550–649) may have 3–5x higher NPL than prime. This drives provisioning decisions.

### Query 4: Geographic KPIs
**Business question:** Expand or tighten by province?
**Technique:** Multi-table `LEFT JOIN`, conditional aggregation across joined tables
**Insight to discuss:** DKI Jakarta has highest volume but not necessarily lowest NPL. Some outer provinces may have better credit quality despite lower volume.

### Query 5: Channel Efficiency
**Business question:** Which acquisition channel has best unit economics?
**Technique:** `GROUP BY` aggregation, calculated metrics
**Insight to discuss:** Mobile App has highest conversion (self-selected, higher intent). Agent channel may have higher loan values but lower credit quality.

### Query 6: Vintage Analysis
**Business question:** Is underwriting quality improving or deteriorating?
**Technique:** Cohort analysis with CTEs, quarter-based grouping
**Insight to discuss:** If Q1 2022 cohort shows 15% NPL but Q4 2023 shows 8%, underwriting improved. Critical for provisioning models.

### Query 7: Customer Segmentation by Income
**Business question:** Which segments should we target?
**Technique:** `CASE WHEN` income banding, `MODE()` aggregate function
**Insight to discuss:** Middle-income (7M–15M) often have best risk-adjusted returns — high enough income, not over-leveraged.

### Query 8: DPD Buckets (OJK Reporting)
**Business question:** What is our regulatory exposure?
**Technique:** Window functions (`SUM() OVER()`), `CASE WHEN` binning, percentage of total
**Insight to discuss:** OJK requires reporting of 90+ DPD as NPL. Banks provision at 1%, 5%, 15%, 50%, 100% for each bucket.

---

## 4. Dashboard Guide

### How to Run the Dashboard
```bash
# Install requirements
pip install streamlit pandas numpy plotly

# Run dashboard
streamlit run dashboard.py
```

### Dashboard Structure

#### Sidebar Filters
- **Date Range** — Filter analysis period
- **Product Type** — Isolate specific products
- **Province** — Geographic drill-down

All charts update dynamically based on filters.

#### Tab 1: Portfolio Trend
Shows disbursement volume and value over time, approval rates by product, and channel quality matrix. Use this to demonstrate understanding of **portfolio growth tracking**.

#### Tab 2: Geographic
Province-level comparison of portfolio value, approval rates, and NPL rates. The scatter plot (approval vs NPL) is ideal for identifying high-quality vs high-risk regions.

#### Tab 3: Credit Risk
Credit score distribution, NPL by tier, DTI vs credit score scatter. Demonstrates **risk analytics** competency.

#### Tab 4: Repayment Health
DPD bucket analysis — the core of **OJK regulatory reporting**. Shows both count-based and exposure-based views.

#### Tab 5: Segmentation
Income segment and employment type analysis. The heatmap shows product affinity by employment type — useful for **product recommendation** and marketing targeting.

---

## 5. Key Business Insights & Findings

These are insights you can articulate during the interview:

### Insight 1: Mobile App Dominates but Agent Matters for Quality
Mobile App drives ~55% of applications with the highest approval rates. However, Agent-sourced loans often have higher ticket sizes. **Recommendation:** Invest in agent training to improve credit quality screening while maintaining volume.

### Insight 2: DKI Jakarta Over-Indexed, Outer Provinces Underserved
DKI Jakarta represents ~25% of applications. Provinces like Kalimantan Timur and Sulawesi Selatan have smaller volumes but comparable credit quality. **Recommendation:** Targeted marketing expansion with province-specific credit policies.

### Insight 3: Sub-Prime Borrowers Need Stricter DTI Caps
Borrowers with credit scores below 550 show disproportionately high NPL rates. **Recommendation:** Implement a hard DTI cap of 30% for this segment, or require collateral/guarantor.

### Insight 4: PayLater is the Volume Engine, KTA is the Revenue Engine
PayLater has highest application volume but lowest loan values. KTA (Personal Loan) generates 3–4x the revenue per loan. **Recommendation:** Cross-sell KTA to PayLater customers with 6+ months of on-time repayment.

### Insight 5: Repayment Concentration in "Late" Category
The "1–30 DPD" (Late) bucket represents significant exposure that doesn't yet count as NPL. Early intervention programs (SMS/WhatsApp reminders) at day 5 past due can prevent migration to Overdue. **Recommendation:** Build an early warning model using days-since-last-payment feature.

---

## 6. Interview Q&A Preparation

### Technical Questions

**Q: How do you handle large datasets in BigQuery?**
> A: I partition tables by date and cluster by frequently-filtered columns (like `product_type` or `province`). For this project, I'd partition `loan_applications` by `application_date` and cluster by `status`. This reduces query costs by 60–80% on typical BI queries.

**Q: How would you build a real-time NPL monitoring system?**
> A: I'd use a scheduled BigQuery query (via Cloud Scheduler) running daily, writing results to a summary table. Looker Studio or a Streamlit dashboard would connect to the summary table. Alerts would be triggered via Cloud Functions if NPL rate exceeds a threshold (e.g., >8%).

**Q: What's the difference between cohort analysis and segmentation?**
> A: Cohort analysis tracks the same group of customers over time (e.g., all loans disbursed in Q1 2022) to observe behavior changes. Segmentation groups customers at a point in time by characteristics (income, age, credit score). Both are in this project — vintage analysis (Query 6) is cohort; income analysis (Query 7) is segmentation.

**Q: How would you calculate LTV (Lifetime Value) for a lending product?**
> A: LTV = (Average Loan Amount × Interest Rate × Tenor) × Probability of Full Repayment − Cost of Acquisition − Cost of Capital. I'd build this in SQL using a CTE joining loan applications, repayments, and a customer acquisition cost table.

### Business/Case Questions

**Q: Our NPL rate increased from 5% to 9% last quarter. What do you do?**
> A: I'd immediately segment by: (1) vintage — is it a new cohort or old ones deteriorating? (2) product type — is it isolated? (3) channel — is one source of leads performing poorly? (4) geography — regional economic factors? (5) underwriting policy changes — did we loosen criteria? I'd present a root cause dashboard to management within 48 hours.

**Q: How would you prioritize which analysis to do first?**
> A: I'd align with management on the top business pain points — typically NPL rate, cost of acquisition, and growth (in that order for a fintech in Indonesia). Then I'd map each to a specific dataset and SQL query, estimate effort, and prioritize by impact/effort ratio.

**Q: How would you explain a complex SQL query to a non-technical stakeholder?**
> A: I'd describe it in plain English first: "We're looking at all loans approved this year, grouping customers by how risky they are, and measuring how many missed payments each group had." Then I'd show the output table, not the query. The query is an implementation detail.

### Questions to Ask the Interviewer

- "What does the current BI stack at Indodana look like? BigQuery, Looker, custom tools?"
- "What is the biggest data quality challenge your team faces today?"
- "How does the BI team collaborate with the Credit Risk and Product teams?"
- "What does a typical first 30-60 days look like for a new BI Analyst?"
- "What are the most important OJK reporting requirements that affect your data pipelines?"

---

## 7. Glossary of Fintech/Lending Terms

| Term | Definition |
|---|---|
| **NPL** | Non-Performing Loan — loans where the borrower is significantly behind on payments (typically 90+ DPD in Indonesia) |
| **DPD** | Days Past Due — how many days overdue a payment is |
| **DTI** | Debt-to-Income Ratio — monthly debt payments / monthly income. OJK recommends max 50% |
| **KTA** | Kredit Tanpa Agunan — unsecured personal loan (no collateral required) |
| **PayLater** | Buy-now-pay-later product, typically short tenor (1–3 months) |
| **Tenor** | Loan repayment period (in months) |
| **Disbursement** | The act of releasing loan funds to the borrower |
| **OJK** | Otoritas Jasa Keuangan — Indonesia's Financial Services Authority (regulator) |
| **POJK** | OJK Regulation — e.g., POJK 10/2022 governs fintech lending |
| **Vintage** | The cohort of loans by their origination period |
| **Credit Score** | A numerical measure of creditworthiness (300–850; higher = lower risk) |
| **Provisioning** | Setting aside capital to cover expected loan losses |
| **CAC** | Customer Acquisition Cost |
| **LTV** | Lifetime Value of a customer |
| **Portfolio at Risk (PAR)** | % of portfolio where loans have at least one missed payment |

---

## 8. Technical Stack

| Component | Technology |
|---|---|
| Data Generation | Python (pandas, numpy) |
| Data Storage | CSV (simulates BigQuery tables) |
| SQL Analysis | Standard SQL (BigQuery/PostgreSQL compatible) |
| Visualization | Plotly (interactive charts) |
| Dashboard | Streamlit |
| Styling | Custom CSS, Google Fonts (DM Sans) |
| Colors | Indodana brand palette (Teal #00B4A6, Navy #1A2B4A) |

### How to Extend This Project
1. **Connect to BigQuery**: Replace CSV loading with `google-cloud-bigquery` client
2. **Add ML Model**: Build a credit scoring model (logistic regression / XGBoost) and add a "Predicted Default Risk" tab
3. **Add Cohort Table**: Build a proper cohort retention table showing repayment rate by month-since-origination
4. **OJK Report Generator**: Add a tab that generates the standard OJK NPL reporting format

---

*This document was created as part of a BI Analyst portfolio project targeting the Indodana Business Intelligence Analyst role. All data is synthetic and does not represent actual Indodana business figures.*
