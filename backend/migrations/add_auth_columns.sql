-- Migration: Add authentication columns to users table
-- Version: 1.0
-- Description: Adds phone and Google OAuth authentication support

-- Add phone_number column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone_number VARCHAR(20);

-- Add phone_verified column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS phone_verified BOOLEAN DEFAULT FALSE;

-- Add google_id column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS google_id VARCHAR(255);

-- Add auth_providers column (JSONB for PostgreSQL)
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS auth_providers JSONB DEFAULT '[]';

-- Add default_auth_method column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS default_auth_method VARCHAR(20) DEFAULT 'password';

-- Add full_name column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS full_name VARCHAR(255);

-- Add avatar_url column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500);

-- Add last_login column
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS last_login TIMESTAMP WITH TIME ZONE;

-- Create phone_verifications table
CREATE TABLE IF NOT EXISTS phone_verifications (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) NOT NULL,
    verification_code VARCHAR(6) NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better query performance
CREATE INDEX IF NOT EXISTS idx_users_phone_number ON users(phone_number);
CREATE INDEX IF NOT EXISTS idx_users_google_id ON users(google_id);
CREATE INDEX IF NOT EXISTS idx_phone_verifications_phone ON phone_verifications(phone_number);

-- Add unique constraints if phone numbers should be unique
-- ALTER TABLE users ADD CONSTRAINT unique_phone_number UNIQUE (phone_number);

-- Add comment for documentation
COMMENT ON COLUMN users.phone_number IS 'Vietnamese phone number format: +84, 0, or 84 followed by 9-10 digits';
COMMENT ON COLUMN users.phone_verified IS 'Whether the phone number has been verified via SMS';
COMMENT ON COLUMN users.google_id IS 'Google OAuth user ID for linking Google accounts';
COMMENT ON COLUMN users.auth_providers IS 'Array of authentication methods: ["password", "phone", "google"]';
COMMENT ON COLUMN users.default_auth_method IS 'Preferred authentication method for this user';
COMMENT ON COLUMN users.full_name IS 'User full name from Google profile';
COMMENT ON COLUMN users.avatar_url IS 'User avatar URL from Google profile';
COMMENT ON COLUMN users.last_login IS 'Last login timestamp';

-- Verify migration
SELECT 'Migration completed successfully!' as status;