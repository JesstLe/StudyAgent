FROM node:22-slim AS frontend-builder

WORKDIR /app
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ .
RUN npm run build

FROM node:22-slim AS frontend
WORKDIR /app
COPY --from=frontend-builder /app/.next/standalone ./
COPY --from=frontend-builder /app/.next/static ./.next/static
COPY --from=frontend-builder /app/public ./public

EXPOSE 3000
ENV PORT=3000
CMD ["node", "server.js"]
