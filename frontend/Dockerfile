FROM node:22-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files first (for better layer caching)
COPY package*.json ./

# Install dependencies (use ci if package-lock exists, otherwise install)
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Copy application source code (now much faster with .dockerignore)
COPY . .

# Build the application for SSR
RUN npm run build

# Production stage
FROM node:22-alpine AS production

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install only production dependencies
RUN npm ci --omit=dev --legacy-peer-deps || npm install --omit=dev --legacy-peer-deps

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist

# Copy any additional files needed for runtime (like astro config)
COPY --from=builder /app/astro.config.mjs ./

# Expose port
EXPOSE 4321

# Start the SSR server
CMD ["npm", "start"]