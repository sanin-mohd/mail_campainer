# Bulk Upload Recipients - User Guide

## Overview
The bulk upload feature allows you to import large numbers of recipients efficiently using CSV or Excel files. The system uses parallel processing and can handle millions of rows.

## Features
✅ Support for CSV (.csv) and Excel (.xlsx, .xls) formats
✅ Automatic email validation
✅ Duplicate detection and skipping
✅ Parallel processing for ultra-fast imports (~2M rows/sec)
✅ Automatic lowercase conversion for emails
✅ Progress tracking and statistics

## File Format

### Required Columns
- **email** (required): Valid email address
- **name** (required): Recipient's name

### Sample CSV Format
```csv
name,email
John Doe,john.doe@example.com
Jane Smith,jane.smith@example.com
Bob Johnson,bob.johnson@example.com
```

### Sample Excel Format
Create an Excel file with the same structure:
| name          | email                    |
|---------------|--------------------------|
| John Doe      | john.doe@example.com     |
| Jane Smith    | jane.smith@example.com   |
| Bob Johnson   | bob.johnson@example.com  |

## How to Use

### Step 1: Access the Bulk Upload Page
1. Go to Django Admin: `http://localhost:8000/admin`
2. Navigate to **Campaigns** → **Recipients**
3. Click the **"Bulk Upload Recipients"** button in the top-right corner

### Step 2: Prepare Your File
1. Create a CSV or Excel file with the required columns
2. Ensure all emails are valid
3. The system will automatically:
   - Convert emails to lowercase
   - Skip invalid emails
   - Skip duplicate emails
   - Set subscription_status to 'subscribed'

### Step 3: Upload
1. Click **"Choose File"** and select your CSV/Excel file
2. Click **"Upload Recipients"**
3. Wait for processing (large files may take a few seconds)
4. View the success message with import statistics

### Step 4: Review Results
After upload, you'll see:
- **Created**: Number of new recipients added
- **Duplicates Skipped**: Number of emails that already existed

## Technical Details

### Performance
- **Architecture**: Multi-process parallel import using PostgreSQL COPY
- **Speed**: Up to 2 million rows per second (hardware dependent)
- **Chunk Size**: 200,000 rows per worker
- **Workers**: Automatically configured based on CPU cores

### Data Processing Flow
1. File upload and validation
2. Excel to CSV conversion (if needed)
3. Email normalization (lowercase, validation)
4. CSV splitting into chunks
5. Parallel COPY to temporary table
6. UPSERT to main table (skip duplicates)
7. Statistics calculation

### Database Operations
- Uses temporary PostgreSQL table for staging
- UPSERT with `ON CONFLICT (email) DO NOTHING`
- Automatically adds `subscription_status = 'subscribed'`
- Sets `created_on` to current timestamp

## Best Practices

### ✅ Do's
- Ensure emails are in a valid format
- Use the sample file as a template
- Remove header rows from Excel before converting to CSV (or keep standard headers)
- Test with a small file first
- Keep email column populated (required)

### ❌ Don'ts
- Don't include special characters in email addresses
- Don't use different column names (must be 'name' and 'email')
- Don't upload files without the email column
- Don't worry about duplicates - they're handled automatically

## Error Handling

### Common Errors and Solutions

**Error: "Invalid file format"**
- Solution: Ensure file is .csv, .xlsx, or .xls

**Error: "No email column found"**
- Solution: Add an 'email' column header to your file

**Error: "Database connection failed"**
- Solution: Check PostgreSQL is running and credentials are correct

**Error: "Out of memory"**
- Solution: The parallel importer is optimized for large files, but if you encounter this, reduce CHUNK_SIZE in importer_v2.py

## Sample Files

sample csv/xlsx files are included: `sample_recipients.csv` `sample_recipients_100k.xlsx` `sample_recipients_100k.csv`

You can use this as a template for your imports.

## Performance Tuning

### Configuration (in `importer_v2.py`)

```python
WORKERS = max(2, cpu_count() // 2)  # Adjust worker count
CHUNK_SIZE = 200_000                # Rows per worker
```

### Recommendations
- **Small files (<10K rows)**: Default settings work fine
- **Large files (100K-1M rows)**: Default settings optimal
- **Huge files (>1M rows)**: Consider increasing CHUNK_SIZE to 500,000

## Monitoring

### Import Statistics
After each upload, you'll receive:
- Total rows processed
- Successfully created recipients
- Duplicates skipped
- Processing time (in logs)

### Database Queries
You can verify imports with:
```sql
SELECT COUNT(*) FROM campaigns_recipient;
SELECT * FROM campaigns_recipient ORDER BY created_on DESC LIMIT 10;
```

## Security

- File uploads are validated for format
- Email validation prevents invalid data
- Django admin authentication required
- No SQL injection risk (parameterized queries)
- Temporary files are cleaned up automatically
