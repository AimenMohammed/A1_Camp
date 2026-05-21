CREATE TABLE IF NOT EXISTS customer_int (
    CustomerID INT,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING,
    Start_Date STRING,
    End_Date STRING,
    Is_Current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\")
STORED AS TEXTFILE;

CREATE EXTERNAL TABLE IF NOT EXISTS customer_ext (
    CustomerID INT,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING,
    Start_Date STRING,
    End_Date STRING,
    Is_Current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\")
LOCATION '/user/itversity/customer_external_data';

LOAD DATA LOCAL INPATH '/home/itversity/customer_scd2_mixed.csv' INTO TABLE customer_int;
LOAD DATA LOCAL INPATH '/home/itversity/customer_scd2_mixed.csv' INTO TABLE customer_ext;

----------------------------------------

CREATE TABLE IF NOT EXISTS customer_dim (
    CustomerID INT,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING,
    Start_Date STRING,
    End_Date STRING,
    Is_Current STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\")
STORED AS TEXTFILE;

LOAD DATA LOCAL INPATH '/home/itversity/customer_scd2_mixed.csv' INTO TABLE customer_dim;

----------------------------------------

CREATE TABLE IF NOT EXISTS customer_stage (
    CustomerID INT,
    Name STRING,
    Email STRING,
    Phone_Number STRING,
    Address STRING,
    JOIN_Date STRING
)
ROW FORMAT SERDE 'org.apache.hadoop.hive.serde2.OpenCSVSerde'
WITH SERDEPROPERTIES ("separatorChar" = ",", "quoteChar" = "\"", "escapeChar" = "\\");

LOAD DATA LOCAL INPATH '/home/itversity/customer_updated.csv' INTO TABLE customer_stage;

----------------------------------------

INSERT OVERWRITE TABLE customer_dim

SELECT
    CustomerID, Name, Email, Phone_Number, Address, JOIN_Date, Start_Date, End_Date, Is_Current
FROM customer_dim
WHERE Is_Current = '0'

UNION ALL

SELECT
    d.CustomerID, d.Name, d.Email, d.Phone_Number, d.Address, d.JOIN_Date, 
    d.Start_Date, d.End_Date, d.Is_Current
FROM customer_dim d
LEFT JOIN customer_stage s ON d.CustomerID = s.CustomerID
WHERE d.Is_Current = '1'
  AND (s.CustomerID IS NULL 
       OR (d.Name = s.Name AND d.Email = s.Email 
           AND d.Phone_Number = s.Phone_Number AND d.Address = s.Address))

UNION ALL

SELECT
    d.CustomerID, d.Name, d.Email, d.Phone_Number, d.Address, d.JOIN_Date, 
    d.Start_Date,
    DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS End_Date,
    '0' AS Is_Current
FROM customer_dim d
JOIN customer_stage s ON d.CustomerID = s.CustomerID
WHERE d.Is_Current = '1'
  AND (d.Name != s.Name OR d.Email != s.Email 
       OR d.Phone_Number != s.Phone_Number OR d.Address != s.Address)

UNION ALL

SELECT
    s.CustomerID, s.Name, s.Email, s.Phone_Number, s.Address, s.JOIN_Date,
    DATE_FORMAT(CURRENT_DATE(), 'yyyy-MM-dd') AS Start_Date,
    NULL AS End_Date,
    '1' AS Is_Current
FROM customer_stage s
LEFT JOIN customer_dim d ON s.CustomerID = d.CustomerID AND d.Is_Current = '1'
WHERE d.CustomerID IS NULL
   OR (d.Name != s.Name OR d.Email != s.Email 
       OR d.Phone_Number != s.Phone_Number OR d.Address != s.Address);

SELECT 
    CustomerID,
    Name,
    Address,
    Start_Date,
    End_Date,
    Is_Current
FROM customer_dim
WHERE CustomerID IN (
    SELECT CustomerID
    FROM customer_dim
    GROUP BY CustomerID
    HAVING COUNT(*) > 1
)
ORDER BY CustomerID, Start_Date;

SELECT 
    COUNT(*) AS Total_Records,
    SUM(CASE WHEN Is_Current = '1' THEN 1 ELSE 0 END) AS Current_Records,
    SUM(CASE WHEN Is_Current = '0' THEN 1 ELSE 0 END) AS Historical_Records,
    COUNT(DISTINCT CustomerID) AS Unique_Customers
FROM customer_dim;

----------------------------------------

-- Show customers who have changed data (have more than one version)
SELECT 
    CustomerID,
    Name,
    Address,
    Start_Date,
    CASE 
        WHEN End_Date IS NULL THEN 'Current'
        ELSE End_Date
    END AS End_Date,
    Is_Current,
    CASE 
        WHEN Is_Current = '1' THEN 'Active'
        ELSE 'Historical'
    END AS Status
FROM customer_dim
WHERE CustomerID IN (
    SELECT CustomerID
    FROM customer_dim
    GROUP BY CustomerID
    HAVING COUNT(*) > 1
)
ORDER BY CustomerID, Start_Date;

----------------------------------------

-- Show number of versions per customer (shows changed customers)
SELECT 
    CustomerID,
    Name,
    COUNT(*) AS number_of_versions,
    MIN(Start_Date) AS first_version_date,
    MAX(CASE WHEN Is_Current = '1' THEN Start_Date END) AS current_version_date
FROM customer_dim
GROUP BY CustomerID, Name
HAVING COUNT(*) > 1
ORDER BY number_of_versions DESC
LIMIT 20;

----------------------------------------

-- Show all currently active records
SELECT 
    CustomerID,
    Name,
    Address,
    Start_Date,
    Is_Current
FROM customer_dim 
WHERE Is_Current = '1'
LIMIT 10;

----------------------------------------

-- Show historical records (that have been replaced)
SELECT 
    CustomerID,
    Name,
    Address,
    Start_Date,
    End_Date,
    Is_Current
FROM customer_dim 
WHERE Is_Current = '0'
LIMIT 10;

----------------------------------------


-- Summary statistics to prove SCD Type 2 is working
SELECT 
    COUNT(*) AS Total_Records,
    SUM(CASE WHEN Is_Current = '1' THEN 1 ELSE 0 END) AS Current_Records,
    SUM(CASE WHEN Is_Current = '0' THEN 1 ELSE 0 END) AS Historical_Records,
    COUNT(DISTINCT CustomerID) AS Unique_Customers
FROM customer_dim;