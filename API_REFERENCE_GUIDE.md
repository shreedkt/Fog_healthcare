# Secure Fog Healthcare - API Reference Guide
## Complete REST API Documentation for Developers

---

## Table of Contents
1. [API Overview](#api-overview)
2. [Authentication](#authentication)
3. [Request/Response Format](#requestresponse-format)
4. [User Management Endpoints](#user-management-endpoints)
5. [Medical Records Endpoints](#medical-records-endpoints)
6. [Cloud Gateway Endpoints](#cloud-gateway-endpoints)
7. [Dashboard Web Routes](#dashboard-web-routes)
8. [Error Handling](#error-handling)
9. [Client Implementation Examples](#client-implementation-examples)
10. [Rate Limiting & Throttling](#rate-limiting--throttling)

---

## API Overview

### Base URL
```
Development:  http://localhost:8000/api/v1
Production:   https://api.hospital.com/api/v1
```

### API Version
- **Current Version**: v1
- **Deprecation**: Versions will be maintained for 12 months after deprecation notice

### Supported Content Types
- Request: `application/json`
- Response: `application/json`

### Authentication Method
- **Type**: Session-based (cookies)
- **Alternative**: JWT tokens (future)
- **Header**: `Authorization: Bearer <token>` (for future token-based auth)

---

## Authentication

### Login
```http
POST /api/v1/auth/login/
Content-Type: application/json

{
    "username": "doctor1",
    "password": "SecurePassword123!"
}
```

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "doctor1",
        "role": "DOCTOR"
    }
}
```

**Cookies Set**:
```
Set-Cookie: sessionid=abcd1234efgh5678ijkl9012mnop3456; Path=/; HttpOnly; Secure; SameSite=Strict
```

**Error Responses**:

| Code | Error | Reason |
|------|-------|--------|
| 401 | Invalid credentials | Username/password incorrect |
| 404 | User not found | Username doesn't exist |
| 400 | Missing fields | username or password empty |

---

### Register
```http
POST /api/v1/auth/register/
Content-Type: application/json

{
    "username": "newdoctor",
    "password": "SecurePassword123!",
    "email": "doctor@hospital.com",
    "role": "DOCTOR"
}
```

**Response (201 Created)**:
```json
{
    "success": true,
    "message": "User registered successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "username": "newdoctor",
        "email": "doctor@hospital.com",
        "role": "DOCTOR",
        "date_joined": "2025-05-08T10:30:00Z"
    }
}
```

**Validation Rules**:
- Username: 3-150 characters, alphanumeric + underscore
- Password: Minimum 8 characters, must pass Django validators
- Email: Valid email format
- Role: DOCTOR, NURSE, or ADMIN

---

### Logout
```http
POST /api/v1/auth/logout/
Cookie: sessionid=<value>
```

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Logout successful"
}
```

---

## Request/Response Format

### Standard Response Format

**Success Response**:
```json
{
    "success": true,
    "message": "Human readable message (optional)",
    "data": {
        // Response data varies by endpoint
    }
}
```

**Error Response**:
```json
{
    "success": false,
    "error": {
        "code": "error_code_string",
        "message": "Human readable error message"
    }
}
```

### Standard HTTP Headers

**Request Headers** (all requests):
```http
Content-Type: application/json
Accept: application/json
Accept-Encoding: gzip, deflate
Connection: keep-alive
```

**Response Headers** (all responses):
```http
Content-Type: application/json
Content-Encoding: gzip
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
```

### HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, POST, PUT |
| 201 | Created | Resource created successfully |
| 204 | No Content | Successful DELETE (no response body) |
| 400 | Bad Request | Validation error, missing fields |
| 401 | Unauthorized | No authentication / session expired |
| 403 | Forbidden | Authenticated but lacks permission |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Resource already exists (duplicate) |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Server Error | Internal error |
| 502 | Bad Gateway | Cloud service unavailable |

---

## User Management Endpoints

### GET /api/v1/auth/user/

**Description**: Get current authenticated user's profile

**Permission**: Authenticated users

**Request**:
```http
GET /api/v1/auth/user/
Cookie: sessionid=<value>
```

**Response (200 OK)**:
```json
{
    "success": true,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "doctor1",
        "email": "doctor@hospital.com",
        "first_name": "John",
        "last_name": "Doe",
        "role": "DOCTOR",
        "is_staff": false,
        "is_superuser": false,
        "is_active": true,
        "date_joined": "2025-01-15T08:00:00Z",
        "last_login": "2025-05-08T10:30:00Z"
    }
}
```

---

### PUT /api/v1/auth/user/

**Description**: Update current user's profile

**Permission**: Authenticated users (self-update only)

**Request**:
```http
PUT /api/v1/auth/user/
Cookie: sessionid=<value>
Content-Type: application/json

{
    "email": "newemail@hospital.com",
    "first_name": "Jonathan",
    "last_name": "Smith"
}
```

**Updatable Fields**:
- email
- first_name
- last_name

**Non-Updatable Fields** (ignored):
- username, role, is_staff, is_superuser

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Profile updated successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "doctor1",
        "email": "newemail@hospital.com",
        "first_name": "Jonathan",
        "last_name": "Smith"
    }
}
```

---

### PUT /api/v1/auth/change-password/

**Description**: Change user password

**Permission**: Authenticated users

**Request**:
```http
PUT /api/v1/auth/change-password/
Cookie: sessionid=<value>
Content-Type: application/json

{
    "old_password": "CurrentPassword123!",
    "new_password": "NewSecurePassword456!"
}
```

**Password Requirements**:
- Minimum 8 characters
- Not entirely numeric
- Not similar to username/email
- Not in common passwords list

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Password changed successfully"
}
```

**Error Responses**:
- 400: Old password incorrect, new password too weak
- 401: Unauthenticated

---

### GET /api/v1/auth/users/

**Description**: List all users (admin only)

**Permission**: ADMIN role only

**Query Parameters**:
- `role`: Filter by role (DOCTOR, NURSE, ADMIN)
- `is_active`: Filter by active status (true/false)
- `search`: Search by username/email
- `limit`: Results per page (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)

**Request**:
```http
GET /api/v1/auth/users/?role=DOCTOR&limit=50&offset=0
Cookie: sessionid=<value>
```

**Response (200 OK)**:
```json
{
    "success": true,
    "data": {
        "total": 150,
        "limit": 50,
        "offset": 0,
        "users": [
            {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "username": "doctor1",
                "email": "doctor1@hospital.com",
                "role": "DOCTOR",
                "is_active": true,
                "date_joined": "2025-01-15T08:00:00Z",
                "last_login": "2025-05-08T10:30:00Z"
            }
        ]
    }
}
```

---

## Medical Records Endpoints

### POST /api/v1/records/create/

**Description**: Create encrypted medical record

**Permission**: CanWriteRecords (DOCTOR, ADMIN)

**Request**:
```http
POST /api/v1/records/create/
Cookie: sessionid=<value>
Content-Type: application/json

{
    "patient_id": "550e8400-e29b-41d4-a716-446655440100",
    "encrypted_payload": "AQECAwQFBgcICQoLDA0ODxARjmKWxQb/...",
    "encrypted_aes_key": "vV5GzMp1Vb8k9LmXp0QyRw==",
    "ephemeral_public_key": "-----BEGIN PUBLIC KEY-----\nMFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAE...\n-----END PUBLIC KEY-----",
    "integrity_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
}
```

**Field Specifications**:

| Field | Type | Format | Validation |
|-------|------|--------|-----------|
| patient_id | String | UUID | Valid UUID format |
| encrypted_payload | String | Base64 | Valid Base64, ≥32 bytes decoded |
| encrypted_aes_key | String | Base64 | Valid Base64 |
| ephemeral_public_key | String | PEM | Valid SECP256R1 ECC public key |
| integrity_hash | String | Hex | 64 hex characters (SHA-256) |

**Validation Process**:
1. Parse JSON and validate field types
2. Verify integrity_hash format (64 hex chars)
3. Base64 decode encrypted_payload
4. Compute SHA256(ciphertext)
5. Compare: computed_hash == provided_hash
6. If hash mismatch → 400 Bad Request
7. If valid → Create MedicalRecord
8. Log CREATE audit action

**Response (201 Created)**:
```json
{
    "success": true,
    "message": "Medical record created successfully",
    "data": {
        "id": "660e8400-e29b-41d4-a716-446655440200",
        "patient_id": "550e8400-e29b-41d4-a716-446655440100",
        "created_at": "2025-05-08T11:00:00Z",
        "created_by": "doctor1"
    }
}
```

**Error Responses**:

| Code | Error | Reason |
|------|-------|--------|
| 400 | Validation error | Invalid field format |
| 400 | Integrity failed | SHA256 hash mismatch |
| 401 | Unauthenticated | No session |
| 403 | Permission denied | User is not DOCTOR/ADMIN |

---

### GET /api/v1/records/<record_id>/

**Description**: Retrieve single encrypted record

**Permission**: CanReadRecords (DOCTOR, NURSE, ADMIN)

**Request**:
```http
GET /api/v1/records/660e8400-e29b-41d4-a716-446655440200/
Cookie: sessionid=<value>
```

**Response (200 OK)**:
```json
{
    "success": true,
    "data": {
        "id": "660e8400-e29b-41d4-a716-446655440200",
        "patient_id": "550e8400-e29b-41d4-a716-446655440100",
        "encrypted_payload": "AQECAwQFBgcICQoLDA0ODxARjmKWxQb/...",
        "encrypted_aes_key": "vV5GzMp1Vb8k9LmXp0QyRw==",
        "ephemeral_public_key": "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----",
        "integrity_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        "created_at": "2025-05-08T11:00:00Z",
        "created_by": "doctor1"
    }
}
```

**Audit**: READ action logged with record ID, user, IP address

---

### DELETE /api/v1/records/<record_id>/

**Description**: Soft-delete medical record

**Permission**: CanDeleteRecords (ADMIN only)

**Request**:
```http
DELETE /api/v1/records/660e8400-e29b-41d4-a716-446655440200/
Cookie: sessionid=<value>
```

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Medical record deleted successfully"
}
```

**Soft Delete Behavior**:
- Sets `is_deleted = True`
- Does NOT remove from database
- Record not returned by GET requests
- Audit trail preserved
- Can be restored by admin if needed

**Audit**: DELETE action logged

---

### GET /api/v1/records/patient/<patient_id>/

**Description**: List all records for a patient (paginated)

**Permission**: CanReadRecords (DOCTOR, NURSE, ADMIN)

**Query Parameters**:
- `limit`: Items per page (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)
- `created_after`: ISO8601 datetime filter (optional)
- `created_before`: ISO8601 datetime filter (optional)
- `sort`: Sort field (default: -created_at)
  - Options: `created_at`, `-created_at`, `created_by`

**Request**:
```http
GET /api/v1/records/patient/550e8400-e29b-41d4-a716-446655440100/?limit=50&offset=0&created_after=2025-01-01T00:00:00Z
Cookie: sessionid=<value>
```

**Response (200 OK)**:
```json
{
    "success": true,
    "data": {
        "total": 523,
        "limit": 50,
        "offset": 0,
        "has_next": true,
        "has_previous": false,
        "records": [
            {
                "id": "660e8400-e29b-41d4-a716-446655440200",
                "patient_id": "550e8400-e29b-41d4-a716-446655440100",
                "created_at": "2025-05-08T11:00:00Z",
                "created_by": "doctor1"
            }
        ]
    }
}
```

---

## Cloud Gateway Endpoints

### POST /api/v1/records/forward-to-cloud/

**Description**: Forward encrypted record to cloud service

**Permission**: IsDoctorOrAdmin (DOCTOR, ADMIN)

**Request**:
```http
POST /api/v1/records/forward-to-cloud/
Cookie: sessionid=<value>
Content-Type: application/json

{
    "record_id": "660e8400-e29b-41d4-a716-446655440200"
}
```

**Process**:
```
1. Load Fog private key from disk
   ↓
2. Decrypt record using Fog private key
   ↓
3. Load Cloud public key from disk
   ↓
4. Re-encrypt plaintext using Cloud public key
   ↓
5. POST re-encrypted payload to Cloud API
   - URL: {CLOUD_API_URL}
   - Timeout: {CLOUD_API_TIMEOUT}s
   - Retries: {CLOUD_API_MAX_RETRIES} (exponential backoff)
   ↓
6. Log FORWARD audit action
   ↓
7. Return TransmissionResult
```

**Retry Logic**:
- Attempt 1: Immediate
- Attempt 2: Wait 1s, then retry
- Attempt 3: Wait 2s, then retry
- Attempt 4: Wait 4s, then retry
- Failure: 502 Bad Gateway

**Response (200 OK)**:
```json
{
    "success": true,
    "message": "Data forwarded to cloud successfully",
    "data": {
        "record_id": "660e8400-e29b-41d4-a716-446655440200",
        "attempts": 1,
        "cloud_status_code": 200
    }
}
```

**Error Responses**:

| Code | Error | Scenario |
|------|-------|----------|
| 404 | Record not found | record_id doesn't exist |
| 502 | Cloud unavailable | Cloud API down after retries |
| 500 | Key load error | Private/public key files missing |
| 500 | Encryption error | Decryption/re-encryption failed |
| 403 | Permission denied | User not DOCTOR/ADMIN |
| 401 | Unauthenticated | No session |

**Audit**: FORWARD action logged with:
- Attempt count
- Cloud status code
- Success/failure status

---

## Dashboard Web Routes

**Note**: These are server-rendered HTML pages (not JSON API)

### GET /

**Description**: Dashboard home page (redirects to login if not authenticated)

**Login Required**: Yes

---

### GET /login/

**Description**: User login page

**Login Required**: No

**Form Fields**:
- username (text input)
- password (password input)

---

### GET /logout/

**Description**: Logout user and redirect to login

**Login Required**: Yes

---

### GET /records/

**Description**: List of medical records (paginated table)

**Login Required**: Yes

**Permission**: DOCTOR, NURSE, ADMIN

**Query Parameters**:
- `patient_id`: Filter by patient UUID (optional)

---

### GET /records/<record_id>/

**Description**: View decrypted record details

**Login Required**: Yes

**Permission**: DOCTOR, NURSE, ADMIN

**Features**:
- Decrypts record using Fog private key
- Displays plaintext patient data
- Shows integrity status (verified/tampered)
- Displays record metadata

---

## Error Handling

### Error Response Schema

**Standard Error**:
```json
{
    "success": false,
    "error": {
        "code": "error_code_string",
        "message": "Human readable description"
    }
}
```

**Common Error Codes**:

| Code | HTTP | Meaning |
|------|------|---------|
| invalid_credentials | 401 | Username/password incorrect |
| not_found | 404 | Resource doesn't exist |
| permission_denied | 403 | User lacks permission |
| validation_error | 400 | Invalid input data |
| integrity_failed | 400 | SHA256 hash mismatch |
| encryption_error | 500 | Encryption operation failed |
| key_error | 500 | Cannot load crypto keys |
| cloud_unavailable | 502 | Cloud service down |
| rate_limited | 429 | Too many requests |
| server_error | 500 | Unexpected server error |

---

## Client Implementation Examples

### Python (requests library)

```python
import requests
import json
from datetime import datetime

# Base configuration
BASE_URL = "http://localhost:8000/api/v1"
session = requests.Session()

# 1. Login
login_response = session.post(
    f"{BASE_URL}/auth/login/",
    json={
        "username": "doctor1",
        "password": "doctor1pass"
    }
)
print(f"Login status: {login_response.status_code}")
print(f"User: {login_response.json()['data']['username']}")

# 2. Create encrypted record
record_response = session.post(
    f"{BASE_URL}/records/create/",
    json={
        "patient_id": "550e8400-e29b-41d4-a716-446655440100",
        "encrypted_payload": "base64_ciphertext...",
        "encrypted_aes_key": "base64_wrapped_key...",
        "ephemeral_public_key": "-----BEGIN PUBLIC KEY-----\n...",
        "integrity_hash": "sha256_hex..."
    }
)
record_id = record_response.json()['data']['id']
print(f"Record created: {record_id}")

# 3. Retrieve record
get_response = session.get(f"{BASE_URL}/records/{record_id}/")
record = get_response.json()['data']
print(f"Encrypted payload: {record['encrypted_payload'][:50]}...")

# 4. List patient records
list_response = session.get(
    f"{BASE_URL}/records/patient/550e8400-e29b-41d4-a716-446655440100/",
    params={"limit": 20, "offset": 0}
)
records = list_response.json()['data']['records']
print(f"Found {len(records)} records")

# 5. Forward to cloud
forward_response = session.post(
    f"{BASE_URL}/records/forward-to-cloud/",
    json={"record_id": record_id}
)
print(f"Forward result: {forward_response.json()['data']['attempts']} attempt(s)")

# 6. Logout
session.get(f"{BASE_URL}/auth/logout/")
```

### JavaScript (fetch API)

```javascript
// Base configuration
const BASE_URL = "http://localhost:8000/api/v1";

// Helper function for API calls
async function apiCall(endpoint, options = {}) {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...options.headers,
        },
        credentials: "include", // Include cookies
    });
    
    if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
    }
    
    return response.json();
}

