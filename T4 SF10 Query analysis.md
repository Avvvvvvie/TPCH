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

```sql
Sort[l_returnflag ASC, l_linestatus ASC]
  Aggregate(l_returnflag, l_linestatus; sum(l_quantity), sum(l_extendedprice), sum(disc_price), sum(charge), avg(l_quantity), avg(l_extendedprice), avg(l_discount), count_all(*))
    Project(l_returnflag, l_linestatus, l_quantity, l_extendedprice, l_discount, disc_price = (l_extendedprice * (1 - l_discount)), charge = ((l_extendedprice * (1 - l_discount)) * (1 + l_tax)))
      Filter((l_shipdate <= 19980902))
        Scan(lineitem [l_shipdate, l_returnflag, l_linestatus, l_quantity, l_extendedprice, l_discount, l_tax])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>l_returnflag ASC, l_linestatus ASC"]
    ir_1["Aggregate<br/>l_returnflag, l_linestatus; sum(l_quantity), sum(l_extendedprice), sum(disc_price), sum(charge), avg(l_quan..."]
    ir_0 --> ir_1
    ir_2["Project<br/>l_returnflag, l_linestatus, l_quantity, l_extendedprice, l_discount, disc_price = (l_extendedprice * (1 - l..."]
    ir_1 --> ir_2
    ir_3["Filter<br/>(l_shipdate &lt;= 19980902)"]
    ir_2 --> ir_3
    ir_4["Scan<br/>lineitem · l_shipdate, l_returnflag, l_linestatus, l_quantity, l_extendedprice, l_discount, l_tax"]
    ir_3 --> ir_4
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_4 source
    class ir_3 filter
    class ir_1 aggregate
    class ir_2 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Baseline implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 59986052 | 7 | lineitem |  |  |  | l_shipdate, l_returnflag, l_linestatus, l_quantity, l_extendedprice, l_discount, l_tax |
| 1 | Filter | 59142609 | 6 | < | 98.6% | 56.1025 | nofuse |  |
| 2 | Project | 59142609 | 7 |  |  | 13.0981 | fuse | l_returnflag, l_linestatus, l_quantity, l_extendedprice, l_discount, disc_price, charge |
| 3 | Reorder | 59142609 | 7 |  |  | 0.002568 |  |  |
| 4 | GroupBy | 4 | 10 | < | 0.00000676% | 112.201 | hash | l_returnflag, l_linestatus; sum(l_quantity), sum(l_extendedprice), sum(disc_price), sum(charge), avg(l_quantity), avg(l_extendedprice), avg(l_discount), count_all(*) |
| 5 | Sort | 4 | 10 |  |  | 0.53216 | no_skf | l_returnflag ASC, l_linestatus ASC |
|  | Total |  |  |  |  | 181.936 |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>lineitem<br/>l_shipdate, l_returnflag, l_linestatus, l_quantity, l_extendedprice, l_discount, l_tax<br/>59,986,052 × 7"]
    step_1["1 · Filter · 98.6%<br/>59,142,609 × 6"]
    step_0 --> step_1
    step_2["2 · Project<br/>59,142,609 × 7"]
    step_1 --> step_2
    step_3["3 · Reorder<br/>59,142,609 × 7"]
    step_2 --> step_3
    step_4["4 · GroupBy · 0.00000676%<br/>l_returnflag, l_linestatus; sum(l_quantity), sum(l_extendedprice), sum(disc_price), sum(charge), avg(l_quantity), avg(l_extendedprice), avg(l_discount), count_all(*)<br/>4 × 10"]
    step_3 --> step_4
    step_5["5 · Sort<br/>l_returnflag ASC, l_linestatus ASC<br/>4 × 10"]
    step_4 --> step_5
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0 source
    class step_1 filter
    class step_4 aggregate
    class step_2,step_3 transform
    class step_5 ordering
```


## Notes

- Almost a complete table scan

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

```sql
Limit(n=100)
  Sort[s_acctbal DESC, n_name ASC, s_name ASC, p_partkey ASC]
    Project(s_acctbal, s_name, n_name, p_partkey, p_mfgr, s_address, s_phone, s_comment)
      Filter((min_supplycost == ps_supplycost))
        InnerJoin(on=(p_partkey == p_partkey))
          Project(agg_partkey = p_partkey, min_supplycost)
            Aggregate(p_partkey; min(ps_supplycost))
              Project(p_partkey, ps_supplycost, p_mfgr, n_name, s_acctbal, s_name, s_address, s_phone, s_comment)
                InnerJoin(on=(n_nationkey == s_nationkey))
                  Project(n_nationkey, n_name)
                    InnerJoin(on=(r_regionkey == n_regionkey))
                      Filter(str_eq(r_name, "EUROPE"))
                        Scan(region [r_regionkey, r_name])
                      Scan(nation [n_nationkey, n_name, n_regionkey])
                  Project(p_partkey, ps_supplycost, p_mfgr, s_nationkey, s_acctbal, s_name, s_address, s_phone, s_comment)
                    InnerJoin(on=(s_suppkey == ps_suppkey))
                      Scan(supplier [s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal, s_comment])
                      InnerJoin(on=(ps_partkey == p_partkey))
                        Scan(partsupp [ps_partkey, ps_suppkey, ps_supplycost])
                        Project(p_partkey, p_mfgr)
                          Filter(endswith(p_type, "BRASS"))
                            Filter((p_size == 15))
                              Scan(part [p_partkey, p_mfgr, p_type, p_size])
          Project(p_partkey, ps_supplycost, p_mfgr, n_name, s_acctbal, s_name, s_address, s_phone, s_comment)
            InnerJoin(on=(n_nationkey == s_nationkey))
              Project(n_nationkey, n_name)
                InnerJoin(on=(r_regionkey == n_regionkey))
                  Filter(str_eq(r_name, "EUROPE"))
                    Scan(region [r_regionkey, r_name])
                  Scan(nation [n_nationkey, n_name, n_regionkey])
              Project(p_partkey, ps_supplycost, p_mfgr, s_nationkey, s_acctbal, s_name, s_address, s_phone, s_comment)
                InnerJoin(on=(s_suppkey == ps_suppkey))
                  Scan(supplier [s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal, s_comment])
                  InnerJoin(on=(ps_partkey == p_partkey))
                    Scan(partsupp [ps_partkey, ps_suppkey, ps_supplycost])
                    Project(p_partkey, p_mfgr)
                      Filter(endswith(p_type, "BRASS"))
                        Filter((p_size == 15))
                          Scan(part [p_partkey, p_mfgr, p_type, p_size])
```

```mermaid
flowchart TD
    ir_0["Limit<br/>n=100"]
    ir_1["Sort<br/>s_acctbal DESC, n_name ASC, s_name ASC, p_partkey ASC"]
    ir_0 --> ir_1
    ir_2["Project<br/>s_acctbal, s_name, n_name, p_partkey, p_mfgr, s_address, s_phone, s_comment"]
    ir_1 --> ir_2
    ir_3["Filter<br/>(min_supplycost == ps_supplycost)"]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(p_partkey == p_partkey)"]
    ir_3 --> ir_4
    ir_5["Project<br/>agg_partkey = p_partkey, min_supplycost"]
    ir_4 --> ir_5
    ir_6["Aggregate<br/>p_partkey; min(ps_supplycost)"]
    ir_5 --> ir_6
    ir_7["Project<br/>p_partkey, ps_supplycost, p_mfgr, n_name, s_acctbal, s_name, s_address, s_phone, s_comment"]
    ir_6 --> ir_7
    ir_8["InnerJoin<br/>on=(n_nationkey == s_nationkey)"]
    ir_7 --> ir_8
    ir_9["Project<br/>n_nationkey, n_name"]
    ir_8 --> ir_9
    ir_10["InnerJoin<br/>on=(r_regionkey == n_regionkey)"]
    ir_9 --> ir_10
    ir_11["Filter<br/>str_eq(r_name, #quot;EUROPE#quot;)"]
    ir_10 --> ir_11
    ir_12["Scan<br/>region · r_regionkey, r_name"]
    ir_11 --> ir_12
    ir_13["Scan<br/>nation · n_nationkey, n_name, n_regionkey"]
    ir_10 --> ir_13
    ir_14["Project<br/>p_partkey, ps_supplycost, p_mfgr, s_nationkey, s_acctbal, s_name, s_address, s_phone, s_comment"]
    ir_8 --> ir_14
    ir_15["InnerJoin<br/>on=(s_suppkey == ps_suppkey)"]
    ir_14 --> ir_15
    ir_16["Scan<br/>supplier · s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal, s_comment"]
    ir_15 --> ir_16
    ir_17["InnerJoin<br/>on=(ps_partkey == p_partkey)"]
    ir_15 --> ir_17
    ir_18["Scan<br/>partsupp · ps_partkey, ps_suppkey, ps_supplycost"]
    ir_17 --> ir_18
    ir_19["Project<br/>p_partkey, p_mfgr"]
    ir_17 --> ir_19
    ir_20["Filter<br/>endswith(p_type, #quot;BRASS#quot;)"]
    ir_19 --> ir_20
    ir_21["Filter<br/>(p_size == 15)"]
    ir_20 --> ir_21
    ir_22["Scan<br/>part · p_partkey, p_mfgr, p_type, p_size"]
    ir_21 --> ir_22
    ir_23["Project<br/>p_partkey, ps_supplycost, p_mfgr, n_name, s_acctbal, s_name, s_address, s_phone, s_comment"]
    ir_4 --> ir_23
    ir_24["InnerJoin<br/>on=(n_nationkey == s_nationkey)"]
    ir_23 --> ir_24
    ir_25["Project<br/>n_nationkey, n_name"]
    ir_24 --> ir_25
    ir_26["InnerJoin<br/>on=(r_regionkey == n_regionkey)"]
    ir_25 --> ir_26
    ir_27["Filter<br/>str_eq(r_name, #quot;EUROPE#quot;)"]
    ir_26 --> ir_27
    ir_28["Scan<br/>region · r_regionkey, r_name"]
    ir_27 --> ir_28
    ir_29["Scan<br/>nation · n_nationkey, n_name, n_regionkey"]
    ir_26 --> ir_29
    ir_30["Project<br/>p_partkey, ps_supplycost, p_mfgr, s_nationkey, s_acctbal, s_name, s_address, s_phone, s_comment"]
    ir_24 --> ir_30
    ir_31["InnerJoin<br/>on=(s_suppkey == ps_suppkey)"]
    ir_30 --> ir_31
    ir_32["Scan<br/>supplier · s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal, s_comment"]
    ir_31 --> ir_32
    ir_33["InnerJoin<br/>on=(ps_partkey == p_partkey)"]
    ir_31 --> ir_33
    ir_34["Scan<br/>partsupp · ps_partkey, ps_suppkey, ps_supplycost"]
    ir_33 --> ir_34
    ir_35["Project<br/>p_partkey, p_mfgr"]
    ir_33 --> ir_35
    ir_36["Filter<br/>endswith(p_type, #quot;BRASS#quot;)"]
    ir_35 --> ir_36
    ir_37["Filter<br/>(p_size == 15)"]
    ir_36 --> ir_37
    ir_38["Scan<br/>part · p_partkey, p_mfgr, p_type, p_size"]
    ir_37 --> ir_38
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_12,ir_13,ir_16,ir_18,ir_22,ir_28,ir_29,ir_32,ir_34,ir_38 source
    class ir_3,ir_11,ir_20,ir_21,ir_27,ir_36,ir_37 filter
    class ir_4,ir_8,ir_10,ir_15,ir_17,ir_24,ir_26,ir_31,ir_33 join
    class ir_6 aggregate
    class ir_2,ir_5,ir_7,ir_9,ir_14,ir_19,ir_23,ir_25,ir_30,ir_35 transform
    class ir_0,ir_1 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 5 | 2 | region |  |  |  |  |  | r_regionkey, r_name |
| 1 | Filter | 1 | 1 | < | 20% | 0.0493819 | 0.0493819 | nofuse | nofuse |  |
| 2 | SourceTable | 25 | 3 | nation |  |  |  |  |  | n_nationkey, n_name, n_regionkey |
| 3 | EqJoin | 5 | 3 | region⋈nation | 1⋈25 | 0.140861 | 0.140861 | hash_gfur | hash_gfur | regionkey |
| 4 | Reorder | 5 | 4 |  |  | 0.00705179 | 0.00705179 |  |  |  |
| 5 | Project | 5 | 2 |  |  | 0.0621196 | 0.0621196 | nofuse | nofuse | n_nationkey, n_name |
| 6 | SourceTable | 100000 | 7 | supplier |  |  |  |  |  | s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal, s_comment |
| 7 | SourceTable | 8000000 | 3 | partsupp |  |  |  |  |  | ps_partkey, ps_suppkey, ps_supplycost |
| 8 | SourceTable | 2000000 | 4 | part |  |  |  |  |  | p_partkey, p_mfgr, p_type, p_size |
| 9 | Filter | 39575 | 3 | < | 1.98% | 0.781625 | 0.781625 | nofuse | nofuse |  |
| 10 | Filter | 7854 | 2 | < | 19.8% | 0.160744 | 0.160744 | nofuse | nofuse |  |
| 11 | Project | 7854 | 2 |  |  | 0.00236042 | 0.00236042 | nofuse | nofuse | p_partkey, p_mfgr |
| 12 | EqJoin | 31416 | 4 | partsupp⋈part | 8M⋈7.9K | 6.87367 | 6.87367 | hash_gfur | hash_gfur | partkey |
| 13 | Reorder | 31416 | 5 |  |  | 0.00728421 | 0.00728421 |  |  |  |
| 14 | EqJoin | 31416 | 11 | supplier⋈(partsupp⋈part) | 100K⋈31.4K | 1.00285 | 1.00285 | hash_gfur | hash_gfur | suppkey |
| 15 | Reorder | 31416 | 12 |  |  | 0.0165432 | 0.0165432 |  |  |  |
| 16 | Project | 31416 | 9 |  |  | 0.554563 | 0.554563 | nofuse | nofuse | p_partkey, ps_supplycost, p_mfgr, s_nationkey, s_acctbal, s_name, s_address, s_phone, s_comment |
| 17 | EqJoin | 6351 | 10 | (region⋈nation)⋈(supplier⋈(partsupp⋈part)) | 5⋈31.4K | 0.52478 | 0.52478 | hash_gfur | hash_gfur | nationkey |
| 18 | Reorder | 6351 | 11 |  |  | 0.0171646 | 0.0171646 |  |  |  |
| 19 | Project | 6351 | 9 |  |  | 0.405231 | 0.405231 | nofuse | nofuse | p_partkey, ps_supplycost, p_mfgr, n_name, s_acctbal, s_name, s_address, s_phone, s_comment |
| 20 | Reorder | 6351 | 2 |  |  | 0.0266762 | 0.0266762 |  |  |  |
| 21 | GroupBy | 4667 | 2 | < | 73.5% | 0.181685 | 0.149288 | hash | sort_gftr_opt | p_partkey; min(ps_supplycost) |
| 22 | Project | 4667 | 2 |  |  | 0.00282863 | 0.00282863 | nofuse | nofuse | p_partkey, p_mfgr |
| 23 | EqJoin | 6351 | 10 | ((region⋈nation)⋈(supplier⋈(partsupp⋈part))) ⋈ ((region⋈nation)⋈(supplier⋈(partsupp⋈part))) | 4.7K⋈6.4K | 0.474924 | 0.474924 | hash_gfur | hash_gfur | partkey |
| 24 | Reorder | 6351 | 11 |  |  | 0.0170223 | 0.0170223 |  |  |  |
| 25 | Filter | 4667 | 9 | < | 73.5% | 0.485811 | 0.485811 | nofuse | nofuse |  |
| 26 | Project | 4667 | 8 |  |  | 0.00460547 | 0.00460547 | nofuse | nofuse | s_acctbal, s_name, n_name, p_partkey, p_mfgr, s_address, s_phone, s_comment |
| 27 | TopK | 100 | 8 | < | 2.14% | 1.55757 | 1.55757 |  |  |  |
|  | Total |  |  |  |  | 13.3574 | 13.325 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>region<br/>r_regionkey, r_name<br/>5 × 2"]
    step_1["1 · Filter · 20%<br/>1 × 1"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>nation<br/>n_nationkey, n_name, n_regionkey<br/>25 × 3"]
    step_3["3 · EqJoin · 1⋈25<br/>regionkey<br/>5 × 3"]
    step_1 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>5 × 4"]
    step_3 --> step_4
    step_5["5 · Project<br/>5 × 2"]
    step_4 --> step_5
    step_6["6 · SourceTable<br/>supplier<br/>s_suppkey, s_name, s_address, s_nationkey, s_phone, s_acctbal, s_comment<br/>100,000 × 7"]
    step_7["7 · SourceTable<br/>partsupp<br/>ps_partkey, ps_suppkey, ps_supplycost<br/>8,000,000 × 3"]
    step_8["8 · SourceTable<br/>part<br/>p_partkey, p_mfgr, p_type, p_size<br/>2,000,000 × 4"]
    step_9["9 · Filter · 1.98%<br/>39,575 × 3"]
    step_8 --> step_9
    step_10["10 · Filter · 19.8%<br/>7,854 × 2"]
    step_9 --> step_10
    step_11["11 · Project<br/>7,854 × 2"]
    step_10 --> step_11
    step_12["12 · EqJoin · 8M⋈7.9K<br/>partkey<br/>31,416 × 4"]
    step_7 --> step_12
    step_11 --> step_12
    step_13["13 · Reorder<br/>31,416 × 5"]
    step_12 --> step_13
    step_14["14 · EqJoin · 100K⋈31.4K<br/>suppkey<br/>31,416 × 11"]
    step_6 --> step_14
    step_13 --> step_14
    step_15["15 · Reorder<br/>31,416 × 12"]
    step_14 --> step_15
    step_16["16 · Project<br/>31,416 × 9"]
    step_15 --> step_16
    step_17["17 · EqJoin · 5⋈31.4K<br/>nationkey<br/>6,351 × 10"]
    step_5 --> step_17
    step_16 --> step_17
    step_18["18 · Reorder<br/>6,351 × 11"]
    step_17 --> step_18
    step_19["19 · Project<br/>6,351 × 9"]
    step_18 --> step_19
    step_20["20 · Reorder<br/>6,351 × 2"]
    step_19 --> step_20
    step_21["21 · GroupBy · 73.5%<br/>p_partkey; min(ps_supplycost)<br/>4,667 × 2"]
    step_20 --> step_21
    step_22["22 · Project<br/>4,667 × 2"]
    step_21 --> step_22
    step_23["23 · EqJoin · 4.7K⋈6.4K<br/>partkey<br/>6,351 × 10"]
    step_22 --> step_23
    step_19 --> step_23
    step_24["24 · Reorder<br/>6,351 × 11"]
    step_23 --> step_24
    step_25["25 · Filter · 73.5%<br/>4,667 × 9"]
    step_24 --> step_25
    step_26["26 · Project<br/>4,667 × 8"]
    step_25 --> step_26
    step_27["27 · TopK · 2.14%<br/>100 × 8"]
    step_26 --> step_27
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2,step_6,step_7,step_8 source
    class step_1,step_9,step_10,step_25 filter
    class step_3,step_12,step_14,step_17,step_23 join
    class step_21 aggregate
    class step_4,step_5,step_11,step_13,step_15,step_16,step_18,step_19,step_20,step_22,step_24,step_26 transform
    class step_27 ordering
```


## Notes

- This query joins 5 tables.

- Repeated join subtree for the correlated MIN

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

```sql
Limit(n=10)
  Sort[revenue DESC, o_orderdate ASC]
    Project(l_orderkey, revenue, o_orderdate, o_shippriority)
      Aggregate(l_orderkey, o_orderdate, o_shippriority; sum(disc_price))
        Project(l_orderkey, o_orderdate, o_shippriority, disc_price = (l_extendedprice * (1 - l_discount)))
          InnerJoin(on=(l_orderkey == o_orderkey))
            InnerJoin(on=(c_custkey == o_custkey))
              Filter(str_eq(c_mktsegment, "BUILDING"))
                Scan(customer [c_custkey, c_mktsegment])
              Filter((o_orderdate < 19950315))
                Scan(orders [o_orderkey, o_custkey, o_orderdate, o_shippriority])
            Filter((l_shipdate > 19950315))
              Scan(lineitem [l_orderkey, l_extendedprice, l_discount, l_shipdate])
```

