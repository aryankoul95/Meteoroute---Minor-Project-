# MeteoRoute 🌦️
### A Multilingual Platform for Evidence-Grounded Weather Intelligence and Hazard-Aware Route Planning

MeteoRoute is a weather-aware route-planning platform that helps users understand weather conditions and potential hazards along their journeys.

Instead of considering only distance and travel time, MeteoRoute integrates weather information, official weather alerts and rule-based risk assessment to provide additional context for route planning.

The project is developed as a B.Tech Computer Science and Engineering minor project.

---

## 1. Project Overview

MeteoRoute combines route planning, weather intelligence and conversational AI into one platform.

Users can:
- Enter journey requests using natural language.
- Extract origin, destination and departure-time information.
- Generate routes using OpenStreetMap data and OSRM.
- Analyze weather conditions at sampled route waypoints.
- Retrieve and process official IMD CAP alerts.
- Assess route-level and waypoint-level weather risks.
- Interact with a multilingual AI assistant in English and Hindi.

## 2. Key Features

| Feature | Description |
|---|---|
| Natural-language journey input | Extracts journey details from user queries |
| Route planning | Generates routes using OSRM |
| Weather integration | Retrieves weather information from external weather providers |
| Weather sampling | Analyzes conditions at multiple points along a route |
| Official weather alerts | Integrates IMD CAP alert information |
| Risk assessment | Uses a Python-based rule engine to assess weather-related risks |
| AI assistant | Provides conversational weather and journey-related assistance |
| Interactive map | Displays routes and waypoint information using Leaflet |

## 3. Technology Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript |
| Mapping | Leaflet, OpenStreetMap |
| Backend | Python, FastAPI |
| AI / LLM | Google Gemini |
| Routing | OSRM |
| Weather | Open-Meteo, WeatherAPI, OpenWeather |
| Official alerts | IMD CAP |
| Database | PostgreSQL, PostGIS |
| Deployment | Docker, Docker Compose |
| Reverse proxy | Nginx |

## 4. System Architecture

```text
                 USER
                  |
                  v
        REACT + VITE FRONTEND
             LEAFLET MAP
                  |
                  v
          FASTAPI BACKEND
                  |
       +----------+-----------+
       |          |           |
       v          v           v
   ROUTING     WEATHER      AI ASSISTANT
     OSRM      PROVIDERS       GEMINI
       |          |
       |          v
       |      WEATHER DATA
       |          |
       |          v
       |     RISK ENGINE
       |          |
       |          v
       |     RISK RESULTS
       |
       v
   ROUTE GEOMETRY

       IMD CAP ALERT INTEGRATION
                  |
                  v
         ALERT PROCESSING

       POSTGRESQL + POSTGIS
                  |
                  v
          SPATIAL DATA
```

The frontend communicates with the FastAPI backend. The backend coordinates routing, weather retrieval, alert processing, risk assessment and AI-assisted responses.

## 5. Repository Structure

```text
meteoroute-backend/
│
├── app/
│   ├── api/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── meteoroute-frontend/
│   ├── src/
│   ├── public/
│   ├── Dockerfile
│   └── package.json
│
├── docker/
├── data/
├── osrm-data/                 # Local dataset; not committed
│
├── Dockerfile
├── Dockerfile.prod
├── docker-compose.yml
├── docker-compose.prod.yml
├── Caddyfile
├── requirements.txt
├── requirements-prod.txt
└── README.md
```

Some additional testing, configuration and utility files are also present in the repository.

## 6. Running the Project

### Prerequisites

Install the following:

- Git
- Docker Desktop
- Docker Compose
- Node.js (for independent frontend development)

The OSRM routing dataset is also required.

**Important:** The Northern India OSRM dataset is approximately 42.53 GB and is not included in this Git repository. Team members must obtain the dataset separately through the project team.

### Step 1: Clone the repository

```powershell
git clone YOUR_GITHUB_REPOSITORY_URL
cd meteoroute-backend
```

Replace `YOUR_GITHUB_REPOSITORY_URL` with the actual repository URL.

### Step 2: Configure environment variables

Create a `.env` file in the project root.

Use the following template:

```env
POSTGRES_USER=your_database_user
POSTGRES_PASSWORD=your_database_password
POSTGRES_DB=meteoroute

GEMINI_API_KEY=your_gemini_api_key
WEATHERAPI_API_KEY=your_weatherapi_key
OPENWEATHER_API_KEY=your_openweather_key
```

Use your own credentials. Never commit `.env` to GitHub.

### Step 3: Configure the OSRM dataset

Place the required OSRM dataset files inside:

```text
osrm-data/
```

The dataset must include the routing files corresponding to:

```text
northern-zone.osrm
```

### Step 4: Start the application

From the project root:

```powershell
docker compose up --build
```

### Step 5: Open the application

| Component | Local URL |
|---|---|
| Frontend | http://localhost:5178 |
| Backend API | http://localhost:8000 |
| FastAPI Swagger documentation | http://localhost:8000/docs |

The application uses Docker Compose to run the frontend, backend, PostgreSQL/PostGIS database and OSRM routing service.

## 7. Development Setup

### Frontend

```powershell
cd meteoroute-frontend
npm install
npm run dev
```

### Backend

From the repository root, activate your Python virtual environment and install dependencies:

