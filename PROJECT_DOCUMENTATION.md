# Secure Fog-Based Healthcare Data Sharing System
## Academic Documentation & Project Report

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Introduction](#introduction)
3. [System Architecture](#system-architecture)
4. [Technical Implementation](#technical-implementation)
5. [Cryptographic Security](#cryptographic-security)
6. [Database Design](#database-design)
7. [API Documentation](#api-documentation)
8. [User Authentication & Authorization](#user-authentication--authorization)
9. [Audit & Compliance Framework](#audit--compliance-framework)
10. [Deployment & Configuration](#deployment--configuration)
11. [Installation & Setup](#installation--setup)
12. [Future Enhancements](#future-enhancements)

---

## Executive Summary

The **Secure Fog-Based Healthcare Data Sharing System** is a Django-powered distributed healthcare platform designed for secure management and sharing of medical records across fog computing networks. The system implements military-grade hybrid encryption (AES-256-CBC + SECP256R1 ECC) with zero-knowledge principles, ensuring plaintext medical data is never stored in the system.

### Key Objectives:
- **Zero-Knowledge Architecture**: Plaintext data never persists in storage
- **Hybrid Encryption**: Multi-layer encryption combining symmetric (AES-256) and asymmetric (ECC) cryptography
- **Distributed Computing**: Support for fog nodes with cloud gateway integration
- **Role-Based Access Control**: Fine-grained permissions across four user roles
- **Compliance & Audit**: Complete audit trails for HIPAA compliance
- **REST API**: Full-featured API for healthcare integrations and IoT device support

### Platform Statistics:
- **Language**: Python 3.11+
- **Framework**: Django 5.1+
- **Database**: MySQL 8.0+
- **Cryptography**: Python cryptography 43.0+
- **API Framework**: Django REST Framework 3.15+
- **Deployment**: WSGI-compatible (production-ready)

---

## Introduction

### Problem Statement

Healthcare systems face critical challenges in data security and privacy:
1. **Data Breaches**: Centralized cloud storage creates single points of failure
2. **Regulatory Compliance**: HIPAA, GDPR, and regional healthcare laws require strict data governance
3. **IoT Device Integration**: Medical IoT devices require secure data transmission and storage
4. **Access Control**: Complex multi-role access scenarios in hospital environments
5. **Audit Requirements**: Complete audit trails for compliance and forensics

### Solution Architecture

This project addresses these challenges by:
- **Fog Computing Model**: Distributes data processing to edge nodes, reducing latency and exposure
- **End-to-End Encryption**: Data encrypted at the source, never stored in plaintext
- **Zero-Knowledge Design**: System never has access to plaintext medical data
- **Cloud Integration**: Optional cloud gateway for distributed storage with re-encryption
- **Comprehensive Audit**: Every data access and modification is logged immutably

---

## System Architecture

### High-Level System Design

```
┌──────────────────────────────────────────────────────────────────┐
│                        Healthcare Ecosystem                       │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────┐  ┌──────────────────────┐  ┌────────────┐  │
│  │  IoT Devices    │  │   Fog Node           │  │   Cloud    │  │
│  │  • Sensors      ├─→│  (Django Backend)    ├─→│  Gateway   │  │
│  │  • Monitors     │  │  • Encryption        │  │            │  │
│  │  • Wearables    │  │  • Decryption        │  └────────────┘  │
│  └─────────────────┘  │  • Re-encryption     │                  │
│                        │  • Storage           │                  │
│  ┌──────────────────┐  └──────────────────────┘  ┌────────────┐  │
│  │ Dashboard Users  │                             │   Audit    │  │
│  │ • Doctors        │◄────────────────────────────│   Logs     │  │
│  │ • Nurses         │         ┌───────────┐       │            │  │
│  │ • Administrators │────────→│ Database  │       └────────────┘  │
│  └──────────────────┘         │  (MySQL)  │                      │
│                               └───────────┘                      │
└──────────────────────────────────────────────────────────────────┘
```

### Component Breakdown

#### 1. IoT Layer
- **Source**: Medical sensors, devices, and wearables
- **Function**: Generate encrypted patient data before transmission
- **Security**: Data encrypted at source using Fog node's public ECC key
- **Protocol**: HTTPS REST API calls to `/api/v1/records/create/`

#### 2. Fog Node (Django Backend)
The central processing unit with six specialized applications:

**a) Users App (`apps/users/`)**
- Custom User model with UUID primary key
- Role-based access control (DOCTOR, NURSE, ADMIN)
- Password hashing with Django's PBKDF2
- Session management and authentication

**b) Encryption App (`apps/encryption/`)**
- Hybrid encryption/decryption service
- AES-256-CBC symmetric encryption
- SECP256R1 elliptic curve cryptography (ECC)
- SHA-256 integrity verification
- Key generation and management

**c) Medical Records App (`apps/medical_records/`)**
- Encrypted record storage
- REST API for CRUD operations
- Patient data retrieval
- Soft-delete functionality
- Record pagination and filtering

**d) Audit App (`apps/audit/`)**
- Immutable audit trail logging
- Action tracking (READ, CREATE, UPDATE, DELETE, FORWARD)
- User and IP address logging
- Timestamp recording
- Forensic support

**e) Cloud Gateway App (`apps/cloud_gateway/`)**
- Re-encryption service for cloud transmission
- HTTPS transmission with retry logic
- Cloud API integration
- Forward secrecy implementation

**f) Dashboard App (`apps/dashboard/`)**
- Server-rendered web interface
- Login/logout functionality
- Record list and detail views
- Statistics dashboard
- Role-based view rendering

#### 3. Database Layer
- **Engine**: MySQL 8.0+
- **Charset**: UTF-8 MB4 for Unicode support
- **Isolation**: STRICT_TRANS_TABLES mode
- **Tables**: Users, Medical Records, Audit Logs, Encryption Configs

#### 4. Cloud Gateway (Optional)
- **Role**: Secondary storage and disaster recovery
- **Security**: Re-encryption before transmission
- **Protocol**: HTTPS with SSL verification
- **Resilience**: Automatic retry logic (configurable attempts)

---

## Technical Implementation

### Project Structure

```
Fog_healthcare/
├── manage.py                      # Django management script
├── requirements.txt               # Python dependencies
├── README.md                      # Project overview
├── .env                          # Environment variables (git-ignored)
│
├── apps/                         # Django applications
│   ├── users/                    # Authentication & RBAC
│   │   ├── models.py             # Custom User model with roles
│   │   ├── views.py              # User endpoints (login, signup)
│   │   ├── serializers.py        # DRF serializers
│   │   ├── constants.py          # UserRole choices
│   │   ├── urls.py               # User API routes
│   │   ├── admin.py              # Django admin interface
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── seed_users.py # Database seeding utility
│   │   └── migrations/
│   │
│   ├── medical_records/          # Record management
│   │   ├── models.py             # MedicalRecord model
│   │   ├── views.py              # REST endpoints
│   │   ├── serializers.py        # Request/response serializers
│   │   ├── services.py           # Business logic layer
│   │   ├── urls.py               # API routes
│   │   ├── admin.py              # Admin interface
│   │   └── migrations/
│   │
│   ├── encryption/               # Cryptography service
│   │   ├── services.py           # HybridEncryptionService
│   │   ├── models.py             # Encryption configs
│   │   ├── apps.py
│   │   └── migrations/
│   │
│   ├── audit/                    # Audit logging
│   │   ├── models.py             # AuditLog model
│   │   ├── services.py           # AuditService
│   │   ├── admin.py              # Admin interface
│   │   └── migrations/
│   │
│   ├── cloud_gateway/            # Cloud integration
│   │   ├── views.py              # Cloud forwarding endpoint
│   │   ├── services.py           # CloudGatewayService
│   │   ├── serializers.py        # Request serializers
│   │   ├── urls.py
│   │   └── models.py
│   │
│   └── dashboard/                # Web UI
│       ├── views.py              # Server-rendered views
│       ├── services/
│       │   └── dashboard_service.py
│       ├── decorators.py         # Role decorators
│       ├── urls.py
│       ├── static/
│       │   └── dashboard/
│       │       └── css/
│       │           └── styles.css
│       └── templates/
│           └── dashboard/
│               ├── base.html
│               ├── home.html
│               ├── login.html
│               ├── records_list.html
│               └── record_detail.html
│
├── common/                       # Shared utilities
│   ├── exceptions.py             # Custom exception definitions
│   ├── permissions.py            # DRF permission classes
│   ├── constants.py              # Platform-wide constants
│   ├── mixins.py                 # Model mixins (BaseModel)
│   └── __init__.py
│
├── config/                       # Django configuration
│   ├── settings/
│   │   ├── base.py              # Base configuration
│   │   ├── dev.py               # Development settings
│   │   ├── prod.py              # Production settings
│   │   └── __init__.py
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py                  # WSGI application
│   ├── asgi.py                  # ASGI application
│   └── __init__.py
│
├── keys/                         # ECC key storage (git-ignored)
│   ├── fog_private_key.pem
│   ├── fog_public_key.pem
│   ├── cloud_private_key.pem
│   └── cloud_public_key.pem
│
├── scripts/                      # Utility scripts
│   ├── generate_keys.py         # ECC key-pair generation
│   └── iot_simulator.py         # IoT device simulator
│
├── logs/                        # Application logs (git-ignored)
└── staticfiles/                 # Collected static files
```

### Framework & Technology Stack

**Backend Framework**:
- Django 5.1: High-level Python web framework with ORM, middleware, and admin interface
- Django REST Framework (DRF): REST API development with serialization and permission classes

**Cryptography**:
- `cryptography` library v43.0+
  - AES-256-CBC for symmetric encryption
  - SECP256R1 for ECC key generation
  - ECDH for shared secret derivation
  - SHA-256 for integrity verification
  - HKDF for key derivation

**Database**:
- MySQL 8.0+ via mysqlclient driver
- Supports transactions with proper isolation levels
- Database indexes on frequently queried fields (patient_id, timestamps)

**Security**:
- Django's built-in CSRF protection
- Session-based authentication
- Password hashing with PBKDF2 (configurable iterations)
- HTTPS/TLS support (production)

**Additional Libraries**:
- `python-dotenv`: Environment variable management
- `requests`: HTTP client for cloud API calls
- `django-ratelimit`: Rate limiting for API endpoints

---

## Cryptographic Security

### Encryption Architecture: Hybrid AES-256 + ECC

The system employs a sophisticated hybrid encryption scheme combining symmetric and asymmetric cryptography:

#### Encryption Workflow (IoT → Fog)

```
Plain Text Patient Data
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 1: Generate Session Key            │
│ • Random 256-bit AES key (os.urandom)   │
│ • Fresh ephemeral ECC key-pair          │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 2: Encrypt with AES-256-CBC        │
│ • Generate random 128-bit IV            │
│ • Apply PKCS7 padding                   │
│ • Cipher: AES-256-CBC(plaintext, IV)    │
│ • Prepend IV to ciphertext              │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 3: Key Wrapping (ECDH + AES-KW)    │
│ • Derive shared secret: ECDH(ephemeral  │
│   private key, recipient public key)    │
│ • HKDF expansion with platform context  │
│ • Wrap AES key with AES-KW algorithm    │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 4: Integrity Verification          │
│ • Compute SHA-256(ciphertext)           │
│ • Hex digest for tamper detection       │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 5: Encoding & Transport            │
│ • Base64 encode all binary artifacts    │
│ • JSON package for REST transmission    │
│ • HTTPS delivery to Fog API             │
└─────────────────────────────────────────┘
        │
        ↓
   Encrypted Payload Stored
```

**Key Components**:

1. **AES-256-CBC** (Symmetric Encryption)
   - Key Size: 256 bits (32 bytes)
   - Block Size: 128 bits (16 bytes)
   - Mode: Cipher Block Chaining (CBC)
   - IV Generation: Fresh random 16 bytes per encryption
   - Padding: PKCS7 (1-16 bytes)
   - Purpose: Bulk data encryption

2. **SECP256R1 (Asymmetric Encryption)**
   - Curve: NIST P-256 (recommended, widely adopted)
   - Key Length: 256 bits
   - Algorithm: ECDH (Elliptic Curve Diffie-Hellman)
   - Purpose: Key wrapping and forward secrecy
   - Freshness: New ephemeral key-pair per encryption

3. **SHA-256 (Integrity)**
   - Hash Size: 256 bits (32 bytes)
   - Algorithm: SHA-2 family
   - Purpose: Tamper detection and verification
   - Hex Output: 64-character string

4. **HKDF** (Key Derivation)
   - Algorithm: HMAC-based Key Derivation Function
   - Context: `b"fog-healthcare-aes-key-wrap"`
   - Purpose: Derive consistent wrapping keys from shared secrets

#### Decryption Workflow (Fog → Database)

```
Encrypted Payload Received
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 1: Base64 Decode                   │
│ • Decode all artifacts from JSON        │
│ • Extract: ciphertext, wrapped key,     │
│   ephemeral public key, integrity hash  │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 2: Verify Integrity                │
│ • Compute SHA-256(ciphertext)           │
│ • Compare with received hash            │
│ • Raise IntegrityVerificationError      │
│   if mismatch (STOP)                    │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 3: Key Unwrapping                  │
│ • Recipient loads their private key     │
│ • Derive shared secret: ECDH(private    │
│   key, sender's ephemeral public key)   │
│ • HKDF expansion matching encryption    │
│ • Unwrap AES key with AES-KW            │
└─────────────────────────────────────────┘
        │
        ↓
┌─────────────────────────────────────────┐
│ Step 4: Decrypt with AES-256-CBC        │
│ • Extract IV from prepended data        │
│ • Decrypt: AES-256-CBC(ciphertext, IV)  │
│ • Remove PKCS7 padding                  │
└─────────────────────────────────────────┘
        │
        ↓
   Plain Text Available in Memory
```

#### Security Properties

**Forward Secrecy**:
- Fresh ephemeral ECC key-pair for every encryption call
- Compromise of one session key does not affect others
- Receiver's private key never used for direct encryption

**Zero-Knowledge**:
- System never stores plaintext data
- Only encrypted payloads and metadata in database
- Decryption keys never logged or exposed

**Tamper Detection**:
- SHA-256 integrity hash prevents data modification
- Automated verification on retrieval
- Detection of truncation, bit-flipping, or corruption

**Key Management**:
- Separate keys for Fog and Cloud nodes
- Keys stored as PEM files outside web root
- PKCS8 format with no password protection (filesystem security assumed)
- Key rotation supported through admin interface

---

## Database Design

### Entity Relationship Diagram

```
                   ┌────────────────┐
                   │     Users      │
                   ├────────────────┤
                   │ id (UUID)      │ ← Primary Key
                   │ username (str) │
                   │ email (str)    │
                   │ password_hash  │
                   │ role (enum)    │
                   │ is_staff (bool)│
                   │ is_superuser   │
                   │ date_joined    │
                   │ is_active (bool)
                   └────────┬───────┘
                            │
                    ┌───────┴───────┐
                    │ created_by    │
                    │ (FK)          │
                    ↓               ↓
         ┌────────────────────┐  ┌──────────────────────┐
         │ Medical Records    │  │  Audit Logs          │
         ├────────────────────┤  ├──────────────────────┤
         │ id (UUID)          │  │ id (UUID)            │
         │ patient_id (UUID)  │  │ user_id (FK)         │
         │ encrypted_payload  │  │ action (enum)        │
         │ encrypted_aes_key  │  │ record_id (UUID)     │
         │ ephemeral_public_  │  │ ip_address (str)     │
         │   key              │  │ details (text)       │
         │ integrity_hash     │  │ timestamp (datetime) │
         │ created_by (FK)    │  └──────────────────────┘
         │ created_at         │
         │ updated_at         │
         │ is_deleted         │
         └────────────────────┘
```

### Schema Details

#### Users Table
```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,  -- UUID
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) UNIQUE,
    password VARCHAR(128) NOT NULL,  -- PBKDF2 hash
    role VARCHAR(10) NOT NULL DEFAULT 'NURSE',  -- ENUM: DOCTOR, NURSE, ADMIN
    is_staff BOOLEAN DEFAULT FALSE,
    is_superuser BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL,
    KEY idx_role (role),
    KEY idx_username (username)
);
```

#### Medical Records Table
```sql
CREATE TABLE medical_records (
    id CHAR(36) PRIMARY KEY,  -- UUID
    patient_id CHAR(36) NOT NULL,  -- Patient identifier
    encrypted_payload LONGTEXT NOT NULL,  -- Base64 AES ciphertext
    encrypted_aes_key LONGTEXT NOT NULL,  -- Base64 wrapped key
    ephemeral_public_key LONGTEXT NOT NULL,  -- Base64 ECC public key
    integrity_hash VARCHAR(64) NOT NULL,  -- SHA-256 hex
    created_by_id CHAR(36) NOT NULL,  -- FK: users.id
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    KEY idx_patient_id (patient_id),
    KEY idx_created_at (created_at),
    KEY idx_created_by (created_by_id),
    FOREIGN KEY (created_by_id) REFERENCES users(id) ON DELETE PROTECT
);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id CHAR(36) PRIMARY KEY,  -- UUID
    user_id CHAR(36),  -- FK: users.id (nullable for system actions)
    action VARCHAR(10) NOT NULL,  -- ENUM: READ, CREATE, UPDATE, DELETE, FORWARD
    record_id CHAR(36),  -- FK: medical_records.id (nullable)
    ip_address VARCHAR(45),  -- Supports IPv4 and IPv6
    details LONGTEXT DEFAULT '',  -- Additional context
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    KEY idx_user_timestamp (user_id, timestamp),
    KEY idx_record_timestamp (record_id, timestamp),
    KEY idx_action (action),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);
```

### Indexing Strategy

**Performance Optimizations**:
1. **Primary Keys**: UUID on all tables for distributed systems
2. **Foreign Keys**: Indexed for join operations
3. **Query Hotspots**:
   - `patient_id` on medical_records (frequent filtering)
   - `created_at` on records and audit logs (date range queries)
   - `user_id` + `timestamp` compound index on audit logs (audit trail queries)
   - `action` on audit logs (filtering by action type)
4. **Uniqueness**: Username unique index on users table

---

## API Documentation

### Authentication Endpoints

#### 1. User Registration
```
POST /api/v1/auth/register/

Request Body:
{
    "username": "doctor_name",
    "password": "SecurePassword123!",
    "email": "doctor@hospital.com",
    "role": "DOCTOR"  # DOCTOR, NURSE, or ADMIN
}

Response (201 Created):
{
    "success": true,
    "message": "User created successfully",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "doctor_name",
        "role": "DOCTOR",
        "date_joined": "2025-05-08T10:30:00Z"
    }
}

Errors:
- 400: Invalid input (username taken, weak password)
- 500: Server error
```

#### 2. User Login
```
POST /api/v1/auth/login/

Request Body:
{
    "username": "doctor_name",
    "password": "SecurePassword123!"
}

Response (200 OK):
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user_id": "550e8400-e29b-41d4-a716-446655440000",
        "username": "doctor_name",
        "role": "DOCTOR",
        "token": "..."  # Session-based
    }
}

Errors:
- 401: Invalid credentials
- 404: User not found
```

### Medical Records Endpoints

#### 3. Create Medical Record (IoT → Fog)
```
POST /api/v1/records/create/

Permission: CanWriteRecords (DOCTOR, ADMIN)

Request Body:
{
    "patient_id": "550e8400-e29b-41d4-a716-446655440001",
    "encrypted_payload": "base64EncodedCiphertext...",
    "encrypted_aes_key": "base64WrappedKey...",
    "ephemeral_public_key": "base64EphemeralPublicKey...",
    "integrity_hash": "sha256HexDigest..."
}

Response (201 Created):
{
    "success": true,
    "message": "Medical record created successfully",
    "data": {
        "id": "660e8400-e29b-41d4-a716-446655440002",
        "patient_id": "550e8400-e29b-41d4-a716-446655440001",
        "created_at": "2025-05-08T10:35:00Z",
        "created_by": "doctor_name"
    }
}

Errors:
- 400: Invalid input or integrity check failed
- 401: Not authenticated
- 403: Insufficient permissions
```

#### 4. Retrieve Medical Record
```
GET /api/v1/records/<record_id>/

Permission: CanReadRecords (DOCTOR, NURSE, ADMIN)

Response (200 OK):
{
    "success": true,
    "data": {
        "id": "660e8400-e29b-41d4-a716-446655440002",
        "patient_id": "550e8400-e29b-41d4-a716-446655440001",
        "encrypted_payload": "base64EncodedCiphertext...",
        "encrypted_aes_key": "base64WrappedKey...",
        "ephemeral_public_key": "base64EphemeralPublicKey...",
        "integrity_hash": "sha256HexDigest...",
        "created_at": "2025-05-08T10:35:00Z",
        "created_by": "doctor_name"
    }
}

Errors:
- 404: Record not found
- 403: Insufficient permissions
```

#### 5. Delete Medical Record (Soft-Delete)
```
DELETE /api/v1/records/<record_id>/

Permission: CanDeleteRecords (ADMIN only)

Response (200 OK):
{
    "success": true,
    "message": "Medical record deleted successfully"
}

Errors:
- 404: Record not found
- 403: Insufficient permissions
```

#### 6. List Patient Records
```
GET /api/v1/records/patient/<patient_id>/?limit=20&offset=0

Permission: CanReadRecords (DOCTOR, NURSE, ADMIN)

Query Parameters:
- patient_id: UUID of the patient
- limit: Number of records (default: 20)
- offset: Pagination offset (default: 0)

Response (200 OK):
{
    "success": true,
    "data": {
        "total": 150,
        "limit": 20,
        "offset": 0,
        "records": [
            {
                "id": "660e8400-e29b-41d4-a716-446655440002",
                "patient_id": "550e8400-e29b-41d4-a716-446655440001",
                "created_at": "2025-05-08T10:35:00Z",
                "created_by": "doctor_name"
            }
        ]
    }
}
```

### Cloud Gateway Endpoints

#### 7. Forward Record to Cloud
```
POST /api/v1/records/forward-to-cloud/

Permission: IsDoctorOrAdmin (DOCTOR, ADMIN)

Request Body:
{
    "record_id": "660e8400-e29b-41d4-a716-446655440002"
}

Process:
1. Decrypt record on Fog using Fog private key
2. Re-encrypt for Cloud using Cloud public key
3. Transmit to Cloud API via HTTPS
4. Retry up to 3 times on transient failures
5. Log action in audit trail

Response (200 OK):
{
    "success": true,
    "message": "Data forwarded to cloud successfully",
    "data": {
        "record_id": "660e8400-e29b-41d4-a716-446655440002",
        "attempts": 1,
        "cloud_status_code": 200
    }
}

Errors:
- 404: Record not found
- 502: Cloud service unavailable
- 500: Encryption error
```

---

## User Authentication & Authorization

### Role-Based Access Control (RBAC)

The system implements four distinct user roles with hierarchical permissions:

#### Role Hierarchy

```
                    ┌──────────────┐
                    │    ADMIN     │  (Superuser)
                    │ All access   │
                    └──────────────┘
                           ▲
                    ┌──────┴──────┐
            ┌───────┴────────┐  ┌────────────┐
            │    DOCTOR      │  │   NURSE    │
            │ • Read Records │  │ • Read     │
            │ • Write        │  │   Records  │
            │ • Forward Cloud│  │            │
            └───────┬────────┘  └────────────┘
                    │
                    ▼
            ┌──────────────┐
            │   PATIENT    │
            │ • View own   │
            │   data       │
            └──────────────┘
```

#### Permission Matrix

| Action | ADMIN | DOCTOR | NURSE | PATIENT |
|--------|-------|--------|-------|---------|
| View Records | ✓ | ✓ | ✓ | ✓ (own) |
| Create Records | ✓ | ✓ | ✗ | ✗ |
| Update Records | ✓ | ✓ | ✗ | ✗ |
| Delete Records | ✓ | ✗ | ✗ | ✗ |
| Forward to Cloud | ✓ | ✓ | ✗ | ✗ |
| View Audit Logs | ✓ | ✗ | ✗ | ✗ |
| Manage Users | ✓ | ✗ | ✗ | ✗ |

#### DRF Permission Classes

**Base Permissions** (`common/permissions.py`):
```python
class IsAdmin(BasePermission):
    """Allow only ADMIN role users."""

class IsDoctor(BasePermission):
    """Allow only DOCTOR role users."""

class IsNurse(BasePermission):
    """Allow only NURSE role users."""

class IsDoctorOrAdmin(BasePermission):
    """Allow DOCTOR or ADMIN roles."""

class CanReadRecords(BasePermission):
    """DOCTOR, NURSE, ADMIN may read records."""

class CanWriteRecords(BasePermission):
    """DOCTOR, ADMIN may create/update records."""

class CanDeleteRecords(BasePermission):
    """ADMIN only may delete records."""
```

**Implementation Example**:
```python
class RecordCreateView(APIView):
    permission_classes = [CanWriteRecords]  # Enforces DOCTOR or ADMIN
    
    def post(self, request):
        # Automatically checks permission before reaching this method
        # If user lacks permission, returns 403 Forbidden
        ...
```

### Custom User Model

```python
class User(AbstractUser):
    """Custom user with UUID primary key and role field."""
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    role = models.CharField(
        max_length=10,
        choices=UserRole.choices,
        default=UserRole.NURSE,
        db_index=True,
    )
    
    # Helper properties
    @property
    def is_doctor(self) -> bool:
        return self.role == UserRole.DOCTOR
    
    @property
    def is_nurse(self) -> bool:
        return self.role == UserRole.NURSE
    
    @property
    def is_admin_role(self) -> bool:
        return self.role == UserRole.ADMIN
```

### Password Security

**Django's PBKDF2 Implementation**:
- **Algorithm**: PBKDF2 with SHA256
- **Iterations**: 720,000 (Django 5.1+ default)
- **Salt Length**: 128 bits (randomly generated per user)
- **Format**: `pbkdf2_sha256$iterations$salt$hash`

**Password Validators**:
1. `UserAttributeSimilarityValidator`: Prevents password from containing username/email
2. `MinimumLengthValidator`: Enforces 8+ character minimum
3. `CommonPasswordValidator`: Blocks 20,000+ common passwords
4. `NumericPasswordValidator`: Prevents all-numeric passwords

---

## Audit & Compliance Framework

### Audit Trail System

Every data access and modification is logged immutably in the `audit_logs` table:

#### Audit Actions

```python
class AuditAction:
    READ = "READ"        # Record accessed
    CREATE = "CREATE"    # Record created
    UPDATE = "UPDATE"    # Record modified
    DELETE = "DELETE"    # Record deleted
    FORWARD = "FORWARD"  # Record forwarded to cloud
```

#### Audit Log Entry

```python
@dataclass
class AuditLogEntry:
    user: User                  # Who performed the action
    action: str                 # Action type
    record_id: UUID            # Affected record
    ip_address: str            # Client IP
    timestamp: datetime        # When it happened
    details: str              # Additional context
```

#### Sample Audit Trail Query

```python
# Get all records accessed by a specific user
AuditLog.objects.filter(
    user=doctor,
    action=AuditAction.READ
).order_by('-timestamp')[:100]

# Get all records modified in the last 30 days
from datetime import timedelta
from django.utils import timezone

AuditLog.objects.filter(
    action__in=[AuditAction.CREATE, AuditAction.UPDATE],
    timestamp__gte=timezone.now() - timedelta(days=30)
).order_by('-timestamp')

# Find suspicious activity (multiple failed forward attempts)
AuditLog.objects.filter(
    action=AuditAction.FORWARD,
    details__contains='FAILED'
).count()
```

### HIPAA Compliance Features

**HIPAA Security Rule Requirements Addressed**:

1. **Access Controls**
   - Role-based permission enforcement
   - User authentication via session-based auth
   - Audit logging of all access

2. **Audit Controls**
   - Comprehensive audit trails (`audit_logs` table)
   - Integrity logging (SHA-256 hashes)
   - User accountability (all actions attributed to user + IP)

3. **Integrity Controls**
   - SHA-256 integrity verification
   - Detection of data tampering
   - Immutable audit logs (PROTECT constraint)

4. **Transmission Security**
   - HTTPS/TLS for all API communication
   - Encryption in transit (IPsec/TLS recommended)
   - Encrypted at rest (encrypted_payload in database)

5. **Encryption and Decryption**
   - AES-256-CBC symmetric encryption
   - SECP256R1 ECC for key wrapping
   - Zero-knowledge design (plaintext never stored)

### Data Retention & Deletion

**Soft Delete Policy**:
- Records not permanently deleted
- `is_deleted` flag prevents retrieval
- Audit logs preserved for 7+ years (configurable)
- Enables compliance audits and forensics

**Implementation**:
```python
class MedicalRecord(BaseModel):
    is_deleted = models.BooleanField(default=False)

# Soft delete
record.is_deleted = True
record.save()

# Query excludes deleted records
MedicalRecord.objects.filter(is_deleted=False)

# But audit trail remains
AuditLog.objects.filter(record_id=record.pk)  # Still accessible
```

---

## Deployment & Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# Django Core
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=fog_healthcare
DB_USER=root
DB_PASSWORD=YourSecurePassword123!
DB_HOST=127.0.0.1
DB_PORT=3306

# Encryption Keys
FOG_ECC_PRIVATE_KEY_PATH=/path/to/keys/fog_private_key.pem
FOG_ECC_PUBLIC_KEY_PATH=/path/to/keys/fog_public_key.pem
CLOUD_ECC_PRIVATE_KEY_PATH=/path/to/keys/cloud_private_key.pem
CLOUD_ECC_PUBLIC_KEY_PATH=/path/to/keys/cloud_public_key.pem

# Cloud Gateway
CLOUD_API_URL=https://cloud.healthcare-provider.com/api/v1/records/
CLOUD_API_TIMEOUT=30
CLOUD_API_MAX_RETRIES=3

# Email (for notifications)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_FILE_PATH=./logs/app.log
```

### Production Configuration

**Security Checklist**:

```yaml
Web Server:
  - Use Gunicorn or uWSGI
  - Deploy behind Nginx/Apache reverse proxy
  - Enable HTTP/2 and HTTPS/TLS
  - Configure SSL certificates (Let's Encrypt recommended)

Database:
  - Use managed MySQL service (AWS RDS, Google Cloud SQL)
  - Enable encryption at rest
  - Regular automated backups
  - Restrict network access (VPC/security groups)

Application:
  - DEBUG = False
  - Set strong SECRET_KEY (256+ bits)
  - Use environment variables for secrets
  - Enable CSRF and security headers
  - Configure ALLOWED_HOSTS properly
  - Use django-ratelimit for API protection

Monitoring:
  - Application error logging (Sentry recommended)
  - Database query monitoring
  - Uptime monitoring
  - Security event alerts

Keys & Secrets:
  - Store keys outside web root
  - Use hardware security modules (HSM) for production
  - Regular key rotation (annual minimum)
  - Never commit keys to version control

Audit:
  - Enable MySQL binlog for audit trail
  - Log all admin actions
  - Regular audit log reviews
  - Archive logs off-server
```

---

## Installation & Setup

### Prerequisites

- Python 3.11 or higher
- MySQL 8.0 or higher
- pip (Python package manager)
- virtualenv (recommended)

### Step-by-Step Installation

#### 1. Clone Repository
```bash
git clone https://github.com/yourusername/fog-healthcare.git
cd fog_healthcare
```

#### 2. Create Virtual Environment
```bash
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

#### 5. Generate Encryption Keys
```bash
python scripts/generate_keys.py
```

Creates:
- `keys/fog_private_key.pem` and `keys/fog_public_key.pem`
- `keys/cloud_private_key.pem` and `keys/cloud_public_key.pem`

#### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### 7. Create Superuser
```bash
python manage.py createsuperuser
# Follow prompts to create admin user
```

#### 8. Seed Test Users (Optional)
```bash
python manage.py seed_users
```

Creates test users:
- `doctor1` / `doctor1pass` (DOCTOR role)
- `nurse1` / `nurse1pass` (NURSE role)
- `admin1` / `admin1pass` (ADMIN role)

#### 9. Run Development Server
```bash
python manage.py runserver
```

Access:
- Web Dashboard: http://localhost:8000/
- Admin Interface: http://localhost:8000/admin/
- API: http://localhost:8000/api/v1/

#### 10. Run IoT Simulator (Optional, in new terminal)
```bash
python scripts/iot_simulator.py
```

### Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.encryption

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

### Deployment with Gunicorn

```bash
pip install gunicorn

# Run production server
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class sync \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

---

## Future Enhancements

### Phase 2 Features

1. **Multi-Cloud Support**
   - Support multiple cloud providers
   - Data replication across clouds
   - Cloud-to-cloud synchronization

2. **Advanced Analytics**
   - Trend analysis on encrypted data (homomorphic encryption)
   - Anomaly detection
   - Real-time dashboards with charts

3. **Mobile Applications**
   - Native iOS app for clinicians
   - Native Android app for patients
   - End-to-end encryption on mobile

4. **Blockchain Integration**
   - Immutable audit trail on blockchain
   - Smart contracts for access control
   - Decentralized identity management

5. **Machine Learning**
   - Pattern recognition on encrypted data
   - Predictive analytics
   - Federated learning across institutions

6. **Enhanced RBAC**
   - Attribute-Based Access Control (ABAC)
   - Fine-grained patient consent management
   - Delegation of access rights

7. **Performance Optimization**
   - Redis caching for frequently accessed records
   - Database query optimization
   - API rate limiting per role

8. **Interoperability**
   - HL7/FHIR standards compliance
   - Integration with electronic health record (EHR) systems
   - API versioning strategy

### Research Opportunities

1. **Cryptographic Research**
   - Evaluate post-quantum cryptography (CRYSTALS-Kyber)
   - Implement searchable encryption for encrypted records
   - Zero-knowledge proofs for privacy-preserving queries

2. **Security Analysis**
   - Formal verification of encryption protocol
   - Penetration testing and threat modeling
   - Side-channel attack analysis

3. **Performance Studies**
   - Benchmark encryption/decryption throughput
   - Analyze network latency impact
   - Study database query performance at scale

4. **User Experience**
   - Usability testing of dashboard and API
   - User feedback collection
   - Accessibility compliance (WCAG 2.1)

---

## Conclusion

The **Secure Fog-Based Healthcare Data Sharing System** demonstrates a production-ready approach to distributed healthcare data management combining:

- **Advanced Cryptography**: Hybrid AES-256 + ECC encryption with zero-knowledge design
- **Robust Architecture**: Microservices-inspired design with clear separation of concerns
- **Security Best Practices**: RBAC, audit logging, integrity verification, and compliance
- **Scalability**: Distributed fog computing model with optional cloud integration
- **Compliance**: HIPAA-aligned audit trails and data governance

The system is designed for academic study and production deployment in healthcare environments prioritizing patient privacy, data security, and regulatory compliance.

---

## References & Standards

**Cryptographic Standards**:
- NIST SP 800-38D: GCMI and Other Authenticated Encryption Modes
- FIPS 197: Advanced Encryption Standard (AES)
- FIPS 186-4: Digital Signature Standard (DSS)
- SEC 2: Recommended Elliptic Curve Domain Parameters

**Healthcare Standards**:
- HIPAA: Health Insurance Portability and Accountability Act
- HL7: Health Level 7 (medical data exchange standard)
- FHIR: Fast Healthcare Interoperability Resources

**Security & Privacy**:
- OWASP Top 10: Web Application Security Risks
- CWE: Common Weakness Enumeration
- CVSS: Common Vulnerability Scoring System

**Django & Python**:
- Django Documentation: https://docs.djangoproject.com/
- Django REST Framework: https://www.django-rest-framework.org/
- Python cryptography: https://cryptography.io/

---

**Document Version**: 1.0  
**Last Updated**: May 8, 2025  
**Author**: Development Team  
**Status**: Academic & Production Ready
