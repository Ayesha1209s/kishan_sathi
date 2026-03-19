# 🌱 Kishan Sathi — AI Crop Disease Detection Backend

Production-ready Django REST API backend for AI-powered crop disease detection.

---

## 📁 Project Structure

```
kishan_sathi/
├── kishan_sathi/           # Django project config
│   ├── settings.py         # All settings (PostgreSQL, JWT, AI, Email)
│   ├── urls.py             # Root URL router
│   └── wsgi.py
│
├── apps/
│   ├── accounts/           # Auth, User, Profile
│   │   ├── models.py       # User (AbstractUser), Profile, UserActivity
│   │   ├── serializers.py  # Registration, Login, Profile, Password
│   │   ├── views.py        # Register, Login, Logout, Profile, Dashboard
│   │   └── urls.py
│   │
│   ├── analysis/           # Core AI feature
│   │   ├── models.py       # CropImage, AnalysisResult, Disease
│   │   ├── ai_service.py   # AI model interface (Placeholder + TF)
│   │   ├── serializers.py  # Upload, Result, History, Analytics
│   │   ├── views.py        # Upload, Analyze, History, Analytics
│   │   └── urls.py
│   │
│   ├── reports/            # PDF generation
│   │   ├── models.py       # Report model
│   │   ├── pdf_generator.py# ReportLab PDF builder
│   │   ├── views.py        # Generate & Download PDFs
│   │   └── urls.py
│   │
│   └── notifications/      # In-app notifications
│       ├── models.py       # Notification model
│       ├── utils.py        # create_notification() helper
│       ├── views.py        # List, Mark-read, Delete
│       └── urls.py
│
├── media/                  # Uploaded files (git-ignored)
├── logs/                   # Log files (git-ignored)
├── requirements.txt
├── .env.example
├── manage.py
└── Kishan_Sathi_API.postman_collection.json
```

---

## ⚡ Quick Start

### 1. Clone & Virtual Environment
```bash
git clone <repo>
cd kishan_sathi
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your PostgreSQL credentials and secret key
```

### 4. Create PostgreSQL Database
```sql
psql -U postgres
CREATE DATABASE kishan_sathi_db;
\q
```

### 5. Run Migrations
```bash
python manage.py makemigrations accounts analysis reports notifications
python manage.py migrate
```

### 6. Create Superuser
```bash
python manage.py createsuperuser
```

### 7. Create Media & Log Directories
```bash
mkdir -p media logs
```

### 8. Run Development Server
```bash
python manage.py runserver
```

Server runs at: **http://localhost:8000**
Admin panel: **http://localhost:8000/admin/**

---

## 🌐 Complete API Reference

### Base URL: `http://localhost:8000/api/v1`
### Auth Header: `Authorization: Bearer <access_token>`

---

### 🔐 Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register/` | ❌ | Register new user, returns JWT tokens |
| POST | `/auth/login/` | ❌ | Login, returns JWT access + refresh |
| POST | `/auth/logout/` | ✅ | Blacklist refresh token |
| POST | `/auth/token/refresh/` | ❌ | Get new access token |
| POST | `/auth/change-password/` | ✅ | Change password |

**Register Request:**
```json
{
  "username": "ramesh_patel",
  "email": "ramesh@example.com",
  "first_name": "Ramesh",
  "last_name": "Patel",
  "phone": "+919876543210",
  "state": "Odisha",
  "password": "SecurePass@123",
  "confirm_password": "SecurePass@123"
}
```

**Login Response:**
```json
{
  "access": "eyJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 1,
    "email": "ramesh@example.com",
    "full_name": "Ramesh Patel",
    "total_analyses": 12
  }
}
```

---

### 👤 Profile

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/auth/profile/` | ✅ | Get full profile |
| PATCH | `/auth/profile/` | ✅ | Update profile fields |
| POST | `/auth/profile/image/` | ✅ | Upload profile photo |
| GET | `/auth/dashboard/` | ✅ | Dashboard stats + recent activity |
| GET | `/auth/activity/` | ✅ | Login/logout history |

---

### 📷 Analysis

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/analysis/upload-analyze/` | ✅ | **Upload + AI in one step** (recommended) |
| POST | `/analysis/upload/` | ✅ | Upload image only |
| POST | `/analysis/analyze/<id>/` | ✅ | Run AI on uploaded image |
| GET | `/analysis/history/` | ✅ | Paginated history with filters |
| GET | `/analysis/history/<id>/` | ✅ | Single analysis detail |
| DELETE | `/analysis/history/<id>/` | ✅ | Delete a record |
| GET | `/analysis/analytics/?period=30` | ✅ | Dashboard chart data |
| GET | `/analysis/diseases/` | ❌ | Public disease library |

