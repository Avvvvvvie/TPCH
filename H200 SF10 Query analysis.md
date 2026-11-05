# Q1 Pricing Summary Report Query

This query reports the amount of business that was billed, shipped, and returned.

```sql
SELECT
    l_returnflag,
    l_linestatus,
    sum(l_quantity) AS sum_qty,
    sum(l_extendedprice) AS sum_base_price,
    sum(l_extendedprice * (1 - l_discount)) AS sum_disc_price,
    sum(l_extendedprice * (1 - l_discount) * (1 + l_tax)) AS sum_charge,
    avg(l_quantity) AS avg_qty,
    avg(l_extendedprice) AS avg_price,
    avg(l_discount) AS avg_disc,
    count(*) AS count_order
FROM lineitem
WHERE (l_shipdate <= date '1998-12-01' - INTERVAL 90 DAY)
GROUP BY
    l_returnflag,
    l_linestatus
ORDER BY
    l_returnflag,
    l_linestatus;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 4.85085 | 4.39262 | fuse | nofuse |
| 2 | Project | 1.73698 | 1.73698 | nofuse | nofuse |
| 3 | Reorder | 0.00298933 | 0.00298933 |  |  |
| 4 | GroupBy | 7.10716 | 7.10716 | hash | hash |
| 5 | Sort | 0.494104 | 0.494104 | no_skf | no_skf |
|  | Total | 14.1921 | 13.7339 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q1.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q1.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q1.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q1.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q1.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q1_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q2 Minimum Cost Supplier Query

```sql
SELECT
    s_acctbal,
    s_name,
    n_name,
    p_partkey,
    p_mfgr,
    s_address,
    s_phone,
    s_comment
FROM part, supplier, partsupp, nation, region
WHERE (p_partkey = ps_partkey)
    AND (s_suppkey = ps_suppkey)
    AND (p_size = 15)
    AND (p_type LIKE '%BRASS')
    AND (s_nationkey = n_nationkey)
    AND (n_regionkey = r_regionkey)
    AND (r_name = 'EUROPE')
    AND (ps_supplycost = (
        SELECT min(ps_supplycost)
        FROM partsupp, supplier, nation, region
        WHERE (p_partkey = ps_partkey)
            AND (s_suppkey = ps_suppkey)
            AND (s_nationkey = n_nationkey)
            AND (n_regionkey = r_regionkey)
            AND (r_name = 'EUROPE')
    ))
ORDER BY
    s_acctbal DESC,
    n_name,
    s_name,
    p_partkey
LIMIT 100;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class REGION,NATION,SUPPLIER,PART,PARTSUPP active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.0588899 | 0.0588899 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.154222 | 0.127599 | hash_gfur | sort_merge_gfur |
| 4 | Reorder | 0.0048802 | 0.0048802 |  |  |
| 5 | Project | 0.0635615 | 0.0635615 | nofuse | nofuse |
| 6 | SourceTable |  |  |  |  |
| 7 | SourceTable |  |  |  |  |
| 8 | SourceTable |  |  |  |  |
| 9 | Filter | 0.268281 | 0.242449 | fuse | nofuse |
| 10 | Filter | 0.159258 | 0.159258 | fuse | fuse |
| 11 | Project | 0.0030878 | 0.0030878 | nofuse | nofuse |
| 12 | EqJoin | 1.08715 | 1.08715 | hash_gfur | hash_gfur |
| 13 | Reorder | 0.00584178 | 0.00584178 |  |  |
| 14 | EqJoin | 0.487042 | 0.487042 | hash_gfur | hash_gfur |
| 15 | Reorder | 0.0123243 | 0.0123243 |  |  |
| 16 | Project | 0.364658 | 0.364658 | nofuse | nofuse |
| 17 | EqJoin | 0.493813 | 0.493813 | hash_gfur | hash_gfur |
| 18 | Reorder | 0.0147757 | 0.0147757 |  |  |
| 19 | Project | 0.393475 | 0.393475 | nofuse | nofuse |
| 20 | Reorder | 0.0212705 | 0.0212705 |  |  |
| 21 | GroupBy | 0.115513 | 0.115513 | hash | hash |
| 22 | Project | 0.00299496 | 0.00299496 | nofuse | nofuse |
| 23 | EqJoin | 0.480411 | 0.480411 | hash_gfur | hash_gfur |
| 24 | Reorder | 0.0149424 | 0.0149424 |  |  |
| 25 | Filter | 0.538567 | 0.538567 | fuse | fuse |
| 26 | Project | 0.00399565 | 0.00399565 | nofuse | nofuse |
| 27 | TopK | 1.36702 | 1.36702 |  |  |
|  | Total | 6.11597 | 6.06352 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q2.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q2.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q2.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q2.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q2.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q2_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q3 Shipping Priority Query

This query retrieves the 10 unshipped orders with the highest value.

```sql
SELECT
    l_orderkey,
    sum(l_extendedprice * (1 - l_discount)) AS revenue,
    o_orderdate,
    o_shippriority
FROM customer, orders, lineitem
WHERE (c_mktsegment = 'BUILDING')
    AND (c_custkey = o_custkey)
    AND (l_orderkey = o_orderkey)
    AND (o_orderdate < date '1995-03-15')
    AND (l_shipdate > date '1995-03-15')
GROUP BY
    l_orderkey,
    o_orderdate,
    o_shippriority
ORDER BY
    revenue DESC,
    o_orderdate
LIMIT 10;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class CUSTOMER,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.0918359 | 0.0918359 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | Filter | 0.432495 | 0.310359 | fuse | nofuse |
| 4 | EqJoin | 1.18251 | 1.18251 | hash_gfur | hash_gfur |
| 5 | Reorder | 0.003104 | 0.003104 |  |  |
| 6 | SourceTable |  |  |  |  |
| 7 | Filter | 1.488 | 1.03353 | fuse | nofuse |
| 8 | EqJoin | 4.16819 | 2.51627 | hash_gfur | partition_hash_gfur |
| 9 | Reorder | 0.0031231 | 0.0031231 |  |  |
| 10 | Project | 0.0399928 | 0.0399928 | nofuse | nofuse |
| 11 | Reorder | 0.00314477 | 0.00314477 |  |  |
| 12 | GroupBy | 0.129112 | 0.129112 | hash | hash |
| 13 | Project | 0.00301316 | 0.00301316 | nofuse | nofuse |
| 14 | TopK | 0.60155 | 0.60155 |  |  |
|  | Total | 8.14607 | 5.91754 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q3.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q3.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q3.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q3.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q3.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q3_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q4 Order Priority Checking Query

This query determines how well the order priority system is working and gives an assessment of customer satisfaction.

```sql
SELECT
    o_orderpriority,
    count(*) AS order_count
