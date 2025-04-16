import express from 'express';
import dotenv from 'dotenv';
import { graphqlHTTP } from 'express-graphql'; // Import GraphQL middleware
import { buildSchema } from 'graphql'; // Import function to build schema from string

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for Customization API Service (can be overridden by .env)
const port = process.env.PORT || 3017;

// --- Minimal GraphQL Schema (Placeholder) ---
// TODO: Define actual schema based on EditOperation, RevisionHistory, etc.
const schema = buildSchema(`
  type Query {
    hello: String
    # Example: getRevisionHistory(projectId: ID!): RevisionHistory
  }

  type Mutation {
    # Example: updateContent(projectId: ID!, elementId: String!, newValue: String!): EditOperation
    # Example: updateStyle(projectId: ID!, elementId: String!, styleChanges: StyleInput!): EditOperation
    # Example: updateLayout(projectId: ID!, layoutChanges: LayoutInput!): EditOperation
    # Example: revertToRevision(projectId: ID!, revisionId: ID!): Boolean
    placeholderMutation(input: String): String
  }

  # TODO: Define input types (StyleInput, LayoutInput) and output types (RevisionHistory, EditOperation)
`);

// --- Minimal Root Resolver (Placeholder) ---
// TODO: Implement actual resolvers connecting to database/logic
const root = {
  hello: () => {
    return 'Hello from Customization API!';
  },
  placeholderMutation: ({ input }: { input: string }) => {
      console.log("Placeholder mutation called with input:", input);
      return `Received: ${input}`;
  }
  // Add resolvers for actual queries and mutations
};

// Middleware to parse JSON bodies (needed for REST endpoints if any, not strictly for GraphQL)
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'Customization API Service is running!' });
});

// GraphQL endpoint setup
app.use('/graphql', graphqlHTTP({
  schema: schema,
  rootValue: root,
  graphiql: true, // Enable GraphiQL interface for testing in browser
}));


app.listen(port, () => {
  console.log(`[server]: Customization API Service (GraphQL at /graphql) is running at http://localhost:${port}`);
});