```mermaid
flowchart TD
    ir_0["Limit<br/>n=10"]
    ir_1["Sort<br/>revenue DESC, o_orderdate ASC"]
    ir_0 --> ir_1
    ir_2["Project<br/>l_orderkey, revenue, o_orderdate, o_shippriority"]
    ir_1 --> ir_2
    ir_3["Aggregate<br/>l_orderkey, o_orderdate, o_shippriority; sum(disc_price)"]
    ir_2 --> ir_3
    ir_4["Project<br/>l_orderkey, o_orderdate, o_shippriority, disc_price = (l_extendedprice * (1 - l_discount))"]
    ir_3 --> ir_4
    ir_5["InnerJoin<br/>on=(l_orderkey == o_orderkey)"]
    ir_4 --> ir_5
    ir_6["InnerJoin<br/>on=(c_custkey == o_custkey)"]
    ir_5 --> ir_6
    ir_7["Filter<br/>str_eq(c_mktsegment, #quot;BUILDING#quot;)"]
    ir_6 --> ir_7
    ir_8["Scan<br/>customer · c_custkey, c_mktsegment"]
    ir_7 --> ir_8
    ir_9["Filter<br/>(o_orderdate &lt; 19950315)"]
    ir_6 --> ir_9
    ir_10["Scan<br/>orders · o_orderkey, o_custkey, o_orderdate, o_shippriority"]
    ir_9 --> ir_10
    ir_11["Filter<br/>(l_shipdate &gt; 19950315)"]
    ir_5 --> ir_11
    ir_12["Scan<br/>lineitem · l_orderkey, l_extendedprice, l_discount, l_shipdate"]
    ir_11 --> ir_12
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_8,ir_10,ir_12 source
    class ir_7,ir_9,ir_11 filter
    class ir_5,ir_6 join
    class ir_3 aggregate
    class ir_2,ir_4 transform
    class ir_0,ir_1 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 1500000 | 2 | customer |  |  |  |  |  | c_custkey, c_mktsegment |
| 1 | Filter | 300276 | 1 | < | 20% | 0.31404 | 0.31404 | fuse | fuse |  |
| 2 | SourceTable | 15000000 | 4 | orders |  |  |  |  |  | o_orderkey, o_custkey, o_orderdate, o_shippriority |
| 3 | Filter | 7289442 | 4 | < | 48.6% | 3.69772 | 2.94776 | fuse | nofuse |  |
| 4 | EqJoin | 1461923 | 4 | customer⋈orders | 300.3K⋈7.3M | 12.6894 | 12.6894 | hash_gfur | hash_gfur | custkey |
| 5 | Reorder | 1461923 | 5 |  |  | 0.001904 | 0.001904 |  |  |  |
| 6 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_orderkey, l_extendedprice, l_discount, l_shipdate |
| 7 | Filter | 32334250 | 3 | < | 53.9% | 14.9623 | 11.948 | fuse | nofuse |  |
| 8 | EqJoin | 302114 | 7 | (customer⋈orders)⋈lineitem | 1.5M⋈32.3M | 30.8889 | 30.8889 | hash_gfur | hash_gfur | orderkey |
| 9 | Reorder | 302114 | 8 |  |  | 0.002064 | 0.002064 |  |  |  |
| 10 | Project | 302114 | 4 |  |  | 0.123448 | 0.123448 | nofuse | nofuse | l_orderkey, o_orderdate, o_shippriority, disc_price |
| 11 | Reorder | 302114 | 4 |  |  | 0.001812 | 0.001812 |  |  |  |
| 12 | GroupBy | 114003 | 4 | < | 37.7% | 0.45488 | 0.45488 | hash | hash | l_orderkey, o_orderdate, o_shippriority; sum(disc_price) |
| 13 | Project | 114003 | 4 |  |  | 0.002776 | 0.002776 | nofuse | nofuse | l_orderkey, revenue, o_orderdate, o_shippriority |
| 14 | TopK | 10 | 4 | < | 0.00877% | 1.06854 | 1.06854 |  |  |  |
|  | Total |  |  |  |  | 64.2078 | 60.4435 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>customer<br/>c_custkey, c_mktsegment<br/>1,500,000 × 2"]
    step_1["1 · Filter · 20%<br/>300,276 × 1"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>orders<br/>o_orderkey, o_custkey, o_orderdate, o_shippriority<br/>15,000,000 × 4"]
    step_3["3 · Filter · 48.6%<br/>7,289,442 × 4"]
    step_2 --> step_3
    step_4["4 · EqJoin · 300.3K⋈7.3M<br/>custkey<br/>1,461,923 × 4"]
    step_1 --> step_4
    step_3 --> step_4
    step_5["5 · Reorder<br/>1,461,923 × 5"]
    step_4 --> step_5
    step_6["6 · SourceTable<br/>lineitem<br/>l_orderkey, l_extendedprice, l_discount, l_shipdate<br/>59,986,052 × 4"]
    step_7["7 · Filter · 53.9%<br/>32,334,250 × 3"]
    step_6 --> step_7
    step_8["8 · EqJoin · 1.5M⋈32.3M<br/>orderkey<br/>302,114 × 7"]
    step_5 --> step_8
    step_7 --> step_8
    step_9["9 · Reorder<br/>302,114 × 8"]
    step_8 --> step_9
    step_10["10 · Project<br/>302,114 × 4"]
    step_9 --> step_10
    step_11["11 · Reorder<br/>302,114 × 4"]
    step_10 --> step_11
    step_12["12 · GroupBy · 37.7%<br/>l_orderkey, o_orderdate, o_shippriority; sum(disc_price)<br/>114,003 × 4"]
    step_11 --> step_12
    step_13["13 · Project<br/>114,003 × 4"]
    step_12 --> step_13
    step_14["14 · TopK · 0.00877%<br/>10 × 4"]
    step_13 --> step_14
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2,step_6 source
    class step_1,step_3,step_7 filter
    class step_4,step_8 join
    class step_12 aggregate
    class step_5,step_9,step_10,step_11,step_13 transform
    class step_14 ordering
```


## Notes

- Large intermediate join

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

```sql
Sort[o_orderpriority ASC]
  Aggregate(o_orderpriority; count_all(*))
    LeftSemiJoin(on=(o_orderkey == l_orderkey))
      Filter(((o_orderdate >= 19930701) && (o_orderdate < 19931001)))
        Scan(orders [o_orderkey, o_orderdate, o_orderpriority])
      Filter((l_commitdate < l_receiptdate))
        Scan(lineitem [l_orderkey, l_commitdate, l_receiptdate])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>o_orderpriority ASC"]
    ir_1["Aggregate<br/>o_orderpriority; count_all(*)"]
    ir_0 --> ir_1
    ir_2["LeftSemiJoin<br/>on=(o_orderkey == l_orderkey)"]
    ir_1 --> ir_2
    ir_3["Filter<br/>((o_orderdate &gt;= 19930701) &amp;&amp; (o_orderdate &lt; 19931001))"]
    ir_2 --> ir_3
    ir_4["Scan<br/>orders · o_orderkey, o_orderdate, o_orderpriority"]
    ir_3 --> ir_4
    ir_5["Filter<br/>(l_commitdate &lt; l_receiptdate)"]
    ir_2 --> ir_5
    ir_6["Scan<br/>lineitem · l_orderkey, l_commitdate, l_receiptdate"]
    ir_5 --> ir_6
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_4,ir_6 source
    class ir_3,ir_5 filter
    class ir_2 join
    class ir_1 aggregate
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 15000000 | 3 | orders |  |  |  |  |  | o_orderkey, o_orderdate, o_orderpriority |
| 1 | Filter | 573671 | 2 | < | 3.82% | 4.36072 | 3.35254 | fuse | nofuse |  |
| 2 | SourceTable | 59986052 | 3 | lineitem |  |  |  |  |  | l_orderkey, l_commitdate, l_receiptdate |
| 3 | Filter | 37929348 | 1 | < | 63.2% | 6.98947 | 5.87889 | fuse | nofuse |  |
| 4 | SemiJoin | 526040 | 2 | orders⋈lineitem | 573.7K⋈37.9M | 26.8662 | 26.8662 |  |  | o_orderkey; l_orderkey |
| 5 | Reorder | 526040 | 2 |  |  | 0.00768 | 0.00768 |  |  |  |
| 6 | Reorder | 526040 | 1 |  |  | 0.00191262 | 0.00191262 |  |  |  |
| 7 | GroupBy | 5 | 2 | < | 0.00095% | 0.482398 | 0.482398 | hash | hash | o_orderpriority; count_all(*) |
| 8 | Sort | 5 | 2 |  |  | 0.157541 | 0.157541 | no_skf | no_skf | o_orderpriority ASC |
|  | Total |  |  |  |  | 38.8659 | 36.7472 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>orders<br/>o_orderkey, o_orderdate, o_orderpriority<br/>15,000,000 × 3"]
    step_1["1 · Filter · 3.82%<br/>573,671 × 2"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>lineitem<br/>l_orderkey, l_commitdate, l_receiptdate<br/>59,986,052 × 3"]
    step_3["3 · Filter · 63.2%<br/>37,929,348 × 1"]
    step_2 --> step_3
    step_4["4 · SemiJoin · 573.7K⋈37.9M<br/>o_orderkey; l_orderkey<br/>526,040 × 2"]
    step_1 --> step_4
    step_3 --> step_4
    step_5["5 · Reorder<br/>526,040 × 2"]
    step_4 --> step_5
    step_6["6 · Reorder<br/>526,040 × 1"]
    step_5 --> step_6
    step_7["7 · GroupBy · 0.00095%<br/>o_orderpriority; count_all(*)<br/>5 × 2"]
    step_6 --> step_7
    step_8["8 · Sort<br/>o_orderpriority ASC<br/>5 × 2"]
    step_7 --> step_8
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2 source
    class step_1,step_3 filter
    class step_4 join
    class step_7 aggregate
    class step_5,step_6 transform
    class step_8 ordering
```


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

```sql
Sort[revenue DESC]
  Aggregate(n_name; sum(disc_price))
    Project(n_name, disc_price = (l_extendedprice * (1 - l_discount)))
      Filter((c_nationkey == s_nationkey))
        InnerJoin(on=(l_suppkey == s_suppkey))
          InnerJoin(on=(o_orderkey == l_orderkey))
            InnerJoin(on=(c_custkey == o_custkey))
              Scan(customer [c_custkey, c_nationkey])
              Filter(((o_orderdate >= 19940101) && (o_orderdate < 19950101)))
                Scan(orders [o_orderkey, o_custkey, o_orderdate])
            Scan(lineitem [l_orderkey, l_suppkey, l_extendedprice, l_discount])
          InnerJoin(on=(n_nationkey == s_nationkey))
            InnerJoin(on=(r_regionkey == n_regionkey))
              Filter(str_eq(r_name, "ASIA"))
                Scan(region [r_regionkey, r_name])
              Scan(nation [n_nationkey, n_name, n_regionkey])
            Scan(supplier [s_suppkey, s_nationkey])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>revenue DESC"]
    ir_1["Aggregate<br/>n_name; sum(disc_price)"]
    ir_0 --> ir_1
    ir_2["Project<br/>n_name, disc_price = (l_extendedprice * (1 - l_discount))"]
    ir_1 --> ir_2
    ir_3["Filter<br/>(c_nationkey == s_nationkey)"]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(l_suppkey == s_suppkey)"]
    ir_3 --> ir_4
    ir_5["InnerJoin<br/>on=(o_orderkey == l_orderkey)"]
    ir_4 --> ir_5
    ir_6["InnerJoin<br/>on=(c_custkey == o_custkey)"]
    ir_5 --> ir_6
    ir_7["Scan<br/>customer · c_custkey, c_nationkey"]
    ir_6 --> ir_7
    ir_8["Filter<br/>((o_orderdate &gt;= 19940101) &amp;&amp; (o_orderdate &lt; 19950101))"]
    ir_6 --> ir_8
    ir_9["Scan<br/>orders · o_orderkey, o_custkey, o_orderdate"]
    ir_8 --> ir_9
    ir_10["Scan<br/>lineitem · l_orderkey, l_suppkey, l_extendedprice, l_discount"]
    ir_5 --> ir_10
    ir_11["InnerJoin<br/>on=(n_nationkey == s_nationkey)"]
    ir_4 --> ir_11
    ir_12["InnerJoin<br/>on=(r_regionkey == n_regionkey)"]
    ir_11 --> ir_12
    ir_13["Filter<br/>str_eq(r_name, #quot;ASIA#quot;)"]
    ir_12 --> ir_13
    ir_14["Scan<br/>region · r_regionkey, r_name"]
    ir_13 --> ir_14
    ir_15["Scan<br/>nation · n_nationkey, n_name, n_regionkey"]
    ir_12 --> ir_15
    ir_16["Scan<br/>supplier · s_suppkey, s_nationkey"]
    ir_11 --> ir_16
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_7,ir_9,ir_10,ir_14,ir_15,ir_16 source
    class ir_3,ir_8,ir_13 filter
    class ir_4,ir_5,ir_6,ir_11,ir_12 join
    class ir_1 aggregate
    class ir_2 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 1500000 | 2 | customer |  |  |  |  |  | c_custkey, c_nationkey |
| 1 | SourceTable | 15000000 | 3 | orders |  |  |  |  |  | o_orderkey, o_custkey, o_orderdate |
| 2 | Filter | 2275919 | 2 | < | 15.2% | 3.55093 | 2.35943 | fuse | nofuse |  |
| 3 | EqJoin | 2275919 | 3 | customer⋈orders | 1.5M⋈2.3M | 12.5685 | 12.5685 | hash_gfur | hash_gfur | custkey |
| 4 | Reorder | 2275919 | 4 |  |  | 0.001864 | 0.001864 |  |  |  |
| 5 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_orderkey, l_suppkey, l_extendedprice, l_discount |
| 6 | EqJoin | 9103367 | 7 | (customer⋈orders)⋈lineitem | 2.3M⋈60M | 66.4261 | 66.4261 | hash_gfur | hash_gfur | orderkey |
| 7 | Reorder | 9103367 | 8 |  |  | 0.002176 | 0.002176 |  |  |  |
| 8 | SourceTable | 5 | 2 | region |  |  |  |  |  | r_regionkey, r_name |
| 9 | Filter | 1 | 1 | < | 20% | 0.057248 | 0.057248 | fuse | fuse |  |
| 10 | SourceTable | 25 | 3 | nation |  |  |  |  |  | n_nationkey, n_name, n_regionkey |
| 11 | EqJoin | 5 | 3 | region⋈nation | 1⋈25 | 0.162176 | 0.162176 | hash_gfur | hash_gfur | regionkey |
| 12 | Reorder | 5 | 4 |  |  | 0.00712 | 0.00712 |  |  |  |
| 13 | SourceTable | 100000 | 2 | supplier |  |  |  |  |  | s_suppkey, s_nationkey |
| 14 | EqJoin | 20037 | 5 | (region⋈nation)⋈supplier | 5⋈100K | 0.250944 | 0.250944 | hash_gfur | hash_gfur | nationkey |
| 15 | Reorder | 20037 | 6 |  |  | 0.006408 | 0.006408 |  |  |  |
| 16 | EqJoin | 1825042 | 13 | ((customer⋈orders)⋈lineitem)⋈((region⋈nation) ⋈ supplier) | 9.1M⋈20K | 56.1677 | 56.1677 | hash_gfur | hash_gfur | suppkey |
| 17 | Reorder | 1825042 | 14 |  |  | 0.007792 | 0.007792 |  |  |  |
| 18 | Filter | 72985 | 3 | < | 4% | 0.700368 | 0.631832 | fuse | nofuse |  |
| 19 | Project | 72985 | 2 |  |  | 0.041488 | 0.041488 | nofuse | nofuse | n_name, disc_price |
| 20 | Reorder | 72985 | 2 |  |  | 0.002016 | 0.002016 |  |  |  |
| 21 | GroupBy | 5 | 2 | < | 0.00685% | 0.242168 | 0.242168 | hash | hash | n_name; sum(disc_price) |
| 22 | Sort | 5 | 2 |  |  | 0.10648 | 0.10648 | no_skf | no_skf | sum(disc_price) DESC |
|  | Total |  |  |  |  | 140.301 | 139.041 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>customer<br/>c_custkey, c_nationkey<br/>1,500,000 × 2"]
    step_1["1 · SourceTable<br/>orders<br/>o_orderkey, o_custkey, o_orderdate<br/>15,000,000 × 3"]
    step_2["2 · Filter · 15.2%<br/>2,275,919 × 2"]
    step_1 --> step_2
    step_3["3 · EqJoin · 1.5M⋈2.3M<br/>custkey<br/>2,275,919 × 3"]
    step_0 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>2,275,919 × 4"]
    step_3 --> step_4
    step_5["5 · SourceTable<br/>lineitem<br/>l_orderkey, l_suppkey, l_extendedprice, l_discount<br/>59,986,052 × 4"]
    step_6["6 · EqJoin · 2.3M⋈60M<br/>orderkey<br/>9,103,367 × 7"]
    step_4 --> step_6
    step_5 --> step_6
    step_7["7 · Reorder<br/>9,103,367 × 8"]
    step_6 --> step_7
    step_8["8 · SourceTable<br/>region<br/>r_regionkey, r_name<br/>5 × 2"]
    step_9["9 · Filter · 20%<br/>1 × 1"]
    step_8 --> step_9
    step_10["10 · SourceTable<br/>nation<br/>n_nationkey, n_name, n_regionkey<br/>25 × 3"]
    step_11["11 · EqJoin · 1⋈25<br/>regionkey<br/>5 × 3"]
    step_9 --> step_11
    step_10 --> step_11
    step_12["12 · Reorder<br/>5 × 4"]
    step_11 --> step_12
    step_13["13 · SourceTable<br/>supplier<br/>s_suppkey, s_nationkey<br/>100,000 × 2"]
    step_14["14 · EqJoin · 5⋈100K<br/>nationkey<br/>20,037 × 5"]
    step_12 --> step_14
    step_13 --> step_14
    step_15["15 · Reorder<br/>20,037 × 6"]
    step_14 --> step_15
    step_16["16 · EqJoin · 9.1M⋈20K<br/>suppkey<br/>1,825,042 × 13"]
    step_7 --> step_16
    step_15 --> step_16
    step_17["17 · Reorder<br/>1,825,042 × 14"]
    step_16 --> step_17
    step_18["18 · Filter · 4%<br/>72,985 × 3"]
    step_17 --> step_18
    step_19["19 · Project<br/>72,985 × 2"]
    step_18 --> step_19
    step_20["20 · Reorder<br/>72,985 × 2"]
    step_19 --> step_20
    step_21["21 · GroupBy · 0.00685%<br/>n_name; sum(disc_price)<br/>5 × 2"]
    step_20 --> step_21
    step_22["22 · Sort<br/>sum(disc_price) DESC<br/>5 × 2"]
    step_21 --> step_22
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1,step_5,step_8,step_10,step_13 source
    class step_2,step_9,step_18 filter
    class step_3,step_6,step_11,step_14,step_16 join
    class step_21 aggregate
    class step_4,step_7,step_12,step_15,step_17,step_19,step_20 transform
    class step_22 ordering
```


## Notes

- This query joins 6 tables.

- Region and supplier could be filtered from lineitem first before joining

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

```sql
Aggregate(sum(revenue))
  Project(revenue = (l_extendedprice * l_discount))
    Filter((((((l_shipdate >= 19940101) && (l_shipdate < 19950101)) && (l_discount >= 0.05)) && (l_discount <= 0.07)) && (l_quantity < 24)))
      Scan(lineitem [l_shipdate, l_extendedprice, l_discount, l_quantity])
```

```mermaid
flowchart TD
    ir_0["Aggregate<br/>sum(revenue)"]
    ir_1["Project<br/>revenue = (l_extendedprice * l_discount)"]
    ir_0 --> ir_1
    ir_2["Filter<br/>(((((l_shipdate &gt;= 19940101) &amp;&amp; (l_shipdate &lt; 19950101)) &amp;&amp; (l_discount &gt;= 0.05)) &amp;&amp; (l_discount &lt;= 0.07)) ..."]
    ir_1 --> ir_2
    ir_3["Scan<br/>lineitem · l_shipdate, l_extendedprice, l_discount, l_quantity"]
    ir_2 --> ir_3
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_3 source
    class ir_2 filter
    class ir_0 aggregate
    class ir_1 transform
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_shipdate, l_extendedprice, l_discount, l_quantity |
| 1 | Filter | 1139264 | 2 | < | 1.9% | 27.2187 | 15.9113 | fuse | nofuse |  |
| 2 | Project | 1139264 | 1 |  |  | 0.141295 | 0.141295 | nofuse | nofuse | revenue |
| 3 | Reorder | 1139264 | 1 |  |  | 0.00193347 | 0.00193347 |  |  |  |
| 4 | ScalarAgg | 1 | 1 |  |  | 0.080128 | 0.080128 |  |  | sum(revenue) |
|  | Total |  |  |  |  | 27.4421 | 16.1347 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>lineitem<br/>l_shipdate, l_extendedprice, l_discount, l_quantity<br/>59,986,052 × 4"]
    step_1["1 · Filter · 1.9%<br/>1,139,264 × 2"]
    step_0 --> step_1
    step_2["2 · Project<br/>1,139,264 × 1"]
    step_1 --> step_2
    step_3["3 · Reorder<br/>1,139,264 × 1"]
    step_2 --> step_3
    step_4["4 · ScalarAgg<br/>sum(revenue)<br/>1 × 1"]
    step_3 --> step_4
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0 source
    class step_1 filter
    class step_4 aggregate
    class step_2,step_3 transform
```


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

