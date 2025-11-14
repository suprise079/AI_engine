# Use Node.js 18 LTS image
FROM node:18-slim

# Set working directory
WORKDIR /app

# Set environment variables (NODE_ENV will be set to production after build)
ENV PORT=3006

# Install system dependencies (Ollama will be installed separately or assumed available on host)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy package files
COPY package*.json ./

# Install all Node.js dependencies (including dev dependencies for build)
# Using npm install instead of npm ci since package-lock.json may not exist
# NODE_ENV is not set to production here, so dev dependencies will be installed
RUN npm install

# Copy application code
COPY . .

# Build TypeScript (using npx to ensure tsc is found)
RUN npx tsc

# Set NODE_ENV to production and remove dev dependencies to reduce image size
ENV NODE_ENV=production
RUN npm prune --omit=dev

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 3006

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3006/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1

# Run the application
CMD ["node", "dist/app.js"]
