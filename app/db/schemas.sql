CREATE TABLE IF NOT EXISTS user_queries (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    user_prompt TEXT NOT NULL,
    origin_name VARCHAR(255),
    destination_name VARCHAR(255),
    selected_language VARCHAR(50) DEFAULT 'English'
);

CREATE TABLE IF NOT EXISTS route_metadata (
    id SERIAL PRIMARY KEY,
    query_id INT REFERENCES user_queries(id) ON DELETE CASCADE,
    total_distance_km NUMERIC(10, 2),
    est_duration_hrs NUMERIC(10, 2),
    overall_risk_score NUMERIC(5, 2),
    safety_status VARCHAR(100),
    primary_geometry JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
