# Transactions CSV Import Feature

**Date:** October 26, 2025
**Status:** Complete

## Overview

Created a comprehensive CSV import system for transactions using your custom column format: `Date, Merchant, Category, Account, Original Statement, Notes, Amount, Tags`.

---

## Features

### 1. Smart Import System
- **Auto-creates accounts** if they don't exist
- **Auto-creates institutions** using merchant names
- **Skips duplicates** based on unique external ID (date + merchant + amount)
- **Multiple date formats** supported (MM/DD/YYYY, YYYY-MM-DD, etc.)
- **Flexible amount parsing** ($100.50, -50.00, etc.)
- **Rich descriptions** combining merchant, statement, notes, and tags

### 2. Intelligent Data Handling
- **Smart category lookup** - must already exist (won't auto-create)
- **Smart account creation** - creates with merchant as institution
- **Error tracking** - detailed error messages for each row
- **Duplicate detection** - based on date + merchant + amount
- **Row-level error handling** - continues processing even if some rows fail

### 3. User-Friendly Interface
- **Drag and drop** file upload
- **Progress indicator** during processing
- **Detailed results** showing:
  - Transactions created
  - Duplicates skipped
  - Errors encountered
  - First 10 error details

---

## CSV Format

### Required Columns
```csv
Date,Merchant,Category,Account,Original Statement,Notes,Amount,Tags
```

### Example Data
```csv
Date,Merchant,Category,Account,Original Statement,Notes,Amount,Tags
01/15/2024,Walmart,Groceries,Chase Checking,WMT SUPERCENTER #1234,Weekly shopping,"-$125.50",groceries;food
01/16/2024,Acme Corp,Salary,Chase Checking,Direct Deposit - ACME,Bi-weekly paycheck,"$2500.00",income;payroll
01/17/2024,Shell Gas,Gas & Fuel,Credit Card,SHELL OIL 12345,Filled up tank,"-$45.00",transportation;gas
```

### Field Descriptions

| Column | Required | Description | Examples |
|--------|----------|-------------|----------|
| **Date** | Yes | Transaction date | 01/15/2024, 2024-01-15 |
| **Merchant** | Yes | Merchant/vendor name | Walmart, Amazon, Acme Corp |
| **Category** | Yes | Category (must exist!) | Groceries, Salary, Gas & Fuel |
| **Account** | Yes | Account name | Chase Checking, Credit Card |
| **Original Statement** | No | Original bank statement text | WMT SUPERCENTER #1234 |
| **Notes** | No | Personal notes | Weekly shopping |
| **Amount** | Yes | Transaction amount | $125.50, -$50.00, 100 |
| **Tags** | No | Tags for categorization | groceries;food |

---

## Files Created/Modified

### Backend (API)

#### `api/transaction/controllers.py`
**Completely rewrote** the `/api/transaction/csv_import` endpoint:

**Key Features:**
- Validates required headers (Date, Merchant, Category, Account, Amount)
- Supports multiple date formats
- Creates unique external_id from date + merchant + amount
- Smart category lookup (returns None if not found)
- Smart account creation with `ensure_account_exists_smart()`
- Builds rich descriptions from all optional fields
- Detailed error tracking with row numbers
- Returns comprehensive statistics

**New Method Added:**
```python
def ensure_account_exists_smart(self, account_name, merchant_name):
    """
    Find or create account with smart institution handling
    Uses merchant name as institution if institution doesn't exist
    """
```

**Updated Method:**
```python
def ensure_category_exists(self, category_name):
    """Find category by name, return ID or None if not found"""
    # Now returns None instead of creating category
```

### Frontend (Web)

#### `app/transactions/controllers.py`
**No changes needed** - `/transactions/import` route already existed

#### `app/templates/transactions/import.html`
**Completely replaced** the dropzone-based upload with custom interface:
- Clean, modern upload UI
- Drag & drop support
- Detailed instructions with examples
- Warning about categories needing to exist
- Link to categories import
- Progress bar and results display

#### `app/static/js/transactions/import.js`
**Created new file** with full upload functionality:
- Drag and drop handling
- File validation
- AJAX upload to API
- Progress tracking
- Detailed success/error messages
- Error details display (first 10)
- Links to view transactions or import more

#### `app/templates/transactions/index.html`
**Modified** the import button:
- Changed from inactive button to active link
- Links to `/transactions/import`
- Added upload icon

---

## Usage

### For Users

1. **Import Categories First** (if not done yet)
   - Go to `/categories/import`
   - Upload `data/categories_data.csv`

2. **Navigate to Transactions Import**
   - Go to `/transactions`
   - Click "Import CSV" button

3. **Upload CSV**
   - Drag and drop your transaction CSV OR
   - Click "Browse File" to select

4. **Review Results**
   - See transactions created
   - See duplicates skipped
   - See any errors with details

### For Developers

**API Endpoint:**
```bash
POST /api/transaction/csv_import
Content-Type: multipart/form-data

# Form data:
file: <CSV file>
```

**Success Response:**
```json
{
  "message": "Import completed",
  "transactions_created": 150,
  "transactions_skipped": 25,
  "errors": 3,
  "error_details": [
    "Row 15: Category 'Unknown' not found",
    "Row 23: Invalid amount '$ABC'",
    "Row 45: Unable to parse date: 2024/99/99"
  ]
}
```

---

## Technical Details

### Import Process Flow

1. **Validate** user authentication and file
2. **Parse CSV** with DictReader
3. **Validate headers** (Date, Merchant, Category, Account, Amount required)
4. For each row:
   - **Parse date** (try multiple formats)
   - **Parse amount** (handle $, commas, negative)
   - **Determine transaction type** (positive/negative)
   - **Create external_id** (date-merchant-amount)
   - **Check for duplicates** using external_id
   - **Lookup category** (error if not found)
   - **Get/create account** with smart institution handling
   - **Build description** from merchant + statement + notes + tags
   - **Create transaction**
5. **Track statistics** (created, skipped, errors)
6. **Clean up** uploaded file
7. **Return results** with details

### Smart Account Creation

When an account doesn't exist:
1. Check if institution with merchant name exists
2. If not, create institution with:
   - Name: merchant name
   - Location: "Auto-created"
   - Description: "Auto-created from transaction import"
3. Create account with:
   - Name: account name from CSV
   - Institution: the merchant institution
   - Number: "Auto-imported"
   - Type: checking
   - Class: asset
   - Balance: 0

### Duplicate Detection

Transactions are considered duplicates if they have the same external_id:
```python
external_id = f"{date_str}-{merchant}-{amount_str}".replace('/', '-').replace(' ', '-')
# Example: "01-15-2024-Walmart--$125.50"
```

### Description Building

The transaction description combines available fields:
```
Merchant: Walmart | Statement: WMT SUPERCENTER #1234 | Notes: Weekly shopping | Tags: groceries;food
```

### Date Format Support

Supports multiple formats automatically:
- `MM/DD/YYYY` (01/15/2024)
- `YYYY-MM-DD` (2024-01-15)
- `MM-DD-YYYY` (01-15-2024)
- `DD/MM/YYYY` (15/01/2024)

### Error Handling

| Error Type | Handling | User Impact |
|------------|----------|-------------|
| Missing categories | Skip row, add to errors | Must import categories first |
| Invalid date format | Skip row, add to errors | Shows which format was expected |
| Invalid amount | Skip row, add to errors | Shows what value was invalid |
| Duplicate transaction | Skip row, increment skipped | No error, just skipped |
| Missing required field | Skip row, increment skipped | Silently skipped |
| Account creation failure | Skip row, add to errors | Rare, usually succeeds |

---

## Testing

### Test the Import

1. **Restart Flask app** to load updated endpoint
2. **Navigate** to http://localhost:5000/transactions
3. **Click** "Import CSV" button
4. **Create a test CSV** with your format
5. **Upload** and verify results

### Sample Test CSV

Create `test_transactions.csv`:
```csv
Date,Merchant,Category,Account,Original Statement,Notes,Amount,Tags
01/15/2024,Walmart,Groceries,Chase Checking,WMT SUPERCENTER,Weekly shopping,"-$125.50",groceries
01/16/2024,Employer,Salary,Chase Checking,Direct Deposit,Paycheck,"$2500.00",income
01/17/2024,Gas Station,Gas & Fuel,Credit Card,SHELL OIL,Fill up,"-$45.00",gas
```

**Expected Results:**
- 3 transactions created (if categories exist)
- 0 duplicates skipped (first import)
- 0 errors (if all categories exist)
- Accounts auto-created if needed
- Institutions created from merchant names

---

## Common Issues & Solutions

### Issue 1: "Category 'X' not found"
**Solution:** Import categories first using `/categories/import`

### Issue 2: "Unable to parse date"
**Solution:** Ensure dates are in format MM/DD/YYYY or YYYY-MM-DD

### Issue 3: "Invalid amount"
**Solution:** Ensure amounts are numbers, can have $, commas, negative signs

### Issue 4: All transactions skipped
**Solution:** Check if transactions already exist (based on date + merchant + amount)

---

## Differences from Original Import

### Old Format
- Expected: `Transaction ID, Category, Institution, Account, Date, Amount, Description`
- Hardcoded date format: `%m/%d/%Y`
- Failed if category didn't exist
- Required institution name

### New Format
- Expects: `Date, Merchant, Category, Account, Original Statement, Notes, Amount, Tags`
- Multiple date formats supported
- Returns error if category doesn't exist (doesn't create)
- Uses merchant as institution name
- Builds rich description from multiple fields
- Better error handling and reporting

---

## API Documentation

### POST /api/transaction/csv_import

**Description:** Import transactions from CSV file

**Authentication:** Required (session-based)

**Content-Type:** multipart/form-data

**Parameters:**
- `file` (required): CSV file with columns: Date, Merchant, Category, Account, Amount (and optional: Original Statement, Notes, Tags)

**Success Response (201):**
```json
{
  "message": "Import completed",
  "transactions_created": 150,
  "transactions_skipped": 25,
  "errors": 3,
  "error_details": [
    "Row 15: Category 'Unknown' not found",
    "Row 23: Invalid amount '$ABC'"
  ]
}
```

**Error Responses:**

- `400`: Invalid request (missing file, wrong format, invalid CSV headers)
- `401`: Not authenticated
- `500`: Server error during processing

---

## Summary

**Complete transaction CSV import system**
- Custom column format support (Date, Merchant, Category, Account, etc.)
- Smart account and institution creation
- Rich transaction descriptions
- Duplicate detection
- Detailed error reporting
- User-friendly interface
- Multiple date format support

**The feature is ready to use!** Just restart your Flask application and:
1. Import categories first at `/categories/import`
2. Then import transactions at `/transactions/import`
