import express from 'express';
import dotenv from 'dotenv';

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for Analytics Collection Service (can be overridden by .env)
const port = process.env.PORT || 3020;

// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Analytics Collection Service is running!' });
});

// Placeholder endpoint for receiving analytics events
interface AnalyticsEventInput {
    userId?: string;
    sessionId?: string;
    eventType: string; // e.g., 'pageView', 'elementClick', 'wizardStepComplete', 'editAction'
    data: object; // Event-specific data payload
    timestamp?: string; // Optional timestamp from client, otherwise server sets it
    deviceInfo?: object; // Optional client device info
}
app.post('/event', async (req: Request, res: Response) => {
    const eventData: AnalyticsEventInput = req.body;

    if (!eventData.eventType || !eventData.data) {
        return res.status(400).json({ message: 'Invalid input: "eventType" and "data" are required.' });
    }

    const serverTimestamp = new Date().toISOString();
    console.log(`Received analytics event: ${eventData.eventType} at ${serverTimestamp}`, eventData);

    // TODO: Implement analytics event processing logic
    // 1. Validate/Sanitize eventData
    // 2. Add server timestamp if client timestamp is missing
    // 3. Send data to the time-series database (InfluxDB, TimescaleDB)
    //    - This will require setting up the DB client based on .env config
    //    - Example: influxClient.writePoint(...)

    // For now, just acknowledge receipt
    res.status(202).json({ message: 'Event received successfully.' });
});

// Placeholder endpoint for retrieving dashboard data (likely admin-only)
app.get('/analytics/dashboard', async (req: Request, res: Response) => {
    console.log("Request received for analytics dashboard data");
    // TODO: Implement logic to query aggregated data from the time-series DB
    res.status(501).json({ message: 'Dashboard endpoint not implemented yet.' });
});

// Placeholder endpoint for generating reports (likely admin-only)
app.get('/analytics/report/:type', async (req: Request, res: Response) => {
    const reportType = req.params.type;
    console.log(`Request received for analytics report type: ${reportType}`);
    // TODO: Implement logic to query and format specific reports from the time-series DB
    res.status(501).json({ message: `Report type '${reportType}' not implemented yet.` });
});


app.listen(port, () => {
  console.log(`[server]: Analytics Collection Service is running at http://localhost:${port}`);
});