FROM orders
WHERE (o_orderdate >= date '1993-07-01')
    AND (o_orderdate < date '1993-07-01' + INTERVAL 3 MONTH)
    AND EXISTS (
        SELECT *
        FROM lineitem
        WHERE (l_orderkey = o_orderkey)
            AND (l_commitdate < l_receiptdate)
    )
GROUP BY o_orderpriority
ORDER BY o_orderpriority;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.654736 | 0.454201 | fuse | nofuse |
| 2 | SourceTable |  |  |  |  |
| 3 | Filter | 0.75837 | 0.460355 | fuse | nofuse |
| 4 | SemiJoin | 2.73211 | 2.73211 |  |  |
| 5 | Reorder | 0.00592229 | 0.00592229 |  |  |
| 6 | Reorder | 0.003072 | 0.003072 |  |  |
| 7 | GroupBy | 0.166769 | 0.166769 | hash | hash |
| 8 | Sort | 0.130956 | 0.130956 | no_skf | no_skf |
|  | Total | 4.45194 | 3.95339 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q4.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q4.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q4.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q4.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q4.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q4_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q5 Local Supplier Volume Query

This query lists the revenue volume done through local suppliers.

```sql
SELECT
    n_name,
    sum(l_extendedprice * (1 - l_discount)) AS revenue
FROM customer, orders, lineitem, supplier, nation, region
WHERE (c_custkey = o_custkey)
    AND (l_orderkey = o_orderkey)
    AND (l_suppkey = s_suppkey)
    AND (c_nationkey = s_nationkey)
    AND (s_nationkey = n_nationkey)
    AND (n_regionkey = r_regionkey)
    AND (r_name = 'ASIA')
    AND (o_orderdate >= date '1994-01-01')
    AND (o_orderdate < date '1994-01-01' + INTERVAL 1 YEAR)
GROUP BY n_name
ORDER BY revenue DESC;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class REGION,NATION,SUPPLIER,CUSTOMER,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | Filter | 0.481111 | 0.281935 | fuse | nofuse |
| 3 | EqJoin | 0.623867 | 0.623867 | hash_gfur | hash_gfur |
| 4 | Reorder | 0.00314105 | 0.00314105 |  |  |
| 5 | SourceTable |  |  |  |  |
| 6 | EqJoin | 8.61465 | 4.02494 | hash_gfur | partition_hash_gfur |
| 7 | Reorder | 0.00309979 | 0.00309979 |  |  |
| 8 | SourceTable |  |  |  |  |
| 9 | Filter | 0.0581381 | 0.0541886 | fuse | nofuse |
| 10 | SourceTable |  |  |  |  |
| 11 | EqJoin | 0.152311 | 0.129901 | hash_gfur | sort_merge_gfur |
| 12 | Reorder | 0.00512168 | 0.00512168 |  |  |
| 13 | SourceTable |  |  |  |  |
| 14 | EqJoin | 0.171262 | 0.171262 | hash_gfur | hash_gfur |
| 15 | Reorder | 0.00504926 | 0.00504926 |  |  |
| 16 | EqJoin | 2.7372 | 2.25072 | hash_gfur | sort_merge_gfur |
| 17 | Reorder | 0.00598147 | 0.00598147 |  |  |
| 18 | Filter | 0.238403 | 0.210577 | fuse | nofuse |
| 19 | Project | 0.025072 | 0.025072 | nofuse | nofuse |
| 20 | Reorder | 0.00313179 | 0.00313179 |  |  |
| 21 | GroupBy | 0.126915 | 0.126915 | hash | hash |
| 22 | Sort | 0.0822097 | 0.0822097 | no_skf | no_skf |
|  | Total | 13.3367 | 8.00711 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q5.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q5.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q5.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q5.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q5.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q5_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q6 Forecasting Revenue Change Query

This query quantifies the amount of revenue increase that would have resulted from eliminating certain company-wide discounts in a given percentage range in a given year. Asking this type of "what if" query can be used to look for ways to increase revenues.

```sql
SELECT
    sum(l_extendedprice * l_discount) AS revenue
FROM lineitem
WHERE (l_shipdate >= date '1994-01-01')
    AND (l_shipdate < date '1994-01-01' + INTERVAL 1 YEAR)
    AND (l_discount BETWEEN 0.06::Decimal(12,2) - 0.01::Decimal(12,2) AND 0.06::Decimal(12,2) + 0.01::Decimal(12,2))
    AND (l_quantity < 24);
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 3.51391 | 1.43578 | fuse | nofuse |
| 2 | Project | 0.0184859 | 0.0184859 | nofuse | nofuse |
| 3 | Reorder | 0.00304366 | 0.00304366 |  |  |
| 4 | ScalarAgg | 0.0340743 | 0.0340743 |  |  |
|  | Total | 3.56951 | 1.49138 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q6.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q6.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q6.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q6.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q6.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q6_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q7 Volume Shipping Query

This query determines the value of goods shipped between certain nations to help in the re-negotiation of shipping contracts.

