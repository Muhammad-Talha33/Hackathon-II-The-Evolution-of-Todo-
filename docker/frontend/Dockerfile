# =============================================================================
# Stage 1: Dependencies - Install Node modules
# =============================================================================
FROM node:18-alpine AS deps

LABEL maintainer="Todo AI Chatbot Team"
LABEL description="Multi-stage build for Next.js frontend"

# Set working directory
WORKDIR /app

# Install dependencies required for node-gyp (if needed)
RUN apk add --no-cache libc6-compat

# Copy package files
COPY package.json package-lock.json* ./

# Install dependencies (production only for smaller image)
RUN npm ci --only=production

# =============================================================================
# Stage 2: Builder - Build Next.js application
# =============================================================================
FROM node:18-alpine AS builder

WORKDIR /app

# Copy dependencies from deps stage
COPY --from=deps /app/node_modules ./node_modules

# Copy all source files
COPY . .

# Set build-time environment variable for API URL
ARG NEXT_PUBLIC_API_URL=http://backend:8000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build the Next.js application
RUN npm run build

# =============================================================================
# Stage 3: Runtime - Minimal production image
# =============================================================================
FROM node:18-alpine

LABEL maintainer="Todo AI Chatbot Team"
LABEL description="Next.js frontend for Todo AI Chatbot"
LABEL version="1.0.0"

WORKDIR /app

# Create non-root user for security
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy only necessary files from builder
# Next.js standalone output (optimized for production)
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Switch to non-root user
USER nextjs

# Expose frontend port
EXPOSE 3000

# Set environment variables
ENV NODE_ENV=production \
    PORT=3000 \
    HOSTNAME="0.0.0.0"

# Health check - verify Next.js server is responding
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:3000/ || exit 1

# Start Next.js server
CMD ["node", "server.js"]
