import { createClient, RedisClientType } from 'redis';
import config from '../config'; // Session service configuration

// Create the Redis client instance using the URL from the session service config
const redisClient: RedisClientType = createClient({
  url: config.redisUrl,
});

redisClient.on('error', (err) => console.error('[redis][session-service]: Redis Client Error', err));

// Connect the client using an IIFE
(async () => {
  try {
    await redisClient.connect();
    console.log('[redis][session-service]: Connected to Redis successfully.');
  } catch (err) {
    console.error('[redis][session-service]: Could not connect to Redis:', err);
    // Handle connection error appropriately for the session service
  }
})();

// Export the connected client
export default redisClient;
