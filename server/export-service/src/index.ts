import express from 'express';
import dotenv from 'dotenv';
import archiver from 'archiver'; // For creating zip archives
import fs from 'fs'; // File system access (needed for reading generated files)
import path from 'path'; // Path manipulation

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for Export Service (can be overridden by .env)
const port = process.env.PORT || 3018;

// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Export Service is running!' });
});

// Placeholder endpoint for exporting as static ZIP
interface ExportStaticInput {
    projectId: string;
    bundlePath: string; // Path to the generated website bundle directory
}
app.post('/export/static', async (req: Request, res: Response) => {
    const { projectId, bundlePath }: ExportStaticInput = req.body;

    if (!projectId || !bundlePath) {
        return res.status(400).json({ message: 'Invalid input: "projectId" and "bundlePath" are required.' });
    }

    console.log(`Received request to export static site for project: ${projectId} from ${bundlePath}`);

    // TODO: Implement actual static export logic
    // 1. Verify bundlePath exists and contains expected files (index.html etc.)
    // 2. Create a zip archive using 'archiver'
    // 3. Add files from bundlePath to the archive
    // 4. Finalize the archive
    // 5. Stream the archive back to the client or provide a download link

    // For now, return placeholder
    res.setHeader('Content-Type', 'application/zip');
    res.setHeader('Content-Disposition', `attachment; filename=${projectId}-static-export.zip`);
    // Create a dummy zip stream for now (replace with actual archiver logic)
    const archive = archiver('zip', { zlib: { level: 9 } });
    archive.pipe(res); // Pipe archive data to response
    archive.append('Placeholder content', { name: 'readme.txt' }); // Add a dummy file
    await archive.finalize();

    // Note: In a real scenario, you'd likely generate the zip to a temp location
    // and then stream it or provide a link, rather than streaming directly during generation.
    // res.status(501).json({ message: 'Static export not fully implemented.' });
});

// Placeholder endpoint for exporting to CMS format
app.post('/export/cms/:platform', async (req: Request, res: Response) => {
    const platform = req.params.platform;
    const { projectId, bundlePath } = req.body; // Assuming similar input

    if (!projectId || !bundlePath) {
        return res.status(400).json({ message: 'Invalid input: "projectId" and "bundlePath" are required.' });
    }

    console.log(`Received request to export site for project ${projectId} to CMS: ${platform}`);

    // TODO: Implement CMS-specific export logic
    // - Adapt HTML/CSS/JS for WordPress theme, Shopify theme, etc.
    // - Package necessary files (theme.json, templates, assets)
    // - Create appropriate archive format

    res.status(501).json({ message: `CMS export for ${platform} not implemented yet.` });
});

// Placeholder endpoint for exporting as container
app.post('/export/container', async (req: Request, res: Response) => {
    const { projectId, bundlePath } = req.body; // Assuming similar input

     if (!projectId || !bundlePath) {
        return res.status(400).json({ message: 'Invalid input: "projectId" and "bundlePath" are required.' });
    }

    console.log(`Received request to export site for project ${projectId} as container`);

    // TODO: Implement containerization logic
    // - Create a Dockerfile (e.g., using nginx or node static server)
    // - Copy bundlePath contents into the Docker image context
    // - Potentially build the image or provide the Dockerfile + context as a tarball

    res.status(501).json({ message: 'Container export not implemented yet.' });
});


app.listen(port, () => {
  console.log(`[server]: Export Service is running at http://localhost:${port}`);
});
