import dotenv from 'dotenv';

dotenv.config(); // Load .env file contents into process.env

// Validate essential environment variables
const requiredEnvVars = [
  'REDIS_URL',
  'PORT',
  'SESSION_TTL_SECONDS'
];

for (const varName of requiredEnvVars) {
  if (!process.env[varName]) {
    console.warn(`Warning: Environment variable ${varName} is not defined. Using default value.`);
    // Consider throwing an error in production if a variable is critical
    // throw new Error(`Missing required environment variable: ${varName}`);
  }
}

// Parse SESSION_TTL_SECONDS to a number, providing a default
const sessionTtlSeconds = parseInt(process.env.SESSION_TTL_SECONDS || '86400', 10);
if (isNaN(sessionTtlSeconds)) {
    console.warn(`Warning: Invalid SESSION_TTL_SECONDS value. Using default 86400 seconds (24 hours).`);
}

export const config = {
  port: process.env.PORT || '3002',
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379', // Default Redis URL
  sessionTTL: isNaN(sessionTtlSeconds) ? 86400 : sessionTtlSeconds, // Use parsed value or default
};

export default config;