```sql
SELECT
    supp_nation,
    cust_nation,
    l_year,
    sum(volume) AS revenue
FROM (
    SELECT
        n1.n_name AS supp_nation,
        n2.n_name AS cust_nation,
        extract(year FROM l_shipdate) AS l_year,
        l_extendedprice * (1 - l_discount) AS volume
    FROM supplier, lineitem, orders, customer, nation AS n1, nation AS n2
    WHERE (s_suppkey = l_suppkey)
        AND (o_orderkey = l_orderkey)
        AND (c_custkey = o_custkey)
        AND (s_nationkey = n1.n_nationkey)
        AND (c_nationkey = n2.n_nationkey)
        AND (
            ((n1.n_name = 'FRANCE') AND (n2.n_name = 'GERMANY'))
            OR ((n1.n_name = 'GERMANY') AND (n2.n_name = 'FRANCE'))
        )
        AND (l_shipdate BETWEEN date '1995-01-01' AND date '1996-12-31')
) AS shipping
GROUP BY
    supp_nation,
    cust_nation,
    l_year
ORDER BY
    supp_nation,
    cust_nation,
    l_year;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class NATION,SUPPLIER,CUSTOMER,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.148727 | 0.148727 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.14919 | 0.14919 | hash_gfur | hash_gfur |
| 4 | Reorder | 0.00496941 | 0.00496941 |  |  |
| 5 | SourceTable |  |  |  |  |
| 6 | Filter | 2.29524 | 1.4563 | fuse | nofuse |
| 7 | EqJoin | 2.63849 | 2.25706 | hash_gfur | partition_hash_gfur |
| 8 | Reorder | 0.00548141 | 0.00548141 |  |  |
| 9 | SourceTable |  |  |  |  |
| 10 | EqJoin | 2.55783 | 2.32139 | hash_gfur | partition_hash_gfur |
| 11 | Reorder | 0.00541427 | 0.00541427 |  |  |
| 12 | SourceTable |  |  |  |  |
| 13 | Filter | 0.150251 | 0.150251 | fuse | fuse |
| 14 | SourceTable |  |  |  |  |
| 15 | EqJoin | 0.304995 | 0.242906 | hash_gfur | sort_merge_gfur |
| 16 | Reorder | 0.00487278 | 0.00487278 |  |  |
| 17 | EqJoin | 0.454962 | 0.454962 | hash_gfur | hash_gfur |
| 18 | Reorder | 0.00830431 | 0.00830431 |  |  |
| 19 | Filter | 0.362012 | 0.362012 | fuse | fuse |
| 20 | Project | 0.0360991 | 0.0360991 | nofuse | nofuse |
| 21 | Reorder | 0.00310024 | 0.00310024 |  |  |
| 22 | GroupBy | 0.21541 | 0.21541 | hash | hash |
| 23 | Sort | 0.526052 | 0.526052 | no_skf | no_skf |
|  | Total | 9.8714 | 8.3525 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q7.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q7.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q7.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q7.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q7.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q7_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q8 National Market Share Query

This query determines how the market share of a given nation within a given region has changed over two years for a given part type.

```sql
SELECT
    o_year,
    sum(CASE
        WHEN nation = 'BRAZIL' THEN volume
        ELSE 0
    END) / sum(volume) AS mkt_share
FROM (
    SELECT
        extract(year FROM o_orderdate) AS o_year,
        l_extendedprice * (1 - l_discount) AS volume,
        n2.n_name AS nation
    FROM part, supplier, lineitem, orders, customer, nation AS n1, nation AS n2, region
    WHERE (p_partkey = l_partkey)
        AND (s_suppkey = l_suppkey)
        AND (l_orderkey = o_orderkey)
        AND (o_custkey = c_custkey)
        AND (c_nationkey = n1.n_nationkey)
        AND (n1.n_regionkey = r_regionkey)
        AND (r_name = 'AMERICA')
        AND (s_nationkey = n2.n_nationkey)
        AND (o_orderdate BETWEEN date '1995-01-01' AND date '1996-12-31')
        AND (p_type = 'ECONOMY ANODIZED STEEL')
) AS all_nations
GROUP BY o_year
ORDER BY o_year;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class REGION,NATION,SUPPLIER,CUSTOMER,PART,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.0578225 | 0.0578225 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.0946095 | 0.0693878 | hash_gfur | sort_merge_gfur |
| 4 | Reorder | 0.00309867 | 0.00309867 |  |  |
| 5 | SourceTable |  |  |  |  |
| 6 | EqJoin | 0.28597 | 0.187988 | hash_gfur | sort_merge_gftr |
| 7 | Reorder | 0.0031261 | 0.0031261 |  |  |
| 8 | SourceTable |  |  |  |  |
| 9 | Filter | 0.509275 | 0.308518 | fuse | nofuse |
| 10 | EqJoin | 0.818409 | 0.818409 | hash_gfur | hash_gfur |
| 11 | Reorder | 0.00311314 | 0.00311314 |  |  |
| 12 | SourceTable |  |  |  |  |
| 13 | EqJoin | 7.87875 | 3.75945 | hash_gfur | partition_hash_gfur |
| 14 | Reorder | 0.00304305 | 0.00304305 |  |  |
| 15 | SourceTable |  |  |  |  |
| 16 | Filter | 0.0883771 | 0.0883771 | fuse | fuse |
| 17 | EqJoin | 0.454684 | 0.454684 | hash_gfur | hash_gfur |
| 18 | Reorder | 0.00303924 | 0.00303924 |  |  |
| 19 | SourceTable |  |  |  |  |
| 20 | EqJoin | 0.222791 | 0.222791 | hash_gfur | hash_gfur |
| 21 | Reorder | 0.0031101 | 0.0031101 |  |  |
| 22 | SourceTable |  |  |  |  |
| 23 | EqJoin | 1.24059 | 0.640065 | hash_gfur | sort_merge_gfur |
| 24 | Reorder | 0.00630629 | 0.00630629 |  |  |
| 25 | Project | 0.0905051 | 0.0905051 | nofuse | nofuse |
| 26 | Project | 0.0265608 | 0.0265608 | nofuse | nofuse |
| 27 | Project | 0.0113128 | 0.0113128 | nofuse | nofuse |
| 28 | Reorder | 0.00305524 | 0.00305524 |  |  |
| 29 | GroupBy | 0.0960358 | 0.0731163 | hash | sort_gfur |
| 30 | Project | 0.0108495 | 0.0108495 | nofuse | nofuse |
| 31 | Sort | 0.0120556 | 0.0120556 | no_skf | no_skf |
|  | Total | 11.9265 | 6.85978 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q8.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q8.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q8.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q8.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q8.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q8_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q9 Product Type Profit Measure Query

This query determines how much profit is made on a given line of parts, broken out by supplier nation and year.

