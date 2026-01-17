-- Initialize PostgreSQL database for lecture-scraper
-- This file is executed automatically when the database container starts

-- Create users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL,
    full_name VARCHAR(255),
    hashed_password VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for users table
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Create courses table
CREATE TABLE IF NOT EXISTS courses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for courses table
CREATE INDEX IF NOT EXISTS idx_courses_user_id ON courses(user_id);

-- Create lectures table
CREATE TABLE IF NOT EXISTS lectures (
    id SERIAL PRIMARY KEY,
    lecture_id VARCHAR(255) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    course_id INTEGER REFERENCES courses(id) ON DELETE SET NULL,
    filename VARCHAR(255) NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration FLOAT,
    summary TEXT,
    qdrant_collection VARCHAR(255) NOT NULL
);

-- Create indexes for lectures table
CREATE INDEX IF NOT EXISTS idx_lectures_lecture_id ON lectures(lecture_id);
CREATE INDEX IF NOT EXISTS idx_lectures_user_id ON lectures(user_id);
CREATE INDEX IF NOT EXISTS idx_lectures_course_id ON lectures(course_id);

-- Create updated_at trigger function (optional, for future use)
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';
