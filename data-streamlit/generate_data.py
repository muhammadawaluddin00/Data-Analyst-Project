import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

np.random.seed(42)
random.seed(42)
N = 5000

# --- LOAN APPLICATIONS ---
provinces = ['DKI Jakarta','Jawa Barat','Jawa Tengah','Jawa Timur','Banten','Sumatera Utara',
             'Sulawesi Selatan','Kalimantan Timur','Bali','DIY Yogyakarta']
prov_weights = [0.25,0.20,0.15,0.12,0.08,0.06,0.05,0.04,0.03,0.02]

products = ['PayLater','KTA (Personal Loan)','Business Loan','Education Loan']
prod_weights = [0.45,0.30,0.15,0.10]

channels = ['Mobile App','Web','Partner API','Agent']
chan_weights = [0.55,0.20,0.15,0.10]

employment = ['Employed','Self-Employed','Business Owner','Freelancer','Student']
emp_weights = [0.50,0.20,0.18,0.08,0.04]

start_date = datetime(2022, 1, 1)
end_date   = datetime(2024, 12, 31)
date_range = (end_date - start_date).days

loan_ids = [f"LN{str(i).zfill(6)}" for i in range(1, N+1)]
customer_ids = [f"CUS{str(random.randint(1,3500)).zfill(5)}" for _ in range(N)]
app_dates = [start_date + timedelta(days=random.randint(0, date_range)) for _ in range(N)]

ages = np.clip(np.random.normal(32, 8, N).astype(int), 18, 65)
monthly_income = np.clip(np.random.lognormal(np.log(5_000_000), 0.6, N).astype(int), 1_500_000, 80_000_000)
credit_scores = np.clip(np.random.normal(650, 80, N).astype(int), 300, 850)

loan_amounts_by_product = {
    'PayLater':          (500_000,    5_000_000),
    'KTA (Personal Loan)':(5_000_000, 50_000_000),
    'Business Loan':     (10_000_000,200_000_000),
    'Education Loan':    (5_000_000,  30_000_000),
}

selected_products = np.random.choice(products, N, p=prod_weights)
loan_amounts = []
for p in selected_products:
    lo, hi = loan_amounts_by_product[p]
    loan_amounts.append(int(np.random.uniform(lo, hi)))
loan_amounts = np.array(loan_amounts)

tenors = np.random.choice([1,3,6,12,18,24,36], N, p=[0.10,0.15,0.20,0.25,0.15,0.10,0.05])
interest_rates = np.clip(np.random.normal(2.5, 0.5, N), 1.0, 4.5).round(2)

dti = (loan_amounts / tenors) / monthly_income
approval_prob = 1 / (1 + np.exp(-(credit_scores - 620)/50 - (0.5 - dti*10)))
statuses = np.where(np.random.random(N) < approval_prob, 'Approved',
           np.where(np.random.random(N) < 0.3, 'Rejected', 'Pending'))

disburse_dates = [
    (d + timedelta(days=random.randint(1,5))).strftime('%Y-%m-%d') if s == 'Approved' else None
    for d, s in zip(app_dates, statuses)
]

loans_df = pd.DataFrame({
    'loan_id': loan_ids,
    'customer_id': customer_ids,
    'application_date': [d.strftime('%Y-%m-%d') for d in app_dates],
    'disbursement_date': disburse_dates,
    'product_type': selected_products,
    'channel': np.random.choice(channels, N, p=chan_weights),
    'province': np.random.choice(provinces, N, p=prov_weights),
    'age': ages,
    'employment_type': np.random.choice(employment, N, p=emp_weights),
    'monthly_income_idr': monthly_income,
    'loan_amount_idr': loan_amounts,
    'tenor_months': tenors,
    'interest_rate_pct': interest_rates,
    'credit_score': credit_scores,
    'dti_ratio': (dti*100).round(2),
    'status': statuses,
})
loans_df.to_csv('/home/claude/indodana_bi_project/data/loan_applications.csv', index=False)

# --- REPAYMENT TABLE (approved loans only) ---
approved = loans_df[loans_df['status'] == 'Approved'].copy()
repay_rows = []
for _, row in approved.iterrows():
    disb = datetime.strptime(row['disbursement_date'], '%Y-%m-%d')
    monthly_payment = int((row['loan_amount_idr'] * (row['interest_rate_pct']/100)) +
                         (row['loan_amount_idr'] / row['tenor_months']))
    for mo in range(int(row['tenor_months'])):
        due = disb + timedelta(days=30*(mo+1))
        if due > end_date + timedelta(days=180):
            break
        delay_prob = max(0, (row['dti_ratio']/100 - 0.3) * 2)
        delay_days = 0
        if random.random() < delay_prob:
            delay_days = random.randint(1, 90)
        paid_date = due + timedelta(days=delay_days)
        repay_status = 'On Time' if delay_days == 0 else ('Late' if delay_days <= 30 else 'Overdue')
        repay_rows.append({
            'repayment_id': f"RP{len(repay_rows)+1:07d}",
            'loan_id': row['loan_id'],
            'customer_id': row['customer_id'],
            'installment_no': mo+1,
            'due_date': due.strftime('%Y-%m-%d'),
            'paid_date': paid_date.strftime('%Y-%m-%d') if paid_date <= end_date + timedelta(days=180) else None,
            'monthly_payment_idr': monthly_payment,
            'delay_days': delay_days,
            'repayment_status': repay_status,
        })

repay_df = pd.DataFrame(repay_rows)
repay_df.to_csv('/home/claude/indodana_bi_project/data/repayments.csv', index=False)

print(f"Loans: {len(loans_df)} rows")
print(f"Repayments: {len(repay_df)} rows")
print(loans_df['status'].value_counts())
