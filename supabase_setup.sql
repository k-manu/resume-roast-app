-- ==============================================
-- Resume Roast App - Supabase Table Setup
-- ==============================================

-- Table for logging AI processing events (privacy-friendly)
CREATE TABLE IF NOT EXISTS processing_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    file_type VARCHAR(10) NOT NULL, -- 'pdf', 'txt'
    processing_time_seconds DECIMAL(10,3) NOT NULL,
    roast_length_chars INTEGER NOT NULL,
    success BOOLEAN DEFAULT TRUE,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Indexes for performance
    CONSTRAINT processing_logs_file_type_check CHECK (file_type IN ('pdf', 'txt', 'unknown'))
);

-- Table for storing user preferences
CREATE TABLE IF NOT EXISTS user_preferences (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE UNIQUE,
    preferences JSONB NOT NULL DEFAULT '{}',
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure one preference record per user
    UNIQUE(user_id)
);

-- Optional: Table for storing AI model performance metrics
CREATE TABLE IF NOT EXISTS ai_model_metrics (
    id BIGSERIAL PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL UNIQUE,
    average_processing_time DECIMAL(10,3),
    success_rate DECIMAL(5,2),
    total_requests INTEGER DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ==============================================
-- Row Level Security (RLS) Policies
-- ==============================================

-- Enable RLS on all tables
ALTER TABLE processing_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE ai_model_metrics ENABLE ROW LEVEL SECURITY;

-- Processing logs: Users can only see their own logs
CREATE POLICY "Users can view own processing logs" ON processing_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own processing logs" ON processing_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User preferences: Users can manage their own preferences
CREATE POLICY "Users can view own preferences" ON user_preferences
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own preferences" ON user_preferences
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own preferences" ON user_preferences
    FOR UPDATE USING (auth.uid() = user_id);

-- AI model metrics: Read-only for authenticated users
CREATE POLICY "Authenticated users can view model metrics" ON ai_model_metrics
    FOR SELECT USING (auth.role() = 'authenticated');

-- ==============================================
-- Indexes for Performance
-- ==============================================

-- Index for processing logs queries
CREATE INDEX IF NOT EXISTS idx_processing_logs_user_id 
    ON processing_logs(user_id);

CREATE INDEX IF NOT EXISTS idx_processing_logs_processed_at 
    ON processing_logs(processed_at DESC);

CREATE INDEX IF NOT EXISTS idx_processing_logs_user_date 
    ON processing_logs(user_id, processed_at DESC);

-- Index for user preferences
CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id 
    ON user_preferences(user_id);

-- Index for AI model metrics
CREATE INDEX IF NOT EXISTS idx_ai_model_metrics_name 
    ON ai_model_metrics(model_name);

-- ==============================================
-- Database Functions (Optional)
-- ==============================================

-- Function to get user statistics
CREATE OR REPLACE FUNCTION get_user_processing_stats(target_user_id UUID)
RETURNS TABLE (
    total_roasts BIGINT,
    successful_roasts BIGINT,
    avg_processing_time DECIMAL,
    total_processing_time DECIMAL,
    favorite_file_type TEXT,
    last_roast_date TIMESTAMP WITH TIME ZONE
) 
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*) as total_roasts,
        COUNT(*) FILTER (WHERE success = true) as successful_roasts,
        ROUND(AVG(processing_time_seconds), 3) as avg_processing_time,
        ROUND(SUM(processing_time_seconds), 3) as total_processing_time,
        MODE() WITHIN GROUP (ORDER BY file_type) as favorite_file_type,
        MAX(processed_at) as last_roast_date
    FROM processing_logs 
    WHERE user_id = target_user_id;
END;
$$;

-- Function to update AI model metrics (called by application)
CREATE OR REPLACE FUNCTION update_model_metrics(
    model_name_param VARCHAR(100),
    processing_time DECIMAL(10,3),
    success_flag BOOLEAN
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    current_metrics RECORD;
BEGIN
    -- Get current metrics
    SELECT * INTO current_metrics 
    FROM ai_model_metrics 
    WHERE model_name = model_name_param;
    
    IF current_metrics IS NULL THEN
        -- Insert new model metrics
        INSERT INTO ai_model_metrics (
            model_name, 
            average_processing_time, 
            success_rate, 
            total_requests
        ) VALUES (
            model_name_param,
            processing_time,
            CASE WHEN success_flag THEN 100.0 ELSE 0.0 END,
            1
        );
    ELSE
        -- Update existing metrics
        UPDATE ai_model_metrics 
        SET 
            average_processing_time = (
                (current_metrics.average_processing_time * current_metrics.total_requests + processing_time) 
                / (current_metrics.total_requests + 1)
            ),
            success_rate = (
                (current_metrics.success_rate * current_metrics.total_requests + 
                 CASE WHEN success_flag THEN 100.0 ELSE 0.0 END) 
                / (current_metrics.total_requests + 1)
            ),
            total_requests = current_metrics.total_requests + 1,
            last_updated = NOW()
        WHERE model_name = model_name_param;
    END IF;
END;
$$;

-- ==============================================
-- Sample Data (Optional)
-- ==============================================

-- Insert initial AI model metrics (safe insertion)
INSERT INTO ai_model_metrics (model_name, average_processing_time, success_rate, total_requests)
VALUES ('gemini-2.0-pro-exp-02-05', 2.5, 99.5, 0)
ON CONFLICT (model_name) DO UPDATE SET
    last_updated = NOW();

-- ==============================================
-- Grants and Permissions
-- ==============================================

-- Grant necessary permissions to authenticated users
GRANT SELECT, INSERT ON processing_logs TO authenticated;
GRANT SELECT, INSERT, UPDATE ON user_preferences TO authenticated;
GRANT SELECT ON ai_model_metrics TO authenticated;

-- Grant usage on sequences
GRANT USAGE ON SEQUENCE processing_logs_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE user_preferences_id_seq TO authenticated;
GRANT USAGE ON SEQUENCE ai_model_metrics_id_seq TO authenticated; 