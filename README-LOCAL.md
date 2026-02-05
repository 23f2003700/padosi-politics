# 🏠 Padosi Politics - Local Development Setup

A modern society complaint management system built with Flask (Backend) and Vue.js (Frontend).

**Built by Aaryan (23F2003700) for IIT Madras BS Program**

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![Vue](https://img.shields.io/badge/vue-3.4-brightgreen.svg)

## 🌟 Features

- 📝 **Complaint Management** - File, track, and resolve society complaints
- 🗳️ **Voting System** - Support or oppose complaints anonymously
- 💬 **Comments** - Discuss issues with society members
- 🏆 **Karma Points** - Earn points for contributions
- 📊 **Leaderboard** - Top contributors recognition
- 🔔 **Notifications** - Real-time updates
- 👤 **Role-based Access** - Admin, Secretary, Committee, Resident
- 📱 **Responsive Design** - Works on all devices

## 📋 Prerequisites

- **Python 3.10+** - [Download](https://www.python.org/downloads/)
- **Node.js 18+** - [Download](https://nodejs.org/)
- **Git** - [Download](https://git-scm.com/)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/23f2003700/padosi-politics-local.git
cd padosi-politics-local
```

### 2. Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
copy .env.example .env   # Windows
# cp .env.example .env   # macOS/Linux

# Initialize database with seed data
python seed_db.py

# Run backend server
python run.py
```

Backend will run at: **http://localhost:5000**

### 3. Frontend Setup (New Terminal)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run at: **http://localhost:5173**

### 4. Open the App

Visit: **http://localhost:5173**

## 🔑 Demo Accounts

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@padosipolitics.com | password123 |
| Secretary | secretary@greenvalley.com | password123 |
| Resident | resident1@greenvalley.com | password123 |

## 📁 Project Structure

```
padosi-politics-local/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API endpoints
│   │   ├── services/        # Business logic
│   │   └── utils/           # Helper functions
│   ├── config.py            # Configuration
│   ├── requirements.txt     # Python dependencies
│   ├── seed_db.py          # Database seeder
│   └── run.py              # Entry point
│
├── frontend/
│   ├── src/
│   │   ├── components/      # Vue components
│   │   ├── views/           # Page components
│   │   ├── stores/          # Pinia stores
│   │   ├── services/        # API services
│   │   └── router/          # Vue Router
│   ├── package.json         # Node dependencies
│   └── vite.config.js       # Vite configuration
│
└── README.md
```

## 🔧 Configuration

### Backend (.env)

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-change-in-production
DATABASE_URL=sqlite:///padosi.db
```

### Frontend (.env.development)

```env
VITE_API_URL=/api
```

## 📚 API Documentation

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/profile` - Get current user profile

### Complaints
- `GET /api/complaints` - List all complaints
- `POST /api/complaints` - Create new complaint
- `GET /api/complaints/:id` - Get complaint details
- `PATCH /api/complaints/:id/status` - Update status

### Votes & Comments
- `POST /api/complaints/:id/vote` - Vote on complaint
- `POST /api/complaints/:id/comments` - Add comment

### Dashboard
- `GET /api/dashboard/stats` - Get statistics
- `GET /api/leaderboard` - Get karma leaderboard

## 🛠️ Development Commands

### Backend
```bash
# Run with auto-reload
python run.py

# Run tests
pytest

# Database migration (if using Flask-Migrate)
flask db upgrade
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🐛 Troubleshooting

### Common Issues

**1. Port already in use**
```bash
# Kill process on port 5000 (Windows)
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Kill process on port 5173 (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

**2. Module not found (Backend)**
```bash
# Make sure venv is activated
venv\Scripts\activate  # Windows
source venv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

**3. npm install fails**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**4. CORS errors**
- Make sure backend is running on port 5000
- Check Vite proxy config in `vite.config.js`

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- IIT Madras BS Program
- Flask & Vue.js communities
- All contributors

---

**Made with ❤️ by Aaryan (23F2003700)**
