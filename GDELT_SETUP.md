# GDELT BigQuery Integration Setup Guide

This guide explains how to set up Google Cloud BigQuery access for historical Korean financial news sentiment data.

## Overview

The RateStance pipeline now supports two data sources:
- **Google News RSS**: Current data (last 2-4 weeks only)
- **GDELT BigQuery**: Historical data (2015-present)

GDELT provides comprehensive news sentiment analysis with tone/sentiment scores dating back to 2015, enabling analysis of older rate change events (e.g., 2024-10-11 rate cut).

## Quick Setup (Recommended)

### Option 1: Public Dataset Access (Free, No Setup Required)

The easiest way to use GDELT is with public dataset access. No Google Cloud account required.

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Set environment variables in `.env`:
   ```bash
   # GDELT Configuration (Public Dataset - Free)
   GDELT_USE_PUBLIC=true
   ENABLE_GDELT=true
   GDELT_CUTOFF_DATE=2025-08-01
   ```

3. Run the pipeline:
   ```bash
   uv run ratestance collect
   ```

**Note**: Public access has rate limits (1TB/month free tier). For production use, consider authenticated access.

## Optional: Authenticated Access (Higher Limits)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Note your Project ID (e.g., `my-project-12345`)

### Step 2: Enable BigQuery API

1. In Cloud Console, navigate to **APIs & Services > Library**
2. Search for "BigQuery API"
3. Click **Enable**

### Step 3: Set Up Authentication

#### Option A: Service Account (Recommended for Production)

1. Navigate to **IAM & Admin > Service Accounts**
2. Click **Create Service Account**
3. Name: `ratestance-gdelt`
4. Click **Create and Continue**
5. Grant role: **BigQuery User** (roles/bigquery.user)
6. Click **Done**

7. Click on the service account you just created
8. Go to **Keys** tab
9. Click **Add Key > Create new key**
10. Select **JSON** format
11. Download the key file

12. Save the key file securely (e.g., `~/.config/gcloud/ratestance-key.json`)
13. Set environment variable:
    ```bash
    export GOOGLE_APPLICATION_CREDENTIALS="~/.config/gcloud/ratestance-key.json"
    ```

#### Option B: Application Default Credentials (For Development)

1. Install Google Cloud SDK:
   ```bash
   # macOS
   brew install google-cloud-sdk

   # Linux
   curl https://sdk.cloud.google.com | bash
   ```

2. Initialize and authenticate:
   ```bash
   gcloud init
   gcloud auth application-default login
   ```

### Step 4: Configure RateStance

Add to your `.env` file:

```bash
# GDELT Configuration (Authenticated Access)
GDELT_PROJECT_ID=your-project-id
GDELT_USE_PUBLIC=false
ENABLE_GDELT=true
GDELT_CUTOFF_DATE=2025-08-01

# Google Cloud credentials (if using service account)
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your-key.json
```

## Configuration Options

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `ENABLE_GDELT` | bool | `true` | Enable GDELT integration |
| `GDELT_USE_PUBLIC` | bool | `true` | Use public dataset (free) |
| `GDELT_PROJECT_ID` | string | `null` | Google Cloud project ID |
| `GDELT_CUTOFF_DATE` | date | `2025-08-01` | Date cutoff for using GDELT vs RSS |

## How It Works

The pipeline automatically selects the data source based on date:

- **Before `GDELT_CUTOFF_DATE`**: Uses GDELT BigQuery (historical backfill)
- **On/After `GDELT_CUTOFF_DATE`**: Uses Google News RSS (current data)

Both datasets are combined seamlessly, maintaining the same schema.

### Example Flow

```
Request: 2024-01-01 to 2025-12-31

├─ 2024-01-01 to 2025-07-31: GDELT BigQuery (historical)
└─ 2025-08-01 to 2025-12-31: Google News RSS (current)

Result: Combined dataset with full coverage
```

## Data Schema

GDELT data is mapped to match the existing news schema:

| GDELT Column | Output Column | Description |
|--------------|---------------|-------------|
| `DATE` | `published_at` | Publication date |
| `DocumentIdentifier` | `google_url` | Article URL |
| `Themes` | `title` | Article themes (truncated) |
| `Tone`, `PositiveScore`, `NegativeScore` | `summary` | Sentiment summary |
| - | `query` | Search query used |

### GDELT Tone Scores

GDELT provides sentiment analysis in the `Tone` column:
- **Range**: -100 (very negative) to +100 (very positive)
- **Positive tone**: May indicate hawkish stance (rate hike expectations)
- **Negative tone**: May indicate dovish stance (rate cut expectations)

The pipeline includes tone information in the article summary for reference.

## Testing

### Test GDELT Access

```bash
# Test with public dataset
GDELT_USE_PUBLIC=true uv run python -c "
from ratestance.collector import GdeltClient
from datetime import date

client = GdeltClient(use_public=True)
print(f'GDELT available: {client.is_available()}')

# Test collection for 2024 rate cut period
df = client.collect(
    queries=['한국은행 기준금리'],
    start_date=date(2024, 10, 1),
    end_date=date(2024, 10, 20),
    max_items=10
)
print(f'Collected {len(df)} articles')
print(df.head())
"
```

### Test Full Pipeline

```bash
# Test with historical date range
uv run ratestance collect --start-date=2024-10-01 --end-date=2024-10-20
```

Expected output:
- GDELT collects ~50-200 articles for the period
- Event study shows actual values for 2024-10-11 rate cut event

## Troubleshooting

### Issue: "BigQuery client not initialized"

**Cause**: Missing credentials or public access disabled

**Solution**:
1. Set `GDELT_USE_PUBLIC=true` for free public access
2. Or set up authenticated access with service account
3. Verify `GOOGLE_APPLICATION_CREDENTIALS` is set

### Issue: "GDELT query failed:_quotaExceeded"

**Cause**: Exceeded free tier quota (1TB/month)

**Solution**:
1. Use authenticated access for higher limits
2. Reduce date range for each query
3. Filter queries to reduce data volume

### Issue: "No articles found from GDELT"

**Cause**: No Korean news for the specified period/keywords

**Solution**:
1. Verify date range (GDELT coverage starts 2015)
2. Check keywords are in Korean
3. Try broader date range first

### Issue: "ImportError: No module named 'google.cloud.bigquery'"

**Cause**: Dependencies not installed

**Solution**:
```bash
uv sync
```

## Cost Considerations

### Public Dataset (Free)
- **Cost**: Free
- **Limit**: 1TB query data per month
- **Best for**: Development, testing, small projects

### Authenticated Access (Pay-as-you-go)
- **Cost**: $5 per TB queried
- **Limit**: No quota limits (subject to billing)
- **Best for**: Production, high-volume queries

### Cost Optimization Tips

1. **Filter by date**: Always specify date ranges
2. **Filter by language**: Use `Language = 'Korean'` filter
3. **Limit results**: Use `LIMIT` clause to reduce data transfer
4. **Cache results**: Store queried data locally

## References

- [GDELT Project](https://www.gdeltproject.org/)
- [BigQuery Public Datasets](https://cloud.google.com/bigquery/public-data)
- [BigQuery Pricing](https://cloud.google.com/bigquery/pricing)
- [BigQuery Python Client](https://googleapis.dev/python/bigquery/latest/index.html)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify environment variables are set correctly
3. Review logs for detailed error messages
4. Consult GDELT documentation for schema details
