# @Study:ST-004 @Study:ST-008
# Modamoda Invisible Mannequin - Technical Documentation

## Overview

This document provides technical documentation for the Modamoda Invisible Mannequin platform.

## Architecture

### Backend Architecture
- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL
- **Cache**: Redis
- **Task Queue**: Celery
- **Authentication**: JWT with bcrypt

### Frontend Architecture
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: React Context/Redux

## API Documentation

### Health Check
```
GET /health
Response: {"status": "healthy"}
```

### Root Endpoint
```
GET /
Response: {"message": "Modamoda Invisible Mannequin API", "status": "running"}
```

## Development Setup

1. Install dependencies: `poetry install`
2. Run backend: `uvicorn src.backend.main:app --reload`
3. Run frontend: `npm run dev`
4. Run tests: `pytest`

## Compliance & Governance

This project follows strict governance standards defined in the studies and governance framework. All changes must pass compliance checks before merging.

For more details, see:
- [Governance Framework](../../governance/active/GOVERNANCE_FRAMEWORK.md)
- [Project Setup Analysis](../../PROJECT_SETUP_ANALYSIS.md)
