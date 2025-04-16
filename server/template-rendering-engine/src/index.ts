import express from 'express';
import dotenv from 'dotenv';
import React from 'react'; // Import React
import ReactDOMServer from 'react-dom/server'; // Import ReactDOMServer for SSR
import PlaceholderTemplate from './templates/PlaceholderTemplate'; // Import the placeholder template

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for Template Rendering Engine (can be overridden by .env)
const port = process.env.PORT || 3014;

// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Template Rendering Engine is running!' });
});

// Define structure for content input, mirroring TemplateProps in PlaceholderTemplate.tsx
interface SectionData {
    id: string;
    title: string;
    content: string;
    seoScore?: number;
}
interface PageData {
    type: string;
    sections: SectionData[];
}
interface ContentData {
    pages: PageData[];
}

// Placeholder endpoint for rendering a template with content
interface RenderInput {
    templateId: string;
    content: ContentData; // Use the more specific type
    branding: object; // Branding info (colors, fonts, etc.) - keep as object for now
}

app.post('/render', async (req: Request, res: Response) => {
    const renderInput: RenderInput = req.body;

    if (!renderInput.templateId || !renderInput.content) {
        return res.status(400).json({ message: 'Invalid input: "templateId" and "content" are required.' });
    }

    console.log(`Received request to render template: ${renderInput.templateId}`);

    // TODO: Implement actual rendering logic
    // 1. Load the specified template component (e.g., React component)
    // 2. Use React SSR (ReactDOMServer.renderToString or renderToPipeableStream)
    //    or another templating engine to combine the template with the content data.
    // 3. Return the generated static HTML/CSS/JS bundle (or parts of it).

    try {
        // Basic SSR using the placeholder template
        // In a real scenario, you'd dynamically import the correct template based on templateId
        if (renderInput.templateId === 'placeholder') { // Example check
            const htmlOutput = ReactDOMServer.renderToString(
                React.createElement(PlaceholderTemplate, {
                    content: renderInput.content,
                    branding: renderInput.branding
                })
            );
            // Send the rendered HTML string
            res.setHeader('Content-Type', 'text/html');
            res.send(htmlOutput);
        } else {
            res.status(404).json({ message: `Template with ID '${renderInput.templateId}' not found or supported.` });
        }

    } catch (error: any) {
        console.error(`Error rendering template ${renderInput.templateId}:`, error);
        res.status(500).json({ message: 'Error during template rendering.', error: error.message });
    }
});


app.listen(port, () => {
  console.log(`[server]: Template Rendering Engine is running at http://localhost:${port}`);
});
