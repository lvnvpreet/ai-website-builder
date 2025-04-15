import express, { Express, Request, Response } from 'express';
import dotenv from 'dotenv';
import sessionRoutes from './routes/sessionRoutes'; // Import session routes
import redisClient from './utils/redisClient'; // Import Redis client (will attempt connection on import)
import config from './config'; // Import config

dotenv.config(); // Load environment variables from .env file

const app: Express = express();
const port = process.env.PORT || 3002; // Use a different port, e.g., 3002

app.use(express.json()); // Middleware to parse JSON bodies

// Basic route for testing
app.get('/', (req: Request, res: Response) => {
  res.send('Session Service is running!');
});

// Mount the session routes
app.use('/api/wizard', sessionRoutes); // Mount under /api/wizard prefix

// TODO: Add Redis connection check (Handled by redisClient.ts on import and error listener)
// TODO: Add routes for session management

app.listen(port, async () => { // Make the callback async
  console.log(`[server]: Session Service is running at http://localhost:${config.port}`); // Use config.port
  // Explicitly try connecting Redis client after server starts listening
  try {
    // Check if client is already connecting or connected to avoid issues
    if (!redisClient.isReady && !redisClient.isOpen) {
        console.log('[redis][session-service]: Attempting to connect Redis client...');
        await redisClient.connect();
        // Success message is handled by the 'connect' event listener in redisClient.ts
    } else {
         console.log('[redis][session-service]: Redis client already connected or connecting.');
    }
  } catch (err) {
    // Error during explicit connect attempt (might be redundant due to listener)
    console.error('[redis][session-service]: Error during explicit Redis connect attempt:', err);
  }
});

export default app; // Export for potential testing or integration
