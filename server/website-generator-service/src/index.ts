import express from 'express';
import dotenv from 'dotenv';
import axios from 'axios';
import { v4 as uuidv4 } from 'uuid'; // Import UUID generator

// Define types explicitly if needed (often inferred correctly)
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

// Configuration for dependent services
const TEMPLATE_RENDERING_ENGINE_URL = process.env.TEMPLATE_RENDERING_ENGINE_URL || 'http://localhost:3014';
const ASSET_PROCESSING_SERVICE_URL = process.env.ASSET_PROCESSING_SERVICE_URL || 'http://localhost:3013';
const VALIDATION_TESTING_SERVICE_URL = process.env.VALIDATION_TESTING_SERVICE_URL || 'http://localhost:3015';
// Placeholder for where previews might be served (could be another service or this one)
const PREVIEW_SERVICE_BASE_URL = process.env.PREVIEW_SERVICE_BASE_URL || 'http://localhost:3016'; // Assuming a preview service runs on 3016

// In-memory store for generated bundles (Replace with persistent storage in production)
const generatedBundles: Map<string, { htmlContent: string }> = new Map();

const app: Express = express();
const port = process.env.WEBSITE_GENERATOR_PORT || 3012;

// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Website Generator Service is running!' });
});

// --- Helper Functions ---

// Placeholder function to extract asset URLs from content structure
// TODO: Implement robust asset extraction based on actual content format
function extractAssetUrls(content: any): string[] {
    const urls: string[] = [];
    // Simple example: Look for image URLs in section content strings
    if (content && Array.isArray(content.pages)) {
        for (const page of content.pages) {
            if (page && Array.isArray(page.sections)) {
                for (const section of page.sections) {
                    if (section && typeof section.content === 'string') {
                        // Basic regex to find potential image URLs (adjust as needed)
                        const potentialUrls = section.content.match(/https?:\/\/[^\s]+\.(?:jpg|jpeg|png|gif|webp|svg)/gi);
                        if (potentialUrls) {
                            urls.push(...potentialUrls);
                        }
                        // Add logic for other asset types or structured asset fields
                    }
                }
            }
        }
    }
    // Remove duplicates
    return [...new Set(urls)];
}


// --- API Endpoints ---

// Endpoint for website compilation, asset processing, rendering, and validation trigger
app.post('/compile', async (req: Request, res: Response) => {
  const { templateId, content, branding } = req.body;

  if (!templateId || !content || !branding) {
    return res.status(400).json({ message: 'Invalid input: "templateId", "content", and "branding" are required.' });
  }

  const bundleId = uuidv4(); // Generate a unique ID for this compilation attempt
  console.log(`Received request to compile website. Bundle ID: ${bundleId}, Template: ${templateId}`);

  try {
    // 1. Extract asset URLs from the content
    const assetUrls = extractAssetUrls(content);
    let processedAssetsInfo: any = { processedAssets: [] }; // Default structure

    // 2. Call Asset Processing Service (if assets found)
    if (assetUrls.length > 0) {
        console.log(`Found ${assetUrls.length} potential assets to process.`);
        try {
            const assetInput = assetUrls.map(url => ({ assetUrl: url }));
            const assetResponse = await axios.post(`${ASSET_PROCESSING_SERVICE_URL}/process`, {
                assets: assetInput
            });
            // TODO: Use the actual processed asset data when the service is implemented
            // For now, we might just log it or store a placeholder
            console.log('Asset processing service response status:', assetResponse.status);
            // Store or map the response data appropriately
            processedAssetsInfo = assetResponse.data;
            console.log(`Asset processing for bundle ${bundleId} completed.`);
        } catch (assetError: any) {
            console.error(`Error calling Asset Processing Service for bundle ${bundleId}:`, assetError.message);
            // Decide if this is a critical error. For now, log and continue.
            // Consider adding error info to the final response.
        }
    } else {
        console.log(`No potential asset URLs found in content for bundle ${bundleId}.`);
    }


    // 3. Call the Template Rendering Engine's /render endpoint
    //    (Pass original content, branding, and potentially processed asset info)
    const renderPayload = {
        templateId,
        content, // Pass original content structure
        branding,
        // Include processed asset info for the template engine to use
        processedAssets: processedAssetsInfo.processedAssets || []
    };

    console.log(`Calling Template Rendering Engine for bundle ${bundleId} at ${TEMPLATE_RENDERING_ENGINE_URL}/render`);
    const renderResponse = await axios.post(`${TEMPLATE_RENDERING_ENGINE_URL}/render`, renderPayload);

    // 4. Store the generated HTML (replace with proper storage)
    const renderedHtml = renderResponse.data;
    generatedBundles.set(bundleId, { htmlContent: renderedHtml });
    console.log(`Template rendering successful for bundle ${bundleId}. Stored content.`);

    // 5. Construct Preview URL
    const previewUrl = `${PREVIEW_SERVICE_BASE_URL}/preview/${bundleId}`; // URL for validation service

    // 6. Call Validation Testing Service
    let validationResults: any = { tests: [], screenshots: {} }; // Default structure
    try {
        console.log(`Calling Validation Testing Service for bundle ${bundleId} at ${VALIDATION_TESTING_SERVICE_URL}/validate`);
        const validationResponse = await axios.post(`${VALIDATION_TESTING_SERVICE_URL}/validate`, {
            bundleId,
            previewUrl
        });
        validationResults = validationResponse.data;
        console.log(`Validation testing service response status for bundle ${bundleId}:`, validationResponse.status);
    } catch (validationError: any) {
        console.error(`Error calling Validation Testing Service for bundle ${bundleId}:`, validationError.message);
        // Log error and continue, returning placeholder/error info for validation
        validationResults = {
            error: `Failed to run validation: ${validationError.message}`,
            tests: [],
            screenshots: {}
        };
    }

    // 7. Return the final result including bundle ID, preview URL, and validation outcome
    res.status(200).json({
        message: `Website compilation initiated successfully for bundle ${bundleId}.`,
        bundleId: bundleId,
        previewUrl: previewUrl, // Provide the URL for the client/user
        validation: validationResults // Include results from validation service
    });


  } catch (error: any) { // Catch errors from rendering or other steps
    console.error(`Error during compilation process for bundle ${bundleId}:`, error.message);
    if (axios.isAxiosError(error) && error.response) {
      // Forward the error from the rendering engine if possible
      res.status(error.response.status).json({
        message: `Error during template rendering (from engine): ${error.response.data?.message || error.message}`,
        engineError: error.response.data
      });
    } else {
      // General server error
      res.status(500).json({ message: 'Internal server error during website compilation.' });
    }
  }
});

// Placeholder endpoint for preview - This might live here or in a dedicated Preview Service
// This endpoint retrieves the stored HTML for a given bundle ID.
app.get('/preview/:id', (req: Request, res: Response) => {
    const bundleId = req.params.id;
    console.log(`Received request for preview of bundle: ${bundleId}`);

    const bundleData = generatedBundles.get(bundleId);

    if (bundleData) {
        // Serve the stored HTML content
        res.setHeader('Content-Type', 'text/html');
        res.send(bundleData.htmlContent);
    } else {
        res.status(404).json({ message: `Preview for bundle ${bundleId} not found.` });
    }
});


app.listen(port, () => {
  console.log(`[server]: Website Generator Service is running at http://localhost:${port}`);
});
