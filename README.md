# Deadstock Redistribution Engine

A read-only decision support system that analyzes existing ERP inventory exports to identify slow-moving SKUs and recommend store-to-store redistribution opportunities across a retail network.

The system operates independently of live ERP infrastructure and requires no changes to existing retail systems.

---

## Problem Statement
Fashion retailers often face uneven inventory distribution, where some stores accumulate excess stock while others experience higher demand for the same SKUs. Manual redistribution decisions are slow, reactive, and error-prone, leading to markdown losses and missed sell-through opportunities.

---

## Solution Overview
This project ingests ERP inventory and sales exports (CSV format) and applies SKU-level sell-through analysis to:
- Identify overstocked and slow-moving SKUs at store level
- Rank stores where redistribution is most likely to improve sell-through
- Provide decision support without modifying ERP workflows

---

## Key Features
- ERP-agnostic (works on exported reports)
- Read-only architecture (no ERP write-back)
- SKU-level sell-through and deadstoc
