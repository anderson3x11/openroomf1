# Built by Coolify on every push: the static site from web/ and the versioned data/, served by Caddy.
# The pipeline runs on a home PC (deploy/publish.sh): the F1 live timing archive refuses datacenter IPs.
FROM node:22-bookworm-slim AS build
WORKDIR /app
COPY web/package.json web/package-lock.json web/
RUN npm ci --prefix web
COPY web web
COPY data data
RUN npm run build --prefix web

FROM caddy:2-alpine
COPY deploy/Caddyfile /etc/caddy/Caddyfile
COPY --from=build /app/web/build /srv
EXPOSE 80