```sql
Sort[n_name#12 ASC, n_name#14 ASC, l_year ASC]
  Aggregate(n_name#12, n_name#14, l_year; sum(volume))
    Project(supp_nation = n_name#12, cust_nation = n_name#14, l_year = year(l_shipdate), volume = (l_extendedprice * (1 - l_discount)))
      Filter(((str_eq(n_name#12, "FRANCE") && str_eq(n_name#14, "GERMANY")) || (str_eq(n_name#12, "GERMANY") && str_eq(n_name#14, "FRANCE"))))
        InnerJoin(on=(o_custkey == c_custkey))
          InnerJoin(on=(l_orderkey == o_orderkey))
            InnerJoin(on=(s_suppkey == l_suppkey))
              InnerJoin(on=(n_nationkey#11 == s_nationkey))
                Filter(str_in(n_name#12, ["FRANCE", "GERMANY"]))
                  Scan(nation [n_nationkey, n_name])
                Scan(supplier [s_suppkey, s_nationkey])
              Filter(((l_shipdate >= 19950101) && (l_shipdate <= 19961231)))
                Scan(lineitem [l_orderkey, l_suppkey, l_extendedprice, l_discount, l_shipdate])
            Scan(orders [o_orderkey, o_custkey])
          InnerJoin(on=(n_nationkey#13 == c_nationkey))
            Filter(str_in(n_name#14, ["FRANCE", "GERMANY"]))
              Scan(nation [n_nationkey, n_name])
            Scan(customer [c_custkey, c_nationkey])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>n_name#12 ASC, n_name#14 ASC, l_year ASC"]
    ir_1["Aggregate<br/>n_name#12, n_name#14, l_year; sum(volume)"]
    ir_0 --> ir_1
    ir_2["Project<br/>supp_nation = n_name#12, cust_nation = n_name#14, l_year = year(l_shipdate), volume = (l_extendedprice * (1..."]
    ir_1 --> ir_2
    ir_3["Filter<br/>((str_eq(n_name#12, #quot;FRANCE#quot;) &amp;&amp; str_eq(n_name#14, #quot;GERMANY#quot;)) || (str_eq(n_name#12, #quot;GERMANY#quot;) &amp;&amp; str_eq(n..."]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(o_custkey == c_custkey)"]
    ir_3 --> ir_4
    ir_5["InnerJoin<br/>on=(l_orderkey == o_orderkey)"]
    ir_4 --> ir_5
    ir_6["InnerJoin<br/>on=(s_suppkey == l_suppkey)"]
    ir_5 --> ir_6
    ir_7["InnerJoin<br/>on=(n_nationkey#11 == s_nationkey)"]
    ir_6 --> ir_7
    ir_8["Filter<br/>str_in(n_name#12, [#quot;FRANCE#quot;, #quot;GERMANY#quot;])"]
    ir_7 --> ir_8
    ir_9["Scan<br/>nation · n_nationkey, n_name"]
    ir_8 --> ir_9
    ir_10["Scan<br/>supplier · s_suppkey, s_nationkey"]
    ir_7 --> ir_10
    ir_11["Filter<br/>((l_shipdate &gt;= 19950101) &amp;&amp; (l_shipdate &lt;= 19961231))"]
    ir_6 --> ir_11
    ir_12["Scan<br/>lineitem · l_orderkey, l_suppkey, l_extendedprice, l_discount, l_shipdate"]
    ir_11 --> ir_12
    ir_13["Scan<br/>orders · o_orderkey, o_custkey"]
    ir_5 --> ir_13
    ir_14["InnerJoin<br/>on=(n_nationkey#13 == c_nationkey)"]
    ir_4 --> ir_14
    ir_15["Filter<br/>str_in(n_name#14, [#quot;FRANCE#quot;, #quot;GERMANY#quot;])"]
    ir_14 --> ir_15
    ir_16["Scan<br/>nation · n_nationkey, n_name"]
    ir_15 --> ir_16
    ir_17["Scan<br/>customer · c_custkey, c_nationkey"]
    ir_14 --> ir_17
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_9,ir_10,ir_12,ir_13,ir_16,ir_17 source
    class ir_3,ir_8,ir_11,ir_15 filter
    class ir_4,ir_5,ir_6,ir_7,ir_14 join
    class ir_1 aggregate
    class ir_2 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 1 | Filter | 2 | 2 | < | 8% | 0.136859 | 0.136859 | fuse | fuse |  |
| 2 | SourceTable | 100000 | 2 | supplier |  |  |  |  |  | s_suppkey, s_nationkey |
| 3 | EqJoin | 8010 | 3 | nation⋈supplier | 2⋈100K | 0.19464 | 0.19464 | hash_gfur | hash_gfur | nationkey |
| 4 | Reorder | 8010 | 4 |  |  | 0.00575467 | 0.00575467 |  |  |  |
| 5 | SourceTable | 59986052 | 5 | lineitem |  |  |  |  |  | l_orderkey, l_suppkey, l_extendedprice, l_discount, l_shipdate |
| 6 | Filter | 18230325 | 5 | < | 30.4% | 20.7792 | 16.0126 | fuse | nofuse |  |
| 7 | EqJoin | 1460257 | 8 | (nation⋈supplier)⋈lineitem | 8K⋈18.2M | 15.1967 | 15.1967 | hash_gfur | hash_gfur | suppkey |
| 8 | Reorder | 1460257 | 9 |  |  | 0.00783467 | 0.00783467 |  |  |  |
| 9 | SourceTable | 15000000 | 2 | orders |  |  |  |  |  | o_orderkey, o_custkey |
| 10 | EqJoin | 1460257 | 10 | ((nation⋈supplier)⋈lineitem)⋈orders | 1.5M⋈15M | 42.3044 | 42.3044 | hash_gfur | hash_gfur | orderkey |
| 11 | Reorder | 1460257 | 11 |  |  | 0.007248 | 0.007248 |  |  |  |
| 12 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 13 | Filter | 2 | 2 | < | 8% | 0.137792 | 0.137792 | fuse | fuse |  |
| 14 | SourceTable | 1500000 | 2 | customer |  |  |  |  |  | c_custkey, c_nationkey |
| 15 | EqJoin | 120469 | 3 | nation⋈customer | 2⋈1.5M | 1.04668 | 1.04668 | hash_gfur | hash_gfur | nationkey |
| 16 | Reorder | 120469 | 4 |  |  | 0.006192 | 0.006192 |  |  |  |
| 17 | EqJoin | 117014 | 14 | (((nation⋈supplier)⋈lineitem)⋈orders)⋈(nation ⋈ customer) | 1.5M⋈120.5K | 3.37125 | 3.37125 | hash_gfur | hash_gfur | custkey |
| 18 | Reorder | 117014 | 15 |  |  | 0.00813333 | 0.00813333 |  |  |  |
| 19 | Filter | 58365 | 5 | < | 49.9% | 0.421419 | 0.421419 | fuse | fuse |  |
| 20 | Project | 58365 | 4 |  |  | 0.0526347 | 0.0526347 | nofuse | nofuse | supp_nation, cust_nation, l_year, volume |
| 21 | Reorder | 58365 | 4 |  |  | 0.00209067 | 0.00209067 |  |  |  |
| 22 | GroupBy | 4 | 4 | < | 0.00685% | 0.303339 | 0.303339 | hash | hash | supp_nation, cust_nation, l_year; sum(volume) |
| 23 | Sort | 4 | 4 |  |  | 0.672187 | 0.65029 | no_skf | skf | supp_nation ASC, cust_nation ASC, l_year ASC |
|  | Total |  |  |  |  | 84.6544 | 79.8659 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_1["1 · Filter · 8%<br/>2 × 2"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>supplier<br/>s_suppkey, s_nationkey<br/>100,000 × 2"]
    step_3["3 · EqJoin · 2⋈100K<br/>nationkey<br/>8,010 × 3"]
    step_1 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>8,010 × 4"]
    step_3 --> step_4
    step_5["5 · SourceTable<br/>lineitem<br/>l_orderkey, l_suppkey, l_extendedprice, l_discount, l_shipdate<br/>59,986,052 × 5"]
    step_6["6 · Filter · 30.4%<br/>18,230,325 × 5"]
    step_5 --> step_6
    step_7["7 · EqJoin · 8K⋈18.2M<br/>suppkey<br/>1,460,257 × 8"]
    step_4 --> step_7
    step_6 --> step_7
    step_8["8 · Reorder<br/>1,460,257 × 9"]
    step_7 --> step_8
    step_9["9 · SourceTable<br/>orders<br/>o_orderkey, o_custkey<br/>15,000,000 × 2"]
    step_10["10 · EqJoin · 1.5M⋈15M<br/>orderkey<br/>1,460,257 × 10"]
    step_8 --> step_10
    step_9 --> step_10
    step_11["11 · Reorder<br/>1,460,257 × 11"]
    step_10 --> step_11
    step_12["12 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_13["13 · Filter · 8%<br/>2 × 2"]
    step_12 --> step_13
    step_14["14 · SourceTable<br/>customer<br/>c_custkey, c_nationkey<br/>1,500,000 × 2"]
    step_15["15 · EqJoin · 2⋈1.5M<br/>nationkey<br/>120,469 × 3"]
    step_13 --> step_15
    step_14 --> step_15
    step_16["16 · Reorder<br/>120,469 × 4"]
    step_15 --> step_16
    step_17["17 · EqJoin · 1.5M⋈120.5K<br/>custkey<br/>117,014 × 14"]
    step_11 --> step_17
    step_16 --> step_17
    step_18["18 · Reorder<br/>117,014 × 15"]
    step_17 --> step_18
    step_19["19 · Filter · 49.9%<br/>58,365 × 5"]
    step_18 --> step_19
    step_20["20 · Project<br/>58,365 × 4"]
    step_19 --> step_20
    step_21["21 · Reorder<br/>58,365 × 4"]
    step_20 --> step_21
    step_22["22 · GroupBy · 0.00685%<br/>supp_nation, cust_nation, l_year; sum(volume)<br/>4 × 4"]
    step_21 --> step_22
    step_23["23 · Sort<br/>supp_nation ASC, cust_nation ASC, l_year ASC<br/>4 × 4"]
    step_22 --> step_23
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2,step_5,step_9,step_12,step_14 source
    class step_1,step_6,step_13,step_19 filter
    class step_3,step_7,step_10,step_15,step_17 join
    class step_22 aggregate
    class step_4,step_8,step_11,step_16,step_18,step_20,step_21 transform
    class step_23 ordering
```


## Notes

- This query joins 5 tables.

- Nation is read multiple times.

- FIlter is applied twice on nation. This is not a problem since nation is very small.

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

```sql
Sort[o_year ASC]
  Project(o_year, mkt_share = (sum_brazil / sum_total))
    Aggregate(o_year; sum(brazil_volume), sum(volume))
      Project(o_year, volume, brazil_volume = case(is_brazil, volume, 0))
        Project(o_year, volume, is_brazil = str_eq(n_name, "BRAZIL"))
          Project(o_year = year(o_orderdate), volume = (l_extendedprice * (1 - l_discount)), nation = n_name)
            InnerJoin(on=(s_nationkey == n_nationkey#16))
              InnerJoin(on=(l_suppkey == s_suppkey))
                InnerJoin(on=(l_partkey == p_partkey))
                  InnerJoin(on=(o_orderkey == l_orderkey))
                    InnerJoin(on=(c_custkey == o_custkey))
                      InnerJoin(on=(n_nationkey#14 == c_nationkey))
                        InnerJoin(on=(r_regionkey == n_regionkey))
                          Filter(str_eq(r_name, "AMERICA"))
                            Scan(region [r_regionkey, r_name])
                          Scan(nation [n_nationkey, n_regionkey])
                        Scan(customer [c_custkey, c_nationkey])
                      Filter(((o_orderdate >= 19950101) && (o_orderdate <= 19961231)))
                        Scan(orders [o_orderkey, o_custkey, o_orderdate])
                    Scan(lineitem [l_orderkey, l_partkey, l_suppkey, l_extendedprice, l_discount])
                  Filter(str_eq(p_type, "ECONOMY ANODIZED STEEL"))
                    Scan(part [p_partkey, p_type])
                Scan(supplier [s_suppkey, s_nationkey])
              Scan(nation [n_nationkey, n_name])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>o_year ASC"]
    ir_1["Project<br/>o_year, mkt_share = (sum_brazil / sum_total)"]
    ir_0 --> ir_1
    ir_2["Aggregate<br/>o_year; sum(brazil_volume), sum(volume)"]
    ir_1 --> ir_2
    ir_3["Project<br/>o_year, volume, brazil_volume = case(is_brazil, volume, 0)"]
    ir_2 --> ir_3
    ir_4["Project<br/>o_year, volume, is_brazil = str_eq(n_name, #quot;BRAZIL#quot;)"]
    ir_3 --> ir_4
    ir_5["Project<br/>o_year = year(o_orderdate), volume = (l_extendedprice * (1 - l_discount)), nation = n_name"]
    ir_4 --> ir_5
    ir_6["InnerJoin<br/>on=(s_nationkey == n_nationkey#16)"]
    ir_5 --> ir_6
    ir_7["InnerJoin<br/>on=(l_suppkey == s_suppkey)"]
    ir_6 --> ir_7
    ir_8["InnerJoin<br/>on=(l_partkey == p_partkey)"]
    ir_7 --> ir_8
    ir_9["InnerJoin<br/>on=(o_orderkey == l_orderkey)"]
    ir_8 --> ir_9
    ir_10["InnerJoin<br/>on=(c_custkey == o_custkey)"]
    ir_9 --> ir_10
    ir_11["InnerJoin<br/>on=(n_nationkey#14 == c_nationkey)"]
    ir_10 --> ir_11
    ir_12["InnerJoin<br/>on=(r_regionkey == n_regionkey)"]
    ir_11 --> ir_12
    ir_13["Filter<br/>str_eq(r_name, #quot;AMERICA#quot;)"]
    ir_12 --> ir_13
    ir_14["Scan<br/>region · r_regionkey, r_name"]
    ir_13 --> ir_14
    ir_15["Scan<br/>nation · n_nationkey, n_regionkey"]
    ir_12 --> ir_15
    ir_16["Scan<br/>customer · c_custkey, c_nationkey"]
    ir_11 --> ir_16
    ir_17["Filter<br/>((o_orderdate &gt;= 19950101) &amp;&amp; (o_orderdate &lt;= 19961231))"]
    ir_10 --> ir_17
    ir_18["Scan<br/>orders · o_orderkey, o_custkey, o_orderdate"]
    ir_17 --> ir_18
    ir_19["Scan<br/>lineitem · l_orderkey, l_partkey, l_suppkey, l_extendedprice, l_discount"]
    ir_9 --> ir_19
    ir_20["Filter<br/>str_eq(p_type, #quot;ECONOMY ANODIZED STEEL#quot;)"]
    ir_8 --> ir_20
    ir_21["Scan<br/>part · p_partkey, p_type"]
    ir_20 --> ir_21
    ir_22["Scan<br/>supplier · s_suppkey, s_nationkey"]
    ir_7 --> ir_22
    ir_23["Scan<br/>nation · n_nationkey, n_name"]
    ir_6 --> ir_23
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_14,ir_15,ir_16,ir_18,ir_19,ir_21,ir_22,ir_23 source
    class ir_13,ir_17,ir_20 filter
    class ir_6,ir_7,ir_8,ir_9,ir_10,ir_11,ir_12 join
    class ir_2 aggregate
    class ir_1,ir_3,ir_4,ir_5 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 5 | 2 | region |  |  |  |  |  | r_regionkey, r_name |
| 1 | Filter | 1 | 1 | < | 20% | 0.0585326 | 0.0585326 | fuse | fuse |  |
| 2 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_regionkey |
| 3 | EqJoin | 5 | 2 | region⋈nation | 1⋈25 | 0.103954 | 0.103954 | hash_gfur | hash_gfur | regionkey |
| 4 | Reorder | 5 | 3 |  |  | 0.002112 | 0.002112 |  |  |  |
| 5 | SourceTable | 1500000 | 2 | customer |  |  |  |  |  | c_custkey, c_nationkey |
| 6 | EqJoin | 299436 | 4 | (region⋈nation)⋈customer | 5⋈1.5M | 1.42759 | 1.42759 | hash_gfur | hash_gfur | nationkey |
| 7 | Reorder | 299436 | 5 |  |  | 0.00200686 | 0.00200686 |  |  |  |
| 8 | SourceTable | 15000000 | 3 | orders |  |  |  |  |  | o_orderkey, o_custkey, o_orderdate |
| 9 | Filter | 4557513 | 3 | < | 30.4% | 4.67057 | 2.78978 | fuse | nofuse |  |
| 10 | EqJoin | 910360 | 7 | ((region⋈nation)⋈customer)⋈orders | 299.4K⋈4.6M | 8.14634 | 8.14634 | hash_gfur | hash_gfur | custkey |
| 11 | Reorder | 910360 | 8 |  |  | 0.00209371 | 0.00209371 |  |  |  |
| 12 | SourceTable | 59986052 | 5 | lineitem |  |  |  |  |  | l_orderkey, l_partkey, l_suppkey, l_extendedprice, l_discount |
| 13 | EqJoin | 3638929 | 12 | (((region⋈nation)⋈customer)⋈orders)⋈lineitem | 910.4K⋈60M | 57.1499 | 57.1499 | hash_gfur | hash_gfur | orderkey |
| 14 | Reorder | 3638929 | 13 |  |  | 0.00213943 | 0.00213943 |  |  |  |
| 15 | SourceTable | 2000000 | 2 | part |  |  |  |  |  | p_partkey, p_type |
| 16 | Filter | 13452 | 1 | < | 0.673% | 0.371173 | 0.371173 | fuse | fuse |  |
| 17 | EqJoin | 24254 | 13 | ((((region⋈nation)⋈customer)⋈orders)⋈lineitem) ⋈ part | 3.6M⋈13.5K | 6.92702 | 6.92702 | hash_gfur | hash_gfur | partkey |
| 18 | Reorder | 24254 | 14 |  |  | 0.00210286 | 0.00210286 |  |  |  |
| 19 | SourceTable | 100000 | 2 | supplier |  |  |  |  |  | s_suppkey, s_nationkey |
| 20 | EqJoin | 24254 | 15 | (((((region⋈nation)⋈customer)⋈orders)⋈lineitem) ⋈ part)⋈supplier | 24.3K⋈100K | 0.361367 | 0.361367 | hash_gfur | hash_gfur | suppkey |
| 21 | Reorder | 24254 | 16 |  |  | 0.00297143 | 0.00297143 |  |  |  |
| 22 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 23 | EqJoin | 24254 | 17 | ((((((region⋈nation)⋈customer)⋈orders)⋈lineitem) ⋈ part)⋈supplier)⋈nation | 24.3K⋈25 | 1.67774 | 1.67774 | hash_gfur | hash_gfur | nationkey |
| 24 | Reorder | 24254 | 18 |  |  | 0.010272 | 0.010272 |  |  |  |
| 25 | Project | 24254 | 3 |  |  | 0.121842 | 0.121842 | nofuse | nofuse | o_year, volume, nation |
| 26 | Project | 24254 | 3 |  |  | 0.0295131 | 0.0295131 | nofuse | nofuse | o_year, volume, is_brazil |
| 27 | Project | 24254 | 3 |  |  | 0.0164709 | 0.0164709 | nofuse | nofuse | o_year, volume, brazil_volume |
| 28 | Reorder | 24254 | 3 |  |  | 0.00184229 | 0.00184229 |  |  |  |
| 29 | GroupBy | 2 | 3 | < | 0.00825% | 0.222139 | 0.185051 | hash | sort_gfur | o_year; sum(brazil_volume), sum(volume) |
| 30 | Project | 2 | 2 |  |  | 0.016672 | 0.016672 | nofuse | nofuse | o_year, mkt_share |
| 31 | Sort | 2 | 2 |  |  | 0.0351543 | 0.0351543 | no_skf | no_skf | o_year ASC |
|  | Total |  |  |  |  | 81.3615 | 79.4436 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>region<br/>r_regionkey, r_name<br/>5 × 2"]
    step_1["1 · Filter · 20%<br/>1 × 1"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>nation<br/>n_nationkey, n_regionkey<br/>25 × 2"]
    step_3["3 · EqJoin · 1⋈25<br/>regionkey<br/>5 × 2"]
    step_1 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>5 × 3"]
    step_3 --> step_4
    step_5["5 · SourceTable<br/>customer<br/>c_custkey, c_nationkey<br/>1,500,000 × 2"]
    step_6["6 · EqJoin · 5⋈1.5M<br/>nationkey<br/>299,436 × 4"]
    step_4 --> step_6
    step_5 --> step_6
    step_7["7 · Reorder<br/>299,436 × 5"]
    step_6 --> step_7
    step_8["8 · SourceTable<br/>orders<br/>o_orderkey, o_custkey, o_orderdate<br/>15,000,000 × 3"]
    step_9["9 · Filter · 30.4%<br/>4,557,513 × 3"]
    step_8 --> step_9
    step_10["10 · EqJoin · 299.4K⋈4.6M<br/>custkey<br/>910,360 × 7"]
    step_7 --> step_10
    step_9 --> step_10
    step_11["11 · Reorder<br/>910,360 × 8"]
    step_10 --> step_11
    step_12["12 · SourceTable<br/>lineitem<br/>l_orderkey, l_partkey, l_suppkey, l_extendedprice, l_discount<br/>59,986,052 × 5"]
    step_13["13 · EqJoin · 910.4K⋈60M<br/>orderkey<br/>3,638,929 × 12"]
    step_11 --> step_13
    step_12 --> step_13
    step_14["14 · Reorder<br/>3,638,929 × 13"]
    step_13 --> step_14
    step_15["15 · SourceTable<br/>part<br/>p_partkey, p_type<br/>2,000,000 × 2"]
    step_16["16 · Filter · 0.673%<br/>13,452 × 1"]
    step_15 --> step_16
    step_17["17 · EqJoin · 3.6M⋈13.5K<br/>partkey<br/>24,254 × 13"]
    step_14 --> step_17
    step_16 --> step_17
    step_18["18 · Reorder<br/>24,254 × 14"]
    step_17 --> step_18
    step_19["19 · SourceTable<br/>supplier<br/>s_suppkey, s_nationkey<br/>100,000 × 2"]
    step_20["20 · EqJoin · 24.3K⋈100K<br/>suppkey<br/>24,254 × 15"]
    step_18 --> step_20
    step_19 --> step_20
    step_21["21 · Reorder<br/>24,254 × 16"]
    step_20 --> step_21
    step_22["22 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_23["23 · EqJoin · 24.3K⋈25<br/>nationkey<br/>24,254 × 17"]
    step_21 --> step_23
    step_22 --> step_23
    step_24["24 · Reorder<br/>24,254 × 18"]
    step_23 --> step_24
    step_25["25 · Project<br/>24,254 × 3"]
    step_24 --> step_25
    step_26["26 · Project<br/>24,254 × 3"]
    step_25 --> step_26
    step_27["27 · Project<br/>24,254 × 3"]
    step_26 --> step_27
    step_28["28 · Reorder<br/>24,254 × 3"]
    step_27 --> step_28
    step_29["29 · GroupBy · 0.00825%<br/>o_year; sum(brazil_volume), sum(volume)<br/>2 × 3"]
    step_28 --> step_29
    step_30["30 · Project<br/>2 × 2"]
    step_29 --> step_30
    step_31["31 · Sort<br/>o_year ASC<br/>2 × 2"]
    step_30 --> step_31
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2,step_5,step_8,step_12,step_15,step_19,step_22 source
    class step_1,step_9,step_16 filter
    class step_3,step_6,step_10,step_13,step_17,step_20,step_23 join
    class step_29 aggregate
    class step_4,step_7,step_11,step_14,step_18,step_21,step_24,step_25,step_26,step_27,step_28,step_30 transform
    class step_31 ordering
```


