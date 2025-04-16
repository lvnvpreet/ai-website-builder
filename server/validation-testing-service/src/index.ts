import express from 'express';
import dotenv from 'dotenv';
import puppeteer, { Browser, Page } from 'puppeteer'; // Import puppeteer

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for Validation & Testing Service (can be overridden by .env)
const port = process.env.PORT || 3015;

// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Validation & Testing Service is running!' });
});

// Placeholder endpoint for running validation tests
interface ValidationInput {
    bundleId: string; // ID of the website bundle to test
    previewUrl: string; // URL where the generated site can be accessed
    // Add other test parameters if needed (e.g., specific checks to run)
}

interface TestResult {
    name: string;
    passed: boolean;
    details: string;
    severity: 'INFO' | 'WARNING' | 'ERROR';
}

interface ScreenshotResult {
    desktop?: string; // Path or URL to desktop screenshot
    tablet?: string; // Path or URL to tablet screenshot
    mobile?: string; // Path or URL to mobile screenshot
}

interface ValidationOutput {
    bundleId: string;
    tests: TestResult[];
    screenshots: ScreenshotResult;
}


app.post('/validate', async (req: Request, res: Response) => {
    const validationInput: ValidationInput = req.body;

    if (!validationInput.bundleId || !validationInput.previewUrl) {
        return res.status(400).json({ message: 'Invalid input: "bundleId" and "previewUrl" are required.' });
    }

    console.log(`Received request to validate bundle: ${validationInput.bundleId} at ${validationInput.previewUrl}`);

    // TODO: Implement actual validation logic using Puppeteer
    // 1. Launch Puppeteer browser
    // 2. Open the previewUrl in different viewports (desktop, tablet, mobile)
    // 3. Take screenshots
    // 4. Run accessibility checks, link checks, console error checks, etc.
    // 5. Aggregate results
    // 6. Close browser

    // For now, just return placeholder info
    const placeholderTests: TestResult[] = [
        { name: "Desktop Screenshot", passed: true, details: "Placeholder", severity: "INFO" },
        { name: "Mobile Screenshot", passed: true, details: "Placeholder", severity: "INFO" },
        { name: "Accessibility Check", passed: false, details: "Not implemented", severity: "WARNING" },
    ];
    const placeholderScreenshots: ScreenshotResult = {};

    res.status(501).json({
        message: 'Validation logic not fully implemented yet.',
        bundleId: validationInput.bundleId,
        tests: placeholderTests,
        screenshots: placeholderScreenshots
    });
});


app.listen(port, () => {
  console.log(`[server]: Validation & Testing Service is running at http://localhost:${port}`);
});
