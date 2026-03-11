# Anomaly Detection Test Guide

## Problem Statement
When uploading datasets and running "Commence AI Scan", no anomalies are being detected because:
1. The sample data is too clean
2. Agents need historical data to establish patterns
3. Current test data doesn't contain obvious anomalies

## Solution
I've created test datasets that will trigger the anomaly detection system. These datasets contain transactions with various suspicious patterns that the agents are designed to detect.

## Test Files Created

### 1. `upload_test_dataset.csv` (RECOMMENDED FOR TESTING)
- **Purpose**: Direct upload test file
- **Content**: 20+ transactions with clear anomalies
- **Format**: Simple CSV with essential columns
- **Best for**: Quick testing of the upload and scan functionality

### 2. `comprehensive_test_dataset.csv`
- **Purpose**: Comprehensive test with historical data
- **Content**: Historical transactions + new anomalous transactions
- **Format**: Full schema with all columns
- **Best for**: Testing pattern analysis that requires historical data

### 3. `test_anomaly_detection.py`
- **Purpose**: Standalone test script
- **Content**: Python script to test agents directly
- **Best for**: Debugging agent functionality

## How to Test Anomaly Detection

### Option 1: Quick Test (Recommended)
1. **Download the test file**:
   - Use `upload_test_dataset.csv` from the backend folder
   - This file contains transactions designed to trigger anomalies

2. **Upload in the auditor interface**:
   - Go to the auditor dashboard
   - Upload `upload_test_dataset.csv`
   - Click "Commence AI Scan"

3. **Expected Results**:
   - Multiple transactions should be flagged
   - Risk scores should appear (40+ for medium risk, 70+ for high risk)
   - Evidence and investigation recommendations should be generated
   - You should see items like:
     - "Exact duplicate invoice detected" (High risk)
     - "Vendor payment spike" (Medium risk)
     - "Weekend transaction" (Low risk)
     - "Threshold avoidance" (Medium risk)

### Option 2: Comprehensive Test
1. **First, seed the database with historical data**:
   ```bash
   python scripts/seed_sample_data.py
   ```

2. **Upload comprehensive dataset**:
   - Use `comprehensive_test_dataset.csv`
   - This includes historical data to establish patterns

3. **Run AI Scan** and check results

### Option 3: Direct Agent Testing
1. **Run the test script**:
   ```bash
   python test_anomaly_detection.py
   ```

2. **This will test each agent directly** and show:
   - Which anomalies are detected
   - Risk scores calculated
   - Whether transactions should be flagged

## Types of Anomalies in Test Data

### High Risk (Score ≥ 70)
1. **Exact Duplicate Invoice** (40 points)
   - Same invoice ID and vendor
   - Example: INV-2024-DUP-001 appears twice

### Medium Risk (Score 40-69)
1. **Vendor Payment Spike** (15 points)
   - Unusually high monthly spending for a vendor
   - Example: ABC Corp spending $85k vs usual $15k

2. **Threshold Avoidance** (25 points)
   - Amount just below approval threshold ($9,999.99)
   - Suggests intentional avoidance of approval process

3. **Dormant Vendor** (15 points)
   - Vendor reactivated after long inactivity
   - Example: Old Vendor Co after 200+ days

4. **Unusual Amount** (20 points)
   - Statistical outlier for vendor's typical amounts
   - Example: XYZ Ltd $45k vs usual $5k-$15k

5. **Rapid Repeat Payments** (15 points)
   - Multiple payments to same vendor in short time
   - Example: 3 payments to Tech Solutions in 24 hours

6. **Temporal Clustering** (10 points)
   - Many transactions in short time window
   - Example: 5 transactions from Cluster Vendor in 3 days

### Low Risk (Score < 40)
1. **Round Number** (15 points)
   - Amount divisible by 1000 or common round numbers
   - Example: $100,000.00

2. **Weekend Posting** (10 points)
   - Transaction on Saturday/Sunday
   - Example: Saturday transaction

3. **Quarter-End Spike** (8 points)
   - Increased spending at quarter end
   - Example: Late March transactions

4. **Common Round Number** (15 points)
   - Exact common amounts like $1,000.00

## Troubleshooting

### If still no anomalies detected:
1. **Check database connection**:
   - Ensure database is running
   - Check `DATABASE_URL` in `.env` file

2. **Verify agent initialization**:
   - Check agent logs for errors
   - Ensure agents are properly imported

3. **Check CSV format**:
   - Ensure column names match expected schema
   - Dates should be in YYYY-MM-DD format
   - Amounts should be numeric

4. **Test with script**:
   - Run `python test_anomaly_detection.py`
   - This will show if agents are working independently

### Common Issues:
1. **No historical data**: Agents need past transactions to establish patterns
2. **Date format issues**: Use YYYY-MM-DD format
3. **Missing required columns**: Ensure invoice_id, vendor_id, amount, date, department are present
4. **Database permissions**: Check if application can write to database

## Expected Output Examples

When anomalies are detected, you should see:

```
Transaction: INV-2024-DUP-001
Risk Score: 85/100 (High Risk)
Flagged: ✓ YES
Reasons: Exact duplicate invoice detected; High risk score: 85/100
Evidence: Existing invoice found with same ID and vendor
```

```
Transaction: INV-2024-THRESH-001  
Risk Score: 65/100 (Medium Risk)
Flagged: ✓ YES
Reasons: Threshold avoidance: $9,999.99 (just below $10,000 approval limit)
Evidence: Amount is within 5% below approval threshold
```

## Next Steps

If the test works, you can:
1. **Modify the test data** to create different scenarios
2. **Add more anomaly types** to the detection system
3. **Adjust risk scoring thresholds** in `core/config.py`
4. **Test with real data** (with sensitive information removed)

If the test doesn't work, please provide:
1. Error messages from the console/logs
2. Screenshots of what you see
3. Which test method you used