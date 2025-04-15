import express, { Express, Request, Response } from 'express';
import dotenv from 'dotenv';
// Removed rate limiting imports as Redis is not set up yet
// import rateLimit from 'express-rate-limit';
// import RedisStore from 'rate-limit-redis';
// import redisClient from './utils/redisClient';
// import config from './config'; // config is still needed if used elsewhere, otherwise remove
import authRoutes from './routes/authRoutes'; // Import the auth routes

dotenv.config(); // Load environment variables from .env file

const app: Express = express();
const port = process.env.PORT || 3001; // Default to 3001 if PORT not set

app.use(express.json()); // Middleware to parse JSON bodies

// Rate Limiting code removed for now

// Basic route for testing
app.get('/', (req: Request, res: Response) => {
  res.send('Auth Service is running!');
});

// Mount the authentication routes
app.use('/api/auth', authRoutes);

// TODO: Add JWT middleware (Done via authenticateToken in routes)
// TODO: Add Rate limiting (Skipped for now)
// TODO: Add Database connection (PostgreSQL) (Done via pool)
// TODO: Add Redis connection (Skipped for now)

app.listen(port, () => {
  console.log(`[server]: Auth Service is running at http://localhost:${port}`);
});

export default app; // Export for potential testing or integration
