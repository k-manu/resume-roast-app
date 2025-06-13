-- ==============================================
-- Resume Roast App - Simplified Supabase Setup
-- Run each section separately if you encounter errors
-- ==============================================

-- STEP 1: Create Tables
-- ==============================================

-- Table for logging AI processing events (privacy-friendly)
CREATE TABLE IF NOT EXISTS processing_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    file_type VARCHAR(10) NOT NULL CHECK (file_type IN ('pdf', 'txt', 'unknown')),
    processing_time_seconds DECIMAL(10,3) NOT NULL,
    roast_length_chars INTEGER NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Table for storing user preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    preferences JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Table for storing AI model performance metrics
CREATE TABLE IF NOT EXISTS ai_model_metrics (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL UNIQUE,
    average_processing_time DECIMAL(10,3),
    success_rate DECIMAL(5,2),
    total_requests INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- STEP 2: Enable Row Level Security
-- ==============================================

ALTER TABLE processing_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_model_metrics ENABLE ROW LEVEL SECURITY;

-- STEP 3: Create Security Policies
-- ==============================================

-- Processing logs policies
CREATE POLICY "Users can view own processing logs" ON processing_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own processing logs" ON processing_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User preferences policies
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- AI model metrics policy
CREATE POLICY "Authenticated users can view model metrics" ON ai_model_metrics
    FOR SELECT USING (auth.role() = 'authenticated');

-- STEP 4: Create Indexes
-- ==============================================

CREATE INDEX IF NOT EXISTS idx_processing_logs_user_id ON processing_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_processing_logs_processed_at ON processing_logs(processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_processing_logs_user_date ON processing_logs(user_id, processed_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id ON user_preferences(user_id);
CREATE INDEX IF NOT EXISTS idx_ai_model_metrics_name ON ai_model_metrics(model_name);

-- STEP 5: Grant Permissions
-- ==============================================

GRANT SELECT, INSERT ON processing_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_preferences TO authenticated;
GRANT SELECT ON ai_model_metrics TO authenticated;
GRANT USAGE ON SEQUENCE processing_logs_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE user_preferences_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE ai_model_metrics_id_seq TO authenticated;

-- STEP 6: Insert Sample Data (Optional)
-- ==============================================

INSERT INTO ai_model_metrics (model_name, average_processing_time, success_rate, total_requests)
VALUES ('gemini-2.0-pro-exp-02-05', 2.5, 99.5, 0)
ON CONFLICT (model_name) DO UPDATE SET last_updated = NOW(); 