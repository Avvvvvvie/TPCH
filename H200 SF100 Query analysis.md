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
| 1 | Filter | 45.1205 | 40.6921 | fuse | nofuse |
| 2 | Project | 16.7906 | 16.7906 | nofuse | nofuse |
| 3 | Reorder | 0.003272 | 0.003272 |  |  |
| 4 | GroupBy | 67.6028 | 67.6028 | hash | hash |
| 5 | Sort | 0.506816 | 0.506816 | no_skf | no_skf |
|  | Total | 130.024 | 125.596 |  |  |

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
| 1 | Filter | 0.0575897 | 0.0575897 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.154442 | 0.124894 | hash_gfur | sort_merge_gfur |
| 4 | Reorder | 0.00489703 | 0.00489703 |  |  |
| 5 | Project | 0.0622751 | 0.0622751 | nofuse | nofuse |
| 6 | SourceTable |  |  |  |  |
| 7 | SourceTable |  |  |  |  |
| 8 | SourceTable |  |  |  |  |
| 9 | Filter | 0.782429 | 0.624115 | fuse | nofuse |
| 10 | Filter | 0.175655 | 0.175655 | fuse | fuse |
| 11 | Project | 0.00284077 | 0.00284077 | nofuse | nofuse |
| 12 | EqJoin | 9.36994 | 4.07891 | hash_gfur | partition_hash_gfur |
| 13 | Reorder | 0.00586116 | 0.00586116 |  |  |
| 14 | EqJoin | 1.11779 | 1.11779 | hash_gfur | hash_gfur |
| 15 | Reorder | 0.0128805 | 0.0128805 |  |  |
| 16 | Project | 0.79621 | 0.79621 | nofuse | nofuse |
| 17 | EqJoin | 0.619121 | 0.619121 | hash_gfur | hash_gfur |
| 18 | Reorder | 0.0153899 | 0.0153899 |  |  |
| 19 | Project | 0.476142 | 0.476142 | nofuse | nofuse |
| 20 | Reorder | 0.0216547 | 0.0216547 |  |  |
| 21 | GroupBy | 0.08784 | 0.08784 | hash | hash |
| 22 | Project | 0.00289548 | 0.00289548 | nofuse | nofuse |
| 23 | EqJoin | 0.564072 | 0.564072 | hash_gfur | hash_gfur |
| 24 | Reorder | 0.0149533 | 0.0149533 |  |  |
| 25 | Filter | 0.592584 | 0.592584 | fuse | fuse |
| 26 | Project | 0.004 | 0.004 | nofuse | nofuse |
| 27 | TopK | 1.57315 | 1.57315 |  |  |
|  | Total | 16.5146 | 11.0357 |  |  |

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
| 1 | Filter | 0.304635 | 0.304635 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | Filter | 3.54525 | 2.42647 | fuse | nofuse |
| 4 | EqJoin | 13.077 | 5.57284 | hash_gfur | partition_hash_gfur |
| 5 | Reorder | 0.00296686 | 0.00296686 |  |  |
| 6 | SourceTable |  |  |  |  |
| 7 | Filter | 13.6882 | 9.24604 | fuse | nofuse |
| 8 | EqJoin | 42.8812 | 13.5203 | hash_gfur | partition_hash_gfur |
| 9 | Reorder | 0.00315429 | 0.00315429 |  |  |
| 10 | Project | 0.091456 | 0.091456 | nofuse | nofuse |
| 11 | Reorder | 0.00293029 | 0.00293029 |  |  |
| 12 | GroupBy | 0.417605 | 0.417605 | hash | hash |
| 13 | Project | 0.00289371 | 0.00289371 | nofuse | nofuse |
| 14 | TopK | 0.896402 | 0.896402 |  |  |
|  | Total | 74.9137 | 32.4877 |  |  |

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
| 1 | Filter | 4.97032 | 2.8785 | fuse | nofuse |
| 2 | SourceTable |  |  |  |  |
| 3 | Filter | 7.0624 | 4.15926 | fuse | nofuse |
| 4 | SemiJoin | 25.9175 | 25.9175 |  |  |
| 5 | Reorder | 0.00668554 | 0.00668554 |  |  |
| 6 | Reorder | 0.00293662 | 0.00293662 |  |  |
| 7 | GroupBy | 0.386678 | 0.386678 | hash | hash |
| 8 | Sort | 0.134634 | 0.134634 | no_skf | no_skf |
|  | Total | 38.4812 | 33.4862 |  |  |

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
| 2 | Filter | 3.94944 | 1.85392 | fuse | nofuse |
| 3 | EqJoin | 8.98645 | 3.43966 | hash_gfur | partition_hash_gftr |
| 4 | Reorder | 0.002968 | 0.002968 |  |  |
| 5 | SourceTable |  |  |  |  |
| 6 | EqJoin | 87.8133 | 30.2589 | hash_gfur | partition_hash_gfur |
| 7 | Reorder | 0.002904 | 0.002904 |  |  |
| 8 | SourceTable |  |  |  |  |
| 9 | Filter | 0.059224 | 0.059224 | fuse | fuse |
| 10 | SourceTable |  |  |  |  |
| 11 | EqJoin | 0.160824 | 0.130197 | hash_gfur | sort_merge_gfur |
| 12 | Reorder | 0.007024 | 0.007024 |  |  |
| 13 | SourceTable |  |  |  |  |
| 14 | EqJoin | 0.294264 | 0.231589 | hash_gfur | sort_merge_gfur |
| 15 | Reorder | 0.005328 | 0.005328 |  |  |
| 16 | EqJoin | 31.1792 | 19.6041 | hash_gfur | sort_merge_gfur |
| 17 | Reorder | 0.007104 | 0.007104 |  |  |
| 18 | Filter | 0.609256 | 0.555296 | fuse | nofuse |
| 19 | Project | 0.028784 | 0.028784 | nofuse | nofuse |
| 20 | Reorder | 0.002856 | 0.002856 |  |  |
| 21 | GroupBy | 0.138912 | 0.138912 | hash | hash |
| 22 | Sort | 0.084856 | 0.084856 | no_skf | no_skf |
|  | Total | 133.333 | 56.4136 |  |  |

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
| 1 | Filter | 34.2253 | 12.7669 | fuse | nofuse |
| 2 | Project | 0.0734229 | 0.0734229 | nofuse | nofuse |
| 3 | Reorder | 0.00288213 | 0.00288213 |  |  |
| 4 | ScalarAgg | 0.0600149 | 0.0600149 |  |  |
|  | Total | 34.3616 | 12.9032 |  |  |

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
| 1 | Filter | 0.145513 | 0.145513 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.258967 | 0.219684 | hash_gfur | sort_merge_gfur |
| 4 | Reorder | 0.00461714 | 0.00461714 |  |  |
| 5 | SourceTable |  |  |  |  |
| 6 | Filter | 22.0416 | 13.5634 | fuse | nofuse |
| 7 | EqJoin | 25.0451 | 9.98921 | hash_gfur | partition_hash_gfur |
| 8 | Reorder | 0.00822857 | 0.00822857 |  |  |
| 9 | SourceTable |  |  |  |  |
| 10 | EqJoin | 29.468 | 11.741 | hash_gfur | partition_hash_gfur |
| 11 | Reorder | 0.00670171 | 0.00670171 |  |  |
| 12 | SourceTable |  |  |  |  |
| 13 | Filter | 0.154432 | 0.154432 | fuse | fuse |
| 14 | SourceTable |  |  |  |  |
| 15 | EqJoin | 1.8371 | 0.909451 | hash_gfur | sort_merge_gfur |
| 16 | Reorder | 0.00545829 | 0.00545829 |  |  |
| 17 | EqJoin | 2.20927 | 2.20927 | hash_gfur | hash_gfur |
| 18 | Reorder | 0.009088 | 0.009088 |  |  |
| 19 | Filter | 0.489824 | 0.489824 | fuse | fuse |
| 20 | Project | 0.0485897 | 0.0485897 | nofuse | nofuse |
| 21 | Reorder | 0.00294857 | 0.00294857 |  |  |
| 22 | GroupBy | 0.247127 | 0.247127 | hash | hash |
| 23 | Sort | 0.532229 | 0.532229 | no_skf | no_skf |
|  | Total | 82.5148 | 40.2868 |  |  |

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
| 1 | Filter | 0.05712 | 0.05712 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.0976 | 0.0702446 | hash_gfur | sort_merge_gfur |
| 4 | Reorder | 0.0027776 | 0.0027776 |  |  |
| 5 | SourceTable |  |  |  |  |
| 6 | EqJoin | 1.99967 | 0.837288 | hash_gfur | sort_merge_gftr |
| 7 | Reorder | 0.0028736 | 0.0028736 |  |  |
| 8 | SourceTable |  |  |  |  |
| 9 | Filter | 4.38076 | 2.27523 | fuse | nofuse |
| 10 | EqJoin | 8.4653 | 5.85453 | hash_gfur | sort_merge_gfur |
| 11 | Reorder | 0.002752 | 0.002752 |  |  |
| 12 | SourceTable |  |  |  |  |
| 13 | EqJoin | 82.0811 | 63.2312 | hash_gfur | sort_merge_gfur |
| 14 | Reorder | 0.002816 | 0.002816 |  |  |
| 15 | SourceTable |  |  |  |  |
| 16 | Filter | 0.334035 | 0.334035 | fuse | fuse |
| 17 | EqJoin | 3.14402 | 3.14402 | hash_gfur | hash_gfur |
| 18 | Reorder | 0.002976 | 0.002976 |  |  |
| 19 | SourceTable |  |  |  |  |
| 20 | EqJoin | 0.389421 | 0.389421 | hash_gfur | hash_gfur |
| 21 | Reorder | 0.0029056 | 0.0029056 |  |  |
| 22 | SourceTable |  |  |  |  |
| 23 | EqJoin | 11.07 | 3.87239 | hash_gfur | sort_merge_gfur |
| 24 | Reorder | 0.0097344 | 0.0097344 |  |  |
| 25 | Project | 0.097088 | 0.097088 | nofuse | nofuse |
| 26 | Project | 0.0272832 | 0.0272832 | nofuse | nofuse |
| 27 | Project | 0.0139136 | 0.0139136 | nofuse | nofuse |
| 28 | Reorder | 0.0028992 | 0.0028992 |  |  |
| 29 | GroupBy | 0.107891 | 0.107891 | hash | hash |
| 30 | Project | 0.0131904 | 0.0131904 | nofuse | nofuse |
| 31 | Sort | 0.0146048 | 0.0146048 | no_skf | no_skf |
|  | Total | 112.323 | 80.3692 |  |  |

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
| 2 | Filter | 1.41135 | 1.41135 | fuse | fuse |
| 3 | SourceTable |  |  |  |  |
| 4 | EqJoin | 83.4647 | 28.2872 | hash_gfur | partition_hash_gfur |
| 5 | Reorder | 0.002744 | 0.002744 |  |  |
| 6 | SourceTable |  |  |  |  |
| 7 | EqJoin | 14.5657 | 8.19771 | hash_gfur | sort_merge_gfur |
| 8 | Reorder | 0.00292 | 0.00292 |  |  |
| 9 | SourceTable |  |  |  |  |
| 10 | EqJoin | 31.8466 | 25.3054 | hash_gfur | partition_hash_gfur |
| 11 | Reorder | 0.003056 | 0.003056 |  |  |
| 12 | Filter | 4.19682 | 3.73646 | fuse | nofuse |
| 13 | SourceTable |  |  |  |  |
| 14 | EqJoin | 47.5837 | 12.0011 | hash_gfur | partition_hash_gftr |
| 15 | Reorder | 0.002832 | 0.002832 |  |  |
| 16 | EqJoin | 7.92334 | 7.92334 | hash_gfur | hash_gfur |
| 17 | Reorder | 0.008912 | 0.008912 |  |  |
| 18 | Project | 2.4129 | 2.4129 | nofuse | nofuse |
| 19 | Reorder | 0.007368 | 0.007368 |  |  |
| 20 | GroupBy | 1.75085 | 1.75085 | hash | hash |
| 21 | Sort | 0.5788 | 0.5788 | no_skf | no_skf |
|  | Total | 195.763 | 91.6329 |  |  |

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
| 3 | Filter | 11.111 | 11.111 | nofuse | nofuse |
| 4 | SourceTable |  |  |  |  |
| 5 | Filter | 1.82326 | 1.82326 | nofuse | nofuse |
| 6 | EqJoin | 18.238 | 15.9504 | hash_gfur | sort_merge_gfur |
| 7 | Reorder | 0.00290844 | 0.00290844 |  |  |
| 8 | Project | 0.180722 | 0.180722 | nofuse | nofuse |
| 9 | Reorder | 0.00293333 | 0.00293333 |  |  |
| 10 | GroupBy | 3.52245 | 3.52245 | partition_gfur | partition_gfur |
| 11 | EqJoin | 9.18904 | 8.10676 | hash_gfur | sort_merge_gfur |
| 12 | Reorder | 0.0111396 | 0.0111396 |  |  |
| 13 | EqJoin | 6.51447 | 6.51447 | hash_gfur | hash_gfur |
| 14 | Reorder | 0.0153173 | 0.0153173 |  |  |
| 15 | Project | 5.82231 | 5.82231 | nofuse | nofuse |
| 16 | TopK | 0.711268 | 0.711268 |  |  |
|  | Total | 57.1448 | 53.7749 |  |  |

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
| 2 | Filter | 0.0584573 | 0.0584573 | nofuse | nofuse |
| 3 | SourceTable |  |  |  |  |
| 4 | EqJoin | 0.194377 | 0.122626 | hash_gfur | sort_merge_gfur |
| 5 | Reorder | 0.00299333 | 0.00299333 |  |  |
| 6 | EqJoin | 19.802 | 6.64311 | hash_gfur | partition_hash_gfur |
| 7 | Reorder | 0.00300667 | 0.00300667 |  |  |
| 8 | Project | 0.083872 | 0.04742 | fuse | nofuse |
| 9 | Reorder | 0.0349907 | 0.0349907 |  |  |
| 10 | GroupBy | 0.690875 | 0.49928 | hash | sort_gftr_opt |
| 11 | Reorder | 0.00292533 | 0.00292533 |  |  |
| 12 | ScalarAgg | 0.0407467 | 0.0407467 |  |  |
| 13 | Project | 0.0163133 | 0.0111347 | fuse | nofuse |
| 14 | CrossJoin | 0.112616 | 0.112616 |  |  |
| 15 | Filter | 0.116465 | 0.116465 | nofuse | nofuse |
| 16 | Project | 0.00294667 | 0.00294667 | fuse | fuse |
| 17 | Sort | 0.00292667 | 0.00292667 | no_skf | no_skf |
|  | Total | 21.1655 | 7.70165 |  |  |

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
| 2 | Filter | 39.6031 | 24.9544 | fuse | nofuse |
| 3 | EqJoin | 13.1556 | 13.1556 | hash_gfur | hash_gfur |
| 4 | Reorder | 0.0082272 | 0.0082272 |  |  |
| 5 | Project | 0.279146 | 0.279146 | nofuse | nofuse |
| 6 | Project | 0.0821856 | 0.0821856 | nofuse | nofuse |
| 7 | Reorder | 0.0029408 | 0.0029408 |  |  |
| 8 | GroupBy | 0.282989 | 0.282989 | hash | hash |
| 9 | Sort | 0.137731 | 0.137731 | no_skf | no_skf |
|  | Total | 53.5519 | 38.9032 |  |  |

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
| 2 | Filter | 14.0868 | 14.0868 | nofuse | nofuse |
| 3 | EqJoin | 52.5854 | 12.6386 | hash_gfur | partition_hash_gfur |
| 4 | Reorder | 0.0029376 | 0.0029376 |  |  |
| 5 | Reorder | 0.0030464 | 0.0030464 |  |  |
| 6 | GroupBy | 25.6306 | 10.891 | hash | partition_gftr |
| 7 | AntiJoin | 9.42924 | 9.42924 |  |  |
| 8 | Reorder | 0.0028352 | 0.0028352 |  |  |
| 9 | Project | 0.0461888 | 0.0461888 | nofuse | nofuse |
| 10 | Concat | 0.141702 | 0.141702 |  |  |
| 11 | Reorder | 0.0031424 | 0.0031424 |  |  |
| 12 | GroupBy | 0.539571 | 0.539571 | hash | hash |
| 13 | Sort | 0.265696 | 0.265696 | no_skf | no_skf |
|  | Total | 102.737 | 48.0508 |  |  |

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
| 1 | Filter | 17.3706 | 8.95107 | fuse | nofuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 6.94963 | 4.58478 | hash_gfur | partition_hash_gfur |
| 4 | Reorder | 0.00667276 | 0.00667276 |  |  |
| 5 | Project | 0.209675 | 0.209675 | nofuse | nofuse |
| 6 | Project | 0.0530118 | 0.0530118 | nofuse | nofuse |
| 7 | Reorder | 0.00285105 | 0.00285105 |  |  |
| 8 | ScalarAgg | 0.0933592 | 0.0933592 |  |  |
| 9 | Project | 0.0212785 | 0.0212785 | nofuse | nofuse |
|  | Total | 24.7071 | 13.9227 |  |  |

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
| 2 | Filter | 17.6962 | 9.27094 | fuse | nofuse |
| 3 | Project | 0.236273 | 0.236273 | nofuse | nofuse |
| 4 | Reorder | 0.0029 | 0.0029 |  |  |
| 5 | GroupBy | 2.09492 | 2.09492 | hash | hash |
| 6 | Reorder | 0.0102307 | 0.0102307 |  |  |
| 7 | ScalarAgg | 0.0325333 | 0.0325333 |  |  |
| 8 | CrossJoin | 0.0679853 | 0.0679853 |  |  |
| 9 | Filter | 0.097264 | 0.0834584 | fuse | nofuse |
| 10 | EqJoin | 0.312148 | 0.312148 | hash_gfur | hash_gfur |
| 11 | Reorder | 0.00893467 | 0.00893467 |  |  |
| 12 | Project | 0.182763 | 0.182763 | nofuse | nofuse |
| 13 | Sort | 0.209973 | 0.209973 | no_skf | no_skf |
|  | Total | 20.9521 | 12.5131 |  |  |

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

