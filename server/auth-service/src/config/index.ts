import dotenv from 'dotenv';

dotenv.config(); // Load .env file contents into process.env

// Validate essential environment variables
const requiredEnvVars = [
  'DATABASE_URL',
  'JWT_SECRET',
  'JWT_EXPIRES_IN',
  'REFRESH_TOKEN_SECRET',
  'REFRESH_TOKEN_EXPIRES_IN',
  'REDIS_URL',
  'PORT',
];

for (const varName of requiredEnvVars) {
  if (!process.env[varName]) {
    console.error(`Error: Environment variable ${varName} is not defined.`);
    // In a real application, you might want to throw an error or exit
    // For development, we'll log the error but allow continuation with defaults/undefined
    // throw new Error(`Missing required environment variable: ${varName}`);
  }
}

export const config = {
  port: process.env.PORT || '3001',
  databaseUrl: process.env.DATABASE_URL || 'postgresql://user:password@localhost:5432/mydatabase', // Example placeholder
  jwt: {
    secret: process.env.JWT_SECRET || 'your-very-secret-key', // Replace with a strong secret
    expiresIn: process.env.JWT_EXPIRES_IN || '1h',
  },
  refreshToken: {
    secret: process.env.REFRESH_TOKEN_SECRET || 'your-very-secret-refresh-key', // Replace with a strong secret
    expiresIn: process.env.REFRESH_TOKEN_EXPIRES_IN || '7d',
  },
  redisUrl: process.env.REDIS_URL || 'redis://localhost:6379', // Example placeholder
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // Limit each IP to 100 requests per windowMs
  },
};

export default config;
