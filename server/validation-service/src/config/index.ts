import dotenv from 'dotenv';

dotenv.config(); // Load .env file contents into process.env

// Validate essential environment variables
const requiredEnvVars = [
  'PORT',
  'METADATA_EXTRACTION_SERVICE_URL',
  'INDUSTRY_CLASSIFIER_SERVICE_URL',
  'SEO_ANALYZER_SERVICE_URL', // Add SEO analyzer URL
];

for (const varName of requiredEnvVars) {
  if (!process.env[varName]) {
    console.warn(`Warning: Environment variable ${varName} is not defined. Using default value.`);
  }
}

export const config = {
  port: process.env.PORT || '3003', // Default validation service port
  metadataExtractionServiceUrl: process.env.METADATA_EXTRACTION_SERVICE_URL || 'http://localhost:3004',
  industryClassifierServiceUrl: process.env.INDUSTRY_CLASSIFIER_SERVICE_URL || 'http://localhost:3005',
  seoAnalyzerServiceUrl: process.env.SEO_ANALYZER_SERVICE_URL || 'http://localhost:3006', // Add SEO analyzer URL
};

export default config;
