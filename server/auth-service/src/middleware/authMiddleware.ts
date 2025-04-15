import { Request, Response, NextFunction } from 'express';
import jwt, { Secret, JwtPayload } from 'jsonwebtoken'; // Import Secret and JwtPayload
import config from '../config'; // Application configuration

// Extend the Express Request interface to include the user payload
export interface AuthenticatedRequest extends Request {
  user?: string | JwtPayload; // Add user property to store decoded payload
}

export const authenticateToken = (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (token == null) {
    // No token provided
    res.sendStatus(401); // Unauthorized
    return;
  }

  const jwtSecret: Secret = config.jwt.secret;

  jwt.verify(token, jwtSecret, (err, user) => {
    if (err) {
      console.error('JWT Verification Error:', err.message);
      // Token is invalid (e.g., expired, wrong signature)
      return res.sendStatus(403); // Forbidden
    }

    // Token is valid, attach payload to request object
    req.user = user;
    next(); // Proceed to the next middleware or route handler
  });
};
