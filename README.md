# Toronto Job Tracker 🍁

A web application that aggregates internship/co-op job listings in Toronto from multiple sources and displays them in a clean dashboard.

## Features

- **Multiple Job Sources**: JSearch API (LinkedIn, Indeed, Glassdoor), GitHub curated lists, Indeed RSS, RemoteOK, Arbeitnow
- **Smart Filtering**: Automatically filters for internships/co-ops only
- **Search & Filter**: Search by keyword, filter by source, saved jobs, new jobs, startups
- **Save Jobs**: Bookmark jobs you're interested in
- **Auto-Refresh**: Background refresh every 15 minutes (configurable)
- **Modern UI**: Clean split-view interface with React + Tailwind CSS

## Quick Start

### 1. Install Backend Dependencies

```bash
git clone https://github.com/nickirons/toronto-job-tracker.git
cd toronto-job-tracker

# Create virtual environment (optional but recommended)
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
```

### 3. Start the Backend

```bash
# From the project root
python -m uvicorn backend.main:app --reload --port 8000
```

### 4. Start the Frontend (in a new terminal)

```bash
cd frontend
npm run dev
```

### 5. Open the App

Visit **http://localhost:5173** in your browser.

### 6. Configure API Key

1. Click the **Settings** (gear icon) in the top right
2. Enter your RapidAPI key (get it free from [JSearch on RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch))
3. Click **Save**
4. Click **Refresh** to fetch jobs

## Project Structure

```
toronto-job-tracker/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── database.py          # SQLAlchemy setup
│   ├── models/
│   │   └── job.py           # Job model
│   ├── services/
│   │   ├── job_fetcher.py   # Main orchestrator
│   │   ├── jsearch_client.py
│   │   ├── github_fetcher.py
│   │   ├── indeed_fetcher.py
│   │   ├── remoteok_fetcher.py
│   │   └── arbeitnow_fetcher.py
│   ├── utils/
│   │   ├── filters.py       # Internship filtering
│   │   └── url_utils.py     # URL normalization
│   └── routers/
│       ├── jobs.py          # /api/jobs endpoints
│       └── settings.py      # /api/settings endpoints
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   ├── components/
│   │   ├── hooks/
│   │   └── lib/
│   └── package.json
├── requirements.txt
└── README.md
```

## API Endpoints

- `GET /api/jobs` - List all jobs (with filters)
- `GET /api/jobs/{id}` - Get single job
- `PATCH /api/jobs/{id}` - Update job (mark viewed, toggle saved)
- `DELETE /api/jobs/{id}` - Delete job
- `POST /api/jobs/refresh` - Trigger manual refresh
- `GET /api/jobs/stats` - Get job statistics
- `GET /api/settings` - Get settings
- `PUT /api/settings` - Update settings

## Tech Stack

**Backend:**
- FastAPI (Python web framework)
- SQLAlchemy (ORM)
- SQLite (database)
- httpx (async HTTP client)
- APScheduler (background tasks)

**Frontend:**
- React 18
- TypeScript
- Vite
- Tailwind CSS
- React Query
- Lucide Icons

## Job Sources

| Source | Type | API Key Required |
|--------|------|-----------------|
| JSearch | Aggregator (LinkedIn, Indeed, etc.) | Yes (free) |
| GitHub Lists | Curated markdown tables | No |
| Indeed RSS | RSS feed | No |
| RemoteOK | API | No |
| Arbeitnow | API | No |

## Filtering Logic

Jobs are filtered to only include internships:

**MUST contain** (in title OR description):
- "intern", "co-op", "coop", "internship"

**MUST NOT contain** (in title):
- "senior", "sr.", "lead", "manager", "director", "principal", "staff"

---

Built for 3rd year CS students in Toronto 🎓
