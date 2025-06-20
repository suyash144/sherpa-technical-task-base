
# ---------- build stage ----------
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml* package-lock.json* yarn.lock* ./
RUN if [ -f pnpm-lock.yaml ]; then corepack enable && pnpm i --frozen-lockfile;     elif [ -f yarn.lock ]; then yarn install --immutable;     else npm ci; fi
COPY . .
RUN npm run build

# ---------- production stage ----------
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx","-g","daemon off;"]