// 1. Login
async function login(username, password) {
    const result = await apiCall("/auth/login/", {
        method: "POST",
        body: JSON.stringify({ username, password }),
    });
    console.log(`Logged in as: ${result.data.username}`);
    return result.data;
}

// 2. Create record
async function createRecord(patientId, encryptedPayload, aesKey, pubKey, hash) {
    const result = await apiCall("/records/create/", {
        method: "POST",
        body: JSON.stringify({
            patient_id: patientId,
            encrypted_payload: encryptedPayload,
            encrypted_aes_key: aesKey,
            ephemeral_public_key: pubKey,
            integrity_hash: hash,
        }),
    });
    console.log(`Record created: ${result.data.id}`);
    return result.data.id;
}

// 3. Retrieve record
async function getRecord(recordId) {
    const result = await apiCall(`/records/${recordId}/`);
    console.log(`Retrieved record for patient: ${result.data.patient_id}`);
    return result.data;
}

// 4. List records
async function listRecords(patientId, limit = 20, offset = 0) {
    const params = new URLSearchParams({
        limit,
        offset,
    });
    const result = await apiCall(`/records/patient/${patientId}/?${params}`);
    console.log(`Found ${result.data.total} total records`);
    return result.data.records;
}

// 5. Forward to cloud
async function forwardToCloud(recordId) {
    const result = await apiCall("/records/forward-to-cloud/", {
        method: "POST",
        body: JSON.stringify({ record_id: recordId }),
    });
    console.log(`Forward completed in ${result.data.attempts} attempt(s)`);
    return result.data;
}