```powershell
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The backend can be started using:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

For local development, ensure the required database, OSRM service and environment configuration are available.

## 8. Database Management

MeteoRoute uses PostgreSQL with PostGIS extensions.

The database supports spatial data management and application-related records.

Important application tables include:

- `admin_boundaries`
- `route_metadata`
- `user_queries`

PostGIS provides spatial capabilities for geographical data operations.

## 9. Testing and Reliability

The project includes automated tests and integration checks.

Verified testing work includes:

- Weather provider failover and failure-handling tests: 9 automated tests passed.
- Production backend Docker image build.
- Backend application import verification.
- Non-root backend execution verification.
- Read-only filesystem behaviour testing.
- Nginx reverse-proxy end-to-end route request verification.
- Local mobile access over Wi-Fi testing.

These results represent completed individual checks, not a full production-scale performance evaluation.

## 10. Current Development Status

### Implemented

- React-based weather dashboard.
- Natural-language journey intent extraction.
- OSRM-based route generation.
- Route waypoint sampling.
- Weather provider integration and fallback handling.
- IMD CAP alert integration.
- Rule-based route risk assessment.
- Gemini-powered multilingual text assistant.
- PostgreSQL/PostGIS integration.
- Docker-based application setup.

### Pending / Future Work

- Voice input and speech-to-text integration.
- Text-to-speech responses.
- Nationwide routing coverage.
- Public cloud deployment with HTTPS and a domain.
- Load testing and large-scale performance evaluation.
- Further evaluation of explanation accuracy, faithfulness and usability.

## 11. Current Geographic Scope

The current OSRM routing configuration uses a Northern India dataset.

The project focuses on validating the complete weather-aware routing pipeline within its available geographical coverage.

Expansion to other regions and nationwide routing is planned future work.

## 12. Future Scope

- Expand routing coverage across India.
- Introduce scalable cloud deployment.
- Improve multilingual voice interaction.
- Enhance historical weather and alert analysis.
- Introduce caching and performance optimization.
- Evaluate the platform under larger concurrent workloads.

## 13. Project Objective

The main objective of MeteoRoute is to move beyond conventional shortest-route navigation by providing weather-aware and hazard-informed travel intelligence.

**MeteoRoute – Making journeys more informed through weather intelligence.**

---

**Project:** MeteoRoute  
**Academic Programme:** B.Tech Computer Science and Engineering  
**Project Type:** Minor Project  
**Review:** Review-II



## 14. Team Contributions

| Member | Role | Primary Responsibilities |
|---|---|---|
| Member 1 | Frontend Developer | React, Vite, Leaflet, dashboard and UI integration |
| Member 2 | Backend Developer | FastAPI, OSRM, route generation and database integration |
| Member 3 | Weather Intelligence and AI Developer | Weather APIs, IMD CAP, risk engine and Gemini integration |

All team members collaborate on system integration, debugging, testing and documentation.

Proposed team role distribution

Member 1 – Frontend and User Interface
Frontend Developer


Responsibilities
- Develop the React and Vite frontend.
- Design the MeteoRoute dashboard and user interface.
- Integrate Leaflet maps and route visualization.
- Display route information, waypoint weather and risk results.
- Implement responsive layouts and frontend-backend communication.
Viva answer:

"My responsibility was frontend development. I worked on the React dashboard, interactive maps, user interface and integration of backend results so users can easily understand weather-aware routes."


Member 2 – Backend and Routing
Backend Developer


Responsibilities
- Develop REST APIs using Python and FastAPI.
- Implement natural-language journey processing and geocoding integration.
- Integrate OSRM and OpenStreetMap for route generation.
- Implement route waypoint sampling.
- Manage PostgreSQL/PostGIS integration.
- Coordinate communication between backend services.
Viva answer:

"My responsibility was backend development and routing. I worked on FastAPI APIs, journey processing, OSRM route generation, waypoint sampling and database integration."


Member 3 – Weather Intelligence and AI
AI and Data Integration


Responsibilities
- Integrate Open-Meteo and fallback weather providers.
- Process official IMD CAP weather alerts.
- Develop and integrate the rule-based risk assessment engine.
- Integrate Google Gemini for conversational assistance.
- Support English and Hindi text interactions.
- Contribute to testing and reliability validation.
Viva answer:

"My responsibility was weather intelligence and AI integration. I worked on weather data providers, official alert processing, risk assessment and the Gemini-powered multilingual assistant."


How the three members work together
Member 1: React + Leaflet

User interface and visualization

Member 2: FastAPI + OSRM + PostGIS

Backend processing and route generation

Member 3: Weather + IMD CAP + Risk Engine + Gemini

Weather intelligence and AI services

Integrated MeteoRoute Application

Weather-aware route planning


This is a simplified responsibility diagram, not the exact runtime request sequence.
Important questions your examiner may ask
1. Who is the team leader?

Choose the member who coordinated integration and overall project development. The team should agree on this based on actual contributions.

2. Did everyone work independently?

Answer:

"Each member had primary responsibilities, but we collaborated during integration, debugging and testing because all modules are interconnected."

3. Can each member explain the entire project?

Yes. Every member should understand the overall architecture, even if they specialize in one module.

4. What about deployment?

Docker Compose, Nginx, production configuration and reliability testing can be treated as shared integration responsibilities.