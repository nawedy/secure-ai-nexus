# SecureAI Platform API Reference

## Authentication
All API requests must include appropriate authentication headers.

### Get Access Token
```http
POST /auth/token
Content-Type: application/json

{
  "client_id": "your-client-id",
  "client_secret": "your-client-secret",
  "grant_type": "client_credentials",
  "scope": "model.read model.write"
}
```

### Model Management

#### Upload Model
```http
POST /api/v1/models
Authorization: Bearer <token>
Content-Type: multipart/form-data

--boundary
Content-Disposition: form-data; name="model"; filename="model.pt"
Content-Type: application/octet-stream

<model-binary-data>
--boundary
Content-Disposition: form-data; name="metadata"
Content-Type: application/json

{
  "name": "my-model",
  "version": "1.0.0",
  "framework": "pytorch",
  "input_format": "tensor",
  "security_level": "high"
}
```

#### Get Model Status
```http
GET /api/v1/models/{model-id}/status
Authorization: Bearer <token>
```

### Security Endpoints

#### Audit Logs
```http
GET /api/v1/audit/logs
Authorization: Bearer <token>
Query Parameters:
  - start_time: ISO8601 timestamp
  - end_time: ISO8601 timestamp
  - event_type: string
  - severity: string
```
