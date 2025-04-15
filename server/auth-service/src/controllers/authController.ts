import { Request, Response } from 'express';
import bcrypt from 'bcrypt';
import jwt, { Secret, SignOptions, JwtPayload } from 'jsonwebtoken';
import crypto from 'crypto'; // Import crypto for token generation/hashing
import pool from '../utils/db';
import { User } from '../models/User';
import config from '../config';
import { timeStringToSeconds } from '../utils/timeUtils';
import { AuthenticatedRequest } from '../middleware/authMiddleware';

const SALT_ROUNDS = 10; // Cost factor for bcrypt hashing

// POST /api/auth/register
export const register = async (req: Request, res: Response): Promise<void> => { // Return Promise<void>
  const { email, password } = req.body;

  // Basic input validation
  if (!email || !password) {
    res.status(400).json({ message: 'Email and password are required.' }); // Remove return
    return; // Exit function
  }

  try {
    // 1. Check if user already exists
    const existingUserResult = await pool.query('SELECT id FROM users WHERE email = $1', [email]);
    if (existingUserResult.rows.length > 0) {
      res.status(409).json({ message: 'User already exists with this email.' }); // Remove return
      return; // Exit function
    }

    // 2. Hash the password
    const passwordHash = await bcrypt.hash(password, SALT_ROUNDS);

    // 3. Insert the new user into the database
    // Note: Assumes a 'users' table exists with columns: id (uuid), email, password_hash, created_at, last_login
    // You'll need to create this table in your PostgreSQL database.
    const newUserResult = await pool.query(
      'INSERT INTO users (email, password_hash) VALUES ($1, $2) RETURNING id, email, created_at, last_login',
      [email, passwordHash]
    );

    const newUser: Omit<User, 'passwordHash'> = newUserResult.rows[0]; // Exclude passwordHash from response

    // 4. Generate JWT (optional: log user in immediately after registration)
    // const token = jwt.sign({ userId: newUser.id }, config.jwt.secret, { expiresIn: config.jwt.expiresIn });

    // 5. Return success response (without token for now, user needs to login separately)
    res.status(201).json({ message: 'User registered successfully.', user: newUser }); // Remove return

  } catch (error) {
    console.error('Registration error:', error);
    // Check for specific DB errors if needed (e.g., unique constraint violation)
    res.status(500).json({ message: 'Internal server error during registration.' }); // Remove return
  }
};

// POST /api/auth/login
export const login = async (req: Request, res: Response): Promise<void> => { // Return Promise<void>
  const { email, password } = req.body;

  if (!email || !password) {
    res.status(400).json({ message: 'Email and password are required.' }); // Remove return
    return; // Exit function
  }

  try {
    // 1. Find the user by email
    const userResult = await pool.query('SELECT id, email, password_hash, last_login, created_at FROM users WHERE email = $1', [email]);
    if (userResult.rows.length === 0) {
      res.status(401).json({ message: 'Invalid credentials.' }); // User not found
      return; // Exit function
    }

    const user: User & { password_hash: string } = userResult.rows[0]; // Get user data including hash

    // 2. Compare the provided password with the stored hash
    const isMatch = await bcrypt.compare(password, user.password_hash);
    if (!isMatch) {
      res.status(401).json({ message: 'Invalid credentials.' }); // Password doesn't match
      return; // Exit function
    }

    // 3. Generate JWT and Refresh Token
    const payload = { userId: user.id };
    const jwtSecret: Secret = config.jwt.secret;
    const refreshTokenSecret: Secret = config.refreshToken.secret;

    // Convert expiresIn strings to seconds
    const accessTokenExpiresInSeconds = timeStringToSeconds(config.jwt.expiresIn);
    const refreshTokenExpiresInSeconds = timeStringToSeconds(config.refreshToken.expiresIn);

    // Validate conversion results (optional but recommended)
    if (isNaN(accessTokenExpiresInSeconds) || isNaN(refreshTokenExpiresInSeconds)) {
      console.error('Invalid expiresIn format in configuration.');
      // Handle error appropriately, maybe return 500 or use a default value
      res.status(500).json({ message: 'Internal server error: Invalid token configuration.' }); // Remove return
      return; // Exit function
    }

    const jwtOptions: SignOptions = { expiresIn: accessTokenExpiresInSeconds };
    const refreshTokenOptions: SignOptions = { expiresIn: refreshTokenExpiresInSeconds };

    // Use explicitly typed variables with numeric expiresIn
    const accessToken = jwt.sign(payload, jwtSecret, jwtOptions);
    const refreshToken = jwt.sign(payload, refreshTokenSecret, refreshTokenOptions);

    // Log the full access token to the server console (can be removed later)
    console.log('Generated Access Token:', accessToken);
    // Add back refresh token console log
    console.log('Generated Refresh Token:', refreshToken);

    // 4. Calculate refresh token expiry timestamp
    const now = new Date();
    const refreshTokenExpiresAt = new Date(now.getTime() + refreshTokenExpiresInSeconds * 1000);

    // 5. Store refresh token securely in the database
    try {
      // Optional: Clean up old/expired tokens for this user before inserting a new one
      // await pool.query('DELETE FROM refresh_tokens WHERE user_id = $1 AND expires_at < NOW()', [user.id]);

      await pool.query(
        'INSERT INTO refresh_tokens (token, user_id, expires_at) VALUES ($1, $2, $3)',
        [refreshToken, user.id, refreshTokenExpiresAt]
      );
    } catch (dbError) {
      console.error('Error saving refresh token:', dbError);
      // Decide how to handle this - maybe still log the user in but without refresh capability?
      // For now, returning a generic server error.
      res.status(500).json({ message: 'Internal server error during login (token storage).' });
      return;
    }


    // 6. Update last_login timestamp (optional)
    await pool.query('UPDATE users SET last_login = NOW() WHERE id = $1', [user.id]);

    // 7. Return tokens and user info (excluding password hash)
    // Assuming pg maps snake_case 'created_at' to camelCase 'createdAt' when typing the result row
    const userResponse: Omit<User, 'passwordHash'> = {
        id: user.id,
        email: user.email,
        createdAt: user.createdAt, // Use the camelCase property from the typed 'user' object
        lastLogin: new Date() // Reflect the updated login time
    };

    res.status(200).json({ // Remove return
      message: 'Login successful.',
      accessToken,
      refreshToken, // Note: Handle refresh token securely in a real app
      user: userResponse
    });

  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Internal server error during login.' });
  }
};