```sql
SELECT
    nation,
    o_year,
    sum(amount) AS sum_profit
FROM (
    SELECT
        n_name AS nation,
        extract(year FROM o_orderdate) AS o_year,
        l_extendedprice * (1 - l_discount) - ps_supplycost * l_quantity AS amount
    FROM part, supplier, lineitem, partsupp, orders, nation
    WHERE (s_suppkey = l_suppkey)
        AND (ps_suppkey = l_suppkey)
        AND (ps_partkey = l_partkey)
        AND (p_partkey = l_partkey)
        AND (o_orderkey = l_orderkey)
        AND (s_nationkey = n_nationkey)
        AND (p_name LIKE '%green%')
) AS profit
GROUP BY
    nation,
    o_year
ORDER BY
    nation,
    o_year DESC;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class NATION,SUPPLIER,PART,PARTSUPP,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | Filter | 0.206368 | 0.206368 | fuse | fuse |
| 3 | SourceTable |  |  |  |  |
| 4 | EqJoin | 7.92514 | 3.95215 | hash_gfur | partition_hash_gfur |
| 5 | Reorder | 0.00313486 | 0.00313486 |  |  |
| 6 | SourceTable |  |  |  |  |
| 7 | EqJoin | 1.04099 | 1.04099 | hash_gfur | hash_gfur |
| 8 | Reorder | 0.00305371 | 0.00305371 |  |  |
| 9 | SourceTable |  |  |  |  |
| 10 | EqJoin | 3.18718 | 3.18718 | hash_gfur | hash_gfur |
| 11 | Reorder | 0.00307429 | 0.00307429 |  |  |
| 12 | Filter | 0.639678 | 0.579973 | fuse | nofuse |
| 13 | SourceTable |  |  |  |  |
| 14 | EqJoin | 3.09535 | 2.32964 | hash_gfur | partition_hash_gfur |
| 15 | Reorder | 0.00308571 | 0.00308571 |  |  |
| 16 | EqJoin | 0.952586 | 0.789501 | hash_gfur | sort_merge_gfur |
| 17 | Reorder | 0.00581371 | 0.00581371 |  |  |
| 18 | Project | 0.34597 | 0.34597 | nofuse | nofuse |
| 19 | Reorder | 0.00589943 | 0.00589943 |  |  |
| 20 | GroupBy | 0.320315 | 0.320315 | hash | hash |
| 21 | Sort | 0.582536 | 0.582536 | no_skf | no_skf |
|  | Total | 18.3202 | 13.3587 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q9.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q9.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q9.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q9.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q9.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q9_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q10 Returned Item Reporting Query

The query identifies customers who might be having problems with the parts that are shipped to them.

```sql
SELECT
    c_custkey,
    c_name,
    sum(l_extendedprice * (1 - l_discount)) AS revenue,
    c_acctbal,
    n_name,
    c_address,
    c_phone,
    c_comment
FROM customer, orders, lineitem, nation
WHERE (c_custkey = o_custkey)
    AND (l_orderkey = o_orderkey)
    AND (o_orderdate >= date '1993-10-01')
    AND (o_orderdate < date '1993-10-01' + INTERVAL 3 MONTH)
    AND (l_returnflag = 'R')
    AND (c_nationkey = n_nationkey)
GROUP BY
    c_custkey,
    c_name,
    c_acctbal,
    c_phone,
    n_name,
    c_address,
    c_comment
ORDER BY revenue DESC
LIMIT 20;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class NATION,CUSTOMER,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | SourceTable |  |  |  |  |
| 3 | Filter | 1.24017 | 1.24017 | fuse | fuse |
| 4 | SourceTable |  |  |  |  |
| 5 | Filter | 0.477052 | 0.274084 | fuse | nofuse |
| 6 | EqJoin | 1.91269 | 1.91269 | hash_gfur | hash_gfur |
| 7 | Reorder | 0.00309673 | 0.00309673 |  |  |
| 8 | Project | 0.0421348 | 0.0421348 | nofuse | nofuse |
| 9 | Reorder | 0.00310982 | 0.00310982 |  |  |
| 10 | GroupBy | 0.194858 | 0.194858 | hash | hash |
| 11 | EqJoin | 1.2872 | 1.2872 | hash_gfur | hash_gfur |
| 12 | Reorder | 0.0107147 | 0.0107147 |  |  |
| 13 | EqJoin | 1.04025 | 1.04025 | hash_gfur | hash_gfur |
| 14 | Reorder | 0.0128402 | 0.0128402 |  |  |
| 15 | Project | 0.93046 | 0.93046 | nofuse | nofuse |
| 16 | TopK | 0.428992 | 0.428992 |  |  |
|  | Total | 7.58357 | 7.3806 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q10.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q10.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q10.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q10.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q10.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q10_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q11 Important Stock Identification Query

This query finds the most important subset of suppliers' stock in a given nation.
The FRACTION parameter in the HAVING clause is 0.0001 / SF (spec section 2.4.11.3).
Current value 0.0001 is for SF = 1. See the README (section Q11) for other scale factors.

```sql
SELECT
    ps_partkey,
    sum(ps_supplycost * ps_availqty) AS value
FROM partsupp, supplier, nation
WHERE (ps_suppkey = s_suppkey)
    AND (s_nationkey = n_nationkey)
    AND (n_name = 'GERMANY')
GROUP BY ps_partkey
HAVING sum(ps_supplycost * ps_availqty) > (
    SELECT sum(ps_supplycost * ps_availqty) * 0.0001
    FROM partsupp, supplier, nation
    WHERE (ps_suppkey = s_suppkey)
        AND (s_nationkey = n_nationkey)
        AND (n_name = 'GERMANY')
)
ORDER BY value DESC;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class NATION,SUPPLIER,PARTSUPP active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | Filter | 0.0585143 | 0.0585143 | nofuse | nofuse |
| 3 | SourceTable |  |  |  |  |
| 4 | EqJoin | 0.0959592 | 0.0920459 | hash_gfur | sort_merge_gftr |
| 5 | Reorder | 0.0031159 | 0.0031159 |  |  |
| 6 | EqJoin | 1.93671 | 1.32704 | hash_gfur | sort_merge_gfur |
| 7 | Reorder | 0.00309692 | 0.00309692 |  |  |
| 8 | Project | 0.0202147 | 0.0202147 | nofuse | nofuse |
| 9 | Reorder | 0.0133694 | 0.0133694 |  |  |
| 10 | GroupBy | 0.163475 | 0.163475 | sort_gfur | sort_gfur |
| 11 | Reorder | 0.00311879 | 0.00311879 |  |  |
| 12 | ScalarAgg | 0.030872 | 0.030872 |  |  |
| 13 | Project | 0.010543 | 0.010543 | nofuse | nofuse |
| 14 | CrossJoin | 0.0492954 | 0.0492954 |  |  |
| 15 | Filter | 0.0749052 | 0.0749052 | nofuse | nofuse |
| 16 | Project | 0.00307634 | 0.00307634 | nofuse | nofuse |
| 17 | Sort | 0.0031159 | 0.0031159 | no_skf | no_skf |
|  | Total | 2.46938 | 1.8558 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q11.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q11.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q11.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q11.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q11.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q11_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q12 Shipping Modes and Order Priority Query

This query determines whether selecting less expensive modes of shipping is negatively affecting the critical-priority orders by causing more parts to be received by customers after the committed date.

```sql
SELECT
    l_shipmode,
    sum(CASE
        WHEN (o_orderpriority = '1-URGENT')
            OR (o_orderpriority = '2-HIGH')
            THEN 1
        ELSE 0
    END) AS high_line_count,
    sum(CASE
        WHEN (o_orderpriority <> '1-URGENT')
            AND (o_orderpriority <> '2-HIGH')
            THEN 1
        ELSE 0
    END) AS low_line_count
