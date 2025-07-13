# Build stage
FROM node:18-alpine AS builder

RUN npm install -g pnpm

WORKDIR /app

COPY package.json pnpm-lock.yaml* pnpm-workspace.yaml ./
COPY apps/web/package.json ./apps/web/package.json
COPY packages ./packages

RUN pnpm install --frozen-lockfile

COPY . .

ARG APP_VERSION
ENV APP_VERSION=${APP_VERSION}

RUN pnpm build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/apps/web/dist /usr/share/nginx/html
COPY docker/frontend/nginx.conf /etc/nginx/conf.d/default.conf

ARG APP_VERSION
LABEL version=${APP_VERSION}

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