// POST /api/auth/refresh
export const refreshToken = async (req: Request, res: Response): Promise<void> => {
  const { token: providedRefreshToken } = req.body;

  if (!providedRefreshToken) {
    res.status(401).json({ message: 'Refresh token is required.' });
    return;
  }

  // Removed duplicate declaration below
  const refreshTokenSecret: Secret = config.refreshToken.secret;
  const jwtSecret: Secret = config.jwt.secret;

  try {
    // 1. Find the refresh token in the database
    const tokenResult = await pool.query(
      'SELECT user_id, expires_at FROM refresh_tokens WHERE token = $1',
      [providedRefreshToken]
    );

    if (tokenResult.rows.length === 0) {
      console.log('Refresh token not found in DB');
      res.status(403).json({ message: 'Invalid refresh token (not found).' });
      return; // Exit function after sending response
    }

    const storedToken = tokenResult.rows[0];
    const userId = storedToken.user_id;
    const expiresAt = new Date(storedToken.expires_at);

    // 2. Check if the token from the DB has expired
    if (expiresAt < new Date()) {
      console.log('Refresh token found in DB but expired');
      // Optional: Clean up the expired token from DB
      await pool.query('DELETE FROM refresh_tokens WHERE token = $1', [providedRefreshToken]);
      res.status(403).json({ message: 'Invalid refresh token (expired).' });
      return; // Exit function after sending response
    }

    // 3. Verify the token signature (as an extra check against tampering, though DB lookup is primary)
    try {
      jwt.verify(providedRefreshToken, refreshTokenSecret);
      // Signature is valid, proceed. We already have the userId from the DB lookup.
    } catch (verifyError: any) {
      console.error('Refresh Token Signature Verification Error (after DB check):', verifyError.message);
      // If signature is invalid even though DB entry exists and isn't expired, treat as compromised.
      // Clean up the potentially compromised token.
      await pool.query('DELETE FROM refresh_tokens WHERE token = $1', [providedRefreshToken]);
      res.status(403).json({ message: 'Invalid refresh token (verification failed).' });
      return; // Exit function after sending response
    }

    // --- Refresh Token Rotation ---

    // 4. Delete the used refresh token from the database
    await pool.query('DELETE FROM refresh_tokens WHERE token = $1', [providedRefreshToken]);

    // 5. Generate a new access token
    const newAccessTokenPayload = { userId: userId };
    const accessTokenExpiresInSeconds = timeStringToSeconds(config.jwt.expiresIn);
    if (isNaN(accessTokenExpiresInSeconds)) {
      console.error('Invalid JWT_EXPIRES_IN format in configuration.');
      res.status(500).json({ message: 'Internal server error: Invalid token configuration.' });
      return; // Exit function after sending response
    }
    const newAccessToken = jwt.sign(newAccessTokenPayload, jwtSecret, { expiresIn: accessTokenExpiresInSeconds });

    // 6. Generate a new refresh token
    const newRefreshTokenPayload = { userId: userId }; // Keep payload simple for refresh token
    const refreshTokenExpiresInSeconds = timeStringToSeconds(config.refreshToken.expiresIn);
     if (isNaN(refreshTokenExpiresInSeconds)) {
      console.error('Invalid REFRESH_TOKEN_EXPIRES_IN format in configuration.');
      res.status(500).json({ message: 'Internal server error: Invalid token configuration.' });
      return; // Exit function after sending response
    }
    const newRefreshToken = jwt.sign(newRefreshTokenPayload, refreshTokenSecret, { expiresIn: refreshTokenExpiresInSeconds });
    const newRefreshTokenExpiresAt = new Date(new Date().getTime() + refreshTokenExpiresInSeconds * 1000);

    // 7. Store the new refresh token in the database
     try {
      await pool.query(
        'INSERT INTO refresh_tokens (token, user_id, expires_at) VALUES ($1, $2, $3)',
        [newRefreshToken, userId, newRefreshTokenExpiresAt]
      );
    } catch (dbError) {
      console.error('Error saving new refresh token:', dbError);
      // If saving the new refresh token fails, the user might be stuck.
      // Log the error, but maybe still return the new access token? Or return an error?
      // Returning an error is safer.
      res.status(500).json({ message: 'Internal server error during token refresh (storage).' });
      return; // Exit function after sending response
    }

    // 8. Return the new access token and the new refresh token
    res.status(200).json({
      accessToken: newAccessToken,
      refreshToken: newRefreshToken // Send the new refresh token back
    });

  } catch (error) {
    // This catch block handles errors from the initial DB query or other unexpected issues
    // but kept for safety.
    console.error('Refresh token error:', error);
    res.status(500).json({ message: 'Internal server error during token refresh.' });
  }
};