FROM orders, lineitem
WHERE (o_orderkey = l_orderkey)
    AND (l_shipmode IN ('MAIL', 'SHIP'))
    AND (l_commitdate < l_receiptdate)
    AND (l_shipdate < l_commitdate)
    AND (l_receiptdate >= date '1994-01-01')
    AND (l_receiptdate < date '1994-01-01' + INTERVAL 1 YEAR)
GROUP BY l_shipmode
ORDER BY l_shipmode;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | Filter | 4.21226 | 2.70981 | fuse | nofuse |
| 3 | EqJoin | 1.44253 | 1.44253 | hash_gfur | hash_gfur |
| 4 | Reorder | 0.00750673 | 0.00750673 |  |  |
| 5 | Project | 0.128274 | 0.128274 | nofuse | nofuse |
| 6 | Project | 0.043415 | 0.043415 | nofuse | nofuse |
| 7 | Reorder | 0.00308644 | 0.00308644 |  |  |
| 8 | GroupBy | 0.166138 | 0.166138 | hash | hash |
| 9 | Sort | 0.132399 | 0.132399 | no_skf | no_skf |
|  | Total | 6.13561 | 4.63316 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q12.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q12.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q12.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q12.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q12.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q12_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q13 Customer Distribution Query

This query seeks relationships between customers and the size of their orders.

```sql
SELECT
    c_count,
    count(*) AS custdist
FROM (
    SELECT
        c_custkey,
        count(o_orderkey) AS c_count
    FROM customer
    LEFT OUTER JOIN orders ON (c_custkey = o_custkey)
        AND (o_comment NOT LIKE '%special%requests%')
    GROUP BY c_custkey
) AS c_orders
GROUP BY c_count
ORDER BY
    custdist DESC,
    c_count DESC;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class CUSTOMER,ORDERS active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | Filter | 1.48002 | 1.48002 | nofuse | nofuse |
| 3 | EqJoin | 3.08847 | 2.22446 | hash_gfur | sort_merge_gftr |
| 4 | Reorder | 0.00313791 | 0.00313791 |  |  |
| 5 | Reorder | 0.00311116 | 0.00311116 |  |  |
| 6 | GroupBy | 1.49788 | 1.49788 | hash | hash |
| 7 | AntiJoin | 0.93064 | 0.93064 |  |  |
| 8 | Reorder | 0.00309349 | 0.00309349 |  |  |
| 9 | Project | 0.023786 | 0.0186383 | fuse | nofuse |
| 10 | Concat | 0.035627 | 0.035627 |  |  |
| 11 | Reorder | 0.0031169 | 0.0031169 |  |  |
| 12 | GroupBy | 0.138375 | 0.138375 | hash | hash |
| 13 | Sort | 0.263712 | 0.12339 | no_skf | skf |
|  | Total | 7.47097 | 6.46149 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q13.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q13.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q13.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q13.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q13.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q13_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q14 Promotion Effect Query

This query monitors the market response to a promotion such as TV advertisements or a special campaign.

```sql
SELECT
    100.00 * sum(CASE
        WHEN p_type LIKE 'PROMO%'
            THEN l_extendedprice * (1 - l_discount)
        ELSE 0
    END) / sum(l_extendedprice * (1 - l_discount)) AS promo_revenue
FROM lineitem, part
WHERE (l_partkey = p_partkey)
    AND (l_shipdate >= date '1995-09-01')
    AND (l_shipdate < date '1995-09-01' + INTERVAL 1 MONTH);
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class PART,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 1.86234 | 1.02859 | fuse | nofuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.653651 | 0.653651 | hash_gfur | hash_gfur |
| 4 | Reorder | 0.00587485 | 0.00587485 |  |  |
| 5 | Project | 0.0592827 | 0.0592827 | nofuse | nofuse |
| 6 | Project | 0.0143673 | 0.0143673 | nofuse | nofuse |
| 7 | Reorder | 0.00301163 | 0.00301163 |  |  |
| 8 | ScalarAgg | 0.059895 | 0.059895 |  |  |
| 9 | Project | 0.0210363 | 0.0210363 | nofuse | nofuse |
|  | Total | 2.67946 | 1.84571 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q14.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q14.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q14.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q14.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q14.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q14_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q15 Top Supplier Query

This query determines the top supplier so it can be rewarded, given more business, or identified for special recognition.