**Upload + Analyze (multipart/form-data):**
```
image:     <file>
crop_type: wheat
notes:     Orange patches on leaves
```

**Analysis Result Response:**
```json
{
  "result": {
    "disease_name": "Wheat Leaf Rust",
    "scientific_name": "Puccinia triticina",
    "confidence_score": 94.2,
    "is_healthy": false,
    "severity": "high",
    "description": "...",
    "symptoms": "...",
    "chemical_treatment": "Propiconazole 25% EC...",
    "organic_treatment": "Neem oil spray...",
    "alternative_predictions": [
      {"disease": "Powdery Mildew", "confidence": 3.1}
    ],
    "model_version": "v1.0-placeholder",
    "analyzed_at": "2024-03-18T14:30:00Z"
  }
}
```

**History Filters (query params):**
```
?crop_type=wheat
?is_healthy=false
?search=rust
?uploaded_after=2024-01-01
?uploaded_before=2024-12-31
?min_confidence=80
?ordering=-uploaded_at
?page=2
```

---

### 📄 Reports

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/reports/generate/<image_id>/` | ✅ | Generate single PDF |
| POST | `/reports/generate-summary/?period=30` | ✅ | Generate summary PDF |
| GET | `/reports/download/<report_id>/` | ✅ | Download PDF file |
| GET | `/reports/` | ✅ | List generated reports |

---

### 🔔 Notifications

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/notifications/` | ✅ | List all + unread_count |
| GET | `/notifications/unread-count/` | ✅ | Just the count |
| POST | `/notifications/mark-all-read/` | ✅ | Mark all as read |
| PATCH | `/notifications/<id>/read/` | ✅ | Mark one as read |
| DELETE | `/notifications/<id>/delete/` | ✅ | Delete one |

---

## 🧠 AI Model Integration

The AI system uses a **pluggable adapter pattern** (`apps/analysis/ai_service.py`).

### Current Mode: Placeholder (no ML dependencies)
Returns realistic disease predictions for development/testing.

### Switch to TensorFlow:
1. Install: `pip install tensorflow Pillow numpy`
2. Place model at path set in `.env`: `AI_MODEL_PATH=ai_models/model.h5`
3. Set in `.env`: `AI_MODEL_TYPE=tensorflow`

### Add Your Own Model:
```python
# In ai_service.py
class MyCustomModel(BaseCropDiseaseModel):
    def predict(self, image_path: str) -> dict:
        # Your inference code here
        return {
            "disease_name": "...",
            "confidence_score": 94.0,
            "is_healthy": False,
            # ... all required fields
        }

# Register in ModelFactory.get_model():
if model_type == 'custom':
    cls._instance = MyCustomModel()
```

---

## 🗄️ Database Schema

```
users               → Custom AbstractUser (email login)
user_profiles       → Extended profile (bio, farm_size, crops)
user_activities     → Login/logout audit trail

crop_images         → Uploaded crop photos (UUID PK)
analysis_results    → AI prediction output (1:1 with crop_image)
diseases            → Disease reference library

reports             → Generated PDF metadata
notifications       → In-app notification store
```

---

## 🔐 Security Features

- **JWT Authentication** – Short-lived access tokens (60 min), 7-day refresh
- **Token Blacklisting** – Logout invalidates refresh tokens
- **File Validation** – Type, extension, and size checks on upload
- **Ownership Checks** – All queries filtered by `user=request.user`
- **Rate Limiting** – 100/day anon, 1000/day authenticated
- **CORS** – Configurable allowed origins
- **Password Validation** – Django built-in validators enforced

---

## 📧 Email Setup (Gmail)

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your@gmail.com
EMAIL_HOST_PASSWORD=your-app-password  # Gmail App Password, not account password
```

---

## ☁️ Cloudinary Setup (Optional)

```env
USE_CLOUDINARY=True
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

---

## 🚀 Production Deployment

```bash
# Set in .env
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Collect static files
python manage.py collectstatic

# Run with Gunicorn
gunicorn kishan_sathi.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120
```

---

## 🧪 Running Tests

```bash
pytest
pytest apps/accounts/tests.py -v
pytest apps/analysis/tests.py -v
```

---

## 📬 Postman Collection

Import `Kishan_Sathi_API.postman_collection.json` into Postman.

1. Run **Register** → creates user
2. Run **Login** → auto-sets `{{access_token}}`
3. Run **Upload + Analyze** → auto-sets `{{image_id}}`
4. Run **Generate PDF** → auto-sets `{{report_id}}`
5. Run **Download PDF** → saves PDF

---

*Built with ❤️ for Indian farmers | Kishan Sathi 2024*
