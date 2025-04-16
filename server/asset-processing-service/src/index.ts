import express from 'express';
import dotenv from 'dotenv';
import sharp from 'sharp'; // Import sharp for image processing

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for Asset Processing Service (can be overridden by .env)
const port = process.env.PORT || 3013;

// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Asset Processing Service is running!' });
});

// Placeholder endpoint for processing assets
interface AssetInput {
    assetUrl: string; // URL or path to the original asset
    // Add other parameters like desired formats, sizes, quality settings
}

interface ProcessedAssetInfo {
    originalUrl: string;
    processedUrls: {
        desktop?: string;
        tablet?: string;
        mobile?: string;
        // Add other formats/sizes as needed
    };
    type: string; // e.g., 'image/jpeg', 'image/webp'
    // Add other metadata like dimensions, size
}

app.post('/process', async (req: Request, res: Response) => {
    const assetsToProcess: AssetInput[] = req.body.assets; // Assuming input is { "assets": [...] }

    if (!Array.isArray(assetsToProcess) || assetsToProcess.length === 0) {
        return res.status(400).json({ message: 'Invalid input: "assets" array is required.' });
    }

    console.log(`Received request to process ${assetsToProcess.length} assets.`);

    const results: ProcessedAssetInfo[] = [];

    // TODO: Implement actual asset processing loop using sharp
    // - Download image if URL
    // - Use sharp to resize, change format, optimize
    // - Upload processed assets to storage (e.g., S3)
    // - Collect URLs/info for the response

    for (const asset of assetsToProcess) {
        console.log(`Processing asset: ${asset.assetUrl}`);
        // Placeholder result
        results.push({
            originalUrl: asset.assetUrl,
            processedUrls: {}, // Empty for now
            type: "image/jpeg" // Placeholder
        });
    }

    // For now, just return placeholder info
    res.status(501).json({
        message: 'Asset processing logic not fully implemented yet.',
        processedAssets: results
    });
});


app.listen(port, () => {
  console.log(`[server]: Asset Processing Service is running at http://localhost:${port}`);
});
