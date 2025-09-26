# Video Recommendation System Documentation

## Project Overview

The Video Recommendation Engine is a sophisticated system that delivers personalized video content recommendations based on user preferences and engagement patterns. The system implements collaborative filtering algorithms and is designed to handle cold start problems using mood-based recommendations inspired by the Empowerverse App.

## System Architecture

```mermaid
graph TB
    A[FastAPI Application] --> B[Recommendation Service]
    A --> C[Data Collection Service]
    A --> D[Database Layer]
    
    B --> E[Collaborative Filtering]
    B --> F[Cold Start Algorithm]
    B --> G[Category Filtering]
    
    C --> H[Socialverse API]
    C --> I[Redis Cache]
    
    D --> J[PostgreSQL Database]
    D --> K[Alembic Migrations]
    
    L[External APIs] --> H
    M[User Engagements] --> D
    N[Video Content] --> D
    
    style A fill:#e1f5fe
    style B fill:#f3e5f5
    style C fill:#e8f5e8
    style D fill:#fff3e0
```

## Core Functionality

### 1. Personalized Recommendations

The system uses **collaborative filtering** to recommend videos based on:
- User's viewing history and engagement patterns
- Similar users' preferences and behaviors
- Content similarity analysis
- Engagement types (views, likes, inspires, ratings)

**Algorithm Flow:**
1. Collect user engagement data
2. Find users with similar preferences
3. Calculate similarity scores using cosine similarity
4. Recommend videos liked by similar users
5. Apply content-based filtering for relevance

### 2. Cold Start Problem Handling

For new users without engagement history, the system implements **mood-based recommendations**:

- **Motivational Content**: Inspired by Empowerverse App's approach
- **Popular Videos**: Trending content in motivational category
- **Community Favorites**: Highly rated videos by the community
- **Category Diversity**: Mix of different motivational themes

**Cold Start Strategy:**
```python
def get_cold_start_recommendations():
    return {
        "category": "motivational",
        "content_types": [
            "success_stories",
            "productivity_tips", 
            "confidence_building",
            "goal_achievement"
        ],
        "algorithm": "popularity_based"
    }
```

### 3. Category-Based Filtering

The system supports project-specific recommendations:
- **Fitness**: Workout routines, health tips, nutrition advice
- **Business**: Entrepreneurship, productivity, leadership
- **Motivational**: Success stories, inspiration, personal growth
- **Custom Categories**: Extensible for new project codes

## External API Integration

### Socialverse API Integration

The system integrates with Socialverse APIs for data collection:

**Authentication:**
- Uses `Flic-Token` header for all API requests
- Token: `flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f`

**Endpoints:**
- `GET /posts/view` - Viewed posts data
- `GET /posts/like` - Liked posts data  
- `GET /posts/inspire` - Inspired posts data
- `GET /posts/rating` - Rated posts data
- `GET /posts/summary/get` - All posts summary
- `GET /users/get_all` - All users data

**Caching Strategy:**
- TTL-based caching (5 minutes) for API responses
- Redis integration for distributed caching
- Fallback mechanisms for API failures

### Error Handling

**API Error Scenarios:**
- **401 Unauthorized**: Invalid Flic-Token
- **429 Rate Limit**: Too many requests
- **Timeout**: Network connectivity issues
- **500 Server Error**: External API failures

**Fallback Mechanisms:**
- Mock data for development/testing
- Cached responses for offline scenarios
- Graceful degradation to basic recommendations

## Database Schema

### Core Tables