```sql
CREATE VIEW revenue0 AS
    SELECT
        l_suppkey AS supplier_no,
        sum(l_extendedprice * (1 - l_discount)) AS total_revenue
    FROM lineitem
    WHERE (l_shipdate >= date '1996-01-01')
        AND (l_shipdate < date '1996-01-01' + INTERVAL 3 MONTH)
    GROUP BY l_suppkey;


SELECT
    s_suppkey,
    s_name,
    s_address,
    s_phone,
    total_revenue
FROM supplier, revenue0
WHERE (s_suppkey = supplier_no)
    AND (total_revenue = (
        SELECT max(total_revenue)
        FROM revenue0
    ))
ORDER BY s_suppkey;

DROP VIEW revenue0;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class SUPPLIER,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | Filter | 1.88899 | 1.05844 | fuse | nofuse |
| 3 | Project | 0.041622 | 0.041622 | nofuse | nofuse |
| 4 | Reorder | 0.00310515 | 0.00310515 |  |  |
| 5 | GroupBy | 0.20307 | 0.20307 | hash | hash |
| 6 | Reorder | 0.00567205 | 0.00567205 |  |  |
| 7 | ScalarAgg | 0.0317712 | 0.0317712 |  |  |
| 8 | CrossJoin | 0.0465479 | 0.0465479 |  |  |
| 9 | Filter | 0.0824998 | 0.0743098 | fuse | nofuse |
| 10 | EqJoin | 0.26289 | 0.26289 | hash_gfur | hash_gfur |
| 11 | Reorder | 0.0084434 | 0.0084434 |  |  |
| 12 | Project | 0.181643 | 0.181643 | nofuse | nofuse |
| 13 | Sort | 0.206786 | 0.206786 | no_skf | no_skf |
|  | Total | 2.96304 | 2.1243 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q15.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q15.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q15.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q15.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q15.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q15_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q16 Parts/Supplier Relationship Query

This query finds out how many suppliers can supply parts with given attributes. It might be used, for example, to determine whether there is a sufficient number of suppliers for heavily ordered parts.

```sql
SELECT
    p_brand,
    p_type,
    p_size,
    count(DISTINCT ps_suppkey) AS supplier_cnt
FROM partsupp, part
WHERE (p_partkey = ps_partkey)
    AND (p_brand <> 'Brand#45')
    AND (p_type NOT LIKE 'MEDIUM POLISHED%')
    AND (p_size IN (49, 14, 23, 45, 19, 3, 36, 9))
    AND (ps_suppkey NOT IN (
        SELECT s_suppkey
        FROM supplier
        WHERE (s_comment LIKE '%Customer%Complaints%')
    ))
GROUP BY
    p_brand,
    p_type,
    p_size
ORDER BY
    supplier_cnt DESC,
    p_brand,
    p_type,
    p_size;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class SUPPLIER,CUSTOMER,PART,PARTSUPP active
```

| Step | Step kind | Baseline (ms) | Baseline implementation |
| --- | --- | --- | --- |
| 0 | SourceTable |  |  |
| 1 | Filter | 0.606358 | nofuse |
| 2 | SourceTable |  |  |
| 3 | SourceTable |  |  |
| 4 | Filter | 0.0811149 | nofuse |
| 5 | AntiJoin | 0.501175 |  |
| 6 | Reorder | 0.00305055 |  |
| 7 | EqJoin | 1.46021 | sort_merge_gfur |
| 8 | Reorder | 0.00787064 |  |
| 9 | Distinct | 0.625677 | hash |
| 10 | Reorder | 0.00768068 |  |
| 11 | GroupBy | 0.331337 | hash |
| 12 | Sort | 1.68011 | no_skf |
|  | Total | 5.30458 |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q16.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q16.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q16.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q16.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q16.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q16_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q17 Small-Quantity-Order Revenue Query

This query determines how much average yearly revenue would be lost if orders were no longer filled for small quantities of certain parts. This may reduce overhead expenses by concentrating sales on larger shipments.

```sql
SELECT
    sum(l_extendedprice) / 7.0 AS avg_yearly
FROM lineitem, part
WHERE (p_partkey = l_partkey)
    AND (p_brand = 'Brand#23')
    AND (p_container = 'MED BOX')
    AND (l_quantity < (
        SELECT 0.2 * avg(l_quantity)
        FROM lineitem
        WHERE (l_partkey = p_partkey)
    ));
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class PART,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.139752 | 0.139752 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 6.79768 | 3.58748 | hash_gfur | partition_hash_gfur |
| 4 | Reorder | 0.00300612 | 0.00300612 |  |  |
| 5 | Reorder | 0.00808376 | 0.00808376 |  |  |
| 6 | GroupBy | 0.129788 | 0.129788 | hash | hash |
| 7 | Project | 0.0115972 | 0.0115972 | nofuse | nofuse |
| 8 | EqJoin | 0.13391 | 0.13391 | hash_gfur | hash_gfur |
| 9 | Reorder | 0.00302071 | 0.00302071 |  |  |
| 10 | Filter | 0.0601487 | 0.0461784 | fuse | nofuse |
| 11 | Reorder | 0.00309835 | 0.00309835 |  |  |
| 12 | ScalarAgg | 0.0320654 | 0.0320654 |  |  |
| 13 | Project | 0.0114536 | 0.0114536 | nofuse | nofuse |
|  | Total | 7.3336 | 4.10943 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q17.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q17.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q17.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q17.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q17.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q17_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q18 Large Volume Customer Query

The Large Volume Customer Query ranks customers based on their having placed a large quantity order. Large quantity orders are defined as those orders whose total quantity is above a certain level.

```sql
SELECT
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice,
    sum(l_quantity)
FROM customer, orders, lineitem
WHERE (o_orderkey IN (
        SELECT l_orderkey
        FROM lineitem
        GROUP BY l_orderkey
        HAVING sum(l_quantity) > 300
    ))
    AND (c_custkey = o_custkey)
    AND (o_orderkey = l_orderkey)
GROUP BY
    c_name,
    c_custkey,
    o_orderkey,
    o_orderdate,
    o_totalprice
ORDER BY
    o_totalprice DESC,
    o_orderdate
LIMIT 100;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class CUSTOMER,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | SourceTable |  |  |  |  |
| 2 | Reorder | 0.00310639 | 0.00310639 |  |  |
| 3 | GroupBy | 5.06942 | 5.06942 | hash | hash |
| 4 | Filter | 0.27425 | 0.194295 | fuse | nofuse |
| 5 | EqJoin | 1.22586 | 1.22586 | hash_gfur | hash_gfur |
| 6 | Reorder | 0.00305385 | 0.00305385 |  |  |
| 7 | SourceTable |  |  |  |  |
| 8 | EqJoin | 0.339379 | 0.339379 | hash_gfur | hash_gfur |
| 9 | Reorder | 0.00599307 | 0.00599307 |  |  |
| 10 | Project | 0.0824401 | 0.0824401 | nofuse | nofuse |
| 11 | TopK | 0.506281 | 0.506281 |  |  |
|  | Total | 7.50978 | 7.42983 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q18.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q18.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q18.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q18.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q18.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q18_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q19 Discounted Revenue Query

The Discounted Revenue Query reports the gross discounted revenue attributed to the sale of selected parts handled in a particular manner. This query is an example of code such as might be produced programmatically by a data mining tool.

```sql
SELECT
    sum(l_extendedprice * (1 - l_discount)) AS revenue