## Notes

- This query joins 7 tables.

- Nation is read multiple times.

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

```sql
Sort[n_name ASC, o_year DESC]
  Aggregate(n_name, o_year; sum(amount))
    Project(nation = n_name, o_year = year(o_orderdate), amount = ((l_extendedprice * (1 - l_discount)) - (ps_supplycost * l_quantity)))
      InnerJoin(on=(n_nationkey == s_nationkey))
        Scan(nation [n_nationkey, n_name])
        InnerJoin(on=(l_orderkey == o_orderkey))
          Filter((l_suppkey == ps_suppkey))
            InnerJoin(on=(l_partkey == ps_partkey))
              InnerJoin(on=(l_suppkey == s_suppkey))
                InnerJoin(on=(p_partkey == l_partkey))
                  Filter(contains(p_name, "green"))
                    Scan(part [p_partkey, p_name])
                  Scan(lineitem [l_orderkey, l_partkey, l_suppkey, l_quantity, l_extendedprice, l_discount])
                Scan(supplier [s_suppkey, s_nationkey])
              Scan(partsupp [ps_partkey, ps_suppkey, ps_supplycost])
          Scan(orders [o_orderkey, o_orderdate])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>n_name ASC, o_year DESC"]
    ir_1["Aggregate<br/>n_name, o_year; sum(amount)"]
    ir_0 --> ir_1
    ir_2["Project<br/>nation = n_name, o_year = year(o_orderdate), amount = ((l_extendedprice * (1 - l_discount)) - (ps_supplycos..."]
    ir_1 --> ir_2
    ir_3["InnerJoin<br/>on=(n_nationkey == s_nationkey)"]
    ir_2 --> ir_3
    ir_4["Scan<br/>nation · n_nationkey, n_name"]
    ir_3 --> ir_4
    ir_5["InnerJoin<br/>on=(l_orderkey == o_orderkey)"]
    ir_3 --> ir_5
    ir_6["Filter<br/>(l_suppkey == ps_suppkey)"]
    ir_5 --> ir_6
    ir_7["InnerJoin<br/>on=(l_partkey == ps_partkey)"]
    ir_6 --> ir_7
    ir_8["InnerJoin<br/>on=(l_suppkey == s_suppkey)"]
    ir_7 --> ir_8
    ir_9["InnerJoin<br/>on=(p_partkey == l_partkey)"]
    ir_8 --> ir_9
    ir_10["Filter<br/>contains(p_name, #quot;green#quot;)"]
    ir_9 --> ir_10
    ir_11["Scan<br/>part · p_partkey, p_name"]
    ir_10 --> ir_11
    ir_12["Scan<br/>lineitem · l_orderkey, l_partkey, l_suppkey, l_quantity, l_extendedprice, l_discount"]
    ir_9 --> ir_12
    ir_13["Scan<br/>supplier · s_suppkey, s_nationkey"]
    ir_8 --> ir_13
    ir_14["Scan<br/>partsupp · ps_partkey, ps_suppkey, ps_supplycost"]
    ir_7 --> ir_14
    ir_15["Scan<br/>orders · o_orderkey, o_orderdate"]
    ir_5 --> ir_15
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_4,ir_11,ir_12,ir_13,ir_14,ir_15 source
    class ir_6,ir_10 filter
    class ir_3,ir_5,ir_7,ir_8,ir_9 join
    class ir_1 aggregate
    class ir_2 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 1 | SourceTable | 2000000 | 2 | part |  |  |  |  |  | p_partkey, p_name |
| 2 | Filter | 108782 | 1 | < | 5.44% | 1.0344 | 1.0344 | fuse | fuse |  |
| 3 | SourceTable | 59986052 | 6 | lineitem |  |  |  |  |  | l_orderkey, l_partkey, l_suppkey, l_quantity, l_extendedprice, l_discount |
| 4 | EqJoin | 3261613 | 6 | part⋈lineitem | 108.8K⋈60M | 53.2063 | 53.2063 | hash_gfur | hash_gfur | partkey |
| 5 | Reorder | 3261613 | 7 |  |  | 0.00196 | 0.00196 |  |  |  |
| 6 | SourceTable | 100000 | 2 | supplier |  |  |  |  |  | s_suppkey, s_nationkey |
| 7 | EqJoin | 3261613 | 8 | (part⋈lineitem)⋈supplier | 3.3M⋈100K | 25.2001 | 25.2001 | hash_gfur | hash_gfur | suppkey |
| 8 | Reorder | 3261613 | 9 |  |  | 0.002168 | 0.002168 |  |  |  |
| 9 | SourceTable | 8000000 | 3 | partsupp |  |  |  |  |  | ps_partkey, ps_suppkey, ps_supplycost |
| 10 | EqJoin | 13046452 | 11 | ((part⋈lineitem)⋈supplier)⋈partsupp | 3.3M⋈8M | 35.6903 | 35.6903 | hash_gfur | hash_gfur | partkey |
| 11 | Reorder | 13046452 | 12 |  |  | 0.00336 | 0.00336 |  |  |  |
| 12 | Filter | 3261613 | 6 | < | 25% | 4.71559 | 4.71559 | fuse | fuse |  |
| 13 | SourceTable | 15000000 | 2 | orders |  |  |  |  |  | o_orderkey, o_orderdate |
| 14 | EqJoin | 3261613 | 7 | (((part⋈lineitem)⋈supplier)⋈partsupp)⋈orders | 3.3M⋈15M | 65.2255 | 65.2255 | hash_gfur | hash_gfur | orderkey |
| 15 | Reorder | 3261613 | 8 |  |  | 0.001824 | 0.001824 |  |  |  |
| 16 | EqJoin | 3261613 | 9 | nation⋈((((part⋈lineitem)⋈supplier)⋈partsupp) ⋈ orders) | 25⋈3.3M | 5.33718 | 5.33718 | hash_gfur | hash_gfur | nationkey |
| 17 | Reorder | 3261613 | 10 |  |  | 0.011896 | 0.011896 |  |  |  |
| 18 | Project | 3261613 | 3 |  |  | 2.9913 | 2.9913 | nofuse | nofuse | nation, o_year, amount |
| 19 | Reorder | 3261613 | 3 |  |  | 0.007056 | 0.007056 |  |  |  |
| 20 | GroupBy | 175 | 3 | < | 0.00537% | 2.02798 | 2.02798 | hash | hash | nation, o_year; sum(amount) |
| 21 | Sort | 175 | 3 |  |  | 0.75868 | 0.762672 | no_skf | skf | nation ASC, o_year DESC |
|  | Total |  |  |  |  | 196.216 | 196.22 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_1["1 · SourceTable<br/>part<br/>p_partkey, p_name<br/>2,000,000 × 2"]
    step_2["2 · Filter · 5.44%<br/>108,782 × 1"]
    step_1 --> step_2
    step_3["3 · SourceTable<br/>lineitem<br/>l_orderkey, l_partkey, l_suppkey, l_quantity, l_extendedprice, l_discount<br/>59,986,052 × 6"]
    step_4["4 · EqJoin · 108.8K⋈60M<br/>partkey<br/>3,261,613 × 6"]
    step_2 --> step_4
    step_3 --> step_4
    step_5["5 · Reorder<br/>3,261,613 × 7"]
    step_4 --> step_5
    step_6["6 · SourceTable<br/>supplier<br/>s_suppkey, s_nationkey<br/>100,000 × 2"]
    step_7["7 · EqJoin · 3.3M⋈100K<br/>suppkey<br/>3,261,613 × 8"]
    step_5 --> step_7
    step_6 --> step_7
    step_8["8 · Reorder<br/>3,261,613 × 9"]
    step_7 --> step_8
    step_9["9 · SourceTable<br/>partsupp<br/>ps_partkey, ps_suppkey, ps_supplycost<br/>8,000,000 × 3"]
    step_10["10 · EqJoin · 3.3M⋈8M<br/>partkey<br/>13,046,452 × 11"]
    step_8 --> step_10
    step_9 --> step_10
    step_11["11 · Reorder<br/>13,046,452 × 12"]
    step_10 --> step_11
    step_12["12 · Filter · 25%<br/>3,261,613 × 6"]
    step_11 --> step_12
    step_13["13 · SourceTable<br/>orders<br/>o_orderkey, o_orderdate<br/>15,000,000 × 2"]
    step_14["14 · EqJoin · 3.3M⋈15M<br/>orderkey<br/>3,261,613 × 7"]
    step_12 --> step_14
    step_13 --> step_14
    step_15["15 · Reorder<br/>3,261,613 × 8"]
    step_14 --> step_15
    step_16["16 · EqJoin · 25⋈3.3M<br/>nationkey<br/>3,261,613 × 9"]
    step_0 --> step_16
    step_15 --> step_16
    step_17["17 · Reorder<br/>3,261,613 × 10"]
    step_16 --> step_17
    step_18["18 · Project<br/>3,261,613 × 3"]
    step_17 --> step_18
    step_19["19 · Reorder<br/>3,261,613 × 3"]
    step_18 --> step_19
    step_20["20 · GroupBy · 0.00537%<br/>nation, o_year; sum(amount)<br/>175 × 3"]
    step_19 --> step_20
    step_21["21 · Sort<br/>nation ASC, o_year DESC<br/>175 × 3"]
    step_20 --> step_21
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1,step_3,step_6,step_9,step_13 source
    class step_2,step_12 filter
    class step_4,step_7,step_10,step_14,step_16 join
    class step_20 aggregate
    class step_5,step_8,step_11,step_15,step_17,step_18,step_19 transform
    class step_21 ordering
```


## Notes

- This query joins 6 tables.

- Multikey joins could result in smaller joins

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

```sql
Limit(n=20)
  Sort[revenue DESC]
    Project(c_custkey, c_name, revenue, c_acctbal, n_name, c_address, c_phone, c_comment)
      InnerJoin(on=(n_nationkey == c_nationkey))
        Scan(nation [n_nationkey, n_name])
        InnerJoin(on=(c_custkey == o_custkey))
          Scan(customer [c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_comment])
          Aggregate(o_custkey; sum(disc_price))
            Project(o_custkey, disc_price = (l_extendedprice * (1 - l_discount)))
              InnerJoin(on=(l_orderkey == o_orderkey))
                Filter(str_eq(l_returnflag, "R"))
                  Scan(lineitem [l_orderkey, l_returnflag, l_extendedprice, l_discount])
                Filter(((o_orderdate >= 19931001) && (o_orderdate < 19940101)))
                  Scan(orders [o_orderkey, o_custkey, o_orderdate])
```

```mermaid
flowchart TD
    ir_0["Limit<br/>n=20"]
    ir_1["Sort<br/>revenue DESC"]
    ir_0 --> ir_1
    ir_2["Project<br/>c_custkey, c_name, revenue, c_acctbal, n_name, c_address, c_phone, c_comment"]
    ir_1 --> ir_2
    ir_3["InnerJoin<br/>on=(n_nationkey == c_nationkey)"]
    ir_2 --> ir_3
    ir_4["Scan<br/>nation · n_nationkey, n_name"]
    ir_3 --> ir_4
    ir_5["InnerJoin<br/>on=(c_custkey == o_custkey)"]
    ir_3 --> ir_5
    ir_6["Scan<br/>customer · c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_comment"]
    ir_5 --> ir_6
    ir_7["Aggregate<br/>o_custkey; sum(disc_price)"]
    ir_5 --> ir_7
    ir_8["Project<br/>o_custkey, disc_price = (l_extendedprice * (1 - l_discount))"]
    ir_7 --> ir_8
    ir_9["InnerJoin<br/>on=(l_orderkey == o_orderkey)"]
    ir_8 --> ir_9
    ir_10["Filter<br/>str_eq(l_returnflag, #quot;R#quot;)"]
    ir_9 --> ir_10
    ir_11["Scan<br/>lineitem · l_orderkey, l_returnflag, l_extendedprice, l_discount"]
    ir_10 --> ir_11
    ir_12["Filter<br/>((o_orderdate &gt;= 19931001) &amp;&amp; (o_orderdate &lt; 19940101))"]
    ir_9 --> ir_12
    ir_13["Scan<br/>orders · o_orderkey, o_custkey, o_orderdate"]
    ir_12 --> ir_13
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_4,ir_6,ir_11,ir_13 source
    class ir_10,ir_12 filter
    class ir_3,ir_5,ir_9 join
    class ir_7 aggregate
    class ir_2,ir_8 transform
    class ir_0,ir_1 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 1 | SourceTable | 1500000 | 7 | customer |  |  |  |  |  | c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_comment |
| 2 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_orderkey, l_returnflag, l_extendedprice, l_discount |
| 3 | Filter | 14808183 | 3 | < | 24.7% | 11.7255 | 11.7255 | fuse | fuse |  |
| 4 | SourceTable | 15000000 | 3 | orders |  |  |  |  |  | o_orderkey, o_custkey, o_orderdate |
| 5 | Filter | 573157 | 2 | < | 3.82% | 3.06078 | 2.06517 | fuse | nofuse |  |
| 6 | EqJoin | 1147084 | 4 | lineitem⋈orders | 14.8M⋈573.2K | 16.2753 | 16.2753 | hash_gfur | hash_gfur | orderkey |
| 7 | Reorder | 1147084 | 5 |  |  | 0.00184686 | 0.00184686 |  |  |  |
| 8 | Project | 1147084 | 2 |  |  | 0.355273 | 0.355273 | nofuse | nofuse | o_custkey, disc_price |
| 9 | Reorder | 1147084 | 2 |  |  | 0.00183314 | 0.00183314 |  |  |  |
| 10 | GroupBy | 381105 | 2 | < | 33.2% | 1.42471 | 1.42471 | hash | hash | o_custkey; sum(disc_price) |
| 11 | EqJoin | 381105 | 8 | customer⋈(lineitem⋈orders) | 1.5M⋈381.1K | 26.842 | 26.842 | hash_gfur | hash_gfur | custkey |
| 12 | Reorder | 381105 | 9 |  |  | 0.0150674 | 0.0150674 |  |  |  |
| 13 | EqJoin | 381105 | 10 | nation⋈(customer⋈(lineitem⋈orders)) | 25⋈381.1K | 7.95907 | 7.95907 | hash_gfur | hash_gfur | nationkey |
| 14 | Reorder | 381105 | 11 |  |  | 0.016224 | 0.016224 |  |  |  |
| 15 | Project | 381105 | 8 |  |  | 7.38965 | 7.38965 | nofuse | nofuse | c_custkey, c_name, revenue, c_acctbal, n_name, c_address, c_phone, c_comment |
| 16 | TopK | 20 | 8 | < | 0.00525% | 0.709536 | 0.709536 |  |  |  |
|  | Total |  |  |  |  | 75.7768 | 74.7812 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_1["1 · SourceTable<br/>customer<br/>c_custkey, c_name, c_address, c_nationkey, c_phone, c_acctbal, c_comment<br/>1,500,000 × 7"]
    step_2["2 · SourceTable<br/>lineitem<br/>l_orderkey, l_returnflag, l_extendedprice, l_discount<br/>59,986,052 × 4"]
    step_3["3 · Filter · 24.7%<br/>14,808,183 × 3"]
    step_2 --> step_3
    step_4["4 · SourceTable<br/>orders<br/>o_orderkey, o_custkey, o_orderdate<br/>15,000,000 × 3"]
    step_5["5 · Filter · 3.82%<br/>573,157 × 2"]
    step_4 --> step_5
    step_6["6 · EqJoin · 14.8M⋈573.2K<br/>orderkey<br/>1,147,084 × 4"]
    step_3 --> step_6
    step_5 --> step_6
    step_7["7 · Reorder<br/>1,147,084 × 5"]
    step_6 --> step_7
    step_8["8 · Project<br/>1,147,084 × 2"]
    step_7 --> step_8
    step_9["9 · Reorder<br/>1,147,084 × 2"]
    step_8 --> step_9
    step_10["10 · GroupBy · 33.2%<br/>o_custkey; sum(disc_price)<br/>381,105 × 2"]
    step_9 --> step_10
    step_11["11 · EqJoin · 1.5M⋈381.1K<br/>custkey<br/>381,105 × 8"]
    step_1 --> step_11
    step_10 --> step_11
    step_12["12 · Reorder<br/>381,105 × 9"]
    step_11 --> step_12
    step_13["13 · EqJoin · 25⋈381.1K<br/>nationkey<br/>381,105 × 10"]
    step_0 --> step_13
    step_12 --> step_13
    step_14["14 · Reorder<br/>381,105 × 11"]
    step_13 --> step_14
    step_15["15 · Project<br/>381,105 × 8"]
    step_14 --> step_15
    step_16["16 · TopK · 0.00525%<br/>20 × 8"]
    step_15 --> step_16
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1,step_2,step_4 source
    class step_3,step_5 filter
    class step_6,step_11,step_13 join
    class step_10 aggregate
    class step_7,step_8,step_9,step_12,step_14,step_15 transform
    class step_16 ordering
```


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

