import { Request, Response } from 'express';
import redisClient from '../utils/redisClient'; // Import Redis client
import config from '../config'; // Import config for TTL
import crypto from 'crypto'; // For generating session IDs

// Placeholder function to get or create a session
export const getOrCreateSession = async (req: Request, res: Response): Promise<void> => {
    // TODO: Implement logic to check for existing session ID (e.g., from cookie or header)
    // TODO: If exists and valid in Redis, return it.
    // TODO: If not exists or invalid, create a new session ID.
    // TODO: Store initial session data in Redis with TTL.
    // TODO: Return the session ID (and potentially set a cookie).

    const sessionId = crypto.randomUUID(); // Example: Generate a new UUID
    const sessionKey = `session:${sessionId}`;
    const initialData = { currentStep: 1, completedSteps: [], formData: {} };

    try {
        // Store initial data with expiry (TTL from config)
        await redisClient.set(sessionKey, JSON.stringify(initialData), {
            EX: config.sessionTTL, // Use TTL from config
        });
        console.log(`[session-service] Created new session: ${sessionId}`);
        res.status(201).json({ sessionId: sessionId, message: "New session created." }); // Send back the new ID
    } catch (error) {
        console.error('[session-service] Error creating session:', error);
        res.status(500).json({ message: 'Failed to create session.' });
    }
};

// Placeholder function to update session data for a specific step
export const updateSessionStep = async (req: Request, res: Response): Promise<void> => {
    const { sessionId } = req.params; // Or get from header/cookie
    const { step } = req.params;
    const stepData = req.body; // Data for this specific step

    if (!sessionId || !step || !stepData) {
        res.status(400).json({ message: 'Session ID, step number, and step data are required.' });
        return;
    }

    const sessionKey = `session:${sessionId}`;
    const stepNumber = parseInt(step, 10); // Ensure step is a number

    if (isNaN(stepNumber)) {
        res.status(400).json({ message: 'Invalid step number provided.' });
        return;
    }

    try {
        // 1. Retrieve existing session data from Redis
        const existingSessionDataString = await redisClient.get(sessionKey);

        if (!existingSessionDataString) {
            res.status(404).json({ message: 'Session not found or expired.' });
            return;
        }

        // 2. Parse existing data
        let sessionData;
        try {
            sessionData = JSON.parse(existingSessionDataString);
        } catch (parseError) {
            console.error(`[session-service] Error parsing session data for ${sessionId}:`, parseError);
            res.status(500).json({ message: 'Failed to parse session data.' });
            return;
        }

        // 3. Merge new stepData with existing formData
        // Assuming stepData is an object containing form fields for the current step
        sessionData.formData = { ...sessionData.formData, ...stepData };

        // 4. Update completedSteps array (add current step if not already present)
        if (!sessionData.completedSteps.includes(stepNumber)) {
            sessionData.completedSteps.push(stepNumber);
            sessionData.completedSteps.sort((a: number, b: number) => a - b); // Keep sorted
        }

        // 5. Update currentStep (optional: could be handled by client logic)
        // Example: sessionData.currentStep = stepNumber + 1;

        // 6. Save updated session data back to Redis, refreshing TTL
        await redisClient.set(sessionKey, JSON.stringify(sessionData), {
            EX: config.sessionTTL // Refresh TTL on update (KEEPTTL is not a valid option here)
        });

        console.log(`[session-service] Updated session ${sessionId}, step ${step}`);
        res.status(200).json({ message: `Session step ${step} updated successfully.` });

    } catch (error) {
        console.error(`[session-service] Error updating session ${sessionId} step ${step}:`, error);
        res.status(500).json({ message: 'Failed to update session step.' });
    }
};

// Placeholder function to get session progress
export const getSessionProgress = async (req: Request, res: Response): Promise<void> => {
    const { sessionId } = req.params; // Or get from header/cookie

     if (!sessionId) {
        res.status(400).json({ message: 'Session ID is required.' });
        return;
    }

    const sessionKey = `session:${sessionId}`;

    try {
        // 1. Retrieve session data from Redis
        const sessionDataString = await redisClient.get(sessionKey);

        if (!sessionDataString) {
            res.status(404).json({ message: 'Session not found or expired.' });
            return;
        }

        // 2. Parse the data
        let sessionData;
        try {
            sessionData = JSON.parse(sessionDataString);
        } catch (parseError) {
            console.error(`[session-service] Error parsing session data for ${sessionId}:`, parseError);
            res.status(500).json({ message: 'Failed to parse session data.' });
            return;
        }

        // 3. Extract and return relevant progress info
        // Ensure default values if properties are missing (though they shouldn't be)
        const progress = {
            currentStep: sessionData.currentStep || 1,
            completedSteps: sessionData.completedSteps || [],
            // Optionally include other relevant metadata if needed
        };

        console.log(`[session-service] Retrieved progress for session ${sessionId}`);
        res.status(200).json(progress);

    } catch (error) {
        console.error(`[session-service] Error getting progress for session ${sessionId}:`, error);
        res.status(500).json({ message: 'Failed to get session progress.' });
    }
};
