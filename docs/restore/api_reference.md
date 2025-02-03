# API Reference Documentation

## Overview

The SecureAI Platform Restore API provides programmatic access to database restore operations. This document details all available endpoints, methods, and integration patterns.

## Authentication

### API Key Authentication
```python
headers = {
    'Authorization': f'Bearer {api_key}',
    'Content-Type': 'application/json'
}
```

### Service Account Authentication
```python
from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    'path/to/service-account.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
```

## REST API Endpoints

### List Backups

```http
GET /api/v1/backups
```

Lists available database backups.

#### Parameters
| Name | Type | In | Description |
|------|------|------|------------|
| limit | integer | query | Maximum number of backups to return |
| offset | integer | query | Number of backups to skip |
| sort | string | query | Sort order (created_at, size) |
| order | string | query | Sort direction (asc, desc) |

#### Response
```json
{
    "backups": [
        {
            "name": "backup_20240101_120000.sql.gz",
            "size": 1048576,
            "created_at": "2024-01-01T12:00:00Z",
            "checksum": "sha256:abc123...",
            "status": "available"
        }
    ],
    "total": 100,
    "limit": 10,
    "offset": 0
}
```

### Initiate Restore

```http
POST /api/v1/restores
```

Initiates a new restore operation.

#### Request Body
```json
{
    "backup_name": "backup_20240101_120000.sql.gz",
    "target_database": "restored_db",
    "options": {
        "verify": true,
        "force": false,
        "parallel_workers": 4
    }
}
```

#### Response
```json
{
    "restore_id": "rst_123abc",
    "status": "in_progress",
    "started_at": "2024-01-02T15:30:00Z",
    "estimated_completion": "2024-01-02T16:00:00Z"
}
```

### Get Restore Status

```http
GET /api/v1/restores/{restore_id}
```

Retrieves the status of a restore operation.

#### Response
```json
{
    "restore_id": "rst_123abc",
    "status": "completed",
    "started_at": "2024-01-02T15:30:00Z",
    "completed_at": "2024-01-02T15:45:00Z",
    "size_bytes": 1048576,
    "duration_seconds": 900,
    "verification_status": "success"
}
```

### Cancel Restore

```http
POST /api/v1/restores/{restore_id}/cancel
```

Cancels an in-progress restore operation.

#### Response
```json
{
    "restore_id": "rst_123abc",
    "status": "cancelled",
    "cancelled_at": "2024-01-02T15:35:00Z"
}
```

## Python SDK

### Installation
```bash
pip install secureai-restore-sdk
```

### Basic Usage
```python
from secureai.restore import RestoreClient

client = RestoreClient(api_key='your-api-key')

# List backups
backups = client.list_backups(limit=10)

# Initiate restore
restore = client.create_restore(
    backup_name='backup_20240101_120000.sql.gz',
    target_database='restored_db'
)

# Check status
status = client.get_restore_status(restore.id)
```

### Advanced Usage
```python
from secureai.restore import RestoreClient, RestoreOptions

# Configure client
client = RestoreClient(
    api_key='your-api-key',
    timeout=300,
    retry_attempts=3
)

# Configure restore options
options = RestoreOptions(
    verify=True,
    force=False,
    parallel_workers=4,
    timeout_seconds=3600
)

# Create restore with monitoring
restore = client.create_restore(
    backup_name='backup_20240101_120000.sql.gz',
    target_database='restored_db',
    options=options,
    on_progress=lambda x: print(f"Progress: {x}%")
)

# Wait for completion
result = restore.wait_for_completion()
```

## WebSocket API

### Connect to Status Stream
```javascript
const ws = new WebSocket('wss://api.secureai.com/v1/restores/stream');
ws.onmessage = (event) => {
    const status = JSON.parse(event.data);
    console.log(`Restore ${status.restore_id}: ${status.status}`);
};
```

### Status Update Format
```json
{
    "type": "restore_update",
    "restore_id": "rst_123abc",
    "status": "in_progress",
    "progress": 45,
    "current_operation": "restoring_data",
    "timestamp": "2024-01-02T15:35:00Z"
}
```

## Error Handling

### Error Response Format
```json
{
    "error": {
        "code": "restore_failed",
        "message": "Failed to restore database",
        "details": {
            "reason": "insufficient_space",
            "required_bytes": 1048576,
            "available_bytes": 524288
        },
        "request_id": "req_xyz789"
    }
}
```

### Common Error Codes
| Code | Description | HTTP Status |
|------|-------------|-------------|
| backup_not_found | Backup does not exist | 404 |
| invalid_request | Invalid request parameters | 400 |
| restore_failed | Restore operation failed | 500 |
| insufficient_space | Not enough storage space | 507 |
| database_exists | Target database already exists | 409 |

## Rate Limiting

### Limits
- 100 requests per minute per API key
- 5 concurrent restore operations
- 1000 requests per hour per IP

### Rate Limit Response
```json
{
    "error": {
        "code": "rate_limit_exceeded",
        "message": "Too many requests",
        "reset_at": "2024-01-02T16:00:00Z"
    }
}
```

## Monitoring & Metrics

### Available Metrics
- `restore_requests_total`
- `restore_duration_seconds`
- `restore_size_bytes`
- `restore_errors_total`

### Prometheus Integration
```python
from prometheus_client import Counter, Histogram

RESTORE_REQUESTS = Counter(
    'restore_requests_total',
    'Total number of restore requests'
)

RESTORE_DURATION = Histogram(
    'restore_duration_seconds',
    'Time taken for restore operations'
)
```

## SDK Examples

### Error Handling
```python
from secureai.restore import RestoreClient, RestoreError

try:
    client = RestoreClient(api_key='your-api-key')
    restore = client.create_restore(
        backup_name='backup.sql.gz',
        target_database='db'
    )
except RestoreError as e:
    print(f"Restore failed: {e.message}")
    print(f"Error code: {e.code}")
    print(f"Request ID: {e.request_id}")
```

### Async Usage
```python
async with RestoreClient(api_key='your-api-key') as client:
    restore = await client.create_restore_async(
        backup_name='backup.sql.gz',
        target_database='db'
    )
    status = await restore.wait_for_completion_async()
```

### Batch Operations
```python
async def restore_multiple(client, backups, target_prefix):
    tasks = []
    for backup in backups:
        task = client.create_restore_async(
            backup_name=backup,
            target_database=f"{target_prefix}_{backup}"
        )
        tasks.append(task)
    return await asyncio.gather(*tasks)