```sql
Sort[partkey_value DESC]
  Project(ps_partkey, partkey_value)
    Filter((partkey_value > threshold))
      CrossJoin
        Aggregate(ps_partkey; sum(value))
          Project(ps_partkey, value = (ps_supplycost * ps_availqty))
            InnerJoin(on=(ps_suppkey == s_suppkey))
              Scan(partsupp [ps_partkey, ps_suppkey, ps_availqty, ps_supplycost])
              InnerJoin(on=(n_nationkey == s_nationkey))
                Filter(str_eq(n_name, "GERMANY"))
                  Scan(nation [n_nationkey, n_name])
                Scan(supplier [s_suppkey, s_nationkey])
        Project(threshold = (global_sum * 0.0001))
          Aggregate(sum(value))
            Project(ps_partkey, value = (ps_supplycost * ps_availqty))
              InnerJoin(on=(ps_suppkey == s_suppkey))
                Scan(partsupp [ps_partkey, ps_suppkey, ps_availqty, ps_supplycost])
                InnerJoin(on=(n_nationkey == s_nationkey))
                  Filter(str_eq(n_name, "GERMANY"))
                    Scan(nation [n_nationkey, n_name])
                  Scan(supplier [s_suppkey, s_nationkey])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>partkey_value DESC"]
    ir_1["Project<br/>ps_partkey, partkey_value"]
    ir_0 --> ir_1
    ir_2["Filter<br/>(partkey_value &gt; threshold)"]
    ir_1 --> ir_2
    ir_3["CrossJoin"]
    ir_2 --> ir_3
    ir_4["Aggregate<br/>ps_partkey; sum(value)"]
    ir_3 --> ir_4
    ir_5["Project<br/>ps_partkey, value = (ps_supplycost * ps_availqty)"]
    ir_4 --> ir_5
    ir_6["InnerJoin<br/>on=(ps_suppkey == s_suppkey)"]
    ir_5 --> ir_6
    ir_7["Scan<br/>partsupp · ps_partkey, ps_suppkey, ps_availqty, ps_supplycost"]
    ir_6 --> ir_7
    ir_8["InnerJoin<br/>on=(n_nationkey == s_nationkey)"]
    ir_6 --> ir_8
    ir_9["Filter<br/>str_eq(n_name, #quot;GERMANY#quot;)"]
    ir_8 --> ir_9
    ir_10["Scan<br/>nation · n_nationkey, n_name"]
    ir_9 --> ir_10
    ir_11["Scan<br/>supplier · s_suppkey, s_nationkey"]
    ir_8 --> ir_11
    ir_12["Project<br/>threshold = (global_sum * 0.0001)"]
    ir_3 --> ir_12
    ir_13["Aggregate<br/>sum(value)"]
    ir_12 --> ir_13
    ir_14["Project<br/>ps_partkey, value = (ps_supplycost * ps_availqty)"]
    ir_13 --> ir_14
    ir_15["InnerJoin<br/>on=(ps_suppkey == s_suppkey)"]
    ir_14 --> ir_15
    ir_16["Scan<br/>partsupp · ps_partkey, ps_suppkey, ps_availqty, ps_supplycost"]
    ir_15 --> ir_16
    ir_17["InnerJoin<br/>on=(n_nationkey == s_nationkey)"]
    ir_15 --> ir_17
    ir_18["Filter<br/>str_eq(n_name, #quot;GERMANY#quot;)"]
    ir_17 --> ir_18
    ir_19["Scan<br/>nation · n_nationkey, n_name"]
    ir_18 --> ir_19
    ir_20["Scan<br/>supplier · s_suppkey, s_nationkey"]
    ir_17 --> ir_20
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_7,ir_10,ir_11,ir_16,ir_19,ir_20 source
    class ir_2,ir_9,ir_18 filter
    class ir_3,ir_6,ir_8,ir_15,ir_17 join
    class ir_4,ir_13 aggregate
    class ir_1,ir_5,ir_12,ir_14 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 8000000 | 4 | partsupp |  |  |  |  |  | ps_partkey, ps_suppkey, ps_availqty, ps_supplycost |
| 1 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 2 | Filter | 1 | 1 | < | 4% | 0.0505006 | 0.0505006 | nofuse | nofuse |  |
| 3 | SourceTable | 100000 | 2 | supplier |  |  |  |  |  | s_suppkey, s_nationkey |
| 4 | EqJoin | 4049 | 2 | nation⋈supplier | 1⋈100K | 0.139422 | 0.139422 | hash_gfur | hash_gfur | nationkey |
| 5 | Reorder | 4049 | 3 |  |  | 0.00201829 | 0.00201829 |  |  |  |
| 6 | EqJoin | 323920 | 6 | partsupp⋈(nation⋈supplier) | 8M⋈4K | 36.9888 | 36.9888 | hash_gfur | hash_gfur | suppkey |
| 7 | Reorder | 323920 | 7 |  |  | 0.002544 | 0.002544 |  |  |  |
| 8 | Project | 323920 | 2 |  |  | 0.0813806 | 0.0813806 | nofuse | nofuse | ps_partkey, value |
| 9 | Reorder | 323920 | 2 |  |  | 0.0388914 | 0.0388914 |  |  |  |
| 10 | GroupBy | 304774 | 2 | < | 94.1% | 0.733605 | 0.563847 | hash | sort_gftr | ps_partkey; sum(value) |
| 11 | Reorder | 323920 | 1 |  |  | 0.00186286 | 0.00186286 |  |  |  |
| 12 | ScalarAgg | 1 | 1 |  |  | 0.0489097 | 0.0489097 |  |  | sum(value) |
| 13 | Project | 1 | 1 |  |  | 0.014512 | 0.014512 | nofuse | nofuse | threshold |
| 14 | CrossJoin | 304774 | 3 | (partsupp⋈(nation⋈supplier))⋈(partsupp⋈(nation ⋈ supplier)) | 304.8K⋈1 | 0.137701 | 0.137701 |  |  |  |
| 15 | Filter | 0 | 2 | < | 0% | 0.133986 | 0.133986 | nofuse | nofuse |  |
| 16 | Project | 0 | 2 |  |  | 0.00196343 | 0.00196343 | nofuse | nofuse | ps_partkey, value |
| 17 | Sort | 0 | 2 |  |  | 0.00207543 | 0.00207543 | no_skf | no_skf | value DESC |
|  | Total |  |  |  |  | 38.3782 | 38.2084 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>partsupp<br/>ps_partkey, ps_suppkey, ps_availqty, ps_supplycost<br/>8,000,000 × 4"]
    step_1["1 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_2["2 · Filter · 4%<br/>1 × 1"]
    step_1 --> step_2
    step_3["3 · SourceTable<br/>supplier<br/>s_suppkey, s_nationkey<br/>100,000 × 2"]
    step_4["4 · EqJoin · 1⋈100K<br/>nationkey<br/>4,049 × 2"]
    step_2 --> step_4
    step_3 --> step_4
    step_5["5 · Reorder<br/>4,049 × 3"]
    step_4 --> step_5
    step_6["6 · EqJoin · 8M⋈4K<br/>suppkey<br/>323,920 × 6"]
    step_0 --> step_6
    step_5 --> step_6
    step_7["7 · Reorder<br/>323,920 × 7"]
    step_6 --> step_7
    step_8["8 · Project<br/>323,920 × 2"]
    step_7 --> step_8
    step_9["9 · Reorder<br/>323,920 × 2"]
    step_8 --> step_9
    step_10["10 · GroupBy · 94.1%<br/>ps_partkey; sum(value)<br/>304,774 × 2"]
    step_9 --> step_10
    step_11["11 · Reorder<br/>323,920 × 1"]
    step_8 --> step_11
    step_12["12 · ScalarAgg<br/>sum(value)<br/>1 × 1"]
    step_11 --> step_12
    step_13["13 · Project<br/>1 × 1"]
    step_12 --> step_13
    step_14["14 · CrossJoin · 304.8K⋈1<br/>304,774 × 3"]
    step_10 --> step_14
    step_13 --> step_14
    step_15["15 · Filter · 0%<br/>0 × 2"]
    step_14 --> step_15
    step_16["16 · Project<br/>0 × 2"]
    step_15 --> step_16
    step_17["17 · Sort<br/>value DESC<br/>0 × 2"]
    step_16 --> step_17
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1,step_3 source
    class step_2,step_15 filter
    class step_4,step_6,step_14 join
    class step_10,step_12 aggregate
    class step_5,step_7,step_8,step_9,step_11,step_13,step_16 transform
    class step_17 ordering
```


## Notes

- Repeated computation of the global threshold

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

```sql
Sort[l_shipmode ASC]
  Aggregate(l_shipmode; sum(high), sum(low))
    Project(l_shipmode, high = case(is_high, 1, 0), low = case(is_high, 0, 1))
      Project(l_shipmode, is_high = (str_eq(o_orderpriority, "1-URGENT") || str_eq(o_orderpriority, "2-HIGH")))
        InnerJoin(on=(o_orderkey == l_orderkey))
          Scan(orders [o_orderkey, o_orderpriority])
          Filter(((((str_in(l_shipmode, ["MAIL", "SHIP"]) && (l_commitdate < l_receiptdate)) && (l_shipdate < l_commitdate)) && (l_receiptdate >= 19940101)) && (l_receiptdate < 19950101)))
            Scan(lineitem [l_orderkey, l_shipmode, l_commitdate, l_receiptdate, l_shipdate])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>l_shipmode ASC"]
    ir_1["Aggregate<br/>l_shipmode; sum(high), sum(low)"]
    ir_0 --> ir_1
    ir_2["Project<br/>l_shipmode, high = case(is_high, 1, 0), low = case(is_high, 0, 1)"]
    ir_1 --> ir_2
    ir_3["Project<br/>l_shipmode, is_high = (str_eq(o_orderpriority, #quot;1-URGENT#quot;) || str_eq(o_orderpriority, #quot;2-HIGH#quot;))"]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(o_orderkey == l_orderkey)"]
    ir_3 --> ir_4
    ir_5["Scan<br/>orders · o_orderkey, o_orderpriority"]
    ir_4 --> ir_5
    ir_6["Filter<br/>((((str_in(l_shipmode, [#quot;MAIL#quot;, #quot;SHIP#quot;]) &amp;&amp; (l_commitdate &lt; l_receiptdate)) &amp;&amp; (l_shipdate &lt; l_commitdate))..."]
    ir_4 --> ir_6
    ir_7["Scan<br/>lineitem · l_orderkey, l_shipmode, l_commitdate, l_receiptdate, l_shipdate"]
    ir_6 --> ir_7
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_5,ir_7 source
    class ir_6 filter
    class ir_4 join
    class ir_1 aggregate
    class ir_2,ir_3 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 15000000 | 2 | orders |  |  |  |  |  | o_orderkey, o_orderpriority |
| 1 | SourceTable | 59986052 | 5 | lineitem |  |  |  |  |  | l_orderkey, l_shipmode, l_commitdate, l_receiptdate, l_shipdate |
| 2 | Filter | 310803 | 2 | < | 0.518% | 29.9621 | 23.6523 | fuse | nofuse |  |
| 3 | EqJoin | 310803 | 3 | orders⋈lineitem | 15M⋈310.8K | 26.6645 | 26.6645 | hash_gfur | hash_gfur | orderkey |
| 4 | Reorder | 310803 | 4 |  |  | 0.0115484 | 0.0115484 |  |  |  |
| 5 | Project | 310803 | 2 |  |  | 0.269799 | 0.269799 | nofuse | nofuse | l_shipmode, is_high |
| 6 | Project | 310803 | 3 |  |  | 0.0946809 | 0.0946809 | nofuse | nofuse | l_shipmode, high, low |
| 7 | Reorder | 310803 | 3 |  |  | 0.00198756 | 0.00198756 |  |  |  |
| 8 | GroupBy | 2 | 3 | < | 0.000643% | 0.397518 | 0.397518 | hash | hash | l_shipmode; sum(high), sum(low) |
| 9 | Sort | 2 | 3 |  |  | 0.178844 | 0.178844 | no_skf | no_skf | l_shipmode ASC |
|  | Total |  |  |  |  | 57.581 | 51.2712 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>orders<br/>o_orderkey, o_orderpriority<br/>15,000,000 × 2"]
    step_1["1 · SourceTable<br/>lineitem<br/>l_orderkey, l_shipmode, l_commitdate, l_receiptdate, l_shipdate<br/>59,986,052 × 5"]
    step_2["2 · Filter · 0.518%<br/>310,803 × 2"]
    step_1 --> step_2
    step_3["3 · EqJoin · 15M⋈310.8K<br/>orderkey<br/>310,803 × 3"]
    step_0 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>310,803 × 4"]
    step_3 --> step_4
    step_5["5 · Project<br/>310,803 × 2"]
    step_4 --> step_5
    step_6["6 · Project<br/>310,803 × 3"]
    step_5 --> step_6
    step_7["7 · Reorder<br/>310,803 × 3"]
    step_6 --> step_7
    step_8["8 · GroupBy · 0.000643%<br/>l_shipmode; sum(high), sum(low)<br/>2 × 3"]
    step_7 --> step_8
    step_9["9 · Sort<br/>l_shipmode ASC<br/>2 × 3"]
    step_8 --> step_9
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1 source
    class step_2 filter
    class step_3 join
    class step_8 aggregate
    class step_4,step_5,step_6,step_7 transform
    class step_9 ordering
```


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

```sql
Sort[custdist DESC, c_count#6 DESC]
  Aggregate(c_count#6; count_all(*))
    Concat(#inputs=2)
      Aggregate(c_custkey#0; count_all(*))
        InnerJoin(on=(c_custkey#0 == o_custkey))
          Scan(customer [c_custkey])
          Filter(!contains_multiple(o_comment, ["special", "requests"]))
            Scan(orders [o_custkey, o_comment])
      Project(c_custkey = c_custkey#0, c_count = 0)
        LeftAntiJoin(on=(c_custkey#0 == o_custkey))
          Scan(customer [c_custkey])
          Filter(!contains_multiple(o_comment, ["special", "requests"]))
            Scan(orders [o_custkey, o_comment])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>custdist DESC, c_count#6 DESC"]
    ir_1["Aggregate<br/>c_count#6; count_all(*)"]
    ir_0 --> ir_1
    ir_2["Concat<br/>#inputs=2"]
    ir_1 --> ir_2
    ir_3["Aggregate<br/>c_custkey#0; count_all(*)"]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(c_custkey#0 == o_custkey)"]
    ir_3 --> ir_4
    ir_5["Scan<br/>customer · c_custkey"]
    ir_4 --> ir_5
    ir_6["Filter<br/>!contains_multiple(o_comment, [#quot;special#quot;, #quot;requests#quot;])"]
    ir_4 --> ir_6
    ir_7["Scan<br/>orders · o_custkey, o_comment"]
    ir_6 --> ir_7
    ir_8["Project<br/>c_custkey = c_custkey#0, c_count = 0"]
    ir_2 --> ir_8
    ir_9["LeftAntiJoin<br/>on=(c_custkey#0 == o_custkey)"]
    ir_8 --> ir_9
    ir_10["Scan<br/>customer · c_custkey"]
    ir_9 --> ir_10
    ir_11["Filter<br/>!contains_multiple(o_comment, [#quot;special#quot;, #quot;requests#quot;])"]
    ir_9 --> ir_11
    ir_12["Scan<br/>orders · o_custkey, o_comment"]
    ir_11 --> ir_12
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_5,ir_7,ir_10,ir_12 source
    class ir_6,ir_11 filter
    class ir_4,ir_9 join
    class ir_1,ir_3 aggregate
    class ir_2,ir_8 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 1500000 | 1 | customer |  |  |  |  |  | c_custkey |
| 1 | SourceTable | 15000000 | 2 | orders |  |  |  |  |  | o_custkey, o_comment |
| 2 | Filter | 14845369 | 1 | < | 99% | 12.0886 | 12.0886 | fuse | fuse |  |
| 3 | EqJoin | 14845369 | 1 | customer⋈orders | 1.5M⋈14.8M | 71.4798 | 71.4798 | hash_gfur | hash_gfur | custkey |
| 4 | Reorder | 14845369 | 2 |  |  | 0.00172 | 0.00172 |  |  |  |
| 5 | Reorder | 14845369 | 1 |  |  | 0.001416 | 0.001416 |  |  |  |
| 6 | GroupBy | 999981 | 2 | < | 6.74% | 46.8193 | 20.7011 | hash | sort_gftr | c_custkey; count_all(*) |
| 7 | AntiJoin | 500019 | 1 | customer⋈orders | 1.5M⋈14.8M | 12.1619 | 12.1619 |  |  | c_custkey; o_custkey |
| 8 | Reorder | 500019 | 1 |  |  | 0.001456 | 0.001456 |  |  |  |
| 9 | Project | 500019 | 2 |  |  | 0.089328 | 0.089328 | nofuse | nofuse | c_custkey, c_count |
| 10 | Concat | 1500000 | 2 |  |  | 0.223456 | 0.223456 |  |  |  |
| 11 | Reorder | 1500000 | 1 |  |  | 0.001824 | 0.001824 |  |  |  |
| 12 | GroupBy | 45 | 2 | < | 0.003% | 0.999672 | 0.999672 | hash | hash | output column 1; count_all(*) |
| 13 | Sort | 45 | 2 |  |  | 0.327088 | 0.135744 | no_skf | skf | count_all(*) DESC, output column 1 DESC |
|  | Total |  |  |  |  | 144.196 | 117.886 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>customer<br/>c_custkey<br/>1,500,000 × 1"]
    step_1["1 · SourceTable<br/>orders<br/>o_custkey, o_comment<br/>15,000,000 × 2"]
    step_2["2 · Filter · 99%<br/>14,845,369 × 1"]
    step_1 --> step_2
    step_3["3 · EqJoin · 1.5M⋈14.8M<br/>custkey<br/>14,845,369 × 1"]
    step_0 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>14,845,369 × 2"]
    step_3 --> step_4
    step_5["5 · Reorder<br/>14,845,369 × 1"]
    step_4 --> step_5
    step_6["6 · GroupBy · 6.74%<br/>c_custkey; count_all(*)<br/>999,981 × 2"]
    step_5 --> step_6
    step_7["7 · AntiJoin · 1.5M⋈14.8M<br/>c_custkey; o_custkey<br/>500,019 × 1"]
    step_0 --> step_7
    step_2 --> step_7
    step_8["8 · Reorder<br/>500,019 × 1"]
    step_7 --> step_8
    step_9["9 · Project<br/>500,019 × 2"]
    step_8 --> step_9
    step_10["10 · Concat<br/>1,500,000 × 2"]
    step_6 --> step_10
    step_9 --> step_10
    step_11["11 · Reorder<br/>1,500,000 × 1"]
    step_10 --> step_11
    step_12["12 · GroupBy · 0.003%<br/>output column 1; count_all(*)<br/>45 × 2"]
    step_11 --> step_12
    step_13["13 · Sort<br/>count_all(*) DESC, output column 1 DESC<br/>45 × 2"]
    step_12 --> step_13
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1 source
    class step_2 filter
    class step_3,step_7 join
    class step_6,step_12 aggregate
    class step_4,step_5,step_8,step_9,step_10,step_11 transform
    class step_13 ordering
```


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

```sql
Project(promo_revenue = ((100 * sum_promo) / sum_total))
  Aggregate(sum(promo_volume), sum(disc_price))
    Project(promo_volume = case(is_promo, disc_price, 0), volume = disc_price)
      Project(disc_price = (l_extendedprice * (1 - l_discount)), is_promo = startswith(p_type, "PROMO"))
        InnerJoin(on=(l_partkey == p_partkey))
          Filter(((l_shipdate >= 19950901) && (l_shipdate < 19951001)))
            Scan(lineitem [l_partkey, l_extendedprice, l_discount, l_shipdate])
          Scan(part [p_partkey, p_type])
```

```mermaid
flowchart TD
    ir_0["Project<br/>promo_revenue = ((100 * sum_promo) / sum_total)"]
    ir_1["Aggregate<br/>sum(promo_volume), sum(disc_price)"]
    ir_0 --> ir_1
    ir_2["Project<br/>promo_volume = case(is_promo, disc_price, 0), volume = disc_price"]
    ir_1 --> ir_2
    ir_3["Project<br/>disc_price = (l_extendedprice * (1 - l_discount)), is_promo = startswith(p_type, #quot;PROMO#quot;)"]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(l_partkey == p_partkey)"]
    ir_3 --> ir_4
    ir_5["Filter<br/>((l_shipdate &gt;= 19950901) &amp;&amp; (l_shipdate &lt; 19951001))"]
    ir_4 --> ir_5
    ir_6["Scan<br/>lineitem · l_partkey, l_extendedprice, l_discount, l_shipdate"]
    ir_5 --> ir_6
    ir_7["Scan<br/>part · p_partkey, p_type"]
    ir_4 --> ir_7
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_6,ir_7 source
    class ir_5 filter
    class ir_4 join
    class ir_1 aggregate
    class ir_0,ir_2,ir_3 transform
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_partkey, l_extendedprice, l_discount, l_shipdate |
| 1 | Filter | 749223 | 3 | < | 1.25% | 14.3196 | 9.97113 | fuse | nofuse |  |
| 2 | SourceTable | 2000000 | 2 | part |  |  |  |  |  | p_partkey, p_type |
| 3 | EqJoin | 749223 | 4 | lineitem⋈part | 749.2K⋈2M | 8.03465 | 8.03465 | hash_gfur | hash_gfur | partkey |
| 4 | Reorder | 749223 | 5 |  |  | 0.00806545 | 0.00806545 |  |  |  |
| 5 | Project | 749223 | 2 |  |  | 0.297175 | 0.297175 | nofuse | nofuse | disc_price, is_promo |
| 6 | Project | 749223 | 2 |  |  | 0.0541745 | 0.0541745 | nofuse | nofuse | promo_volume, volume |
| 7 | Reorder | 749223 | 2 |  |  | 0.00199855 | 0.00199855 |  |  |  |
| 8 | ScalarAgg | 1 | 2 |  |  | 0.113232 | 0.113232 |  |  | sum(promo_volume), sum(volume) |
| 9 | Project | 1 | 1 |  |  | 0.0229658 | 0.0229658 | nofuse | nofuse | promo_revenue |
|  | Total |  |  |  |  | 22.8519 | 18.5034 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>lineitem<br/>l_partkey, l_extendedprice, l_discount, l_shipdate<br/>59,986,052 × 4"]
    step_1["1 · Filter · 1.25%<br/>749,223 × 3"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>part<br/>p_partkey, p_type<br/>2,000,000 × 2"]
    step_3["3 · EqJoin · 749.2K⋈2M<br/>partkey<br/>749,223 × 4"]
    step_1 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>749,223 × 5"]
    step_3 --> step_4
    step_5["5 · Project<br/>749,223 × 2"]
    step_4 --> step_5
    step_6["6 · Project<br/>749,223 × 2"]
    step_5 --> step_6
    step_7["7 · Reorder<br/>749,223 × 2"]
    step_6 --> step_7
    step_8["8 · ScalarAgg<br/>sum(promo_volume), sum(volume)<br/>1 × 2"]
    step_7 --> step_8
    step_9["9 · Project<br/>1 × 1"]
    step_8 --> step_9
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2 source
    class step_1 filter
    class step_3 join
    class step_8 aggregate
    class step_4,step_5,step_6,step_7,step_9 transform
```


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

