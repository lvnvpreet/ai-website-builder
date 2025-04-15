import { createClient, RedisClientType } from 'redis';
import config from '../config'; // Application configuration

// Create the Redis client instance
// The URL is taken from the config, which reads from process.env.REDIS_URL
const redisClient: RedisClientType = createClient({
  url: config.redisUrl,
});

redisClient.on('error', (err) => console.error('[redis]: Redis Client Error', err));

// Connect the client
// We use an immediately invoked async function (IIFE) to handle the async connection
(async () => {
  try {
    await redisClient.connect();
    console.log('[redis]: Connected to Redis successfully.');
  } catch (err) {
    console.error('[redis]: Could not connect to Redis:', err);
    // Depending on the application's needs, you might want to exit or handle this differently
  }
})();

// Export the connected client
export default redisClient;
