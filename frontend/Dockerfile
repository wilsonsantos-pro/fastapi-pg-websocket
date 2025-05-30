# Stage 1: Build React App
FROM node:22 AS client-builder
WORKDIR /app/client
COPY client/package*.json ./
RUN npm install
COPY client .
RUN npm run build

# Stage 2: Prepare Apollo Server
FROM node:22 AS server-builder
WORKDIR /app/server
COPY server/package*.json ./
RUN npm install
COPY server .
RUN npm run build

# Stage 3: Final image
FROM node:22 AS dev
WORKDIR /app

# Copy server
COPY --from=server-builder /app/server/dist ./server
COPY --from=server-builder /app/server/node_modules ./node_modules

# Copy client build output
COPY --from=client-builder /app/client/dist ./server/public

# Install optional PM2 for production process management
RUN npm install -g pm2

EXPOSE 4000

CMD ["pm2-runtime", "server/server.js"]