```sql
Sort[s_suppkey ASC]
  Project(s_suppkey, s_name, s_address, s_phone, total_revenue)
    InnerJoin(on=(s_suppkey == l_suppkey))
      Scan(supplier [s_suppkey, s_name, s_address, s_phone])
      Filter((total_revenue == max_revenue))
        CrossJoin
          Aggregate(l_suppkey; sum(rev))
            Project(supplier_no = l_suppkey, rev = (l_extendedprice * (1 - l_discount)))
              Filter(((l_shipdate >= 19960101) && (l_shipdate < 19960401)))
                Scan(lineitem [l_suppkey, l_extendedprice, l_discount, l_shipdate])
          Aggregate(max(total_revenue))
            Aggregate(l_suppkey; sum(rev))
              Project(supplier_no = l_suppkey, rev = (l_extendedprice * (1 - l_discount)))
                Filter(((l_shipdate >= 19960101) && (l_shipdate < 19960401)))
                  Scan(lineitem [l_suppkey, l_extendedprice, l_discount, l_shipdate])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>s_suppkey ASC"]
    ir_1["Project<br/>s_suppkey, s_name, s_address, s_phone, total_revenue"]
    ir_0 --> ir_1
    ir_2["InnerJoin<br/>on=(s_suppkey == l_suppkey)"]
    ir_1 --> ir_2
    ir_3["Scan<br/>supplier · s_suppkey, s_name, s_address, s_phone"]
    ir_2 --> ir_3
    ir_4["Filter<br/>(total_revenue == max_revenue)"]
    ir_2 --> ir_4
    ir_5["CrossJoin"]
    ir_4 --> ir_5
    ir_6["Aggregate<br/>l_suppkey; sum(rev)"]
    ir_5 --> ir_6
    ir_7["Project<br/>supplier_no = l_suppkey, rev = (l_extendedprice * (1 - l_discount))"]
    ir_6 --> ir_7
    ir_8["Filter<br/>((l_shipdate &gt;= 19960101) &amp;&amp; (l_shipdate &lt; 19960401))"]
    ir_7 --> ir_8
    ir_9["Scan<br/>lineitem · l_suppkey, l_extendedprice, l_discount, l_shipdate"]
    ir_8 --> ir_9
    ir_10["Aggregate<br/>max(total_revenue)"]
    ir_5 --> ir_10
    ir_11["Aggregate<br/>l_suppkey; sum(rev)"]
    ir_10 --> ir_11
    ir_12["Project<br/>supplier_no = l_suppkey, rev = (l_extendedprice * (1 - l_discount))"]
    ir_11 --> ir_12
    ir_13["Filter<br/>((l_shipdate &gt;= 19960101) &amp;&amp; (l_shipdate &lt; 19960401))"]
    ir_12 --> ir_13
    ir_14["Scan<br/>lineitem · l_suppkey, l_extendedprice, l_discount, l_shipdate"]
    ir_13 --> ir_14
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_3,ir_9,ir_14 source
    class ir_4,ir_8,ir_13 filter
    class ir_2,ir_5 join
    class ir_6,ir_10,ir_11 aggregate
    class ir_1,ir_7,ir_12 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 100000 | 4 | supplier |  |  |  |  |  | s_suppkey, s_name, s_address, s_phone |
| 1 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_suppkey, l_extendedprice, l_discount, l_shipdate |
| 2 | Filter | 2265714 | 3 | < | 3.78% | 14.7811 | 10.4679 | fuse | nofuse |  |
| 3 | Project | 2265714 | 2 |  |  | 0.501536 | 0.501536 | nofuse | nofuse | supplier_no, rev |
| 4 | Reorder | 2265714 | 2 |  |  | 0.00173538 | 0.00173538 |  |  |  |
| 5 | GroupBy | 100000 | 2 | < | 4.41% | 3.12183 | 3.12183 | hash | hash | supplier_no; sum(rev) |
| 6 | Reorder | 100000 | 1 |  |  | 0.00999262 | 0.00999262 |  |  |  |
| 7 | ScalarAgg | 1 | 1 |  |  | 0.0358203 | 0.0358203 |  |  | max(sum(rev)) |
| 8 | CrossJoin | 100000 | 3 | lineitem⋈lineitem | 100K⋈1 | 0.0667274 | 0.0667274 |  |  |  |
| 9 | Filter | 1 | 2 | < | 0.001% | 0.0991889 | 0.0882391 | fuse | nofuse |  |
| 10 | EqJoin | 1 | 5 | supplier⋈(lineitem⋈lineitem) | 100K⋈1 | 0.28845 | 0.28845 | hash_gfur | hash_gfur | s_suppkey; supplier_no |
| 11 | Reorder | 1 | 6 |  |  | 0.0118252 | 0.0118252 |  |  |  |
| 12 | Project | 1 | 5 |  |  | 0.18074 | 0.18074 | nofuse | nofuse | s_suppkey, s_name, s_address, s_phone, total_revenue |
| 13 | Sort | 1 | 5 |  |  | 0.239569 | 0.239569 | no_skf | no_skf | s_suppkey ASC |
|  | Total |  |  |  |  | 19.3385 | 15.0144 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>supplier<br/>s_suppkey, s_name, s_address, s_phone<br/>100,000 × 4"]
    step_1["1 · SourceTable<br/>lineitem<br/>l_suppkey, l_extendedprice, l_discount, l_shipdate<br/>59,986,052 × 4"]
    step_2["2 · Filter · 3.78%<br/>2,265,714 × 3"]
    step_1 --> step_2
    step_3["3 · Project<br/>2,265,714 × 2"]
    step_2 --> step_3
    step_4["4 · Reorder<br/>2,265,714 × 2"]
    step_3 --> step_4
    step_5["5 · GroupBy · 4.41%<br/>supplier_no; sum(rev)<br/>100,000 × 2"]
    step_4 --> step_5
    step_6["6 · Reorder<br/>100,000 × 1"]
    step_5 --> step_6
    step_7["7 · ScalarAgg<br/>max(sum(rev))<br/>1 × 1"]
    step_6 --> step_7
    step_8["8 · CrossJoin · 100K⋈1<br/>100,000 × 3"]
    step_5 --> step_8
    step_7 --> step_8
    step_9["9 · Filter · 0.001%<br/>1 × 2"]
    step_8 --> step_9
    step_10["10 · EqJoin · 100K⋈1<br/>s_suppkey; supplier_no<br/>1 × 5"]
    step_0 --> step_10
    step_9 --> step_10
    step_11["11 · Reorder<br/>1 × 6"]
    step_10 --> step_11
    step_12["12 · Project<br/>1 × 5"]
    step_11 --> step_12
    step_13["13 · Sort<br/>s_suppkey ASC<br/>1 × 5"]
    step_12 --> step_13
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1 source
    class step_2,step_9 filter
    class step_8,step_10 join
    class step_5,step_7 aggregate
    class step_3,step_4,step_6,step_11,step_12 transform
    class step_13 ordering
```


## Notes

- Duplicate Aggregation

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

```sql
Sort[supplier_cnt DESC, p_brand ASC, p_type ASC, p_size ASC]
  Aggregate(p_brand, p_type, p_size; count_all(*))
    Distinct(keys=[p_brand, p_type, p_size, ps_suppkey])
      InnerJoin(on=(p_partkey == ps_partkey))
        Filter(((!str_eq(p_brand, "Brand#45") && !startswith(p_type, "MEDIUM POLISHED")) && ((((((((p_size == 49) || (p_size == 14)) || (p_size == 23)) || (p_size == 45)) || (p_size == 19)) || (p_size == 3)) || (p_size == 36)) || (p_size == 9))))
          Scan(part [p_partkey, p_brand, p_type, p_size])
        LeftAntiJoin(on=(ps_suppkey == s_suppkey))
          Scan(partsupp [ps_partkey, ps_suppkey])
          Filter(contains_multiple(s_comment, ["Customer", "Complaints"]))
            Scan(supplier [s_suppkey, s_comment])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>supplier_cnt DESC, p_brand ASC, p_type ASC, p_size ASC"]
    ir_1["Aggregate<br/>p_brand, p_type, p_size; count_all(*)"]
    ir_0 --> ir_1
    ir_2["Distinct<br/>keys=[p_brand, p_type, p_size, ps_suppkey]"]
    ir_1 --> ir_2
    ir_3["InnerJoin<br/>on=(p_partkey == ps_partkey)"]
    ir_2 --> ir_3
    ir_4["Filter<br/>((!str_eq(p_brand, #quot;Brand#45#quot;) &amp;&amp; !startswith(p_type, #quot;MEDIUM POLISHED#quot;)) &amp;&amp; ((((((((p_size == 49) || (p_si..."]
    ir_3 --> ir_4
    ir_5["Scan<br/>part · p_partkey, p_brand, p_type, p_size"]
    ir_4 --> ir_5
    ir_6["LeftAntiJoin<br/>on=(ps_suppkey == s_suppkey)"]
    ir_3 --> ir_6
    ir_7["Scan<br/>partsupp · ps_partkey, ps_suppkey"]
    ir_6 --> ir_7
    ir_8["Filter<br/>contains_multiple(s_comment, [#quot;Customer#quot;, #quot;Complaints#quot;])"]
    ir_6 --> ir_8
    ir_9["Scan<br/>supplier · s_suppkey, s_comment"]
    ir_8 --> ir_9
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_5,ir_7,ir_9 source
    class ir_4,ir_8 filter
    class ir_3,ir_6 join
    class ir_1,ir_2 aggregate
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 2000000 | 4 | part |  |  |  |  |  | p_partkey, p_brand, p_type, p_size |
| 1 | Filter | 296824 | 4 | < | 14.8% | 2.71757 | 2.3772 | fuse | nofuse |  |
| 2 | SourceTable | 8000000 | 2 | partsupp |  |  |  |  |  | ps_partkey, ps_suppkey |
| 3 | SourceTable | 100000 | 2 | supplier |  |  |  |  |  | s_suppkey, s_comment |
| 4 | Filter | 56 | 1 | < | 0.056% | 0.180559 | 0.180559 | fuse | fuse |  |
| 5 | AntiJoin | 7995520 | 2 | partsupp⋈supplier | 8M⋈56 | 2.78452 | 2.78452 |  |  | ps_suppkey; s_suppkey |
| 6 | Reorder | 7995520 | 2 |  |  | 0.00182982 | 0.00182982 |  |  |  |
| 7 | EqJoin | 1186602 | 5 | part⋈(partsupp⋈supplier) | 296.8K⋈8M | 7.72549 | 7.72549 | hash_gfur | hash_gfur | p_partkey; ps_suppkey |
| 8 | Reorder | 1186602 | 6 |  |  | 0.00876218 | 0.00876218 |  |  |  |
| 9 | Distinct | 1186339 | 4 |  |  | 4.38748 | 4.38748 | hash | hash | 1, 2, 3, 5 |
| 10 | Reorder | 1186339 | 3 |  |  | 0.00780509 | 0.00780509 |  |  |  |
| 11 | GroupBy | 27840 | 4 | < | 2.35% | 2.17306 | 2.17306 | hash | hash | output column 0, output column 1, output column 2; count_all(*) |
| 12 | Sort | 27840 | 4 |  |  | 2.96505 | 2.96505 | no_skf | no_skf | count_all(*) DESC, output column 0 ASC, output column 1 ASC, output column 2 ASC |
|  | Total |  |  |  |  | 22.9521 | 22.6118 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>part<br/>p_partkey, p_brand, p_type, p_size<br/>2,000,000 × 4"]
    step_1["1 · Filter · 14.8%<br/>296,824 × 4"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>partsupp<br/>ps_partkey, ps_suppkey<br/>8,000,000 × 2"]
    step_3["3 · SourceTable<br/>supplier<br/>s_suppkey, s_comment<br/>100,000 × 2"]
    step_4["4 · Filter · 0.056%<br/>56 × 1"]
    step_3 --> step_4
    step_5["5 · AntiJoin · 8M⋈56<br/>ps_suppkey; s_suppkey<br/>7,995,520 × 2"]
    step_2 --> step_5
    step_4 --> step_5
    step_6["6 · Reorder<br/>7,995,520 × 2"]
    step_5 --> step_6
    step_7["7 · EqJoin · 296.8K⋈8M<br/>p_partkey; ps_suppkey<br/>1,186,602 × 5"]
    step_1 --> step_7
    step_6 --> step_7
    step_8["8 · Reorder<br/>1,186,602 × 6"]
    step_7 --> step_8
    step_9["9 · Distinct<br/>1, 2, 3, 5<br/>1,186,339 × 4"]
    step_8 --> step_9
    step_10["10 · Reorder<br/>1,186,339 × 3"]
    step_9 --> step_10
    step_11["11 · GroupBy · 2.35%<br/>output column 0, output column 1, output column 2; count_all(*)<br/>27,840 × 4"]
    step_10 --> step_11
    step_12["12 · Sort<br/>count_all(*) DESC, output column 0 ASC, output column 1 ASC, output column 2 ASC<br/>27,840 × 4"]
    step_11 --> step_12
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2,step_3 source
    class step_1,step_4 filter
    class step_5,step_7 join
    class step_11 aggregate
    class step_6,step_8,step_9,step_10 transform
    class step_12 ordering
```


## Notes

- Anti-join with very low selectivity

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

```sql
Project(avg_yearly = (sum_price / 7))
  Aggregate(sum(l_extendedprice))
    Filter((l_quantity < thr))
      InnerJoin(on=(l_partkey == l_partkey))
        Project(l_partkey, thr = (0.2 * avg_qty))
          Aggregate(l_partkey; avg(l_quantity))
            InnerJoin(on=(p_partkey == l_partkey))
              Filter((str_eq(p_brand, "Brand#23") && str_eq(p_container, "MED BOX")))
                Scan(part [p_partkey, p_brand, p_container])
              Scan(lineitem [l_partkey, l_quantity, l_extendedprice])
        InnerJoin(on=(p_partkey == l_partkey))
          Filter((str_eq(p_brand, "Brand#23") && str_eq(p_container, "MED BOX")))
            Scan(part [p_partkey, p_brand, p_container])
          Scan(lineitem [l_partkey, l_quantity, l_extendedprice])
```

```mermaid
flowchart TD
    ir_0["Project<br/>avg_yearly = (sum_price / 7)"]
    ir_1["Aggregate<br/>sum(l_extendedprice)"]
    ir_0 --> ir_1
    ir_2["Filter<br/>(l_quantity &lt; thr)"]
    ir_1 --> ir_2
    ir_3["InnerJoin<br/>on=(l_partkey == l_partkey)"]
    ir_2 --> ir_3
    ir_4["Project<br/>l_partkey, thr = (0.2 * avg_qty)"]
    ir_3 --> ir_4
    ir_5["Aggregate<br/>l_partkey; avg(l_quantity)"]
    ir_4 --> ir_5
    ir_6["InnerJoin<br/>on=(p_partkey == l_partkey)"]
    ir_5 --> ir_6
    ir_7["Filter<br/>(str_eq(p_brand, #quot;Brand#23#quot;) &amp;&amp; str_eq(p_container, #quot;MED BOX#quot;))"]
    ir_6 --> ir_7
    ir_8["Scan<br/>part · p_partkey, p_brand, p_container"]
    ir_7 --> ir_8
    ir_9["Scan<br/>lineitem · l_partkey, l_quantity, l_extendedprice"]
    ir_6 --> ir_9
    ir_10["InnerJoin<br/>on=(p_partkey == l_partkey)"]
    ir_3 --> ir_10
    ir_11["Filter<br/>(str_eq(p_brand, #quot;Brand#23#quot;) &amp;&amp; str_eq(p_container, #quot;MED BOX#quot;))"]
    ir_10 --> ir_11
    ir_12["Scan<br/>part · p_partkey, p_brand, p_container"]
    ir_11 --> ir_12
    ir_13["Scan<br/>lineitem · l_partkey, l_quantity, l_extendedprice"]
    ir_10 --> ir_13
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_8,ir_9,ir_12,ir_13 source
    class ir_2,ir_7,ir_11 filter
    class ir_3,ir_6,ir_10 join
    class ir_1,ir_5 aggregate
    class ir_0,ir_4 transform
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Baseline implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 2000000 | 3 | part |  |  |  | p_partkey, p_brand, p_container |
| 1 | Filter | 2044 | 1 | < | 0.102% | 0.544299 | nofuse |  |
| 2 | SourceTable | 59986052 | 3 | lineitem |  |  |  | l_partkey, l_quantity, l_extendedprice |
| 3 | EqJoin | 61385 | 3 | part⋈lineitem | 2K⋈60M | 41.2013 | hash_gfur | partkey |
| 4 | Reorder | 61385 | 4 |  |  | 0.00205867 |  |  |
| 5 | Reorder | 61385 | 2 |  |  | 0.0178933 |  |  |
| 6 | GroupBy | 2044 | 2 | < | 3.33% | 0.210541 | hash | p_partkey; avg(l_quantity) |
| 7 | Project | 2044 | 2 |  |  | 0.017096 | nofuse | l_partkey, thr |
| 8 | EqJoin | 61385 | 5 | (part⋈lineitem)⋈(part⋈lineitem) | 2K⋈61.4K | 0.181176 | hash_gfur | partkey |
| 9 | Reorder | 61385 | 6 |  |  | 0.002168 |  |  |
| 10 | Filter | 5526 | 1 | < | 9% | 0.0549627 | nofuse |  |
| 11 | Reorder | 5526 | 1 |  |  | 0.00176267 |  |  |
| 12 | ScalarAgg | 1 | 1 |  |  | 0.032704 |  | sum(l_extendedprice) |
| 13 | Project | 1 | 1 |  |  | 0.015232 | nofuse | avg_yearly |
|  | Total |  |  |  |  | 42.2812 |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>part<br/>p_partkey, p_brand, p_container<br/>2,000,000 × 3"]
    step_1["1 · Filter · 0.102%<br/>2,044 × 1"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>lineitem<br/>l_partkey, l_quantity, l_extendedprice<br/>59,986,052 × 3"]
    step_3["3 · EqJoin · 2K⋈60M<br/>partkey<br/>61,385 × 3"]
    step_1 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>61,385 × 4"]
    step_3 --> step_4
    step_5["5 · Reorder<br/>61,385 × 2"]
    step_4 --> step_5
    step_6["6 · GroupBy · 3.33%<br/>p_partkey; avg(l_quantity)<br/>2,044 × 2"]
    step_5 --> step_6
    step_7["7 · Project<br/>2,044 × 2"]
    step_6 --> step_7
    step_8["8 · EqJoin · 2K⋈61.4K<br/>partkey<br/>61,385 × 5"]
    step_7 --> step_8
    step_4 --> step_8
    step_9["9 · Reorder<br/>61,385 × 6"]
    step_8 --> step_9
    step_10["10 · Filter · 9%<br/>5,526 × 1"]
    step_9 --> step_10
    step_11["11 · Reorder<br/>5,526 × 1"]
    step_10 --> step_11
    step_12["12 · ScalarAgg<br/>sum(l_extendedprice)<br/>1 × 1"]
    step_11 --> step_12
    step_13["13 · Project<br/>1 × 1"]
    step_12 --> step_13
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2 source
    class step_1,step_10 filter
    class step_3,step_8 join
    class step_6,step_12 aggregate
    class step_4,step_5,step_7,step_9,step_11,step_13 transform
```


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

```sql
Limit(n=100)
  Sort[o_totalprice DESC, o_orderdate ASC]
    Project(c_name, c_custkey, o_orderkey, o_orderdate, o_totalprice, sum_quantity = sum_qty)
      InnerJoin(on=(o_custkey == c_custkey))
        InnerJoin(on=(o_orderkey == l_orderkey))
          Scan(orders [o_orderkey, o_custkey, o_orderdate, o_totalprice])
          Filter((sum_qty > 300))
            Aggregate(l_orderkey; sum(l_quantity))
              Scan(lineitem [l_orderkey, l_quantity])
        Scan(customer [c_custkey, c_name])
```

```mermaid
flowchart TD
    ir_0["Limit<br/>n=100"]
    ir_1["Sort<br/>o_totalprice DESC, o_orderdate ASC"]
    ir_0 --> ir_1
    ir_2["Project<br/>c_name, c_custkey, o_orderkey, o_orderdate, o_totalprice, sum_quantity = sum_qty"]
    ir_1 --> ir_2
    ir_3["InnerJoin<br/>on=(o_custkey == c_custkey)"]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(o_orderkey == l_orderkey)"]
    ir_3 --> ir_4
    ir_5["Scan<br/>orders · o_orderkey, o_custkey, o_orderdate, o_totalprice"]
    ir_4 --> ir_5
    ir_6["Filter<br/>(sum_qty &gt; 300)"]
    ir_4 --> ir_6
    ir_7["Aggregate<br/>l_orderkey; sum(l_quantity)"]
    ir_6 --> ir_7
    ir_8["Scan<br/>lineitem · l_orderkey, l_quantity"]
    ir_7 --> ir_8
    ir_9["Scan<br/>customer · c_custkey, c_name"]
    ir_3 --> ir_9
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_5,ir_8,ir_9 source
    class ir_6 filter
    class ir_3,ir_4 join
    class ir_7 aggregate
    class ir_2 transform
    class ir_0,ir_1 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 15000000 | 4 | orders |  |  |  |  |  | o_orderkey, o_custkey, o_orderdate, o_totalprice |
| 1 | SourceTable | 59986052 | 2 | lineitem |  |  |  |  |  | l_orderkey, l_quantity |
| 2 | Reorder | 59986052 | 2 |  |  | 0.00211657 | 0.00211657 |  |  |  |
| 3 | GroupBy | 15000000 | 2 | < | 25% | 53.2047 | 53.2047 | hash | hash | l_orderkey; sum(l_quantity) |
| 4 | Filter | 624 | 2 | < | 0.00416% | 1.74166 | 1.6023 | fuse | nofuse |  |
| 5 | EqJoin | 624 | 5 | orders⋈lineitem | 15M⋈624 | 24.6104 | 24.6104 | hash_gfur | hash_gfur | orderkey |
| 6 | Reorder | 624 | 6 |  |  | 0.00191086 | 0.00191086 |  |  |  |
| 7 | SourceTable | 1500000 | 2 | customer |  |  |  |  |  | c_custkey, c_name |
| 8 | EqJoin | 624 | 7 | (orders⋈lineitem)⋈customer | 624⋈1.5M | 0.969454 | 0.969454 | hash_gfur | hash_gfur | custkey |
| 9 | Reorder | 624 | 8 |  |  | 0.00869486 | 0.00869486 |  |  |  |
| 10 | Project | 624 | 6 |  |  | 0.092128 | 0.092128 | nofuse | nofuse | c_name, c_custkey, o_orderkey, o_orderdate, o_totalprice, sum_quantity |
| 11 | TopK | 100 | 6 | < | 16% | 0.639758 | 0.639758 |  |  |  |
|  | Total |  |  |  |  | 81.2708 | 81.1315 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>orders<br/>o_orderkey, o_custkey, o_orderdate, o_totalprice<br/>15,000,000 × 4"]
    step_1["1 · SourceTable<br/>lineitem<br/>l_orderkey, l_quantity<br/>59,986,052 × 2"]
    step_2["2 · Reorder<br/>59,986,052 × 2"]
    step_1 --> step_2
    step_3["3 · GroupBy · 25%<br/>l_orderkey; sum(l_quantity)<br/>15,000,000 × 2"]
    step_2 --> step_3
    step_4["4 · Filter · 0.00416%<br/>624 × 2"]
    step_3 --> step_4
    step_5["5 · EqJoin · 15M⋈624<br/>orderkey<br/>624 × 5"]
    step_0 --> step_5
    step_4 --> step_5
    step_6["6 · Reorder<br/>624 × 6"]
    step_5 --> step_6
    step_7["7 · SourceTable<br/>customer<br/>c_custkey, c_name<br/>1,500,000 × 2"]
    step_8["8 · EqJoin · 624⋈1.5M<br/>custkey<br/>624 × 7"]
    step_6 --> step_8
    step_7 --> step_8
    step_9["9 · Reorder<br/>624 × 8"]
    step_8 --> step_9
    step_10["10 · Project<br/>624 × 6"]
    step_9 --> step_10
    step_11["11 · TopK · 16%<br/>100 × 6"]
    step_10 --> step_11
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_1,step_7 source
    class step_4 filter
    class step_5,step_8 join
    class step_3 aggregate
    class step_2,step_6,step_9,step_10 transform
    class step_11 ordering
```


