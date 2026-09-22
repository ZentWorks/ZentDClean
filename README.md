<p align="center">
  <img src="app/static/icons/icon-512.png" alt="ZentDClean logo" width="180">
</p>

<h1 align="center">ZentDClean</h1>

<p align="center">A small self-hosted web UI for finding and removing unused Docker resources.</p>

It is intentionally simple: open the page, see what is unused, review what can be removed, and clean it up.

## Features

- Finds unused Docker images, volumes, build cache, stopped containers and networks
- Lets you review and select resources before deletion
- Re-checks resources immediately before cleanup
- Uses Docker's native unused-cache prune for build cache
- Optional password protection
- UI in English, German, French, Dutch, Spanish, Portuguese, Polish, Italian and Czech
- No database
- No external frontend dependencies or CDNs

## Docker Compose

```yaml
services:
  zentdclean:
    image: ghcr.io/zentworks/zentdclean:latest
    container_name: zentdclean
    restart: unless-stopped
    ports:
      - "8787:8787"
    environment:
      TZ: "Europe/Berlin"
      # PASSWORD: "change-me"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    read_only: true
    tmpfs:
      - /tmp:size=16m,mode=1777
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
```

Start it with:

```bash
docker compose up -d
```

Open `http://HOST:8787`.

## Docker Run

```bash
docker run -d \
  --name zentdclean \
  -p 8787:8787 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --restart unless-stopped \
  ghcr.io/zentworks/zentdclean:latest
```

To enable the login, add:

```bash
-e PASSWORD="change-me"
```

## Environment variables

| Variable | Default | Description |
| --- | --- | --- |
| `PASSWORD` | empty | Optional login password. If empty or unset, login is disabled. |
| `TZ` | system default | Container timezone, for example `Europe/Berlin`. |
| `COOKIE_SECURE` | `false` | Set to `true` when ZentDClean is served over HTTPS so the login session cookie is marked `Secure`. |
| `PORT` | `8787` | Internal web server port. If changed, adjust the Docker port mapping as well. |

## Build from source

```bash
docker build -t zentdclean:local .
```

Or use the development Compose file from the repository:

```bash
docker compose -f docker-compose.yml up -d --build
```

## Security

ZentDClean needs access to `/var/run/docker.sock` to inspect and remove Docker resources. Access to the Docker socket provides extensive control over the Docker host. Keep ZentDClean on a trusted network and use `PASSWORD` when access is not already protected by another authentication layer. If you expose it through HTTPS, also set `COOKIE_SECURE=true`.

A trailing `+` on a reclaimable size means ZentDClean is showing a conservative minimum. Docker image layers can be shared, so the exact freed space may only be known after cleanup.

## License

MIT. See [LICENSE](LICENSE).
