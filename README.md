# Breezy ATS Microservice

A **production-ready backend microservice** that integrates with the [Breezy HR](https://breezy.hr) Applicant Tracking System (ATS). Built with **Python 3.11**, deployed on **AWS Lambda** via the **Serverless Framework**, and following clean architecture principles.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture](#architecture)
3. [Folder Structure](#folder-structure)
4. [Setting Up Breezy HR](#setting-up-breezy-hr)
5. [Configuration](#configuration)
6. [Local Development](#local-development)
7. [Deployment](#deployment)
8. [API Reference](#api-reference)
9. [Error Handling](#error-handling)

---

## Project Overview

This microservice exposes three standardized REST endpoints that internally communicate with the Breezy HR REST API v3:

| Endpoint | Method | Description |
|---|---|---|
| `/jobs` | `GET` | Fetch open jobs |
| `/candidates` | `POST` | Create & attach a candidate to a job |
| `/applications` | `GET` | List applications for a job |

**Key production features:**

- ✅ Pydantic v2 input validation with field-level error details
- ✅ Exponential-backoff retry (tenacity) on network/5xx errors
- ✅ Full Breezy HR pagination (fetches all pages automatically)
- ✅ Structured JSON logging (CloudWatch-ready via python-json-logger)
- ✅ Centralized error responses with normalized `error.code` + `error.message`
- ✅ Timeout handling on all outbound HTTP calls (httpx)
- ✅ CORS headers on all responses
- ✅ Environment variable-based configuration (dotenv for local, Lambda env for prod)

---

## Architecture

```
API Gateway
    │
    ├─ GET  /jobs          ──► jobs_handler      ──► JobService          ──► BreezyClient
    ├─ POST /candidates    ──► candidates_handler ──► CandidateService    ──► BreezyClient
    └─ GET  /applications  ──► applications_handler ──► ApplicationService ──► BreezyClient

BreezyClient
  ├─ Authentication  (Authorization header)
  ├─ Retry logic     (@with_retry / tenacity)
  ├─ Pagination      (_paginate: fetches all pages)
  └─ Error handling  (raises BreezyAPIError)
```

### Layer Responsibilities

| Layer | Files | Responsibility |
|---|---|---|
| **Handlers** | `src/handlers/` | Parse Lambda events, validate input, call services, return HTTP response |
| **Services** | `src/services/` | Business logic, orchestrate BreezyClient calls, map to domain models |
| **BreezyClient** | `src/services/breezy_client.py` | All HTTP communication with Breezy HR |
| **Models** | `src/models/` | Pydantic request/response schemas and Breezy field mapping |
| **Utils** | `src/utils/` | Response helpers, logging, error types, pagination, retry |
| **Config** | `src/config/settings.py` | Centralized env var loading with LRU-cached singleton |

---

## Folder Structure

```
breezy-ats-microservice/
├── src/
│   ├── __init__.py
│   ├── main.py                         # Local dev entry point / config check
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py                 # Env var config with LRU cache
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── jobs_handler.py             # GET /jobs Lambda handler
│   │   ├── candidates_handler.py       # POST /candidates Lambda handler
│   │   └── applications_handler.py     # GET /applications Lambda handler
│   ├── services/
│   │   ├── __init__.py
│   │   ├── breezy_client.py            # Breezy HR HTTP client (retry, pagination)
│   │   ├── job_service.py              # Job fetch + normalization logic
│   │   ├── candidate_service.py        # Candidate create + attach logic
│   │   └── application_service.py      # Application fetch + normalization logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── job.py                      # Job Pydantic models + Breezy mapping
│   │   ├── candidate.py                # Candidate Pydantic models + validation
│   │   └── application.py             # Application Pydantic models + mapping
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                   # Structured JSON logger
│       ├── response.py                 # API Gateway response helpers
│       ├── error_handler.py            # Custom exceptions + error normalizer
│       ├── pagination.py               # Pagination param parsing + response builder
│       └── retry.py                    # Tenacity retry decorator
├── serverless.yml                      # Serverless Framework config
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variable template
└── README.md
```

---

## Setting Up Breezy HR

### 1. Create a Breezy HR Account

1. Go to [https://app.breezy.hr/signup](https://app.breezy.hr/signup)
2. Sign up with your work email
3. Complete the onboarding (create your company profile)

### 2. Get Your Company ID

1. Log in to your Breezy HR dashboard
2. Navigate to **Settings → Company**
3. Your Company ID is visible in the URL:  
   `https://app.breezy.hr/app/company/**your-company-id**/settings`

### 3. Generate an API Key

1. In Breezy HR, navigate to **Settings → API**  
   (or go to `https://app.breezy.hr/app/company/<your-company-id>/settings/api`)
2. Click **"Generate API Key"**
3. Copy the key immediately — it won't be shown again

> **Note:** Breezy HR API keys are company-scoped. Keep them secret and never commit them to version control.

---

## Configuration

### Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `BREEZY_API_KEY` | ✅ Yes | Your Breezy HR API key |
| `BREEZY_BASE_URL` | No | Default: `https://api.breezy.hr/v3` |
| `BREEZY_COMPANY_ID` | ✅ Yes | Your Breezy HR company ID |
| `LOG_LEVEL` | No | Default: `INFO`. Options: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

## Local Development

### Prerequisites

- **Node.js** 18+ (for Serverless Framework)
- **Python** 3.11+
- **pip** or **virtualenv**

### 1. Install Dependencies

```bash
# Install Serverless Framework globally
npm install -g serverless

# Install Serverless plugins
npm install --save-dev serverless-offline serverless-python-requirements

# Create and activate a Python virtual environment
python -m venv .venv
.venv\Scripts\activate       # Windows
# source .venv/bin/activate  # macOS / Linux

# Install Python packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your Breezy HR credentials
```

### 3. Run Locally

```bash
serverless offline
```

The API will be available at `http://localhost:3000`.

### 4. Validate Config (Optional)

```bash
python src/main.py
```

---

## Deployment

### Prerequisites

- AWS CLI configured (`aws configure`)
- `serverless` CLI installed

### Deploy to AWS

```bash
# Deploy to dev stage
serverless deploy

# Deploy to production
serverless deploy --stage prod
```

### Remove Stack

```bash
serverless remove
```

---

## API Reference

### GET /jobs

Fetch open positions from Breezy HR.

**Query Parameters:**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | `1` | Page number |
| `page_size` | int | `25` | Items per page (max 100) |

**Example:**

```bash
curl http://localhost:3000/jobs
curl "http://localhost:3000/jobs?page=2&page_size=10"
```

**Response (200):**

```json
{
  "data": [
    {
      "id": "abc123",
      "title": "Senior Python Engineer",
      "location": "Remote",
      "status": "OPEN",
      "external_url": "https://company.breezy.hr/position/abc123"
    }
  ],
  "total": 42,
  "page": 1,
  "page_size": 25
}
```

---

### POST /candidates

Create a candidate and attach them to a job.

**Request Body:**

```json
{
  "name": "Jane Doe",
  "email": "jane@example.com",
  "phone": "+919999999999",
  "resume_url": "https://example.com/resume.pdf",
  "job_id": "abc123"
}
```

**Example:**

```bash
curl -X POST http://localhost:3000/candidates \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+919999999999",
    "resume_url": "https://example.com/resume.pdf",
    "job_id": "abc123"
  }'
```

**Response (201):**

```json
{
  "id": "xyz789",
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "+919999999999",
  "resume_url": "https://example.com/resume.pdf",
  "job_id": "abc123",
  "message": "Candidate created and attached to the job successfully."
}
```

---

### GET /applications

Fetch applications for a specific job.

**Query Parameters:**

| Param | Type | Required | Description |
|---|---|---|---|
| `job_id` | string | ✅ Yes | Breezy HR position ID |
| `page` | int | No | Page number (default: 1) |
| `page_size` | int | No | Items per page (default: 25) |

**Example:**

```bash
curl "http://localhost:3000/applications?job_id=abc123"
```

**Response (200):**

```json
{
  "data": [
    {
      "id": "app001",
      "candidate_name": "Jane Doe",
      "email": "jane@example.com",
      "status": "APPLIED"
    }
  ],
  "total": 5,
  "page": 1,
  "page_size": 25
}
```

---

## Error Handling

All errors return a consistent envelope:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description"
  }
}
```

| HTTP Status | Code | Cause |
|---|---|---|
| `400` | `BAD_REQUEST` | Missing/malformed query or body |
| `404` | `NOT_FOUND` | Resource not found |
| `422` | `VALIDATION_ERROR` | Pydantic validation failure (with field details) |
| `500` | `INTERNAL_ERROR` | Unexpected server error |
| `502` | `UPSTREAM_ERROR` | Breezy HR API returned an error |

### Validation Error Example (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request payload validation failed.",
    "details": [
      { "field": "email", "message": "value is not a valid email address" },
      { "field": "job_id", "message": "job_id must not be empty." }
    ]
  }
}
```

---

## Built With

- [Python 3.11](https://python.org)
- [AWS Lambda](https://aws.amazon.com/lambda/)
- [Serverless Framework](https://serverless.com)
- [Pydantic v2](https://docs.pydantic.dev)
- [HTTPX](https://www.python-httpx.org/)
- [Tenacity](https://tenacity.readthedocs.io/)
- [python-json-logger](https://github.com/madzak/python-json-logger)
- [Breezy HR API v3](https://developer.breezy.hr/)