// POST /api/auth/logout
export const logout = async (req: Request, res: Response): Promise<void> => {
  const { token: providedRefreshToken } = req.body;

  if (!providedRefreshToken) {
    // Even if no token is provided, arguably logout should succeed silently client-side.
    // However, requiring the token ensures we attempt to invalidate a specific session.
    res.status(400).json({ message: 'Refresh token is required to logout.' });
    return;
  }

  try {
    // Delete the refresh token from the database
    const deleteResult = await pool.query(
      'DELETE FROM refresh_tokens WHERE token = $1',
      [providedRefreshToken]
    );

    if (deleteResult.rowCount === 0) {
      // Token was not found, maybe already logged out or invalid token provided.
      // Still return success as the goal (user is logged out) is achieved.
      console.log('Logout attempt: Refresh token not found in DB (already invalid or logged out).');
    } else {
      console.log('Logout successful: Refresh token invalidated.');
    }

    // Send success response regardless of whether the token was found/deleted
    // The client should clear its stored tokens upon receiving this success response.
    res.status(200).json({ message: 'Logout successful.' });

  } catch (error) {
    console.error('Logout error:', error);
    res.status(500).json({ message: 'Internal server error during logout.' });
  }
};

// POST /api/auth/forgot-password
export const requestPasswordReset = async (req: Request, res: Response): Promise<void> => {
  const { email } = req.body;

  if (!email) {
    res.status(400).json({ message: 'Email is required.' });
    return;
  }

  try {
    // 1. Find user by email
    const userResult = await pool.query('SELECT id FROM users WHERE email = $1', [email]);
    if (userResult.rows.length === 0) {
      // User not found, but send a generic success response for security
      // This prevents attackers from discovering which emails are registered.
      console.log(`Password reset requested for non-existent email: ${email}`);
      res.status(200).json({ message: 'If an account with that email exists, a password reset token has been generated.' });
      return;
    }
    const userId = userResult.rows[0].id;

    // 2. Generate a secure random token
    const resetToken = crypto.randomBytes(32).toString('hex');

    // 3. Hash the token before storing it in the DB
    // Use SHA256 for hashing the reset token (bcrypt is overkill here)
    const hashedToken = crypto.createHash('sha256').update(resetToken).digest('hex');

    // 4. Set expiry time (e.g., 1 hour from now)
    const expiresAt = new Date(Date.now() + 60 * 60 * 1000); // 1 hour

    // 5. Store the hashed token, user ID, and expiry in the database
    // Optional: Delete any previous reset tokens for this user
    await pool.query('DELETE FROM password_reset_tokens WHERE user_id = $1', [userId]);
    await pool.query(
      'INSERT INTO password_reset_tokens (token, user_id, expires_at) VALUES ($1, $2, $3)',
      [hashedToken, userId, expiresAt]
    );

    // 6. Send the *raw* token back to the client (or ideally, email it)
    // IMPORTANT: In a real app, you would email a reset link containing the raw `resetToken`.
    // Never expose the hashed token. For testing, we send the raw token in the response.
    console.log(`Password reset token generated for ${email}: ${resetToken}`); // Log raw token for testing
    res.status(200).json({
      message: 'Password reset token generated successfully. Check console/email.',
      resetToken: resetToken // Sending raw token for testing purposes ONLY
    });

  } catch (error) {
    console.error('Request password reset error:', error);
    res.status(500).json({ message: 'Internal server error during password reset request.' });
  }
};

