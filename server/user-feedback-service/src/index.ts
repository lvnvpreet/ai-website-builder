import express from 'express';
import dotenv from 'dotenv';
import mongoose from 'mongoose';

// Define types explicitly
type Express = express.Express;
type Request = express.Request;
type Response = express.Response;

// Load environment variables from .env file
dotenv.config();

const app: Express = express();
// Default port for User Feedback Service (can be overridden by .env)
const port = process.env.PORT || 3021;
const mongoUri = process.env.MONGO_URI; // Get MongoDB connection string

// --- MongoDB Connection (Placeholder) ---
if (!mongoUri) {
    console.error("MONGO_URI not found in environment variables. Cannot connect to database.");
    // In a real app, you might exit or prevent the server from starting fully
} else {
    mongoose.connect(mongoUri)
        .then(() => console.log('MongoDB connected successfully.'))
        .catch(err => console.error('MongoDB connection error:', err));
}

// --- Mongoose Schema & Model (Placeholder) ---
// TODO: Define the actual UserFeedback schema based on the design document
const feedbackSchema = new mongoose.Schema({
    userId: String,
    projectId: String,
    componentId: String,
    rating: Number,
    comment: String,
    sentiment: Number,
    createdAt: { type: Date, default: Date.now }
});
const Feedback = mongoose.model('Feedback', feedbackSchema);


// Middleware to parse JSON bodies
app.use(express.json());

// Basic health check endpoint
app.get('/', (req: Request, res: Response) => {
  res.json({ message: 'User Feedback Service is running!' });
});

// Placeholder endpoint for submitting component rating
interface RateInput {
    userId?: string;
    projectId?: string;
    rating: number; // e.g., 1-5
    // Potentially add context
}
app.post('/feedback/rate/:componentId', async (req: Request, res: Response) => {
    const componentId = req.params.componentId;
    const { userId, projectId, rating }: RateInput = req.body;

    if (rating === undefined || typeof rating !== 'number') {
        return res.status(400).json({ message: 'Invalid input: "rating" (number) is required.' });
    }
    console.log(`Received rating for component ${componentId}: ${rating}`);

    // TODO: Implement logic to save rating to MongoDB using Mongoose model
    // Example:
    // const newRating = new Feedback({ userId, projectId, componentId, rating, createdAt: new Date() });
    // await newRating.save();

    res.status(201).json({ message: 'Rating received successfully (not saved yet).' });
});

// Placeholder endpoint for submitting free-form comment
interface CommentInput {
    userId?: string;
    projectId?: string;
    comment: string;
    // Potentially add context (e.g., page URL, component ID)
    context?: object;
}
app.post('/feedback/comment', async (req: Request, res: Response) => {
    const { userId, projectId, comment, context }: CommentInput = req.body;

     if (!comment || typeof comment !== 'string') {
        return res.status(400).json({ message: 'Invalid input: "comment" (string) is required.' });
    }
    console.log(`Received comment: ${comment.substring(0, 50)}...`);

    // TODO: Implement logic to save comment to MongoDB
    // TODO: Implement sentiment analysis (maybe call another service or use a library)
    // Example:
    // const sentimentScore = analyzeSentiment(comment); // Placeholder function
    // const newComment = new Feedback({ userId, projectId, comment, sentiment: sentimentScore, createdAt: new Date() });
    // await newComment.save();

    res.status(201).json({ message: 'Comment received successfully (not saved/analyzed yet).' });
});


app.listen(port, () => {
  console.log(`[server]: User Feedback Service is running at http://localhost:${port}`);
});
