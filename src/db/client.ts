import { drizzle } from 'drizzle-orm/postgres-js';
import postgres from 'postgres';
import * as schema from './schema';

// Check for DATABASE_URL
if (!process.env.DATABASE_URL) {
  throw new Error(
    'DATABASE_URL environment variable is required. Please check your .env.local file.'
  );
}

// Create postgres client
const connectionString = process.env.DATABASE_URL;

// Connection pool configuration
const sql = postgres(connectionString, {
  max: 10, // Maximum number of connections
  idle_timeout: 20, // Close idle connections after 20 seconds
  connect_timeout: 10, // Connection timeout in seconds
});

// Create Drizzle instance with schema
export const db = drizzle(sql, { schema });

// Export the underlying client for raw queries if needed
export { sql };

// Graceful shutdown helper
export async function closeDatabase() {
  await sql.end();
}
