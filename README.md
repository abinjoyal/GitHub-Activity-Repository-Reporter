# GitHub Activity & Repository Reporter

A modular Python application and Streamlit Web Dashboard for aggregating GitHub user analytics, repository statistics, language distributions, and recent activity metrics via the GitHub REST API (v3).

---

## Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Prerequisites & Dependencies](#prerequisites--dependencies)
- [Installation Guide](#installation-guide)
- [Web Dashboard Guide](#web-dashboard-guide)
- [CLI Interface Guide](#cli-interface-guide)
- [Configuration](#configuration)
- [Rate Limit Management](#rate-limit-management)
- [License](#license)

---

## Overview

The **GitHub Activity & Repository Reporter** extracts public data for any GitHub user, computes byte-weighted language distribution metrics across public repositories, aggregates star and fork counts, and parses event streams to analyze recent user activity (commits, pull requests, issues).

The tool offers both:
1. **Interactive Web Dashboard**: Beautiful Streamlit Web UI with interactive Plotly donut charts, metric cards, and one-click report downloads.
2. **CLI Terminal Tool**: Fast command-line interface with structured output tables and ASCII progress bars.

Both interfaces automatically generate standardized Markdown reports (`github-report.md` or `<username>-report.md`).

---

## Key Features

- **Interactive Web Dashboard**: Built with Streamlit and Plotly for real-time visualization.
- **GitHub REST API v3 Integration**: Communicates with GitHub endpoints (`/users/{username}`, `/repos`, `/events`).
- **Language Analytics**: Aggregates raw language byte weights to compute global percentage share with visual charts.
- **Activity Log Parsing**: Tracks commits, pull requests, issue creations, and stars given.
- **Standardized Markdown Export**: Generates reports ready for portfolio inclusion.
- **Rate Limit Resilience**: Supports optional GitHub Personal Access Tokens (PAT) to raise API quotas from 60 to 5,000 requests/hr.

---

## Project Architecture

```
GitHub Activity & Repo Reporter/
├── app.py                         # Web Dashboard (Streamlit & Plotly)
├── main.py                        # CLI Application Entry Point
├── reports/                       # Generated Markdown Reports directory
│   └── GitHub-report.md
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── github_client.py       # REST API client, pagination, rate limits
│   ├── analytics/
│   │   ├── __init__.py
│   │   └── statistics.py          # Data aggregation and metrics engine
│   ├── exporters/
│   │   ├── __init__.py
│   │   └── markdown_exporter.py    # Markdown compiler
│   └── utils/
│       ├── __init__.py
│       └── formatting.py          # Terminal output formatting & progress bars
├── .env.example                   # Environment variable template
├── .gitignore                     # Git rules
├── README.md                      # Technical documentation
└── requirements.txt               # Dependencies (requests, streamlit, plotly, python-dotenv)
```

---

## Prerequisites & Dependencies

- **Python 3.8+**
- `requests>=2.28.0`
- `python-dotenv>=1.0.0`
- `streamlit>=1.25.0`
- `plotly>=5.15.0`

---

## Installation Guide

Execute the following commands in your terminal:

```bash
# 1. Navigate to project directory
cd "d:/Python/Python Project/GitHub Activity & Repo Reporter"

# 2. Activate Python virtual environment

# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat

# 3. Install required packages
pip install -r requirements.txt
```

---

## Web Dashboard Guide

Launch the Web UI in your browser:

```bash
streamlit run app.py
```

This will automatically open `http://localhost:8501` in your web browser, where you can:
- Enter any GitHub username.
- View interactive metric cards and language distribution pie charts.
- Download the generated Markdown report directly.

---

## CLI Interface Guide

Run the command-line utility:

```bash
# Interactive username entry
python main.py

# Specify username via CLI flag
python main.py -u GitHub

# Custom report output name
python main.py -u GitHub -o reports/custom-report.md
```

---

## Configuration

Optionally add a GitHub Personal Access Token (PAT) in `.env`:

```env
GITHUB_TOKEN=your_personal_access_token_here
```

---

## Rate Limit Management

- **Unauthenticated requests**: 60 requests per hour.
- **Authenticated requests**: 5,000 requests per hour.

---

## License

Distributed under the MIT License.
