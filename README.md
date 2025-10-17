# PSAI_A + Teknoledg Unified System

## 🚀 One-Click Render Deployment

This package contains the complete PSAI_A system with Teknoledg authentication, optimized for Render.com deployment.

### 📦 What's Included

- **Unified Flask Application** (`unified_system.py`)
- **Teknoledg Authentication** (Password-protected access)
- **PSAI_1 Visual Timeline** (Interactive process dashboard)
- **Client Management** (Multi-client support)
- **Production Ready** (Docker, health checks, logging)

### 🔑 Access Information

- **Password**: `316h7y$!x-71ck13-516n41!`
- **Features**: Visual timeline, settings drawer, report generation
- **Security**: JWT authentication, IP logging

### 🚀 Deploy to Render

1. **Fork/Clone** this repository
2. **Connect** to Render.com
3. **Deploy** using the `render.yaml` configuration
4. **Access** your deployed application

### 📁 File Structure

```
├── unified_system.py      # Main Flask application
├── auth.html             # Authentication page
├── scripts/              # PSAI_1 timeline and backend
├── images/               # Assets (logos, police bot)
├── clients/              # Client configuration
├── requirements.txt      # Python dependencies
├── render.yaml          # Render deployment config
├── Dockerfile           # Container configuration
└── Procfile            # Process definition
```

### ⚙️ Environment Variables

- `TEKNOLEDG_PASSCODE`: Authentication password
- `TEKNOLEDG_JWT_SECRET`: JWT signing secret (auto-generated)
- `FLASK_ENV`: Production environment
- `PORT`: Application port (10000)

### 🔧 Features

- **Multi-client Support**: Different passwords for different clients
- **Visual Timeline**: Interactive PSAI_1 process visualization
- **Settings Management**: Configurable sources and parameters
- **Report Generation**: Automated weekly briefs
- **Health Monitoring**: Built-in health checks
- **Logging**: Comprehensive logging system

### 📊 PSAI_1 Process

1. **HARVEST**: Collect data from RSS, Reddit, YouTube
2. **EXTRACT**: Process with AI models (Ollama)
3. **REPORT**: Generate weekly brief with citations
4. **REVIEW**: Analyst approval workflow

### 🛡️ Security

- JWT-based authentication
- IP address logging
- Environment variable configuration
- Secure session management

### 📞 Support

For issues or questions, check the logs in the Render dashboard or contact the development team.

---

**Ready for Production Deployment!** 🎉
