FROM node:22-alpine

WORKDIR /app/frontend

# Use corepack instead of npm -g pnpm (more stable and versioned)
RUN corepack enable 

# Copy manifests separately (cache layers)
COPY package.json pnpm-lock.yaml ./
RUN pnpm install

# Copy the rest of the sources
COPY . .

EXPOSE 3000

CMD ["pnpm", "run", "dev"]
