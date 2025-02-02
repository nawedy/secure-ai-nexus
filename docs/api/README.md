# SecureAI Platform API Documentation

## Overview
This document provides detailed information about the SecureAI Platform API endpoints, authentication, and usage.

## Authentication
All API requests require authentication using JWT tokens.

### Obtaining a Token
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "your-password"
}
```

### Using Authentication
Include the JWT token in the Authorization header:
```http
Authorization: Bearer <your-jwt-token>
```

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/auth/login` | POST | Authenticate user |
| `/api/auth/refresh` | POST | Refresh JWT token |
| `/api/auth/logout` | POST | Invalidate token |

### User Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/users/me` | GET | Get current user |
| `/api/users` | POST | Create new user |
| `/api/users/{id}` | PUT | Update user |
| `/api/users/{id}` | DELETE | Delete user |

### Model Management
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/models` | GET | List models |
| `/api/models` | POST | Create model |
| `/api/models/{id}` | GET | Get model details |
| `/api/models/{id}` | PUT | Update model |
| `/api/models/{id}` | DELETE | Delete model |

### Monitoring
| Endpoint | Method | Description |
|----------|---------|-------------|
| `/api/monitoring/metrics` | GET | Get system metrics |
| `/api/monitoring/health` | GET | Health check |
| `/api/monitoring/logs` | GET | Get system logs |

## Request/Response Examples

### Authentication
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}

Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Error Responses
```json
{
  "error": {
    "code": "unauthorized",
    "message": "Invalid credentials"
  }
}
```

## Rate Limiting
- 100 requests per minute per IP
- 1000 requests per hour per user

## Security
- All endpoints use HTTPS
- JWT tokens expire after 1 hour
- Requests must include valid API key