| Step | Step kind | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation |
| --- | --- | --- | --- | --- | --- |
| 0 | SourceTable |  |  |  |  |
| 1 | Filter | 3.3117 | 2.38065 | fuse | nofuse |
| 2 | SourceTable |  |  |  |  |
| 3 | SourceTable |  |  |  |  |
| 4 | Filter | 0.1404 | 0.1404 | fuse | fuse |
| 5 | AntiJoin | 4.07513 | 4.07513 |  |  |
| 6 | Reorder | 0.00294756 | 0.00294756 |  |  |
| 7 | EqJoin | 13.3018 | 6.8942 | hash_gfur | partition_hash_gfur |
| 8 | Reorder | 0.00777956 | 0.00777956 |  |  |
| 9 | Distinct | 5.38999 | 5.38999 | hash | hash |
| 10 | Reorder | 0.00710578 | 0.00710578 |  |  |
| 11 | GroupBy | 1.28193 | 1.28193 | hash | hash |
| 12 | Sort | 1.32812 | 1.32812 | no_skf | no_skf |
|  | Total | 28.8469 | 21.5083 |  |  |

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
| 1 | Filter | 0.601256 | 0.601256 | nofuse | nofuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 68.507 | 21.5718 | hash_gfur | partition_hash_gfur |
| 4 | Reorder | 0.003052 | 0.003052 |  |  |
| 5 | Reorder | 0.018472 | 0.018472 |  |  |
| 6 | GroupBy | 0.230132 | 0.230132 | sort_gfur | sort_gfur |
| 7 | Project | 0.013436 | 0.013436 | nofuse | nofuse |
| 8 | EqJoin | 0.23364 | 0.23364 | hash_gfur | hash_gfur |
| 9 | Reorder | 0.002932 | 0.002932 |  |  |
| 10 | Filter | 0.050732 | 0.050732 | nofuse | nofuse |
| 11 | Reorder | 0.002976 | 0.002976 |  |  |
| 12 | ScalarAgg | 0.0309 | 0.0309 |  |  |
| 13 | Project | 0.012416 | 0.012416 | nofuse | nofuse |
|  | Total | 69.7069 | 22.7717 |  |  |

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
| 2 | Reorder | 0.002936 | 0.002936 |  |  |
| 3 | GroupBy | 50.2635 | 47.6114 | hash | partition_gftr |
| 4 | Filter | 2.1528 | 1.37173 | fuse | nofuse |
| 5 | EqJoin | 11.6483 | 11.6483 | hash_gfur | hash_gfur |
| 6 | Reorder | 0.00294 | 0.00294 |  |  |
| 7 | SourceTable |  |  |  |  |
| 8 | EqJoin | 1.88825 | 1.73671 | hash_gfur | sort_merge_gfur |
| 9 | Reorder | 0.006028 | 0.006028 |  |  |
| 10 | Project | 0.08108 | 0.08108 | nofuse | nofuse |
| 11 | TopK | 0.615056 | 0.615056 |  |  |
|  | Total | 66.6609 | 63.0762 |  |  |

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
| 1 | Filter | 26.07 | 26.07 | fuse | fuse |
| 2 | Project | 0.00296 | 0.00296 | nofuse | nofuse |
| 3 | SourceTable |  |  |  |  |
| 4 | EqJoin | 12.1951 | 8.13585 | hash_gfur | partition_hash_gfur |
| 5 | Reorder | 0.009376 | 0.009376 |  |  |
| 6 | Filter | 5.31573 | 3.526 | fuse | nofuse |
| 7 | Project | 0.0224853 | 0.0224853 | nofuse | nofuse |
| 8 | Reorder | 0.00286133 | 0.00286133 |  |  |
| 9 | ScalarAgg | 0.033728 | 0.033728 |  |  |
|  | Total | 43.6522 | 37.8033 |  |  |

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
| 1 | Filter | 0.0579904 | 0.0548952 | fuse | nofuse |
| 2 | SourceTable |  |  |  |  |
| 3 | EqJoin | 0.342086 | 0.292699 | hash_gfur | sort_merge_gfur |
| 4 | Reorder | 0.00752427 | 0.00752427 |  |  |
| 5 | Project | 0.147763 | 0.147763 | nofuse | nofuse |
| 6 | SourceTable |  |  |  |  |
| 7 | SemiJoin | 3.91161 | 3.91161 |  |  |
| 8 | Reorder | 0.00290133 | 0.00290133 |  |  |
| 9 | SourceTable |  |  |  |  |
| 10 | Filter | 0.358187 | 0.358187 | fuse | fuse |
| 11 | SemiJoin | 0.259851 | 0.259851 |  |  |
| 12 | Reorder | 0.00286507 | 0.00286507 |  |  |
| 13 | SourceTable |  |  |  |  |
| 14 | Filter | 17.8253 | 9.39103 | fuse | nofuse |
| 15 | EqJoin | 10.5945 | 4.67836 | hash_gfur | partition_hash_gfur |
| 16 | Reorder | 0.00294187 | 0.00294187 |  |  |
| 17 | Filter | 0.119812 | 0.10547 | fuse | nofuse |
| 18 | Reorder | 0.00296747 | 0.00296747 |  |  |
| 19 | GroupBy | 0.101035 | 0.101035 | hash | hash |
| 20 | Project | 0.0129963 | 0.0129963 | nofuse | nofuse |
| 21 | EqJoin | 0.123287 | 0.123287 | hash_gfur | hash_gfur |
| 22 | Reorder | 0.00300587 | 0.00300587 |  |  |
| 23 | Filter | 0.114524 | 0.103279 | fuse | nofuse |
| 24 | Filter | 0.0545728 | 0.0429844 | fuse | nofuse |
| 25 | SemiJoin | 0.217805 | 0.217805 |  |  |
| 26 | Reorder | 0.00765867 | 0.00765867 |  |  |
| 27 | Project | 0.132499 | 0.132499 | nofuse | nofuse |
| 28 | Sort | 0.623511 | 0.623511 | no_skf | no_skf |
|  | Total | 35.0272 | 20.5871 |  |  |

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
| 1 | Filter | 0.059256 | 0.059256 | fuse | fuse |
| 2 | SourceTable |  |  |  |  |
| 3 | Filter | 10.0174 | 7.1155 | fuse | nofuse |
| 4 | SourceTable |  |  |  |  |
| 5 | Distinct | 140.289 | 84.8111 | hash | sort_skf |
| 6 | Reorder | 0.003 | 0.003 |  |  |
| 7 | GroupBy | 52.5801 | 48.7716 | hash | partition_gftr |
| 8 | Filter | 1.80159 | 1.16376 | fuse | nofuse |
| 9 | SemiJoin | 26.8239 | 26.8239 |  |  |
| 10 | Reorder | 0.0032 | 0.0032 |  |  |
| 11 | Distinct | 88.8734 | 53.5904 | hash | sort_skf |
| 12 | Reorder | 0.002936 | 0.002936 |  |  |
| 13 | GroupBy | 40.1629 | 31.3653 | hash | partition_gftr |
| 14 | Filter | 1.4842 | 0.897184 | fuse | nofuse |
| 15 | SemiJoin | 19.4861 | 19.4861 |  |  |
| 16 | Reorder | 0.00288 | 0.00288 |  |  |
| 17 | SourceTable |  |  |  |  |
| 18 | EqJoin | 7.1316 | 5.77893 | hash_gfur | sort_merge_gfur |
| 19 | Reorder | 0.007624 | 0.007624 |  |  |
| 20 | SourceTable |  |  |  |  |
| 21 | Filter | 1.68442 | 1.68442 | fuse | fuse |
| 22 | EqJoin | 21.6843 | 7.78187 | hash_gfur | partition_hash_gfur |
| 23 | Reorder | 0.007208 | 0.007208 |  |  |
| 24 | EqJoin | 1.33366 | 0.785856 | hash_gfur | sort_merge_gfur |
| 25 | Reorder | 0.008096 | 0.008096 |  |  |
| 26 | Reorder | 0.003856 | 0.003856 |  |  |
| 27 | GroupBy | 0.188864 | 0.188864 | hash | hash |
| 28 | TopK | 1.69238 | 1.69238 |  |  |
|  | Total | 415.332 | 292.035 |  |  |

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
| 1 | Project | 0.485938 | 0.485938 | nofuse | nofuse |
| 2 | Filter | 0.819134 | 0.819134 | fuse | fuse |
| 3 | Filter | 0.109892 | 0.0803905 | fuse | nofuse |
| 4 | Reorder | 0.00295636 | 0.00295636 |  |  |
| 5 | ScalarAgg | 0.0411338 | 0.0411338 |  |  |
| 6 | CrossJoin | 0.28806 | 0.28806 |  |  |
| 7 | Filter | 0.373785 | 0.321051 | fuse | nofuse |
| 8 | SourceTable |  |  |  |  |
| 9 | AntiJoin | 9.06576 | 9.06576 |  |  |
| 10 | Reorder | 0.006504 | 0.006504 |  |  |
| 11 | Reorder | 0.00292727 | 0.00292727 |  |  |
| 12 | GroupBy | 0.188468 | 0.188468 | hash | hash |
| 13 | Sort | 0.135198 | 0.135198 | no_skf | no_skf |
|  | Total | 11.5198 | 11.4375 |  |  |

## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q22.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q22.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q22.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q22.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q22.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q22_comparison.jpg" alt="GH200 SF100" width="200"> |

## Runtime breakdown legend

![Runtime breakdown legend|200x0](assets/runtime-breakdowns/H200_SF100_legend.jpg)
