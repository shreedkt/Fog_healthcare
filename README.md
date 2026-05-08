# Secure Fog-Based Healthcare Data Sharing System

A Django-powered healthcare platform that securely manages and shares medical records using hybrid encryption (AES-256 + ECC) and fog computing architecture. Designed for distributed IoT healthcare networks with zero-knowledge principles—plaintext data is never stored.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![Django](https://img.shields.io/badge/Django-5.1+-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

---

## Key Features

- **Hybrid Encryption**: AES-256-CBC + SECP256R1 (ECC) + SHA-256 integrity verification
- **Fog Computing**: Distributed architecture with cloud gateway integration
- **Role-Based Access Control**: Nurse, Doctor, Administrator, and Patient roles
- **Medical Records Management**: Secure storage and retrieval of encrypted patient data
- **Dashboard**: Real-time monitoring and analytics interface
- **Audit Logging**: Complete audit trail of all data access and modifications
- **REST API**: Full-featured DRF API for healthcare integrations
- **Rate Limiting**: Built-in protection against abuse
- **IoT Support**: Native support for IoT device data ingestion

---

## Architecture Overview

### System Components

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────┐
│  IoT Devices    │────▶│   Fog Node       │────▶│   Cloud     │
│  (Encrypted)    │     │   (Encryption)   │     │   Gateway   │
└─────────────────┘     └──────────────────┘     └─────────────┘
                               │
                               ▼
                        ┌──────────────────┐
                        │  Django Backend  │
                        │  • Users         │
                        │  • Records       │
                        │  • Audit Log     │
                        │  • Dashboard     │
                        └──────────────────┘
```

### Data Flow

1. **Encryption (IoT → Fog)**
   - Generate random AES-256 session key
   - Encrypt payload with AES-256-CBC (IV prepended)
   - Wrap AES key using ECDH + recipient's public key
   - Compute SHA-256 integrity hash
   - Base64 encode for JSON transport

2. **Storage (Fog → Database)**
   - Store encrypted payload, wrapped key, ephemeral public key
   - Maintain audit trail
   - Never store plaintext

3. **Decryption (On Demand)**
   - Re-derive shared secret using recipient's private key
   - Unwrap AES session key
   - Decrypt ciphertext
   - Verify SHA-256 hash

---

## Project Structure

```
Fog_healthcare/
├── apps/                              # Django applications
│   ├── users/                         # User authentication & roles
│   │   ├── models.py                  # Custom User model
│   │   ├── views.py                   # User endpoints
│   │   ├── serializers.py             # DRF serializers
│   │   └── management/
│   │       └── commands/
│   │           └── seed_users.py      # Database seeding
│   │
│   ├── medical_records/               # Medical records management
│   │   ├── models.py                  # MedicalRecord model
│   │   ├── services.py                # Business logic
│   │   ├── views.py                   # REST endpoints
│   │   └── serializers.py             # DTO serialization
│   │
│   ├── encryption/                    # Hybrid encryption service
│   │   ├── models.py                  # Encryption config/keys
│   │   ├── services.py                # AES-256 + ECC + SHA-256
│   │   └── apps.py
│   │
│   ├── audit/                         # Audit logging
│   │   ├── models.py                  # AuditLog model
│   │   └── services.py                # Audit trail recording
│   │
│   ├── dashboard/                     # Web dashboard
│   │   ├── views.py                   # Dashboard rendering
│   │   ├── services/                  # Business logic
│   │   ├── templates/
│   │   │   └── dashboard/
│   │   │       ├── base.html
│   │   │       ├── home.html
│   │   │       ├── login.html
│   │   │       ├── records_list.html
│   │   │       └── record_detail.html
│   │   └── static/
│   │       └── dashboard/
│   │           └── css/
│   │               └── styles.css
│   │
│   └── cloud_gateway/                 # Cloud integration
│       ├── models.py
│       ├── services.py                # Cloud sync logic
│       └── views.py
│
├── common/                            # Shared utilities
│   ├── constants.py                   # Project-wide constants
│   ├── exceptions.py                  # Custom exceptions
│   ├── mixins.py                      # Base model mixins
│   └── permissions.py                 # DRF permission classes
│
├── config/                            # Django configuration
│   ├── settings/
│   │   ├── base.py                    # Common settings
│   │   ├── dev.py                     # Development settings
│   │   └── prod.py                    # Production settings
│   ├── urls.py                        # Root URL router
│   ├── asgi.py                        # ASGI config
│   └── wsgi.py                        # WSGI config
│
├── keys/                              # Encryption keys storage (gitignored)
├── logs/                              # Application logs
├── scripts/                           # Utility scripts
│   ├── generate_keys.py               # Generate ECC keypairs
│   └── iot_simulator.py               # Simulate IoT devices
│
├── manage.py                          # Django management command
├── requirements.txt                   # Python dependencies
└── README.md                          # This file
```

---

## Quick Start

### Prerequisites

- **Python** 3.11+
- **MySQL** 8.0+
- **pip** (or poetry)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/fog-healthcare.git
   cd fog-healthcare
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Generate encryption keys**
   ```bash
   python scripts/generate_keys.py
   ```

6. **Run migrations**
   ```bash
   python manage.py migrate
   ```

7. **Seed sample data** (optional)
   ```bash
   python manage.py seed_users
   ```

8. **Start development server**
   ```bash
   python manage.py runserver
   ```

   Access at `http://localhost:8000`

---

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.mysql
DB_NAME=fog_healthcare
DB_USER=root
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=3306

# Encryption
ENCRYPTION_KEY_PATH=./keys/private_key.pem
PUBLIC_KEY_PATH=./keys/public_key.pem

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Cloud Gateway
CLOUD_GATEWAY_URL=https://api.cloud-gateway.com
CLOUD_GATEWAY_API_KEY=your-api-key

# Security
CSRF_TRUSTED_ORIGINS=http://localhost:8000
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
```

### Settings Profiles

- **Development**: `python manage.py runserver --settings=config.settings.dev`
- **Production**: `gunicorn config.wsgi --settings=config.settings.prod`

---

## API Documentation

### Authentication

All endpoints require Bearer token authentication:

```bash
Authorization: Bearer <token>
```

### Core Endpoints

#### Users
- `POST /api/users/register/` - Register new user
- `POST /api/users/login/` - Login and get token
- `GET /api/users/profile/` - Get current user profile
- `PUT /api/users/profile/` - Update profile

#### Medical Records
- `GET /api/records/` - List records (paginated)
- `POST /api/records/` - Create encrypted record
- `GET /api/records/{id}/` - Retrieve record (auto-decrypt)
- `PUT /api/records/{id}/` - Update record
- `DELETE /api/records/{id}/` - Delete record

#### Audit Logs
- `GET /api/audit/` - View audit trail (admin only)
- `GET /api/audit/{id}/` - View specific log entry

### Example Request

```bash
# Create encrypted medical record
curl -X POST http://localhost:8000/api/records/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "550e8400-e29b-41d4-a716-446655440000",
    "plaintext_payload": "Patient vitals: BP 120/80, HR 72",
    "data_type": "vital_signs"
  }'