// Usage example
(async () => {
    const user = await login("doctor1", "doctor1pass");
    const recordId = await createRecord(...);
    const record = await getRecord(recordId);
    const records = await listRecords(user.patient_id);
    const result = await forwardToCloud(recordId);
})();
```

### cURL

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"doctor1","password":"doctor1pass"}' \
  -c cookies.txt

# Create record
curl -X POST http://localhost:8000/api/v1/records/create/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{
    "patient_id":"550e8400-e29b-41d4-a716-446655440100",
    "encrypted_payload":"...",
    "encrypted_aes_key":"...",
    "ephemeral_public_key":"...",
    "integrity_hash":"..."
  }'

# Get record
curl -X GET http://localhost:8000/api/v1/records/{record_id}/ \
  -H "Content-Type: application/json" \
  -b cookies.txt

# List records
curl -X GET "http://localhost:8000/api/v1/records/patient/{patient_id}/?limit=20" \
  -H "Content-Type: application/json" \
  -b cookies.txt

# Forward to cloud
curl -X POST http://localhost:8000/api/v1/records/forward-to-cloud/ \
  -H "Content-Type: application/json" \
  -b cookies.txt \
  -d '{"record_id":"660e8400-e29b-41d4-a716-446655440200"}'

# Logout
curl -X GET http://localhost:8000/api/v1/auth/logout/ \
  -b cookies.txt
```

---

## Rate Limiting & Throttling

### Rate Limits

**Authentication Endpoints**:
- Login: 5 attempts per 15 minutes per IP
- Register: 3 attempts per hour per IP

**API Endpoints** (per authenticated user):
- Medical Records: 1,000 requests per hour
- Cloud Gateway: 100 requests per hour

**By Role**:
- ADMIN: No rate limiting
- DOCTOR/NURSE: Standard limits
- PATIENT: Reduced limits (50% of standard)

### Rate Limit Headers

**Response Headers**:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 950
X-RateLimit-Reset: 1620000000
```

### Handling Rate Limits

**Exceeded Response** (429):
```json
{
    "success": false,
    "error": {
        "code": "rate_limited",
        "message": "Rate limit exceeded. Try again in 60 seconds."
    },
    "retry_after": 60
}
```

**Best Practices**:
1. Check `X-RateLimit-Remaining` header
2. Implement exponential backoff for retries
3. Cache data when possible
4. Batch requests to reduce call count
5. Contact admin for rate limit increase if needed

---

**API Version**: 1.0  
**Last Updated**: May 8, 2025  
**Status**: Production Ready  
**Documentation Version**: 1.0
