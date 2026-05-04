-- ============================================================
-- INDODANA BI ANALYST PROJECT — SQL ANALYSIS QUERIES
-- Author: BI Analyst Portfolio Project
-- Data: Synthetic Lending Data (2022–2024)
-- Tools: Compatible with BigQuery / PostgreSQL / MySQL
-- ============================================================

-- ============================================================
-- 1. LOAN APPLICATION FUNNEL — Approval Rate by Product
-- ============================================================
-- Business Question: Which loan products have the highest
-- approval rates and where is the biggest drop-off?

SELECT
    product_type,
    COUNT(*)                                                          AS total_applications,
    SUM(CASE WHEN status = 'Approved'  THEN 1 ELSE 0 END)            AS approved,
    SUM(CASE WHEN status = 'Rejected'  THEN 1 ELSE 0 END)            AS rejected,
    SUM(CASE WHEN status = 'Pending'   THEN 1 ELSE 0 END)            AS pending,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                                 AS approval_rate_pct,
    ROUND(AVG(loan_amount_idr) / 1e6, 2)                             AS avg_loan_amount_mio,
    ROUND(AVG(credit_score), 0)                                      AS avg_credit_score
FROM test.loan_applications
GROUP BY product_type
ORDER BY approval_rate_pct DESC;


-- ============================================================
-- 2. PORTFOLIO DISBURSEMENT TREND — Monthly Volume & Value
-- ============================================================
-- Business Question: How is loan disbursement growing MoM?
-- Useful for revenue forecasting and capacity planning.

SELECT
    DATE_FORMAT(disbursement_date, '%Y-%m')                          AS disburse_month,
    product_type,
    COUNT(*)                                                          AS loans_disbursed,
    ROUND(SUM(loan_amount_idr) / 1e9, 2)                             AS total_disbursed_bio_idr,
    ROUND(AVG(loan_amount_idr) / 1e6, 2)                             AS avg_loan_mio_idr,
    ROUND(AVG(interest_rate_pct), 2)                                  AS avg_interest_rate
FROM test.loan_applications
WHERE status = 'Approved'
  AND disbursement_date IS NOT NULL
GROUP BY DATE_FORMAT(disbursement_date, '%Y-%m'), product_type
ORDER BY disburse_month, product_type;


-- ============================================================
-- 3. CREDIT RISK SEGMENTATION — NPL Analysis
-- ============================================================
-- Business Question: What is our Non-Performing Loan rate
-- across different customer risk tiers?

