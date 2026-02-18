# Disaster DSS Backend API

Production-ready FastAPI backend for the AI-Driven Disaster & Homeland Security Decision Support System.

## Features

- **Real AI Models**: YOLOv8 for damage detection, BERT for NLP analysis
- **Risk Scoring Engine**: Weighted algorithms for threat assessment
- **Recommendation Engine**: AI-powered response strategies
- **WebSocket Support**: Real-time updates to connected clients
- **PostgreSQL Database**: Persistent storage for all data
- **Redis Cache**: Fast data access and session management
- **Docker Deployment**: Easy containerized deployment
- **Horizontal Scaling**: Kubernetes-ready architecture

## Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone and navigate to backend directory
cd backend

# Copy environment file
cp .env.example .env

# Start all services
docker-compose up -d

# API will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Manual Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up PostgreSQL and Redis (must be running)
# Update DATABASE_URL and REDIS_URL in .env

# Run database migrations
alembic upgrade head

# Start the API
uvicorn app.main:app --reload
```

## API Endpoints

### Incidents
- `GET /api/v1/incidents` - List all incidents
- `POST /api/v1/incidents` - Create new incident
- `GET /api/v1/incidents/{id}` - Get incident details

### Zones
- `GET /api/v1/zones` - List zones
- `POST /api/v1/zones` - Create zone
- `GET /api/v1/risk/zone/{id}` - Get risk assessment

### Resources
- `GET /api/v1/resources` - List resources
- `POST /api/v1/resources` - Create resource
- `POST /api/v1/resources/{id}/assign` - Assign to zone

### Analysis
- `POST /api/v1/analyze/image` - Analyze image for damage
- `POST /api/v1/analyze/text` - Analyze text/report

### Recommendations
- `GET /api/v1/recommendations` - List recommendations
- `POST /api/v1/recommendations/generate/{zone_id}` - Generate AI recommendations
- `POST /api/v1/recommendations/{id}/execute` - Mark as executed

### Dashboard
- `GET /api/v1/dashboard/stats` - Get dashboard statistics
- `GET /api/v1/dashboard/map` - Get map data

### WebSocket
- `WS /ws` - Real-time updates connection

## AI Models

### Computer Vision (YOLOv8)
- Damage detection in satellite/drone imagery
- Building collapse identification
- Fire and flood extent mapping
- Bounding box annotations with confidence scores

### NLP (BERT)
- Emergency report classification
- Sentiment analysis
- Entity extraction (locations, organizations)
- Urgency detection

### Risk Scoring
- Damage severity calculation (0-100%)
- Survival probability estimation
- Threat level classification
- Priority scoring for response

## Database Schema

### Tables
- `incidents` - Disaster incidents
- `zones` - Geographic zones within incidents
- `resources` - Emergency response resources
- `timeline_events` - Chronological incident events
- `analysis_results` - AI analysis outputs
- `recommendations` - AI-generated recommendations
- `sensor_data` - IoT sensor readings
- `social_media_reports` - Analyzed social media posts

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL async connection string | Required |
| `REDIS_URL` | Redis connection string | Required |
| `KAFKA_BOOTSTRAP_SERVERS` | Kafka broker addresses | localhost:9092 |
| `MODEL_PATH` | Path to AI model weights | ./models/weights |
| `MAX_UPLOAD_SIZE` | Max image upload size (bytes) | 104857600 (100MB) |
| `CORS_ORIGINS` | Allowed CORS origins | http://localhost:5173 |

## Deployment

### Docker Compose
```bash
docker-compose up -d
```

### Kubernetes
```bash
kubectl apply -f k8s/
```

### Production Checklist
- [ ] Change SECRET_KEY
- [ ] Set up SSL/TLS certificates
- [ ] Configure external API keys
- [ ] Set up monitoring (Prometheus/Grafana)
- [ ] Configure log aggregation
- [ ] Set up backup strategy
- [ ] Configure rate limiting
- [ ] Enable request logging

## Monitoring

- Prometheus metrics at `:9090`
- Grafana dashboards at `:3000`
- API docs at `/docs` (Swagger UI)
- Health check at `/health`

## License

MIT License - See LICENSE file
