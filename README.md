# Virtual Data Analyst - Team Project

## Project Structure

```
Virtual_Data_Analyst-TP/
├── backend/                    # FastAPI application
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── genai_core/        # LLM components (Router, Query Generator, Response Summarizer)
│   │   ├── data_tools/        # Pre-defined Python modules
│   │   ├── cache/             # Redis integration
│   │   ├── database/          # Database connection (read-only)
│   │   └── config.py          # Configuration
│   ├── main.py                # Entry point
│   ├── pyproject.toml         # Dependencies (uv)
│   └── Dockerfile.dev
├── frontend/                   # React + Vite application
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── api/               # Backend API client
│   │   └── App.jsx
│   ├── package.json
│   └── Dockerfile.dev
├── db/                        # Database initialization
│   └── init/
│       └── 01-init.sql
├── docker-compose.yml         # Local development setup
├── .env.example               # Environment variables template
└── README.md
```