WITH credit_tiers AS (
    SELECT
        loan_id,
        customer_id,
        credit_score,
        CASE
            WHEN credit_score >= 750 THEN 'Tier 1: Prime (750+)'
            WHEN credit_score >= 650 THEN 'Tier 2: Near-Prime (650–749)'
            WHEN credit_score >= 550 THEN 'Tier 3: Sub-Prime (550–649)'
            ELSE                          'Tier 4: High Risk (<550)'
        END AS credit_tier,
        loan_amount_idr,
        dti_ratio
    FROM test.loan_applications
    WHERE status = 'Approved'
),
repayment_perf AS (
    SELECT
        loan_id,
        COUNT(*)                                                       AS total_installments,
        SUM(CASE WHEN repayment_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_count,
        SUM(CASE WHEN repayment_status = 'Late'    THEN 1 ELSE 0 END) AS late_count,
        AVG(delay_days)                                                AS avg_delay_days
    FROM test.repayments
    GROUP BY loan_id
)
SELECT
    ct.credit_tier,
    COUNT(DISTINCT ct.loan_id)                                         AS total_loans,
    ROUND(AVG(ct.loan_amount_idr) / 1e6, 2)                           AS avg_loan_mio,
    ROUND(AVG(ct.dti_ratio), 2)                                        AS avg_dti_pct,
    ROUND(AVG(rp.avg_delay_days), 1)                                   AS avg_delay_days,
    SUM(rp.overdue_count)                                              AS total_overdue_installments,
    ROUND(
        100.0 * SUM(rp.overdue_count)
        / NULLIF(SUM(rp.total_installments), 0), 2
    )                                                                  AS npl_rate_pct
FROM credit_tiers ct
LEFT JOIN repayment_perf rp ON ct.loan_id = rp.loan_id
GROUP BY ct.credit_tier
ORDER BY ct.credit_tier;


-- ============================================================
-- 4. GEOGRAPHIC PERFORMANCE — Province-Level KPIs
-- ============================================================
-- Business Question: Which provinces deliver the best ROI
-- and where should we expand or tighten credit policy?

SELECT
    la.province,
    COUNT(la.loan_id)                                                  AS total_apps,
    SUM(CASE WHEN la.status = 'Approved' THEN 1 ELSE 0 END)           AS approved_count,
    ROUND(
        100.0 * SUM(CASE WHEN la.status = 'Approved' THEN 1 ELSE 0 END)
        / COUNT(la.loan_id), 2
    )                                                                  AS approval_rate_pct,
    ROUND(SUM(CASE WHEN la.status='Approved' THEN la.loan_amount_idr ELSE 0 END) / 1e9, 2)
                                                                       AS portfolio_value_bio,
    ROUND(AVG(CASE WHEN la.status='Approved' THEN la.credit_score END), 0)
                                                                       AS avg_credit_score,
    ROUND(
        100.0 * SUM(CASE WHEN r.repayment_status = 'Overdue' THEN 1 ELSE 0 END)
        / NULLIF(COUNT(r.repayment_id), 0), 2
    )                                                                  AS overdue_rate_pct
FROM test.loan_applications la
LEFT JOIN test.repayments r ON la.loan_id = r.loan_id
GROUP BY la.province
ORDER BY portfolio_value_bio DESC;


-- ============================================================
-- 5. CHANNEL EFFICIENCY — CAC Proxy & Conversion
-- ============================================================
-- Business Question: Which acquisition channel converts best
-- and what is the quality of leads per channel?

SELECT
    channel,
    COUNT(*)                                                           AS total_applications,
    SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END)              AS conversions,
    ROUND(
        100.0 * SUM(CASE WHEN status = 'Approved' THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                                  AS conversion_rate_pct,
    ROUND(AVG(credit_score), 0)                                        AS avg_credit_score,
    ROUND(AVG(loan_amount_idr) / 1e6, 2)                              AS avg_ticket_size_mio,
    ROUND(AVG(dti_ratio), 2)                                           AS avg_dti_pct
FROM test.loan_applications
GROUP BY channel
ORDER BY conversion_rate_pct DESC;


-- ============================================================
-- 6. VINTAGE ANALYSIS — Cohort Default Tracking
-- ============================================================
-- Business Question: Do loans disbursed in certain quarters
-- perform worse (early warning for underwriting quality)?

WITH cohort AS (
    SELECT
        loan_id,
        CONCAT(YEAR(disbursement_date), '-Q',
               QUARTER(disbursement_date))                             AS disburse_cohort,
        loan_amount_idr
    FROM test.loan_applications
    WHERE status = 'Approved'
      AND disbursement_date IS NOT NULL
),
cohort_perf AS (
    SELECT
        c.disburse_cohort,
        COUNT(DISTINCT c.loan_id)                                      AS loans_in_cohort,
        ROUND(SUM(c.loan_amount_idr) / 1e9, 2)                        AS cohort_value_bio,
        SUM(CASE WHEN r.repayment_status = 'Overdue' THEN 1 ELSE 0 END) AS overdue_payments,
        SUM(CASE WHEN r.repayment_status = 'Late'    THEN 1 ELSE 0 END) AS late_payments,
        COUNT(r.repayment_id)                                           AS total_payments
    FROM cohort c
    LEFT JOIN test.repayments r ON c.loan_id = r.loan_id
    GROUP BY c.disburse_cohort
)
SELECT
    disburse_cohort,
    loans_in_cohort,
    cohort_value_bio,
    overdue_payments,
    late_payments,
    total_payments,
    ROUND(100.0 * overdue_payments / NULLIF(total_payments, 0), 2)     AS overdue_rate_pct,
    ROUND(100.0 * late_payments    / NULLIF(total_payments, 0), 2)     AS late_rate_pct
FROM cohort_perf
ORDER BY disburse_cohort;


-- ============================================================
-- 7. CUSTOMER SEGMENTATION — Income vs Loan Behavior
-- ============================================================
-- Business Question: What income segments are our best
-- customers and how do we tailor products to each segment?

SELECT
    CASE
        WHEN monthly_income_idr < 3000000  THEN 'A: <3M'
        WHEN monthly_income_idr < 7000000  THEN 'B: 3M–7M'
        WHEN monthly_income_idr < 15000000 THEN 'C: 7M–15M'
        WHEN monthly_income_idr < 30000000 THEN 'D: 15M–30M'
        ELSE                                      'E: >30M'
    END                                                                AS income_segment,
    COUNT(*)                                                           AS applications,
    ROUND(
        100.0 * SUM(CASE WHEN status='Approved' THEN 1 ELSE 0 END)
        / COUNT(*), 2
    )                                                                  AS approval_rate_pct,
    ROUND(AVG(loan_amount_idr) / 1e6, 2)                              AS avg_loan_mio,
    ROUND(AVG(credit_score), 0)                                        AS avg_credit_score,
    ROUND(AVG(dti_ratio), 2)                                           AS avg_dti_pct,
    --- MODE() WITHIN GROUP (ORDER BY product_type)                        AS top_product
    COUNT(DISTINCT product_type)									   AS top_product
FROM test.loan_applications
GROUP BY income_segment
ORDER BY income_segment;


-- ============================================================
-- 8. REPAYMENT HEALTH DASHBOARD — Rolling 30/60/90 DPD
-- ============================================================
-- Business Question: What is our current Day Past Due (DPD)
-- exposure for risk reporting to OJK?

SELECT
    CASE
        WHEN delay_days = 0         THEN 'Current (0 DPD)'
        WHEN delay_days BETWEEN 1  AND 30  THEN '1–30 DPD'
        WHEN delay_days BETWEEN 31 AND 60  THEN '31–60 DPD'
        WHEN delay_days BETWEEN 61 AND 90  THEN '61–90 DPD'
        ELSE                                    '90+ DPD (NPL)'
    END                                                                AS dpd_bucket,
    COUNT(*)                                                           AS installment_count,
    ROUND(SUM(monthly_payment_idr) / 1e9, 2)                         AS exposure_bio_idr,
    ROUND(
        100.0 * COUNT(*)
        / SUM(COUNT(*)) OVER (), 2
    )                                                                  AS pct_of_portfolio
FROM test.repayments 
WHERE paid_date IS NOT NULL
GROUP BY dpd_bucket
ORDER BY
    CASE dpd_bucket
        WHEN 'Current (0 DPD)'  THEN 1
        WHEN '1–30 DPD'         THEN 2
        WHEN '31–60 DPD'        THEN 3
        WHEN '61–90 DPD'        THEN 4
        ELSE 5
    END;