FROM lineitem, part
WHERE (
        (p_partkey = l_partkey)
        AND (p_brand = 'Brand#12')
        AND (p_container IN ('SM CASE', 'SM BOX', 'SM PACK', 'SM PKG'))
        AND (l_quantity >= 1) AND (l_quantity <= 1 + 10)
        AND (p_size BETWEEN 1 AND 5)
        AND (l_shipmode IN ('AIR', 'AIR REG'))
        AND (l_shipinstruct = 'DELIVER IN PERSON')
    )
    OR (
        (p_partkey = l_partkey)
        AND (p_brand = 'Brand#23')
        AND (p_container IN ('MED BAG', 'MED BOX', 'MED PKG', 'MED PACK'))
        AND (l_quantity >= 10) AND (l_quantity <= 10 + 10)
        AND (p_size BETWEEN 1 AND 10)
        AND (l_shipmode IN ('AIR', 'AIR REG'))
        AND (l_shipinstruct = 'DELIVER IN PERSON')
    )
    OR (
        (p_partkey = l_partkey)
        AND (p_brand = 'Brand#34')
        AND (p_container IN ('LG CASE', 'LG BOX', 'LG PACK', 'LG PKG'))
        AND (l_quantity >= 20) AND (l_quantity <= 20 + 10)
        AND (p_size BETWEEN 1 AND 15)
        AND (l_shipmode IN ('AIR', 'AIR REG'))
        AND (l_shipinstruct = 'DELIVER IN PERSON')
    );
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class PART,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 2.79634 | 2.79634 | fuse | fuse |
| 2 | Project | 0.00310839 | 0.00310839 | nofuse | nofuse |
| 3 | SourceTable |  |  |  |  |
| 4 | EqJoin | 1.02685 | 1.02685 | hash_gfur | hash_gfur |
| 5 | Reorder | 0.00723984 | 0.00723984 |  |  |
| 6 | Filter | 1.0221 | 0.677223 | fuse | nofuse |
| 7 | Project | 0.020971 | 0.020971 | nofuse | nofuse |
| 8 | Reorder | 0.00300957 | 0.00300957 |  |  |
| 9 | ScalarAgg | 0.0299115 | 0.0299115 |  |  |
|  | Total | 4.90953 | 4.56465 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q19.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q19.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q19.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q19.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q19.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q19_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q20 Potential Part Promotion Query

The Potential Part Promotion Query identifies suppliers in a particular nation having selected parts that may be candidates for a promotional offer.

```sql
SELECT
    s_name,
    s_address
FROM supplier, nation
WHERE (s_suppkey IN (
        SELECT ps_suppkey
        FROM partsupp
        WHERE (ps_partkey IN (
                SELECT p_partkey
                FROM part
                WHERE (p_name LIKE 'forest%')
            ))
            AND (ps_availqty > (
                SELECT 0.5 * sum(l_quantity)
                FROM lineitem
                WHERE (l_partkey = ps_partkey)
                    AND (l_suppkey = ps_suppkey)
                    AND (l_shipdate >= date '1994-01-01')
                    AND (l_shipdate < date '1994-01-01' + INTERVAL 1 YEAR)
            ))
    ))
    AND (s_nationkey = n_nationkey)
    AND (n_name = 'CANADA')
ORDER BY s_name;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class NATION,SUPPLIER,PART,PARTSUPP,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.0584176 | 0.0584176 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.226944 | 0.226944 | hash_gfur | hash_gfur |
| 4 | Reorder | 0.00729248 | 0.00729248 |  |  |
| 5 | Project | 0.136075 | 0.136075 | nofuse | nofuse |
| 6 | SourceTable |  |  |  |  |
| 7 | SemiJoin | 0.483162 | 0.483162 |  |  |
| 8 | Reorder | 0.0031033 | 0.0031033 |  |  |
| 9 | SourceTable |  |  |  |  |
| 10 | Filter | 0.0931647 | 0.0931647 | fuse | fuse |
| 11 | SemiJoin | 0.109158 | 0.109158 |  |  |
| 12 | Reorder | 0.00309767 | 0.00309767 |  |  |
| 13 | SourceTable |  |  |  |  |
| 14 | Filter | 1.9012 | 1.0656 | fuse | nofuse |
| 15 | EqJoin | 1.16194 | 1.16194 | hash_gfur | hash_gfur |
| 16 | Reorder | 0.00315956 | 0.00315956 |  |  |
| 17 | Filter | 0.116621 | 0.102911 | fuse | nofuse |
| 18 | Reorder | 0.00311209 | 0.00311209 |  |  |
| 19 | GroupBy | 0.124026 | 0.124026 | hash | hash |
| 20 | Project | 0.0110678 | 0.0110678 | nofuse | nofuse |
| 21 | EqJoin | 0.119206 | 0.119206 | hash_gfur | hash_gfur |
| 22 | Reorder | 0.00309767 | 0.00309767 |  |  |
| 23 | Filter | 0.104709 | 0.0916693 | fuse | nofuse |
| 24 | Filter | 0.0498792 | 0.0382853 | fuse | nofuse |
| 25 | SemiJoin | 0.204173 | 0.204173 |  |  |
| 26 | Reorder | 0.0074996 | 0.0074996 |  |  |
| 27 | Project | 0.131172 | 0.131172 | nofuse | nofuse |
| 28 | Sort | 0.369399 | 0.369399 | no_skf | no_skf |
|  | Total | 5.43068 | 4.55673 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q20.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q20.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q20.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q20.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q20.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q20_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q21 Suppliers Who Kept Orders Waiting Query

This query identifies certain suppliers who were not able to ship required parts in a timely manner.

```sql
SELECT
    s_name,
    count(*) AS numwait
