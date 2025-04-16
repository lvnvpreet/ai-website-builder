import express from 'express';
import dotenv from 'dotenv';
import http from 'http'; // Import http module
import { WebSocketServer, WebSocket } from 'ws'; // Import WebSocket server

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for Preview Rendering Service (can be overridden by .env)
const port = process.env.PORT || 3016;

// Create HTTP server from Express app
const server = http.createServer(app);

// Create WebSocket server attached to the HTTP server
const wss = new WebSocketServer({ server });

// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Preview Rendering Service is running!' });
});

// Placeholder endpoint to serve the preview page (which would contain the iframe)
app.get('/preview/:projectId', (req: Request, res: Response) => {
    const projectId = req.params.projectId;
    console.log(`Serving preview frame for project: ${projectId}`);
    // TODO: Serve an HTML page that contains the iframe logic
    // The iframe source would point to where the actual generated site is hosted/served
    // This page would also include client-side JS to connect to the WebSocket
    res.status(501).send(`<html><body><h1>Preview Frame for ${projectId} (Not Implemented)</h1><script>/* WebSocket connection logic here */</script></body></html>`);
});


// WebSocket connection handling
wss.on('connection', (ws: WebSocket) => {
    console.log('Client connected via WebSocket');

    // Handle messages from clients (e.g., device change requests)
    ws.on('message', (message: Buffer) => {
        try {
            const data = JSON.parse(message.toString());
            console.log('Received WebSocket message:', data);
            // TODO: Handle incoming messages (e.g., change device viewport in iframe)
            ws.send(JSON.stringify({ type: 'ack', message: 'Message received' }));
        } catch (error) {
            console.error('Failed to parse WebSocket message or invalid message format:', error);
            ws.send(JSON.stringify({ type: 'error', message: 'Invalid message format' }));
        }
    });

    ws.on('close', () => {
        console.log('Client disconnected');
    });

    ws.on('error', (error) => {
        console.error('WebSocket error:', error);
    });

    // Send a welcome message
    ws.send(JSON.stringify({ type: 'info', message: 'Connected to Preview Service WebSocket' }));
});

// Function to broadcast updates to all connected clients (called by other services potentially)
function broadcastPreviewUpdate(projectId: string, updateData: any) {
    console.log(`Broadcasting preview update for project ${projectId}`);
    const message = JSON.stringify({ type: 'preview:update', projectId, data: updateData });
    wss.clients.forEach((client) => {
        if (client.readyState === WebSocket.OPEN) {
            // TODO: Add logic to only send to clients viewing the specific projectId if needed
            client.send(message);
        }
    });
}

// Example: Simulate an update after 10 seconds (for testing)
// setTimeout(() => {
//     broadcastPreviewUpdate('test-project-123', { elementId: 'hero-text', newContent: 'Updated Content!' });
// }, 10000);


// Start the HTTP server (which also starts the WebSocket server)
server.listen(port, () => {
  console.log(`[server]: Preview Rendering Service (HTTP & WebSocket) is running at http://localhost:${port}`);
});
