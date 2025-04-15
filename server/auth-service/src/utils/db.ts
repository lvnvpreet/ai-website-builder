import { Pool } from 'pg';
import config from '../config'; // Adjust path as necessary if config moves

// Create a new PostgreSQL pool
const pool = new Pool({
  connectionString: config.databaseUrl,
  // Optional: Add SSL configuration if required for your database connection
  // ssl: {
  //   rejectUnauthorized: false // Adjust based on your security requirements
  // }
});

// Test the connection (optional, but good practice)
pool.connect((err, client, release) => {
  if (err) {
    // Release might not be defined if connection failed before acquiring client
    if (release) release();
    return console.error('Error acquiring client for DB connection test:', err.stack);
  }
  if (!client) {
    // This case should ideally not happen if err is null, but handles type possibility
    if (release) release();
    return console.error('DB connection test failed: Client is undefined without error.');
  }
  // Now we know client is defined
  client.query('SELECT NOW()', (err, result) => {
    release(); // Release the client back to the pool
    if (err) {
      return console.error('Error executing query for DB connection test:', err.stack);
    }
    console.log('[database]: Connected to PostgreSQL successfully.');
    // console.log('Current time from DB:', result.rows[0].now);
  });
});

// Handle pool errors
pool.on('error', (err, client) => {
  // Check if client is defined before logging potentially client-specific info
  if (client) {
    console.error('Unexpected error on idle PostgreSQL client', err);
  } else {
    console.error('Unexpected error on PostgreSQL pool', err);
  }
  // Depending on the error, you might want to exit the process
  // process.exit(-1);
});

export default pool;