FROM supplier, lineitem AS l1, orders, nation
WHERE (s_suppkey = l1.l_suppkey)
    AND (o_orderkey = l1.l_orderkey)
    AND (o_orderstatus = 'F')
    AND (l1.l_receiptdate > l1.l_commitdate)
    AND EXISTS (
        SELECT *
        FROM lineitem AS l2
        WHERE (l2.l_orderkey = l1.l_orderkey)
            AND (l2.l_suppkey <> l1.l_suppkey)
    )
    AND NOT EXISTS (
        SELECT *
        FROM lineitem AS l3
        WHERE (l3.l_orderkey = l1.l_orderkey)
            AND (l3.l_suppkey <> l1.l_suppkey)
            AND (l3.l_receiptdate > l3.l_commitdate)
    )
    AND (s_nationkey = n_nationkey)
    AND (n_name = 'SAUDI ARABIA')
GROUP BY s_name
ORDER BY
    numwait DESC,
    s_name
LIMIT 100;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class NATION,SUPPLIER,ORDERS,LINEITEM active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 0.0567973 | 0.0567973 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | Filter | 1.09018 | 0.790027 | fuse | nofuse |
| 4 | SourceTable |  |  |  |  |
| 5 | Distinct | 14.0313 | 8.9001 | hash | sort_skf |
| 6 | Reorder | 0.00309333 | 0.00309333 |  |  |
| 7 | GroupBy | 5.53234 | 5.53234 | hash | hash |
| 8 | Filter | 0.227179 | 0.160523 | fuse | nofuse |
| 9 | SemiJoin | 2.7431 | 2.7431 |  |  |
| 10 | Reorder | 0.00309867 | 0.00309867 |  |  |
| 11 | Distinct | 8.83483 | 5.85235 | hash | sort_skf |
| 12 | Reorder | 0.00308267 | 0.00308267 |  |  |
| 13 | GroupBy | 4.24377 | 3.93013 | hash | partition_gftr |
| 14 | Filter | 0.19748 | 0.136115 | fuse | nofuse |
| 15 | SemiJoin | 2.01023 | 2.01023 |  |  |
| 16 | Reorder | 0.00319467 | 0.00319467 |  |  |
| 17 | SourceTable |  |  |  |  |
| 18 | EqJoin | 0.702605 | 0.702605 | hash_gfur | hash_gfur |
| 19 | Reorder | 0.00585333 | 0.00585333 |  |  |
| 20 | SourceTable |  |  |  |  |
| 21 | Filter | 0.227664 | 0.227664 | fuse | fuse |
| 22 | EqJoin | 1.64034 | 1.64034 | hash_gfur | hash_gfur |
| 23 | Reorder | 0.00579733 | 0.00579733 |  |  |
| 24 | EqJoin | 0.283723 | 0.283723 | hash_gfur | hash_gfur |
| 25 | Reorder | 0.005192 | 0.005192 |  |  |
| 26 | Reorder | 0.003016 | 0.003016 |  |  |
| 27 | GroupBy | 0.174853 | 0.174853 | hash | hash |
| 28 | TopK | 1.09594 | 1.09594 |  |  |
|  | Total | 43.1247 | 34.2692 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q21.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q21.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q21.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q21.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q21.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q21_comparison.jpg" alt="GH200 SF100" width="200"> |

# Q22 Global Sales Opportunity Query

The Global Sales Opportunity Query identifies geographies where there are customers who may be likely to make a purchase.

```sql
SELECT
    cntrycode,
    count(*) AS numcust,
    sum(c_acctbal) AS totacctbal
FROM (
    SELECT
        substring(c_phone FROM 1 FOR 2) AS cntrycode,
        c_acctbal
    FROM customer
    WHERE (substring(c_phone FROM 1 FOR 2) IN ('13', '31', '23', '29', '30', '18', '17'))
        AND (c_acctbal > (
            SELECT avg(c_acctbal)
            FROM customer
            WHERE (c_acctbal > 0.00)
                AND (substring(c_phone FROM 1 FOR 2) IN ('13', '31', '23', '29', '30', '18', '17'))
        ))
        AND NOT EXISTS (
            SELECT *
            FROM orders
            WHERE (o_custkey = c_custkey)
        )
) AS custsale
GROUP BY cntrycode
ORDER BY cntrycode;
```
```mermaid
flowchart LR
    REGION --> NATION
    NATION --> SUPPLIER
    NATION --> CUSTOMER
    CUSTOMER --> ORDERS
    ORDERS --> LINEITEM
    PART --> PARTSUPP
    SUPPLIER --> PARTSUPP
    PART --> LINEITEM
    SUPPLIER --> LINEITEM
    PARTSUPP --> LINEITEM
    classDef active fill:#d1fae5,stroke:#059669,stroke-width:1px,color:#064e3b
    class CUSTOMER,ORDERS active
```

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Project | 0.117342 | 0.117342 | nofuse | nofuse |
| 2 | Filter | 0.251124 | 0.251124 | fuse | fuse |
| 3 | Filter | 0.0605121 | 0.0512898 | fuse | nofuse |
| 4 | Reorder | 0.00312369 | 0.00312369 |  |  |
| 5 | ScalarAgg | 0.0345893 | 0.0345893 |  |  |
| 6 | CrossJoin | 0.122071 | 0.122071 |  |  |
| 7 | Filter | 0.195488 | 0.183978 | fuse | nofuse |
| 8 | SourceTable |  |  |  |  |
| 9 | AntiJoin | 1.01497 | 1.01497 |  |  |
| 10 | Reorder | 0.00575768 | 0.00575768 |  |  |
| 11 | Reorder | 0.00301238 | 0.00301238 |  |  |
| 12 | GroupBy | 0.157869 | 0.157869 | hash | hash |
| 13 | Sort | 0.13226 | 0.13226 | no_skf | no_skf |
|  | Total | 2.09812 | 2.07739 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q22.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q22.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q22.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q22.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q22.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q22_comparison.jpg" alt="GH200 SF100" width="200"> |

## Runtime breakdown legend

![Runtime breakdown legend|200x0](assets/runtime-breakdowns/H200_SF10_legend.jpg)
