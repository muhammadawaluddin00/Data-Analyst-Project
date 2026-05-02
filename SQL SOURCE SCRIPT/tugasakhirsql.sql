SELECT
  nama_bulan,
  total_penjualan
FROM (
  SELECT
    FORMAT_TIMESTAMP('%B', od.order_date) AS nama_bulan,
    EXTRACT(MONTH FROM od.order_date) AS nomor_bulan,
    SUM(td.total_paid) AS total_penjualan
  FROM
    `finpro.transaction-detail` td
  JOIN
    `finpro.order-detail` od
  ON
    td.customer_id = od.customer_id
  WHERE
    EXTRACT(YEAR FROM od.order_date) = 2024
  GROUP BY
    nama_bulan, nomor_bulan
  ORDER BY
    nomor_bulan
);

SELECT * FROM (
  SELECT
    pd.category,
    EXTRACT(YEAR FROM od.order_date) AS sales_year,
    od.quantity
  FROM
    `finpro.order-detail` AS od
  LEFT JOIN
    `finpro.product-detail` pd ON od.sku_id = pd.sku_id
  WHERE
    od.is_valid = 1
    AND EXTRACT(YEAR FROM od.order_date) BETWEEN 2020 AND 2024
)
PIVOT(
  SUM(quantity)
  FOR sales_year IN (2020, 2021, 2022, 2023, 2024)
)
ORDER BY category;

-- query soal no. 3 final project
-- poin 1
select
  date_trunc(date(order_date), month) as order_month,
  channel_type,
  count(distinct order_id) as total_orders,
  sum(after_discount) as total_revenue
from
  `finpro.order-detail`
where
  date(order_date) between '2024-01-01' and '2024-12-31'
and
  is_valid = 1
group by 1,2
order by 1,2;

-- revisi query soal no. 3 final project
-- poin 2
with monthly_data as (
  select
    extract(year from order_date) as year,
    extract(month from order_date) as month,
    channel_type,
    sum(after_discount) as total_revenue
  from
    `finpro.order-detail`
  where
    extract(year from order_date) in (2023, 2024)
    and
    is_valid = 1
  group by 1,2,3
),

revenue_2023 as (
  select
    month,
    channel_type,
    total_revenue as revenue_2023
  from
    monthly_data
  where
    year = 2023
),

revenue_2024 as (
  select
    month,
    channel_type,
    total_revenue as revenue_2024
  from
    monthly_data
  where
    year = 2024
)

select
  r24.month,
  r24.channel_type,
  r23.revenue_2023,
  r24.revenue_2024,
  format('%.2f%%',
    safe_divide(
      (r24.revenue_2024 - r23.revenue_2023),
      r23.revenue_2023
    ) * 100) as yoy_growth_in_percent
from
  revenue_2024 as r24
left join revenue_2023 as r23 on r24.month = r23.month
and r24.channel_type = r23.channel_type
order by
  r24.month, r24.channel_type;

select
  channel_source,
  count(*) as total_events,
  count(distinct order_id) as total_orders,
  (count(distinct order_id) / count(*) * 100 || '%') as conversion_rate
from `finpro.funnel-detail`
where event = 'Organic'
  and funnel_date between '2024-01-01' and '2024-12-31'
group by channel_source
order by conversion_rate desc;

SELECT
  FORMAT_DATE('%Y-%m', DATE(registration_date)) AS month,
  registration_channel,
  COUNT(DISTINCT customer_id) AS total_new_customers
FROM `finpro.customer_det`
WHERE DATE(registration_date) BETWEEN '2024-01-01' AND '2024-12-31'
GROUP BY
  month,
  registration_channel
ORDER BY
  month,
  registration_channel;

WITH first_order AS (
  SELECT
    customer_id, MIN(order_date) AS first_order_date
  FROM `finpro.order-detail`
  WHERE
    is_valid = 1
  GROUP BY
    customer_id
)
SELECT
  FORMAT_DATE('%Y-%m', c.registration_date) AS registration_month,
  AVG(
    DATE_DIFF(
      DATE(f.first_order_date),
      DATE(c.registration_date),
      DAY
    )
  ) AS avg_days_to_first_purchase
FROM
  `finpro.customer_det` c
JOIN
  first_order f ON c.customer_id = f.customer_id
WHERE
  EXTRACT(YEAR FROM c.registration_date) = 2024
GROUP BY
  registration_month
ORDER BY
  registration_month;