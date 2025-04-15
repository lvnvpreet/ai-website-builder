import { Router, RequestHandler } from 'express';
import {
  register,
  login,
  getProfile,
  refreshToken,
  logout,
  requestPasswordReset, // Add requestPasswordReset
  resetPassword         // Add resetPassword
} from '../controllers/authController';
import { authenticateToken } from '../middleware/authMiddleware'; // Import the middleware

const router = Router();

// Define authentication routes
// Explicitly cast controller functions to RequestHandler if needed,
// although usually not necessary if signatures match.
// Let's try without casting first, relying on signature compatibility.
router.post('/register', register as RequestHandler);
router.post('/login', login as RequestHandler);

// Protected route - requires authentication
router.get('/profile', authenticateToken, getProfile as RequestHandler); // Apply middleware before controller

// Route to refresh the access token
router.post('/refresh', refreshToken as RequestHandler);

// Route to logout (invalidate refresh token)
router.post('/logout', logout as RequestHandler);

// Password Reset Routes
router.post('/forgot-password', requestPasswordReset as RequestHandler);
router.post('/reset-password', resetPassword as RequestHandler);


export default router;