## Notes

- Aggregating the entire LINEITEM table

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

```sql
Aggregate(sum(disc_price))
  Project(disc_price = (l_extendedprice * (1 - l_discount)))
    Filter((((((((str_eq(p_brand, "Brand#12") && str_in(p_container, ["SM CASE", "SM BOX", "SM PACK", "SM PKG"])) && (l_quantity >= 1)) && (l_quantity <= 11)) && (p_size >= 1)) && (p_size <= 5)) || (((((str_eq(p_brand, "Brand#23") && str_in(p_container, ["MED BAG", "MED BOX", "MED PKG", "MED PACK"])) && (l_quantity >= 10)) && (l_quantity <= 20)) && (p_size >= 1)) && (p_size <= 10))) || (((((str_eq(p_brand, "Brand#34") && str_in(p_container, ["LG CASE", "LG BOX", "LG PACK", "LG PKG"])) && (l_quantity >= 20)) && (l_quantity <= 30)) && (p_size >= 1)) && (p_size <= 15))))
      InnerJoin(on=(l_partkey == p_partkey))
        Project(l_partkey, l_quantity, l_extendedprice, l_discount)
          Filter((str_in(l_shipmode, ["AIR", "AIR REG"]) && str_eq(l_shipinstruct, "DELIVER IN PERSON")))
            Scan(lineitem [l_partkey, l_quantity, l_extendedprice, l_discount, l_shipmode, l_shipinstruct])
        Scan(part [p_partkey, p_brand, p_container, p_size])
```

```mermaid
flowchart TD
    ir_0["Aggregate<br/>sum(disc_price)"]
    ir_1["Project<br/>disc_price = (l_extendedprice * (1 - l_discount))"]
    ir_0 --> ir_1
    ir_2["Filter<br/>(((((((str_eq(p_brand, #quot;Brand#12#quot;) &amp;&amp; str_in(p_container, [#quot;SM CASE#quot;, #quot;SM BOX#quot;, #quot;SM PACK#quot;, #quot;SM PKG#quot;])) &amp;&amp; (..."]
    ir_1 --> ir_2
    ir_3["InnerJoin<br/>on=(l_partkey == p_partkey)"]
    ir_2 --> ir_3
    ir_4["Project<br/>l_partkey, l_quantity, l_extendedprice, l_discount"]
    ir_3 --> ir_4
    ir_5["Filter<br/>(str_in(l_shipmode, [#quot;AIR#quot;, #quot;AIR REG#quot;]) &amp;&amp; str_eq(l_shipinstruct, #quot;DELIVER IN PERSON#quot;))"]
    ir_4 --> ir_5
    ir_6["Scan<br/>lineitem · l_partkey, l_quantity, l_extendedprice, l_discount, l_shipmode, l_shipinstruct"]
    ir_5 --> ir_6
    ir_7["Scan<br/>part · p_partkey, p_brand, p_container, p_size"]
    ir_3 --> ir_7
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_6,ir_7 source
    class ir_2,ir_5 filter
    class ir_3 join
    class ir_0 aggregate
    class ir_1,ir_4 transform
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 59986052 | 6 | lineitem |  |  |  |  |  | l_partkey, l_quantity, l_extendedprice, l_discount, l_shipmode, l_shipinstruct |
| 1 | Filter | 2141904 | 4 | < | 3.57% | 23.0009 | 23.0009 | fuse | fuse |  |
| 2 | Project | 2141904 | 4 |  |  | 0.001784 | 0.001784 | nofuse | nofuse | l_partkey, l_quantity, l_extendedprice, l_discount |
| 3 | SourceTable | 2000000 | 4 | part |  |  |  |  |  | p_partkey, p_brand, p_container, p_size |
| 4 | EqJoin | 2141904 | 7 | lineitem⋈part | 2.1M⋈2M | 17.4938 | 17.4938 | hash_gfur | hash_gfur | partkey |
| 5 | Reorder | 2141904 | 8 |  |  | 0.012192 | 0.012192 |  |  |  |
| 6 | Filter | 1134 | 2 | < | 0.0529% | 3.85935 | 3.18491 | fuse | nofuse |  |
| 7 | Project | 1134 | 1 |  |  | 0.0213067 | 0.0213067 | nofuse | nofuse | disc_price |
| 8 | Reorder | 1134 | 1 |  |  | 0.00196533 | 0.00196533 |  |  |  |
| 9 | ScalarAgg | 1 | 1 |  |  | 0.031792 | 0.031792 |  |  | sum(disc_price) |
|  | Total |  |  |  |  | 44.4231 | 43.7487 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>lineitem<br/>l_partkey, l_quantity, l_extendedprice, l_discount, l_shipmode, l_shipinstruct<br/>59,986,052 × 6"]
    step_1["1 · Filter · 3.57%<br/>2,141,904 × 4"]
    step_0 --> step_1
    step_2["2 · Project<br/>2,141,904 × 4"]
    step_1 --> step_2
    step_3["3 · SourceTable<br/>part<br/>p_partkey, p_brand, p_container, p_size<br/>2,000,000 × 4"]
    step_4["4 · EqJoin · 2.1M⋈2M<br/>partkey<br/>2,141,904 × 7"]
    step_2 --> step_4
    step_3 --> step_4
    step_5["5 · Reorder<br/>2,141,904 × 8"]
    step_4 --> step_5
    step_6["6 · Filter · 0.0529%<br/>1,134 × 2"]
    step_5 --> step_6
    step_7["7 · Project<br/>1,134 × 1"]
    step_6 --> step_7
    step_8["8 · Reorder<br/>1,134 × 1"]
    step_7 --> step_8
    step_9["9 · ScalarAgg<br/>sum(disc_price)<br/>1 × 1"]
    step_8 --> step_9
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_3 source
    class step_1,step_6 filter
    class step_4 join
    class step_9 aggregate
    class step_2,step_5,step_7,step_8 transform
```


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

```sql
Sort[s_name ASC]
  Project(s_name, s_address)
    LeftSemiJoin(on=(s_suppkey == ps_suppkey))
      Project(s_suppkey, s_name, s_address)
        InnerJoin(on=(s_nationkey == n_nationkey))
          Filter(str_eq(n_name, "CANADA"))
            Scan(nation [n_nationkey, n_name])
          Scan(supplier [s_suppkey, s_name, s_address, s_nationkey])
      Filter((ps_availqty > qty_threshold))
        Filter((ps_suppkey == l_suppkey))
          InnerJoin(on=(ps_partkey == l_partkey))
            Project(l_partkey, l_suppkey, qty_threshold = (sum_quantity * 0.5))
              Aggregate(l_partkey, l_suppkey; sum(l_quantity))
                Filter((ps_suppkey == l_suppkey))
                  InnerJoin(on=(ps_partkey == l_partkey))
                    LeftSemiJoin(on=(ps_partkey == p_partkey))
                      LeftSemiJoin(on=(ps_suppkey == s_suppkey))
                        Scan(partsupp [ps_partkey, ps_suppkey, ps_availqty])
                        Project(s_suppkey, s_name, s_address)
                          InnerJoin(on=(s_nationkey == n_nationkey))
                            Filter(str_eq(n_name, "CANADA"))
                              Scan(nation [n_nationkey, n_name])
                            Scan(supplier [s_suppkey, s_name, s_address, s_nationkey])
                      Filter(startswith(p_name, "forest"))
                        Scan(part [p_partkey, p_name])
                    Filter(((l_shipdate >= 19940101) && (l_shipdate < 19950101)))
                      Scan(lineitem [l_partkey, l_suppkey, l_quantity, l_shipdate])
            LeftSemiJoin(on=(ps_partkey == p_partkey))
              LeftSemiJoin(on=(ps_suppkey == s_suppkey))
                Scan(partsupp [ps_partkey, ps_suppkey, ps_availqty])
                Project(s_suppkey, s_name, s_address)
                  InnerJoin(on=(s_nationkey == n_nationkey))
                    Filter(str_eq(n_name, "CANADA"))
                      Scan(nation [n_nationkey, n_name])
                    Scan(supplier [s_suppkey, s_name, s_address, s_nationkey])
              Filter(startswith(p_name, "forest"))
                Scan(part [p_partkey, p_name])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>s_name ASC"]
    ir_1["Project<br/>s_name, s_address"]
    ir_0 --> ir_1
    ir_2["LeftSemiJoin<br/>on=(s_suppkey == ps_suppkey)"]
    ir_1 --> ir_2
    ir_3["Project<br/>s_suppkey, s_name, s_address"]
    ir_2 --> ir_3
    ir_4["InnerJoin<br/>on=(s_nationkey == n_nationkey)"]
    ir_3 --> ir_4
    ir_5["Filter<br/>str_eq(n_name, #quot;CANADA#quot;)"]
    ir_4 --> ir_5
    ir_6["Scan<br/>nation · n_nationkey, n_name"]
    ir_5 --> ir_6
    ir_7["Scan<br/>supplier · s_suppkey, s_name, s_address, s_nationkey"]
    ir_4 --> ir_7
    ir_8["Filter<br/>(ps_availqty &gt; qty_threshold)"]
    ir_2 --> ir_8
    ir_9["Filter<br/>(ps_suppkey == l_suppkey)"]
    ir_8 --> ir_9
    ir_10["InnerJoin<br/>on=(ps_partkey == l_partkey)"]
    ir_9 --> ir_10
    ir_11["Project<br/>l_partkey, l_suppkey, qty_threshold = (sum_quantity * 0.5)"]
    ir_10 --> ir_11
    ir_12["Aggregate<br/>l_partkey, l_suppkey; sum(l_quantity)"]
    ir_11 --> ir_12
    ir_13["Filter<br/>(ps_suppkey == l_suppkey)"]
    ir_12 --> ir_13
    ir_14["InnerJoin<br/>on=(ps_partkey == l_partkey)"]
    ir_13 --> ir_14
    ir_15["LeftSemiJoin<br/>on=(ps_partkey == p_partkey)"]
    ir_14 --> ir_15
    ir_16["LeftSemiJoin<br/>on=(ps_suppkey == s_suppkey)"]
    ir_15 --> ir_16
    ir_17["Scan<br/>partsupp · ps_partkey, ps_suppkey, ps_availqty"]
    ir_16 --> ir_17
    ir_18["Project<br/>s_suppkey, s_name, s_address"]
    ir_16 --> ir_18
    ir_19["InnerJoin<br/>on=(s_nationkey == n_nationkey)"]
    ir_18 --> ir_19
    ir_20["Filter<br/>str_eq(n_name, #quot;CANADA#quot;)"]
    ir_19 --> ir_20
    ir_21["Scan<br/>nation · n_nationkey, n_name"]
    ir_20 --> ir_21
    ir_22["Scan<br/>supplier · s_suppkey, s_name, s_address, s_nationkey"]
    ir_19 --> ir_22
    ir_23["Filter<br/>startswith(p_name, #quot;forest#quot;)"]
    ir_15 --> ir_23
    ir_24["Scan<br/>part · p_partkey, p_name"]
    ir_23 --> ir_24
    ir_25["Filter<br/>((l_shipdate &gt;= 19940101) &amp;&amp; (l_shipdate &lt; 19950101))"]
    ir_14 --> ir_25
    ir_26["Scan<br/>lineitem · l_partkey, l_suppkey, l_quantity, l_shipdate"]
    ir_25 --> ir_26
    ir_27["LeftSemiJoin<br/>on=(ps_partkey == p_partkey)"]
    ir_10 --> ir_27
    ir_28["LeftSemiJoin<br/>on=(ps_suppkey == s_suppkey)"]
    ir_27 --> ir_28
    ir_29["Scan<br/>partsupp · ps_partkey, ps_suppkey, ps_availqty"]
    ir_28 --> ir_29
    ir_30["Project<br/>s_suppkey, s_name, s_address"]
    ir_28 --> ir_30
    ir_31["InnerJoin<br/>on=(s_nationkey == n_nationkey)"]
    ir_30 --> ir_31
    ir_32["Filter<br/>str_eq(n_name, #quot;CANADA#quot;)"]
    ir_31 --> ir_32
    ir_33["Scan<br/>nation · n_nationkey, n_name"]
    ir_32 --> ir_33
    ir_34["Scan<br/>supplier · s_suppkey, s_name, s_address, s_nationkey"]
    ir_31 --> ir_34
    ir_35["Filter<br/>startswith(p_name, #quot;forest#quot;)"]
    ir_27 --> ir_35
    ir_36["Scan<br/>part · p_partkey, p_name"]
    ir_35 --> ir_36
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_6,ir_7,ir_17,ir_21,ir_22,ir_24,ir_26,ir_29,ir_33,ir_34,ir_36 source
    class ir_5,ir_8,ir_9,ir_13,ir_20,ir_23,ir_25,ir_32,ir_35 filter
    class ir_2,ir_4,ir_10,ir_14,ir_15,ir_16,ir_19,ir_27,ir_28,ir_31 join
    class ir_12 aggregate
    class ir_1,ir_3,ir_11,ir_18,ir_30 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 1 | Filter | 1 | 1 | < | 4% | 0.0508587 | 0.0508587 | fuse | fuse |  |
| 2 | SourceTable | 100000 | 4 | supplier |  |  |  |  |  | s_suppkey, s_name, s_address, s_nationkey |
| 3 | EqJoin | 4054 | 4 | nation⋈supplier | 1⋈100K | 0.279927 | 0.279927 | hash_gfur | hash_gfur | nationkey |
| 4 | Reorder | 4054 | 5 |  |  | 0.00998222 | 0.00998222 |  |  |  |
| 5 | Project | 4054 | 3 |  |  | 0.132469 | 0.132469 | nofuse | nofuse | s_suppkey, s_name, s_address |
| 6 | SourceTable | 8000000 | 3 | partsupp |  |  |  |  |  | ps_partkey, ps_suppkey, ps_availqty |
| 7 | SemiJoin | 324320 | 3 | partsupp⋈(nation⋈supplier) | 8M⋈4.1K | 2.65559 | 2.65559 |  |  | ps_suppkey; s_suppkey |
| 8 | Reorder | 324320 | 3 |  |  | 0.00180978 | 0.00180978 |  |  |  |
| 9 | SourceTable | 2000000 | 2 | part |  |  |  |  |  | p_partkey, p_name |
| 10 | Filter | 21551 | 1 | < | 1.08% | 0.469333 | 0.469333 | fuse | fuse |  |
| 11 | SemiJoin | 3517 | 3 | (partsupp⋈(nation⋈supplier))⋈part | 324.3K⋈21.6K | 0.197577 | 0.197577 |  |  | ps_suppkey; p_partkey |
| 12 | Reorder | 3517 | 3 |  |  | 0.00184 | 0.00184 |  |  |  |
| 13 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_partkey, l_suppkey, l_quantity, l_shipdate |
| 14 | Filter | 9099165 | 3 | < | 15.2% | 16.3136 | 11.858 | fuse | nofuse |  |
| 15 | EqJoin | 15984 | 5 | ((partsupp⋈(nation⋈supplier))⋈part)⋈lineitem | 3.5K⋈9.1M | 5.92658 | 5.92658 | hash_gfur | hash_gfur | ps_suppkey; l_partkey |
| 16 | Reorder | 15984 | 6 |  |  | 0.00217422 | 0.00217422 |  |  |  |
| 17 | Filter | 4015 | 3 | < | 25.1% | 0.126164 | 0.100346 | fuse | nofuse |  |
| 18 | Reorder | 4015 | 3 |  |  | 0.00162311 | 0.00162311 |  |  |  |
| 19 | GroupBy | 2384 | 3 | < | 59.4% | 0.171047 | 0.171047 | hash | hash | ps_suppkey, l_suppkey; sum(l_quantity) |
| 20 | Project | 2384 | 3 |  |  | 0.0182471 | 0.0182471 | nofuse | nofuse | l_partkey, l_suppkey, qty_threshold |
| 21 | EqJoin | 2667 | 5 | (((partsupp⋈(nation⋈supplier))⋈part)⋈lineitem) ⋈ ((partsupp⋈(nation⋈supplier))⋈part) | 2.4K⋈3.5K | 0.121593 | 0.121593 | hash_gfur | hash_gfur | l_partkey; ps_suppkey |
| 22 | Reorder | 2667 | 6 |  |  | 0.00193956 | 0.00193956 |  |  |  |
| 23 | Filter | 2384 | 3 | < | 89.4% | 0.108002 | 0.0876145 | fuse | nofuse |  |
| 24 | Filter | 2377 | 1 | < | 99.7% | 0.0561493 | 0.0374764 | fuse | nofuse |  |
| 25 | SemiJoin | 1804 | 3 | (nation⋈supplier)⋈((((partsupp⋈(nation⋈supplier)) ⋈ part)⋈lineitem)⋈((partsupp⋈(nation⋈supplier)) ⋈ part)) | 4.1K⋈2.4K | 0.206946 | 0.206946 |  |  | s_suppkey; ps_partkey |
| 26 | Reorder | 1804 | 3 |  |  | 0.00971378 | 0.00971378 |  |  |  |
| 27 | Project | 1804 | 2 |  |  | 0.128533 | 0.128533 | nofuse | nofuse | s_name, s_address |
| 28 | Sort | 1804 | 2 |  |  | 0.778987 | 0.778987 | no_skf | no_skf | s_name ASC |
|  | Total |  |  |  |  | 27.7707 | 23.2502 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_1["1 · Filter · 4%<br/>1 × 1"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>supplier<br/>s_suppkey, s_name, s_address, s_nationkey<br/>100,000 × 4"]
    step_3["3 · EqJoin · 1⋈100K<br/>nationkey<br/>4,054 × 4"]
    step_1 --> step_3
    step_2 --> step_3
    step_4["4 · Reorder<br/>4,054 × 5"]
    step_3 --> step_4
    step_5["5 · Project<br/>4,054 × 3"]
    step_4 --> step_5
    step_6["6 · SourceTable<br/>partsupp<br/>ps_partkey, ps_suppkey, ps_availqty<br/>8,000,000 × 3"]
    step_7["7 · SemiJoin · 8M⋈4.1K<br/>ps_suppkey; s_suppkey<br/>324,320 × 3"]
    step_6 --> step_7
    step_5 --> step_7
    step_8["8 · Reorder<br/>324,320 × 3"]
    step_7 --> step_8
    step_9["9 · SourceTable<br/>part<br/>p_partkey, p_name<br/>2,000,000 × 2"]
    step_10["10 · Filter · 1.08%<br/>21,551 × 1"]
    step_9 --> step_10
    step_11["11 · SemiJoin · 324.3K⋈21.6K<br/>ps_suppkey; p_partkey<br/>3,517 × 3"]
    step_8 --> step_11
    step_10 --> step_11
    step_12["12 · Reorder<br/>3,517 × 3"]
    step_11 --> step_12
    step_13["13 · SourceTable<br/>lineitem<br/>l_partkey, l_suppkey, l_quantity, l_shipdate<br/>59,986,052 × 4"]
    step_14["14 · Filter · 15.2%<br/>9,099,165 × 3"]
    step_13 --> step_14
    step_15["15 · EqJoin · 3.5K⋈9.1M<br/>ps_suppkey; l_partkey<br/>15,984 × 5"]
    step_12 --> step_15
    step_14 --> step_15
    step_16["16 · Reorder<br/>15,984 × 6"]
    step_15 --> step_16
    step_17["17 · Filter · 25.1%<br/>4,015 × 3"]
    step_16 --> step_17
    step_18["18 · Reorder<br/>4,015 × 3"]
    step_17 --> step_18
    step_19["19 · GroupBy · 59.4%<br/>ps_suppkey, l_suppkey; sum(l_quantity)<br/>2,384 × 3"]
    step_18 --> step_19
    step_20["20 · Project<br/>2,384 × 3"]
    step_19 --> step_20
    step_21["21 · EqJoin · 2.4K⋈3.5K<br/>l_partkey; ps_suppkey<br/>2,667 × 5"]
    step_20 --> step_21
    step_12 --> step_21
    step_22["22 · Reorder<br/>2,667 × 6"]
    step_21 --> step_22
    step_23["23 · Filter · 89.4%<br/>2,384 × 3"]
    step_22 --> step_23
    step_24["24 · Filter · 99.7%<br/>2,377 × 1"]
    step_23 --> step_24
    step_25["25 · SemiJoin · 4.1K⋈2.4K<br/>s_suppkey; ps_partkey<br/>1,804 × 3"]
    step_5 --> step_25
    step_24 --> step_25
    step_26["26 · Reorder<br/>1,804 × 3"]
    step_25 --> step_26
    step_27["27 · Project<br/>1,804 × 2"]
    step_26 --> step_27
    step_28["28 · Sort<br/>s_name ASC<br/>1,804 × 2"]
    step_27 --> step_28
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2,step_6,step_9,step_13 source
    class step_1,step_10,step_14,step_17,step_23,step_24 filter
    class step_3,step_7,step_11,step_15,step_21,step_25 join
    class step_19 aggregate
    class step_4,step_5,step_8,step_12,step_16,step_18,step_20,step_22,step_26,step_27 transform
    class step_28 ordering
```


