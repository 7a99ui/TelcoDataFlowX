-- =================================================================
-- 🚀 TRINO ANALYTICS INITIALIZATION SCRIPT
-- =================================================================
-- This file contains everything needed to set up Analytics on Trino.
-- It is divided into 3 steps. Run them in order.
-- =================================================================

-- =================================================================
-- STEP 1: INFRASTRUCTURE SETUP
-- (Create Schema & Register Tables from MinIO/S3)
-- =================================================================

-- 1. Create the Schema
CREATE SCHEMA IF NOT EXISTS delta.telco_churn
WITH (location = 's3://telco-churn/');

-- 2. Register Tables
-- Bronze: Raw Data
CALL delta.system.register_table(
    schema_name => 'telco_churn',
    table_name => 'bronze',
    table_location => 's3://telco-churn/bronze/telco_churn'
);

-- Silver: Cleaned Data (Use for BI/Analytics)
CALL delta.system.register_table(
    schema_name => 'telco_churn',
    table_name => 'silver',
    table_location => 's3://telco-churn/silver/telco_churn'
);

-- Gold: ML Training Data (Augmented/Balanced - DO NOT USE FOR BI)
CALL delta.system.register_table(
    schema_name => 'telco_churn',
    table_name => 'gold',
    table_location => 's3://telco-churn/gold/telco_churn'
);


-- =================================================================
-- STEP 2: CREATE PERSISTENT VIEWS (Best for Superset/BI)
-- (Run this to create permanent shortcuts for your dashboards)
-- =================================================================

-- 1. 🏆 MASTER DASHBOARD VIEW
-- Pre-calculates segments (Tenure Group, Spending, Age) for easy drag-and-drop.
CREATE OR REPLACE VIEW delta.telco_churn.view_master_dashboard AS
SELECT 
    *,
    -- Tenure Groups
    CASE 
        WHEN tenure <= 12 THEN '0-12 Months (New)'
        WHEN tenure <= 24 THEN '12-24 Months'
        WHEN tenure <= 48 THEN '24-48 Months'
        WHEN tenure <= 60 THEN '48-60 Months'
        ELSE '60+ Months (Loyal)'
    END as tenure_group,
    
    -- High Value Segment estimate
    CASE 
        WHEN MonthlyCharges > 100 THEN 'Very High'
        WHEN MonthlyCharges > 70 THEN 'High'
        WHEN MonthlyCharges > 30 THEN 'Medium'
        ELSE 'Low'
    END as spending_segment,

    -- Readable Labels
    CASE WHEN SeniorCitizen = 1 THEN 'Senior' ELSE 'Standard' END as age_segment,
    CASE WHEN Churn = 1 THEN 'Yes' ELSE 'No' END as is_churned

FROM delta.telco_churn.silver;


-- 2. 🚨 KPI SUMMARY VIEW
CREATE OR REPLACE VIEW delta.telco_churn.view_kpi_summary AS
SELECT 
    COUNT(*) as total_customers,
    SUM(Churn) as churned_count,
    ROUND(CAST(SUM(Churn) AS DOUBLE) / COUNT(*) * 100, 2) as churn_rate_pct,
    SUM(CASE WHEN Churn=1 THEN TotalCharges ELSE 0 END) as revenue_lost
FROM delta.telco_churn.silver;


-- 3. 📉 CONTRACT METRICS VIEW
CREATE OR REPLACE VIEW delta.telco_churn.view_contract_metrics AS
SELECT 
    Contract,
    COUNT(*) as count,
    ROUND(CAST(SUM(Churn) AS DOUBLE) / COUNT(*) * 100, 2) as churn_rate
FROM delta.telco_churn.silver
GROUP BY Contract;


-- =================================================================
-- STEP 3: AD-HOC ANALYTICAL QUERIES (Examples)
-- (Run these one-off to explore the data)
-- =================================================================

-- Example: Check Payment Method Churn
/*
SELECT 
    PaymentMethod,
    ROUND(AVG(MonthlyCharges), 2) as avg_monthly_bill,
    ROUND(CAST(SUM(CASE WHEN Churn = 1 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) * 100, 2) as churn_rate
FROM delta.telco_churn.silver
GROUP BY PaymentMethod
ORDER BY churn_rate DESC;
*/

-- Example: Check Tech Support Impact
/*
SELECT 
    TechSupport,
    COUNT(*) as customers,
    ROUND(CAST(SUM(CASE WHEN Churn = 1 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) * 100, 2) as churn_rate
FROM delta.telco_churn.silver
GROUP BY TechSupport
ORDER BY churn_rate ASC;
*/
