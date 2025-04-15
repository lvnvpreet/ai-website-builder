import { Router, RequestHandler } from 'express';
import {
    validateInput,
    analyzeInput,
    classifyInput,
    generateSeo
} from '../controllers/validationController';

const router = Router();

// Route to validate input data
router.post('/validate', validateInput as RequestHandler);

// Placeholder routes for other processing steps
router.post('/analyze', analyzeInput as RequestHandler);
router.post('/classify', classifyInput as RequestHandler);
router.post('/seo', generateSeo as RequestHandler);


export default router;