**Users Table:**
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP NOT NULL
);
```

**Videos Table:**
```sql
CREATE TABLE videos (
    video_id UUID PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    posted_at TIMESTAMP NOT NULL,
    description TEXT,
    metadata JSON
);
```

**User Engagements Table:**
```sql
CREATE TABLE user_engagements (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    video_id UUID REFERENCES videos(video_id),
    engagement_type ENUM('VIEW', 'LIKE', 'INSPIRE', 'RATING'),
    rating_score INTEGER,
    timestamp TIMESTAMP NOT NULL
);
```

## API Endpoints

### 1. Personalized Feed
```
GET /api/v1/feed?username={username}&limit={limit}
```

**Parameters:**
- `username` (required): User identifier
- `limit` (optional): Number of recommendations (1-20, default: 5)

**Response:**
```json
{
    "recommendations": [
        {
            "video_id": "uuid",
            "title": "Video Title",
            "category": "motivational",
            "description": "Video description",
            "posted_at": "2024-01-15T10:00:00Z",
            "recommendation_score": 0.95,
            "recommendation_reason": "Similar users also enjoyed this"
        }
    ],
    "total_count": 1,
    "user_id": "uuid",
    "algorithm_used": "collaborative_filtering"
}
```

### 2. Category Feed
```
GET /api/v1/feed/category?username={username}&project_code={project_code}&limit={limit}
```

**Parameters:**
- `username` (required): User identifier
- `project_code` (required): Category filter (e.g., "fitness", "business")
- `limit` (optional): Number of recommendations (1-20, default: 5)

### 3. Health Check
```
GET /api/v1/health
```

**Response:**
```json
{
    "status": "healthy",
    "service": "video-recommendation-engine",
    "version": "1.0.0",
    "timestamp": "2024-01-20T10:00:00Z"
}
```

## Setup and Running Instructions

### Prerequisites
- Python 3.8+
- PostgreSQL 12+
- Redis (optional, for caching)

### Installation

1. **Clone Repository:**
```bash
git clone https://github.com/Tim-Alpha/video-recommendation-assignment.git
cd video-recommendation-engine
```

2. **Create Virtual Environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure Environment:**
Create `.env` file:
```env
FLIC_TOKEN=flic_11d3da28e403d182c36a3530453e290add87d0b4a40ee50f17611f180d47956f
API_BASE_URL=https://api.socialverseapp.com
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/video_recommendation
REDIS_URL=redis://localhost:6379/0
DEBUG=true
```

5. **Run Database Migrations:**
```bash
alembic upgrade head
```

6. **Start the Server:**
```bash
uvicorn app.main:app --reload
```

### Access Points
- **API Documentation**: http://127.0.0.1:8000/docs
- **Health Check**: http://127.0.0.1:8000/health
- **Personalized Feed**: http://127.0.0.1:8000/api/v1/feed?username=testuser

## Edge Cases and Error Handling

### 1. Missing User Data
- **Scenario**: User has no engagement history
- **Solution**: Fallback to cold start recommendations
- **Response**: Motivational content with `algorithm_used: "cold_start_mood_based"`

### 2. Invalid Parameters
- **Scenario**: Empty username or invalid project_code
- **Solution**: Return 400 Bad Request with descriptive error
- **Response**: `{"error": "Username cannot be empty"}`

### 3. API Failures
- **Scenario**: External API unavailable
- **Solution**: Use cached data or mock responses
- **Fallback**: Basic recommendations based on popular content

### 4. Database Errors
- **Scenario**: Database connection issues
- **Solution**: Graceful error handling with 500 status
- **Response**: `{"error": "Internal server error"}`

### 5. Rate Limiting
- **Scenario**: Too many API requests
- **Solution**: Implement exponential backoff
- **Strategy**: Cache responses and reduce API calls

## Future Neural Network Implementation

### Proposed Architecture

**Multi-layer Feedforward Neural Network:**

```python
class RecommendationNeuralNetwork:
    def __init__(self):
        self.input_features = [
            "user_embedding",      # Learned user representation
            "video_embedding",     # Content features
            "interaction_history", # View, like, inspire, rating
            "temporal_features",   # Time of day, day of week
            "contextual_features"  # Device, location
        ]
        
        self.model_structure = [
            "Input Layer: User and video feature vectors",
            "Hidden Layer 1: 128 neurons with ReLU activation",
            "Hidden Layer 2: 64 neurons with ReLU activation", 
            "Hidden Layer 3: 32 neurons with ReLU activation",
            "Output Layer: Sigmoid for recommendation probability"
        ]
        
        self.loss_function = "Binary cross-entropy with negative sampling"
```

### Training Data Requirements
- User-video interaction matrix
- Video content features (title, category, description)
- User demographic and behavioral data
- Temporal interaction patterns

### Advantages
- Better handling of sparse data
- Automatic feature learning
- Scalable to large user/item bases
- Can incorporate complex user behaviors

## Performance Optimization

### Caching Strategy
- **API Responses**: 5-minute TTL cache
- **User Recommendations**: 10-minute TTL cache
- **Popular Content**: 1-hour TTL cache

### Database Optimization
- **Indexes**: On user_id, video_id, engagement_type, timestamp
- **Connection Pooling**: Async SQLAlchemy with connection pooling
- **Query Optimization**: Efficient joins and filtering

### Monitoring and Logging
- **Structured Logging**: JSON format for easy parsing
- **Performance Metrics**: Response times, cache hit rates
- **Error Tracking**: Comprehensive error logging and alerting

## Security Considerations

### API Security
- **Authentication**: Flic-Token validation
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Input Validation**: Sanitize all user inputs

### Data Privacy
- **User Data**: Encrypt sensitive information
- **Audit Logging**: Track data access and modifications
- **GDPR Compliance**: User data deletion and portability

## Testing Strategy

### Unit Tests
- Recommendation algorithm accuracy
- API endpoint functionality
- Database operations
- Error handling scenarios

### Integration Tests
- External API integration
- Database migrations
- End-to-end recommendation flow

### Performance Tests
- Load testing with multiple concurrent users
- Cache performance validation
- Database query optimization

## Deployment Considerations

### Production Environment
- **Containerization**: Docker for consistent deployment
- **Orchestration**: Kubernetes for scaling and management
- **Monitoring**: Prometheus and Grafana for metrics
- **Logging**: ELK stack for log aggregation

### Scaling Strategy
- **Horizontal Scaling**: Multiple API instances
- **Database Scaling**: Read replicas for query distribution
- **Cache Scaling**: Redis cluster for distributed caching

## Conclusion

The Video Recommendation Engine provides a robust foundation for personalized video recommendations with comprehensive error handling, caching strategies, and future neural network integration capabilities. The system successfully addresses cold start problems through mood-based recommendations and provides scalable architecture for production deployment.
