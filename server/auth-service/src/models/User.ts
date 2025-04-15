// Define the structure for the User object based on the system design
export interface User {
  id: string; // Assuming UUID will be represented as a string
  email: string;
  passwordHash: string;
  createdAt: Date;
  lastLogin: Date | null; // Allow null for users who haven't logged in yet
  // subscription: SubscriptionType; // TODO: Define SubscriptionType enum/interface if needed later
}

// Optional: Define SubscriptionType if you plan to use it soon
// export enum SubscriptionType {
//   FREE = 'free',
//   BASIC = 'basic',
//   PREMIUM = 'premium',
// }
