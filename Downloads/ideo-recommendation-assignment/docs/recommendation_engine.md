Recommendation Engine

Cold Start
- Returns recent posts when no engagements exist for the user.

Personalized
- Builds a user preference vector from engagements (view, like, inspire, rating).
- Vectorizes posts by category and metadata, uses cosine similarity for scoring.

Category Recommendations
- Filters posts by `project_code` (category) and returns paginated results.


