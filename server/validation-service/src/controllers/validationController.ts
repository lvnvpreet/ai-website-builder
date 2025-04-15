import { Request, Response } from 'express';
import { z } from 'zod'; // Import Zod for schema definition
import axios from 'axios'; // Import axios
import config from '../config'; // Import config

// Define a basic example schema (adjust based on actual wizard input)
const wizardInputSchema = z.object({
  projectName: z.string().min(1, { message: "Project name is required" }),
  businessType: z.string().optional(),
  contactEmail: z.string().email({ message: "Invalid email address" }).optional(),
  // Add other fields from your wizard steps here...
  // Add a 'text' field if it's expected by the analyze endpoint
  text: z.string().optional(), // Assuming text might be part of the overall wizard data
});

// POST /api/process/validate
export const validateInput = async (req: Request, res: Response): Promise<void> => {
    const inputData = req.body;

    try {
        // Validate the input data against the schema
        wizardInputSchema.parse(inputData); // Throws an error if validation fails

        // If validation passes:
        // TODO: Implement sanitization (e.g., trimming strings, removing harmful scripts)
        // TODO: Implement normalization (e.g., standardizing formats)

        res.status(200).json({ message: "Input data is valid." });

    } catch (error) {
        if (error instanceof z.ZodError) {
            // Zod validation error
            console.error('[validation-service] Validation failed:', error.errors);
            // Return detailed validation errors
            res.status(400).json({ message: "Validation failed", errors: error.flatten().fieldErrors });
        } else {
            // Other unexpected errors
            console.error('[validation-service] Unexpected error during validation:', error);
            res.status(500).json({ message: 'Internal server error during validation.' });
        }
    }
};

// POST /api/process/analyze
export const analyzeInput = async (req: Request, res: Response): Promise<void> => {
    const inputData = req.body;
    // Assume inputData contains a 'text' field based on metadata service input schema
    const textToAnalyze = inputData.text;

    if (!textToAnalyze) {
        res.status(400).json({ message: 'Text field is required for analysis.' });
        return;
    }

    console.log(`[validation-service] Received request for /analyze for text: ${textToAnalyze.substring(0, 50)}...`);

    try {
        // Call the metadata extraction service
        const metadataServiceUrl = `${config.metadataExtractionServiceUrl}/extract`;
        console.log(`[validation-service] Calling metadata service at: ${metadataServiceUrl}`);

        const response = await axios.post(metadataServiceUrl, {
            text: textToAnalyze
            // Pass sessionId if needed: sessionId: inputData.sessionId
        });

        // Forward the successful response from the metadata service
        res.status(response.status).json(response.data);

    } catch (error: any) { // Use 'any' or a more specific error type if known
        console.error('[validation-service] Error calling metadata extraction service:', error.message);

        // Handle errors from the axios request or the downstream service
        if (axios.isAxiosError(error) && error.response) {
            // Forward the error status and data from the downstream service if available
            res.status(error.response.status).json({
                message: 'Error during metadata extraction.',
                downstreamError: error.response.data
            });
        } else {
            // Generic internal server error for other issues (e.g., network error)
            res.status(500).json({ message: 'Internal server error while calling analysis service.' });
        }
    }
};

// POST /api/process/classify
export const classifyInput = async (req: Request, res: Response): Promise<void> => {
    const inputData = req.body;
    // Assume inputData contains fields needed for classification (e.g., business_description)
    const description = inputData.business_description;
    const categories = inputData.selected_categories; // Optional

    if (!description) {
        res.status(400).json({ message: 'Business description is required for classification.' });
        return;
    }

    console.log(`[validation-service] Received request for /classify for description: ${description.substring(0, 50)}...`);

    try {
        // Call the industry classifier service
        const classifierServiceUrl = `${config.industryClassifierServiceUrl}/classify`;
        console.log(`[validation-service] Calling classifier service at: ${classifierServiceUrl}`);

        const response = await axios.post(classifierServiceUrl, {
            business_description: description,
            selected_categories: categories
            // Pass sessionId if needed: sessionId: inputData.sessionId
        });

        // Forward the successful response from the classifier service
        res.status(response.status).json(response.data);

    } catch (error: any) {
        console.error('[validation-service] Error calling industry classifier service:', error.message);

        // Handle errors from the axios request or the downstream service
        if (axios.isAxiosError(error) && error.response) {
            res.status(error.response.status).json({
                message: 'Error during industry classification.',
                downstreamError: error.response.data
            });
        } else {
            res.status(500).json({ message: 'Internal server error while calling classifier service.' });
        }
    }
};

// POST /api/process/seo
export const generateSeo = async (req: Request, res: Response): Promise<void> => {
    const inputData = req.body;
    // Assume inputData contains 'text' and potentially 'target_keywords'
    const textToAnalyze = inputData.text;
    const targetKeywords = inputData.target_keywords; // Optional

    if (!textToAnalyze) {
        res.status(400).json({ message: 'Text field is required for SEO analysis.' });
        return;
    }

    console.log(`[validation-service] Received request for /seo for text: ${textToAnalyze.substring(0, 50)}...`);

    try {
        // Call the SEO analyzer service
        const seoServiceUrl = `${config.seoAnalyzerServiceUrl}/seo`;
        console.log(`[validation-service] Calling SEO analyzer service at: ${seoServiceUrl}`);

        const response = await axios.post(seoServiceUrl, {
            text: textToAnalyze,
            target_keywords: targetKeywords
            // Pass sessionId if needed: sessionId: inputData.sessionId
        });

        // Forward the successful response from the SEO service
        res.status(response.status).json(response.data);

    } catch (error: any) {
        console.error('[validation-service] Error calling SEO analyzer service:', error.message);

        // Handle errors from the axios request or the downstream service
        if (axios.isAxiosError(error) && error.response) {
            res.status(error.response.status).json({
                message: 'Error during SEO analysis.',
                downstreamError: error.response.data
            });
        } else {
            res.status(500).json({ message: 'Internal server error while calling SEO analyzer service.' });
        }
    }
};
