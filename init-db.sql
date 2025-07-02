-- Initialize database for AI Code Analysis Microservice

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create analysis_results table
CREATE TABLE IF NOT EXISTS analysis_results (
    id SERIAL PRIMARY KEY,
    file_path VARCHAR(500) UNIQUE NOT NULL,
    language VARCHAR(50) NOT NULL,
    functions JSONB,
    classes JSONB,
    imports JSONB,
    metrics JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create alert_data table
CREATE TABLE IF NOT EXISTS alert_data (
    id SERIAL PRIMARY KEY,
    alert_type VARCHAR(100) NOT NULL,
    alert_message TEXT,
    file_path VARCHAR(500),
    line_number INTEGER,
    severity VARCHAR(20),
    analysis_result JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_analysis_results_file_path 
ON analysis_results(file_path);

CREATE INDEX IF NOT EXISTS idx_analysis_results_language 
ON analysis_results(language);

CREATE INDEX IF NOT EXISTS idx_analysis_results_created_at 
ON analysis_results(created_at);

CREATE INDEX IF NOT EXISTS idx_alert_data_created_at 
ON alert_data(created_at);

CREATE INDEX IF NOT EXISTS idx_alert_data_alert_type 
ON alert_data(alert_type);

CREATE INDEX IF NOT EXISTS idx_alert_data_severity 
ON alert_data(severity);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger for analysis_results table
CREATE TRIGGER update_analysis_results_updated_at 
    BEFORE UPDATE ON analysis_results 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Insert some sample data for testing
INSERT INTO analysis_results (file_path, language, functions, classes, imports, metrics) VALUES
(
    '/app/repo/sample.py',
    'python',
    '[{"name": "main", "parameters": [], "complexity": 1}]',
    '[{"name": "SampleClass", "methods": [], "complexity": 1}]',
    '[{"text": "import os", "type": "import"}]',
    '{"total_lines": 10, "code_lines": 8, "comment_lines": 1, "blank_lines": 1, "average_complexity": 1.0}'
) ON CONFLICT (file_path) DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO code_analysis_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO code_analysis_user; 