// POST /api/auth/reset-password
export const resetPassword = async (req: Request, res: Response): Promise<void> => {
  const { token: rawResetToken, newPassword } = req.body;

  if (!rawResetToken || !newPassword) {
    res.status(400).json({ message: 'Reset token and new password are required.' });
    return;
  }

  // Basic password validation (add more rules as needed)
  if (newPassword.length < 6) {
     res.status(400).json({ message: 'Password must be at least 6 characters long.' });
     return;
  }

  // 1. Hash the raw token provided by the user to match the stored hash
  const hashedToken = crypto.createHash('sha256').update(rawResetToken).digest('hex');

  try {
    // 2. Find the matching hashed token in the database
    const tokenResult = await pool.query(
      'SELECT user_id, expires_at FROM password_reset_tokens WHERE token = $1',
      [hashedToken]
    );

    if (tokenResult.rows.length === 0) {
      res.status(400).json({ message: 'Invalid or expired password reset token.' });
      return;
    }

    const storedToken = tokenResult.rows[0];
    const userId = storedToken.user_id;
    const expiresAt = new Date(storedToken.expires_at);

    // 3. Check if the token has expired
    if (expiresAt < new Date()) {
      // Clean up expired token
      await pool.query('DELETE FROM password_reset_tokens WHERE token = $1', [hashedToken]);
      res.status(400).json({ message: 'Invalid or expired password reset token.' });
      return;
    }

    // 4. Hash the new password
    const newPasswordHash = await bcrypt.hash(newPassword, SALT_ROUNDS);

    // 5. Update the user's password in the users table
    await pool.query(
      'UPDATE users SET password_hash = $1 WHERE id = $2',
      [newPasswordHash, userId]
    );

    // 6. Delete the used reset token from the database
    await pool.query('DELETE FROM password_reset_tokens WHERE token = $1', [hashedToken]);

    // 7. Send success response
    res.status(200).json({ message: 'Password has been reset successfully.' });

  } catch (error) {
    console.error('Reset password error:', error);
    res.status(500).json({ message: 'Internal server error during password reset.' });
  }
};


// GET /api/auth/profile (Protected Route)
export const getProfile = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  // The authenticateToken middleware should have attached the user payload
  // We expect req.user to contain { userId: 'some-uuid', iat: ..., exp: ... }
  const userPayload = req.user as JwtPayload; // Type assertion

  if (!userPayload || !userPayload.userId) {
    // This shouldn't happen if authenticateToken middleware is working correctly
    res.status(401).json({ message: 'Unauthorized: User information not found in token.' });
    return;
  }

  const userId = userPayload.userId;

  try {
    // Fetch user profile information from the database, excluding the password hash
    const userResult = await pool.query(
      'SELECT id, email, created_at, last_login FROM users WHERE id = $1',
      [userId]
    );

    if (userResult.rows.length === 0) {
      // This might indicate a deleted user or an invalid token payload
      res.status(404).json({ message: 'User profile not found.' });
      return;
    }

    // Assuming pg maps snake_case 'created_at' and 'last_login' to camelCase
    const userProfile: Omit<User, 'passwordHash'> = {
        id: userResult.rows[0].id,
        email: userResult.rows[0].email,
        createdAt: userResult.rows[0].created_at, // Adjust if mapping is different
        lastLogin: userResult.rows[0].last_login  // Adjust if mapping is different
    };


    res.status(200).json(userProfile);

  } catch (error) {
    console.error('Get profile error:', error);
    res.status(500).json({ message: 'Internal server error while fetching profile.' });
  }
};
