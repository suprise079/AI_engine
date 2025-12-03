# Use Node.js 18 LTS image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Set environment variables (don't set NODE_ENV=production yet, we need dev deps for build)
ENV PORT=3002

# Install system dependencies and Ollama
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.com/install.sh | sh

# Pull llama3.1 model (this happens as root, models stored in /root/.ollama/models)
RUN ollama pull llama3.1

# Copy package files
COPY package*.json ./

# Install all Node.js dependencies (including dev dependencies needed for build)
RUN npm install

# Copy application code
COPY . .

# Build TypeScript
RUN npm run build

# Now set NODE_ENV=production and remove dev dependencies
ENV NODE_ENV=production
RUN npm prune --production

# Create non-root user for security
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Copy Ollama models from root to appuser's directory so appuser can access them
RUN mkdir -p /home/nodejs/.ollama && \
    cp -r /root/.ollama/* /home/nodejs/.ollama/ && \
    chown -R nodejs:nodejs /home/nodejs/.ollama

# Switch to non-root user
USER nodejs

# Expose port
EXPOSE 3002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3002/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Run the application
CMD ["node", "dist/app.js"]