```

---

## Security Features

### Encryption Details

**Algorithm**: Hybrid Encryption (AES-256-CBC + ECC SECP256R1)

| Component | Algorithm | Details |
|-----------|-----------|---------|
| Data Encryption | AES-256-CBC | 256-bit key, random IV |
| Key Encryption | ECC SECP256R1 | Via ECDH key agreement |
| Key Wrapping | AES-KW | RFC 3394 compliant |
| Integrity | SHA-256 | Tamper detection hash |
| Random Source | os.urandom() | CSPRNG |

### Security Principles

- **Zero-Knowledge**: Plaintext never stored on server
- **Forward Secrecy**: Ephemeral keys for each encryption
- **Integrity Verification**: SHA-256 hash validation
- **Role-Based Access**: Granular permission control
- **Audit Trail**: Complete logging of all access
- **Rate Limiting**: Protection against brute force
- **HTTPS Enforced**: Production environment only

---

## Testing

### Run Tests
```bash
python manage.py test
```

### Run Specific Test Suite
```bash
python manage.py test apps.encryption
python manage.py test apps.medical_records
python manage.py test apps.users
```

### Test Coverage
```bash
coverage run --source='.' manage.py test
coverage report
coverage html
```

---

## Database Schema

### Key Models

**User**
- UUID id (primary key)
- username (unique)
- email
- role (nurse, doctor, admin, patient)
- created_at, updated_at

**MedicalRecord**
- UUID id (primary key)
- patient_id (UUID)
- encrypted_payload (base64)
- encrypted_aes_key (base64)
- ephemeral_public_key (base64)
- integrity_hash (SHA-256)
- created_by (FK: User)
- created_at, updated_at

**AuditLog**
- id (auto-increment)
- user (FK: User)
- action (create, read, update, delete)
- resource_type (medical_record, user, etc.)
- resource_id (UUID)
- timestamp
- ip_address
- details (JSON)

---

## Development Workflow

### Create a New Feature

1. **Create branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Add feature to app**
   ```bash
   python manage.py startapp feature_name
   ```

3. **Make migrations** (if models changed)
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Run tests**
   ```bash
   python manage.py test
   ```

5. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use [Black](https://github.com/psf/black) for formatting
- Use [isort](https://pycqa.github.io/isort/) for import sorting
- Use [flake8](https://flake8.pycqa.org/) for linting

```bash
black .
isort .
flake8 .
```

---

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| Django | 5.1+ | Web framework |
| djangorestframework | 3.15+ | REST API |
| cryptography | 43.0+ | Encryption library |
| mysqlclient | 2.2+ | MySQL driver |
| python-dotenv | 1.0+ | Environment management |
| requests | 2.32+ | HTTP client |
| django-ratelimit | 4.1+ | Rate limiting |

---

## Deployment

### Production Checklist

- [ ] Set `DEBUG=False` in production settings
- [ ] Generate strong `DJANGO_SECRET_KEY`
- [ ] Configure allowed hosts
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Enable rate limiting
- [ ] Run `python manage.py collectstatic`
- [ ] Configure gunicorn/uWSGI
- [ ] Set up reverse proxy (Nginx)

### Deploy with Docker

```bash
docker build -t fog-healthcare .
docker run -p 8000:8000 fog-healthcare
```

---

## Scripts

### Generate Encryption Keys
```bash
python scripts/generate_keys.py
```
Generates RSA keypair for encryption operations.

### IoT Device Simulator
```bash
python scripts/iot_simulator.py --devices 5 --records 100
```
Simulates IoT devices sending encrypted medical records.

### Seed Database
```bash
python manage.py seed_users
```
Populates database with sample users and roles.

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

### Code Review Criteria

- Tests included and passing
- Documentation updated
- Follows PEP 8 style guide
- No security vulnerabilities
- Performance optimized

---

## Roadmap

- [ ] **v2.0**: Multi-tenant support
- [ ] **v2.1**: GraphQL API
- [ ] **v2.2**: Machine learning analytics
- [ ] **v3.0**: Blockchain audit trail
- [ ] **v3.1**: Mobile app (iOS/Android)
- [ ] **v3.2**: Real-time collaboration

---

## Known Issues & Limitations

- MySQL 8.0+ required (strict mode)
- Large file uploads (>100MB) may require config tuning
- Rate limiting based on IP address (consider reverse proxy setup)
- Encryption keys must be rotated every 90 days

---

## Support & Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/fog-healthcare/issues)
- **Email**: support@fog-healthcare.dev
- **Documentation**: [Wiki](https://github.com/yourusername/fog-healthcare/wiki)

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Authors

- **Your Name** - _Initial work_ - [GitHub](https://github.com/yourusername)

---

## Acknowledgments

- Django community for excellent framework
- Cryptography library maintainers
- Healthcare data security best practices
- Contributors and testers

---

**Made for secure healthcare data sharing**
