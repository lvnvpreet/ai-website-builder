import { Router, RequestHandler } from 'express';
import {
    getOrCreateSession,
    updateSessionStep,
    getSessionProgress
} from '../controllers/sessionController';

const router = Router();

// Route to get or create a new session
// The actual logic for checking existing session ID needs to be implemented in the controller
router.get('/session', getOrCreateSession as RequestHandler);

// Route to update data for a specific step in a session
// We need both sessionId and step number in the path or body/query
// Using path parameters here for clarity:
router.put('/session/:sessionId/step/:step', updateSessionStep as RequestHandler);

// Route to get the progress of a specific session
router.get('/session/:sessionId/progress', getSessionProgress as RequestHandler);

// Note: The API endpoints in the original design diagram were slightly different
// (e.g., PUT /api/wizard/session/:step, GET /api/wizard/progress).
// We are using /api/wizard/session/:sessionId/... here for clarity in identifying the session.
// This can be adjusted later if needed.

export default router;
