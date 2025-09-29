# Multi-stage build for optimized React app
FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production=false

# Copy source code
COPY . .

# Build arguments for environment variables (available at build time)
ARG VITE_API_BASE_URL
ARG VITE_API_URL

# Set environment variables for Vite build
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_API_URL=$VITE_API_URL

# Build the application
RUN npm run build

# Production stage - serve with Node.js
FROM node:20-alpine

# Set working directory
WORKDIR /app

# Install serve globally for serving static files
RUN npm install -g serve

# Copy built assets from builder
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/package.json ./

# Expose port (Railway will override with PORT env var)
EXPOSE 3000

# Start the application
# serve -s serves static files from dist directory
# -l $PORT tells serve to use Railway's PORT env var
CMD serve -s dist -l ${PORT:-3000}