## Notes

- This query joins 5 tables.

- Duplicated subplans and joins

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

```sql
Limit(n=100)
  Sort[numwait DESC, s_name ASC]
    Aggregate(s_name; count_all(*))
      InnerJoin(on=(n_nationkey == s_nationkey))
        Filter(str_eq(n_name, "SAUDI ARABIA"))
          Scan(nation [n_nationkey, n_name])
        InnerJoin(on=(l_orderkey#2 == o_orderkey))
          InnerJoin(on=(l_suppkey#3 == s_suppkey))
            LeftSemiJoin(on=(l_orderkey#2 == l_orderkey#2))
              LeftSemiJoin(on=(l_orderkey#2 == l_orderkey#0))
                Filter((l_receiptdate > l_commitdate))
                  Scan(lineitem [l_orderkey, l_suppkey, l_commitdate, l_receiptdate])
                Filter((n_supp > 1))
                  Aggregate(l_orderkey#0; count_all(*))
                    Distinct(keys=[l_orderkey#0, l_suppkey#1])
                      Scan(lineitem [l_orderkey, l_suppkey])
              Filter((n_failed_supp == 1))
                Aggregate(l_orderkey#2; count_all(*))
                  Distinct(keys=[l_orderkey#2, l_suppkey#3])
                    Filter((l_receiptdate > l_commitdate))
                      Scan(lineitem [l_orderkey, l_suppkey, l_commitdate, l_receiptdate])
            Scan(supplier [s_suppkey, s_name, s_nationkey])
          Filter(str_eq(o_orderstatus, "F"))
            Scan(orders [o_orderkey, o_orderstatus])
```

```mermaid
flowchart TD
    ir_0["Limit<br/>n=100"]
    ir_1["Sort<br/>numwait DESC, s_name ASC"]
    ir_0 --> ir_1
    ir_2["Aggregate<br/>s_name; count_all(*)"]
    ir_1 --> ir_2
    ir_3["InnerJoin<br/>on=(n_nationkey == s_nationkey)"]
    ir_2 --> ir_3
    ir_4["Filter<br/>str_eq(n_name, #quot;SAUDI ARABIA#quot;)"]
    ir_3 --> ir_4
    ir_5["Scan<br/>nation · n_nationkey, n_name"]
    ir_4 --> ir_5
    ir_6["InnerJoin<br/>on=(l_orderkey#2 == o_orderkey)"]
    ir_3 --> ir_6
    ir_7["InnerJoin<br/>on=(l_suppkey#3 == s_suppkey)"]
    ir_6 --> ir_7
    ir_8["LeftSemiJoin<br/>on=(l_orderkey#2 == l_orderkey#2)"]
    ir_7 --> ir_8
    ir_9["LeftSemiJoin<br/>on=(l_orderkey#2 == l_orderkey#0)"]
    ir_8 --> ir_9
    ir_10["Filter<br/>(l_receiptdate &gt; l_commitdate)"]
    ir_9 --> ir_10
    ir_11["Scan<br/>lineitem · l_orderkey, l_suppkey, l_commitdate, l_receiptdate"]
    ir_10 --> ir_11
    ir_12["Filter<br/>(n_supp &gt; 1)"]
    ir_9 --> ir_12
    ir_13["Aggregate<br/>l_orderkey#0; count_all(*)"]
    ir_12 --> ir_13
    ir_14["Distinct<br/>keys=[l_orderkey#0, l_suppkey#1]"]
    ir_13 --> ir_14
    ir_15["Scan<br/>lineitem · l_orderkey, l_suppkey"]
    ir_14 --> ir_15
    ir_16["Filter<br/>(n_failed_supp == 1)"]
    ir_8 --> ir_16
    ir_17["Aggregate<br/>l_orderkey#2; count_all(*)"]
    ir_16 --> ir_17
    ir_18["Distinct<br/>keys=[l_orderkey#2, l_suppkey#3]"]
    ir_17 --> ir_18
    ir_19["Filter<br/>(l_receiptdate &gt; l_commitdate)"]
    ir_18 --> ir_19
    ir_20["Scan<br/>lineitem · l_orderkey, l_suppkey, l_commitdate, l_receiptdate"]
    ir_19 --> ir_20
    ir_21["Scan<br/>supplier · s_suppkey, s_name, s_nationkey"]
    ir_7 --> ir_21
    ir_22["Filter<br/>str_eq(o_orderstatus, #quot;F#quot;)"]
    ir_6 --> ir_22
    ir_23["Scan<br/>orders · o_orderkey, o_orderstatus"]
    ir_22 --> ir_23
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_5,ir_11,ir_15,ir_20,ir_21,ir_23 source
    class ir_4,ir_10,ir_12,ir_16,ir_19,ir_22 filter
    class ir_3,ir_6,ir_7,ir_8,ir_9 join
    class ir_2,ir_13,ir_14,ir_17,ir_18 aggregate
    class ir_0,ir_1 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Best (ms) | Baseline implementation | Best implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 25 | 2 | nation |  |  |  |  |  | n_nationkey, n_name |
| 1 | Filter | 1 | 1 | < | 4% | 0.05228 | 0.05228 | fuse | fuse |  |
| 2 | SourceTable | 59986052 | 4 | lineitem |  |  |  |  |  | l_orderkey, l_suppkey, l_commitdate, l_receiptdate |
| 3 | Filter | 37929348 | 2 | < | 63.2% | 10.8185 | 9.72552 | fuse | nofuse |  |
| 4 | SourceTable | 59986052 | 2 | lineitem |  |  |  |  |  | l_orderkey, l_suppkey |
| 5 | Distinct | 59984817 | 2 |  |  | 139.122 | 125.6 | hash | sort_skf | 0, 1 |
| 6 | Reorder | 59984817 | 1 |  |  | 0.001896 | 0.001896 |  |  |  |
| 7 | GroupBy | 15000000 | 2 | < | 25% | 57.5717 | 57.5717 | hash | hash | l_orderkey; count_all(*) |
| 8 | Filter | 12856058 | 1 | < | 85.7% | 1.7535 | 1.65297 | fuse | nofuse |  |
| 9 | SemiJoin | 36573988 | 2 | lineitem⋈lineitem | 37.9M⋈12.9M | 36.141 | 36.141 |  |  | l_orderkey; l_orderkey |
| 10 | Reorder | 36573988 | 2 |  |  | 0.00188 | 0.00188 |  |  |  |
| 11 | Distinct | 37928859 | 2 |  |  | 87.8783 | 79.602 | hash | sort_skf | 0, 1 |
| 12 | Reorder | 37928859 | 1 |  |  | 0.001632 | 0.001632 |  |  |  |
| 13 | GroupBy | 13753474 | 2 | < | 36.3% | 44.9404 | 44.9404 | hash | hash | l_orderkey; count_all(*) |
| 14 | Filter | 3372250 | 1 | < | 24.5% | 1.25962 | 1.18282 | fuse | nofuse |  |
| 15 | SemiJoin | 2016924 | 2 | (lineitem⋈lineitem)⋈lineitem | 36.6M⋈3.4M | 17.3358 | 17.3358 |  |  | l_orderkey; l_orderkey |
| 16 | Reorder | 2016924 | 2 |  |  | 0.001616 | 0.001616 |  |  |  |
| 17 | SourceTable | 100000 | 3 | supplier |  |  |  |  |  | s_suppkey, s_name, s_nationkey |
| 18 | EqJoin | 2016924 | 4 | ((lineitem⋈lineitem)⋈lineitem)⋈supplier | 2M⋈100K | 9.60445 | 9.60445 | hash_gfur | hash_gfur | suppkey |
| 19 | Reorder | 2016924 | 5 |  |  | 0.009112 | 0.009112 |  |  |  |
| 20 | SourceTable | 15000000 | 2 | orders |  |  |  |  |  | o_orderkey, o_orderstatus |
| 21 | Filter | 7309184 | 1 | < | 48.7% | 1.67194 | 1.67194 | fuse | fuse |  |
| 22 | EqJoin | 990572 | 5 | (((lineitem⋈lineitem)⋈lineitem)⋈supplier)⋈orders | 2M⋈7.3M | 31.9133 | 31.9133 | hash_gfur | hash_gfur | orderkey |
| 23 | Reorder | 990572 | 6 |  |  | 0.010896 | 0.010896 |  |  |  |
| 24 | EqJoin | 39448 | 6 | nation⋈((((lineitem⋈lineitem)⋈lineitem)⋈supplier) ⋈ orders) | 1⋈990.6K | 0.832344 | 0.832344 | hash_gfur | hash_gfur | nationkey |
| 25 | Reorder | 39448 | 7 |  |  | 0.006832 | 0.006832 |  |  |  |
| 26 | Reorder | 39448 | 1 |  |  | 0.001504 | 0.001504 |  |  |  |
| 27 | GroupBy | 4009 | 2 | < | 10.2% | 0.258112 | 0.249096 | hash | partition_gftr | s_name; count_all(*) |
| 28 | TopK | 100 | 2 | < | 2.49% | 2.12464 | 2.12464 |  |  |  |
|  | Total |  |  |  |  | 443.313 | 420.236 |  |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>nation<br/>n_nationkey, n_name<br/>25 × 2"]
    step_1["1 · Filter · 4%<br/>1 × 1"]
    step_0 --> step_1
    step_2["2 · SourceTable<br/>lineitem<br/>l_orderkey, l_suppkey, l_commitdate, l_receiptdate<br/>59,986,052 × 4"]
    step_3["3 · Filter · 63.2%<br/>37,929,348 × 2"]
    step_2 --> step_3
    step_4["4 · SourceTable<br/>lineitem<br/>l_orderkey, l_suppkey<br/>59,986,052 × 2"]
    step_5["5 · Distinct<br/>0, 1<br/>59,984,817 × 2"]
    step_4 --> step_5
    step_6["6 · Reorder<br/>59,984,817 × 1"]
    step_5 --> step_6
    step_7["7 · GroupBy · 25%<br/>l_orderkey; count_all(*)<br/>15,000,000 × 2"]
    step_6 --> step_7
    step_8["8 · Filter · 85.7%<br/>12,856,058 × 1"]
    step_7 --> step_8
    step_9["9 · SemiJoin · 37.9M⋈12.9M<br/>l_orderkey; l_orderkey<br/>36,573,988 × 2"]
    step_3 --> step_9
    step_8 --> step_9
    step_10["10 · Reorder<br/>36,573,988 × 2"]
    step_9 --> step_10
    step_11["11 · Distinct<br/>0, 1<br/>37,928,859 × 2"]
    step_3 --> step_11
    step_12["12 · Reorder<br/>37,928,859 × 1"]
    step_11 --> step_12
    step_13["13 · GroupBy · 36.3%<br/>l_orderkey; count_all(*)<br/>13,753,474 × 2"]
    step_12 --> step_13
    step_14["14 · Filter · 24.5%<br/>3,372,250 × 1"]
    step_13 --> step_14
    step_15["15 · SemiJoin · 36.6M⋈3.4M<br/>l_orderkey; l_orderkey<br/>2,016,924 × 2"]
    step_10 --> step_15
    step_14 --> step_15
    step_16["16 · Reorder<br/>2,016,924 × 2"]
    step_15 --> step_16
    step_17["17 · SourceTable<br/>supplier<br/>s_suppkey, s_name, s_nationkey<br/>100,000 × 3"]
    step_18["18 · EqJoin · 2M⋈100K<br/>suppkey<br/>2,016,924 × 4"]
    step_16 --> step_18
    step_17 --> step_18
    step_19["19 · Reorder<br/>2,016,924 × 5"]
    step_18 --> step_19
    step_20["20 · SourceTable<br/>orders<br/>o_orderkey, o_orderstatus<br/>15,000,000 × 2"]
    step_21["21 · Filter · 48.7%<br/>7,309,184 × 1"]
    step_20 --> step_21
    step_22["22 · EqJoin · 2M⋈7.3M<br/>orderkey<br/>990,572 × 5"]
    step_19 --> step_22
    step_21 --> step_22
    step_23["23 · Reorder<br/>990,572 × 6"]
    step_22 --> step_23
    step_24["24 · EqJoin · 1⋈990.6K<br/>nationkey<br/>39,448 × 6"]
    step_1 --> step_24
    step_23 --> step_24
    step_25["25 · Reorder<br/>39,448 × 7"]
    step_24 --> step_25
    step_26["26 · Reorder<br/>39,448 × 1"]
    step_25 --> step_26
    step_27["27 · GroupBy · 10.2%<br/>s_name; count_all(*)<br/>4,009 × 2"]
    step_26 --> step_27
    step_28["28 · TopK · 2.49%<br/>100 × 2"]
    step_27 --> step_28
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_2,step_4,step_17,step_20 source
    class step_1,step_3,step_8,step_14,step_21 filter
    class step_9,step_15,step_18,step_22,step_24 join
    class step_7,step_13,step_27 aggregate
    class step_5,step_6,step_10,step_11,step_12,step_16,step_19,step_23,step_25,step_26 transform
    class step_28 ordering
```


## Notes

- Lineitem is read multiple times.

- Expensive aggregation
- Two DISTINCT on lineitem

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

```sql
Sort[cntrycode ASC]
  Aggregate(cntrycode; count_all(*), sum(c_acctbal))
    LeftAntiJoin(on=(c_custkey == o_custkey))
      Filter((c_acctbal > avg_acctbal))
        CrossJoin
          Filter(str_in(cntrycode, ["13", "31", "23", "29", "30", "18", "17"]))
            Project(c_custkey, c_acctbal, cntrycode = substring(c_phone, 1, 2))
              Scan(customer [c_custkey, c_phone, c_acctbal])
          Aggregate(avg(c_acctbal))
            Filter((c_acctbal > 0))
              Filter(str_in(cntrycode, ["13", "31", "23", "29", "30", "18", "17"]))
                Project(c_custkey, c_acctbal, cntrycode = substring(c_phone, 1, 2))
                  Scan(customer [c_custkey, c_phone, c_acctbal])
      Scan(orders [o_custkey])
```

```mermaid
flowchart TD
    ir_0["Sort<br/>cntrycode ASC"]
    ir_1["Aggregate<br/>cntrycode; count_all(*), sum(c_acctbal)"]
    ir_0 --> ir_1
    ir_2["LeftAntiJoin<br/>on=(c_custkey == o_custkey)"]
    ir_1 --> ir_2
    ir_3["Filter<br/>(c_acctbal &gt; avg_acctbal)"]
    ir_2 --> ir_3
    ir_4["CrossJoin"]
    ir_3 --> ir_4
    ir_5["Filter<br/>str_in(cntrycode, [#quot;13#quot;, #quot;31#quot;, #quot;23#quot;, #quot;29#quot;, #quot;30#quot;, #quot;18#quot;, #quot;17#quot;])"]
    ir_4 --> ir_5
    ir_6["Project<br/>c_custkey, c_acctbal, cntrycode = substring(c_phone, 1, 2)"]
    ir_5 --> ir_6
    ir_7["Scan<br/>customer · c_custkey, c_phone, c_acctbal"]
    ir_6 --> ir_7
    ir_8["Aggregate<br/>avg(c_acctbal)"]
    ir_4 --> ir_8
    ir_9["Filter<br/>(c_acctbal &gt; 0)"]
    ir_8 --> ir_9
    ir_10["Filter<br/>str_in(cntrycode, [#quot;13#quot;, #quot;31#quot;, #quot;23#quot;, #quot;29#quot;, #quot;30#quot;, #quot;18#quot;, #quot;17#quot;])"]
    ir_9 --> ir_10
    ir_11["Project<br/>c_custkey, c_acctbal, cntrycode = substring(c_phone, 1, 2)"]
    ir_10 --> ir_11
    ir_12["Scan<br/>customer · c_custkey, c_phone, c_acctbal"]
    ir_11 --> ir_12
    ir_13["Scan<br/>orders · o_custkey"]
    ir_2 --> ir_13
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class ir_7,ir_12,ir_13 source
    class ir_3,ir_5,ir_9,ir_10 filter
    class ir_2,ir_4 join
    class ir_1,ir_8 aggregate
    class ir_6,ir_11 transform
    class ir_0 ordering
```


| Step | Operation | Rows | Cols | Tables | Selectivity / Join inputs | Baseline (ms) | Baseline implementation | Physical plan keys / columns |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 0 | SourceTable | 1500000 | 3 | customer |  |  |  | c_custkey, c_phone, c_acctbal |
| 1 | Project | 1500000 | 3 |  |  | 0.736377 | nofuse | c_custkey, c_acctbal, cntrycode |
| 2 | Filter | 419974 | 3 | < | 28% | 0.795591 | nofuse |  |
| 3 | Filter | 381776 | 1 | < | 90.9% | 0.0802169 | nofuse |  |
| 4 | Reorder | 381776 | 1 |  |  | 0.00161422 |  |  |
| 5 | ScalarAgg | 1 | 1 |  |  | 0.0375671 |  | avg(c_acctbal) |
| 6 | CrossJoin | 419974 | 4 | customer⋈customer | 420K⋈1 | 0.336489 |  |  |
| 7 | Filter | 190691 | 3 | < | 45.4% | 0.321772 | nofuse |  |
| 8 | SourceTable | 15000000 | 1 | orders |  |  |  | o_custkey |
| 9 | AntiJoin | 63914 | 3 | (customer⋈customer)⋈orders | 190.7K⋈15M | 11.5145 |  | c_custkey; o_custkey |
| 10 | Reorder | 63914 | 3 |  |  | 0.00709689 |  |  |
| 11 | Reorder | 63914 | 2 |  |  | 0.00208356 |  |  |
| 12 | GroupBy | 7 | 3 | < | 0.011% | 0.21308 | hash | cntrycode; count_all(*), sum(c_acctbal) |
| 13 | Sort | 7 | 3 |  |  | 0.167294 | no_skf | cntrycode ASC |
|  | Total |  |  |  |  | 14.2137 |  |  |

```mermaid
flowchart TD
    step_0["0 · SourceTable<br/>customer<br/>c_custkey, c_phone, c_acctbal<br/>1,500,000 × 3"]
    step_1["1 · Project<br/>1,500,000 × 3"]
    step_0 --> step_1
    step_2["2 · Filter · 28%<br/>419,974 × 3"]
    step_1 --> step_2
    step_3["3 · Filter · 90.9%<br/>381,776 × 1"]
    step_2 --> step_3
    step_4["4 · Reorder<br/>381,776 × 1"]
    step_3 --> step_4
    step_5["5 · ScalarAgg<br/>avg(c_acctbal)<br/>1 × 1"]
    step_4 --> step_5
    step_6["6 · CrossJoin · 420K⋈1<br/>419,974 × 4"]
    step_2 --> step_6
    step_5 --> step_6
    step_7["7 · Filter · 45.4%<br/>190,691 × 3"]
    step_6 --> step_7
    step_8["8 · SourceTable<br/>orders<br/>o_custkey<br/>15,000,000 × 1"]
    step_9["9 · AntiJoin · 190.7K⋈15M<br/>c_custkey; o_custkey<br/>63,914 × 3"]
    step_7 --> step_9
    step_8 --> step_9
    step_10["10 · Reorder<br/>63,914 × 3"]
    step_9 --> step_10
    step_11["11 · Reorder<br/>63,914 × 2"]
    step_10 --> step_11
    step_12["12 · GroupBy · 0.011%<br/>cntrycode; count_all(*), sum(c_acctbal)<br/>7 × 3"]
    step_11 --> step_12
    step_13["13 · Sort<br/>cntrycode ASC<br/>7 × 3"]
    step_12 --> step_13
    classDef source fill:#dbeafe,stroke:#2563eb,color:#1e3a8a
    classDef filter fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef join fill:#ede9fe,stroke:#7c3aed,color:#4c1d95
    classDef aggregate fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef transform fill:#f3f4f6,stroke:#6b7280,color:#1f2937
    classDef ordering fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
    class step_0,step_8 source
    class step_2,step_3,step_7 filter
    class step_6,step_9 join
    class step_5,step_12 aggregate
    class step_1,step_4,step_10,step_11 transform
    class step_13 ordering
```


## Runtime breakdown comparison

| T4 SF1 | T4 SF10 | H200 SF10 | H200 SF30 | H200 SF100 | GH200 SF100 |
| --- | --- | --- | --- | --- | --- |
| <img src="assets/runtime-breakdowns/T4_SF1_Q22.jpg" alt="T4 SF1" width="200"> | <img src="assets/runtime-breakdowns/T4_SF10_Q22.jpg" alt="T4 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF10_Q22.jpg" alt="H200 SF10" width="200"> | <img src="assets/runtime-breakdowns/H200_SF30_Q22.jpg" alt="H200 SF30" width="200"> | <img src="assets/runtime-breakdowns/H200_SF100_Q22.jpg" alt="H200 SF100" width="200"> | <img src="assets/runtime-breakdowns/GH200_SF100_Q22_comparison.jpg" alt="GH200 SF100" width="200"> |

## Runtime breakdown legend

![Runtime breakdown legend|200x0](assets/runtime-breakdowns/T4_SF10_legend.jpg)
