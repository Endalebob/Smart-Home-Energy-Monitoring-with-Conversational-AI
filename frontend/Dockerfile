#########################################################
# 1 ─── Build stage
# after deployment I am getting this error: Bad Gateway what is the issue?
#########################################################
FROM node:18-alpine AS builder
WORKDIR /app

# Copy the lock-file first to maximise Docker cache reuse
COPY package.json package-lock.json ./

# Install all deps (prod + dev) needed to compile the app
RUN npm ci

# Copy the rest of the source and build
COPY . .
RUN npm run build          # requires next.config.{js,ts} ⇒ output: 'standalone'

#########################################################
# 2 ─── Runtime stage
#########################################################
FROM node:18-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
EXPOSE 3000

# Copy ONLY the artefacts needed to run – no node_modules here
COPY --from=builder /app/public              ./public
COPY --from=builder /app/.next/standalone    ./
COPY --from=builder /app/.next/static        ./.next/static

CMD ["node", "server.js"]
