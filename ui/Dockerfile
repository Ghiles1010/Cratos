# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm ci

# Copy source
COPY . .

# Build arguments for environment variables
ARG VITE_SCHEDULER_API_URL
ENV VITE_SCHEDULER_API_URL=$VITE_SCHEDULER_API_URL

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 3001
EXPOSE 3001

CMD ["nginx", "-g", "daemon off;"]
