​E-Commerce Data Warehouse (Olist Dataset)
​📌 Project Overview
​This project implements a complete End-to-End Data Warehouse (DWH) solution using the Brazilian E-Commerce Public Dataset by Olist. The system extracts raw CSV data, transforms it into a structured Star Schema, and provides analytical insights through a Command Line Interface (CLI).
​🏗️ Architecture & Design
​The project follows modern data engineering principles:
​Multi-Layer Storage:
​Raw Layer: Initial ingestion of CSV files into PostgreSQL.
​Warehouse Layer: Cleaned, transformed data organized into Facts and Dimensions.
​Gold Layer (Reporting): A unified View (reporting_sales_master) for simplified querying.
​SCD Type 2: Implemented for dim_customers and dim_products to track historical changes (e.g., customer location shifts).
Numeric Surrogate Keys: Used for optimized JOIN performance across all tables.
​🛠️ Tech Stack
​Language: Python 3.x
​Database: PostgreSQL
​Libraries: Pandas, SQLAlchemy, Psycopg2
Analytical Insights Provided
​Sales Trending: Monthly revenue growth analysis.
​Customer Lifetime Value: Identification of Most Valuable Customers (MVCs).
​Logistics Performance: Average delivery delay per state (KPI).
​Category Analysis: Revenue contribution by product category.
DataWarehouse/
├── config/
│   └── db_config.py        # Database connection & SQLAlchemy engine settings
├── docs/
│   └── documentation.pdf   # Comprehensive technical report & ERD diagrams
├── scripts/
│   ├── init_raw_db.py      # Automates creation of the raw staging area
│   ├── create_schema.py    # Defines Star Schema DDL and Analytical Views
│   ├── load_dimensions.py  # Handles SCD Type 2 logic for evolving attributes
│   ├── load_facts.py       # Maps business processes into Fact tables
│   └── load_static_dims.py # Populates time dimensions and static lookups
├── utils/
│   └── helpers.py          # Core data cleaning & transformation logic
├── extract_raw.py          # High-speed data ingestion from SQLite to PostgreSQL
├── main.py                 # The central CLI interface and ETL orchestrator
└── requirements.txt        # Minimized production-ready library dependencies
        # Cleaned dependencies list
