import express, { Express, Request, Response } from 'express';
import dotenv from 'dotenv';
import validationRoutes from './routes/validationRoutes'; // Import validation routes
import config from './config'; // Import config

dotenv.config(); // Load environment variables from .env file

const app: Express = express();
const port = process.env.PORT || 3003; // Use a different port, e.g., 3003

app.use(express.json()); // Middleware to parse JSON bodies

// Basic route for testing
app.get('/', (req: Request, res: Response) => {
  res.send('Validation Service is running!');
});

// Mount the validation routes
app.use('/api/process', validationRoutes); // Mount under /api/process prefix

// TODO: Add routes for validation endpoints (e.g., /validate, /analyze) (Partially done)

app.listen(port, () => {
  console.log(`[server]: Validation Service is running at http://localhost:${config.port}`); // Use config.port
});

export default app; // Export for potential testing or integration
