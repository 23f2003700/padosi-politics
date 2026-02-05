# 🏠 Padosi Politics - Society Complaint Management System

> A comprehensive web application for managing apartment/society complaints, built for IIT Madras BS Program.
> 
> **Student:** Aaryan (23F2003700)

## 📋 Overview

Padosi Politics is a full-stack web application that helps residential societies manage complaints efficiently. It features a robust Flask backend with a modern Vue.js frontend, complete with user authentication, role-based access control, karma system, and automated escalation.

## 🏗️ Architecture

```
padosi-politics/
├── backend/                 # Flask REST API
│   ├── app/
│   │   ├── api/            # API blueprints
│   │   ├── models/         # SQLAlchemy models
│   │   ├── tasks/          # Celery background tasks
│   │   └── utils/          # Helpers, decorators, validators
│   ├── config.py           # Configuration management
│   ├── run.py              # Application entry point
│   ├── seed_db.py          # Database seeder
│   └── requirements.txt    # Python dependencies
│
└── frontend/               # Vue.js SPA
    ├── src/
    │   ├── layouts/        # Page layouts
    │   ├── pages/          # Vue page components
    │   ├── stores/         # Pinia state management
    │   ├── services/       # API service layer
    │   └── router/         # Vue Router configuration
    └── package.json        # Node.js dependencies
```

## 🚀 Features

### Core Features
- ✅ **User Authentication** - Register, login, logout with JWT tokens
- ✅ **Role-Based Access Control** - Admin, Secretary, Committee Member, Resident
- ✅ **Complaint Management** - Create, view, update, delete complaints
- ✅ **File Uploads** - Attach evidence (images, documents) to complaints
- ✅ **Voting System** - Upvote important complaints
- ✅ **Comments** - Discuss complaints with threaded comments
- ✅ **Karma System** - Earn points for contributions
- ✅ **Notifications** - Real-time notification system
- ✅ **Auto-Escalation** - Automatic escalation of unresolved complaints
- ✅ **Dashboard** - Statistics and analytics

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | User login |
| GET | `/api/auth/me` | Get current user profile |
| GET | `/api/complaints` | List all complaints |
| POST | `/api/complaints` | Create new complaint |
| GET | `/api/complaints/:id` | Get complaint details |
| PATCH | `/api/complaints/:id` | Update complaint |
| DELETE | `/api/complaints/:id` | Delete complaint |
| POST | `/api/complaints/:id/vote` | Vote on complaint |
| POST | `/api/complaints/:id/comments` | Add comment |
| GET | `/api/karma/leaderboard` | Get karma leaderboard |
| GET | `/api/dashboard/stats` | Get dashboard statistics |

## 🛠️ Tech Stack

### Backend
- **Flask 3.0** - Web framework
- **SQLAlchemy 2.0** - ORM
- **Flask-Security-Too** - Authentication
- **Flask-JWT-Extended** - JWT token management
- **Marshmallow** - Serialization/validation
- **Celery** - Background task processing
- **Redis** - Task queue broker (optional)
- **SQLite/PostgreSQL** - Database

### Frontend
- **Vue 3** - Frontend framework
- **Pinia** - State management
- **Vue Router** - Client-side routing
- **Axios** - HTTP client
- **Tailwind CSS** - Styling
- **Heroicons** - Icon library
- **Vite** - Build tool

## 📦 Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- Redis (optional, for Celery)

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Initialize database
flask db init
flask db migrate
flask db upgrade

# Seed demo data
python seed_db.py

# Run development server
flask run
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Running Celery (Optional)

```bash
# In a new terminal, activate venv and run:
celery -A app.celery_app worker --loglevel=info

# For scheduled tasks:
celery -A app.celery_app beat --loglevel=info
```

## 🔧 Configuration

### Environment Variables

```env
# Flask
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=1

# Database
DATABASE_URL=sqlite:///padosi_politics.db

# JWT
JWT_SECRET_KEY=your-jwt-secret-here

# Mail (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# Celery (optional)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## 👥 Demo Accounts

After running `seed_db.py`, you can use these demo accounts:

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@padosi.com | admin123 |
| Secretary | secretary@padosi.com | secretary123 |
| Committee | committee@padosi.com | committee123 |
| Resident | resident@padosi.com | resident123 |

## 📱 Pages

1. **Login/Register** - User authentication
2. **Dashboard** - Overview with statistics
3. **All Complaints** - Browse and filter complaints
4. **Complaint Detail** - View full complaint with comments
5. **New Complaint** - File a new complaint
6. **My Complaints** - Track your filed complaints
7. **Leaderboard** - Karma rankings
8. **Profile** - User profile management
9. **Notifications** - View all notifications
10. **Admin Panel** - Manage users, escalations, settings

## 🎮 Karma System

| Action | Points |
|--------|--------|
| File a complaint | +5 |
| Complaint resolved | +10 |
| Add a comment | +2 |
| Vote on complaint | +1 |
| Complaint rejected | -3 |

## 🔄 Background Jobs (Celery)

1. **Auto-escalate old complaints** - Runs every 6 hours
2. **Send reminder notifications** - Runs daily
3. **Calculate monthly karma** - Runs monthly
4. **Generate weekly report** - Runs weekly
5. **Cleanup old notifications** - Runs daily

## 📊 Database Schema

### Models
- **User** - User accounts with roles
- **Society** - Residential societies
- **Complaint** - Complaint records
- **ComplaintEvidence** - File attachments
- **ComplaintVote** - Voting records
- **ComplaintComment** - Comments on complaints
- **Escalation** - Escalation records
- **KarmaLog** - Karma point history
- **Notification** - User notifications

## 🔐 Security Features

- JWT token authentication
- Password hashing with bcrypt
- Role-based access control
- Rate limiting
- Input validation with Marshmallow
- CSRF protection
- XSS prevention

## 📈 API Response Format

```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "meta": {
    "pagination": {
      "current_page": 1,
      "total_pages": 5,
      "total_items": 50,
      "per_page": 10
    }
  }
}
```

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm run test
```

## 📝 API Documentation

API documentation is available at `/api/docs` when running the development server.

## 🚀 Deployment

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Use PostgreSQL instead of SQLite
- [ ] Configure proper `SECRET_KEY` and `JWT_SECRET_KEY`
- [ ] Set up Redis for Celery
- [ ] Configure email settings
- [ ] Set up proper CORS settings
- [ ] Use HTTPS
- [ ] Configure proper logging

## 📄 License

This project is created for educational purposes as part of the IIT Madras BS Program.

## 👨‍💻 Author

**Aaryan**  
Roll No: 23F2003700  
IIT Madras BS Program

---

Built with ❤️ for IIT Madras BS Program