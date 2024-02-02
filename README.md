# Prometheus Exporter for Palworld Server

This project contains a [Prometheus Exporter](https://prometheus.io/docs/instrumenting/exporters/) for [Palworld](https://store.steampowered.com/app/1623730/Palworld/) servers to monitor the following metrics:

| name | description | labels | metric type |
|------|-------------|--------|-------------|
| `palworld_player_count` | The current number of players on given server | no extra labels | Gauge |
| `palworld_player` | A player currently logged into the server | Character name, Player UID, and Steam ID | Gauge |
| `palworld_up` | Indicator if last metric scrape was successful | no extra labels | Gauge |

*For more information of [Gauges see here](https://prometheus.io/docs/concepts/metric_types/#gauge).*

# Options

```
$ palworld_exporter --help
Usage: palworld_exporter [OPTIONS]

Options:
  --rcon-host TEXT                RCON hostname or IP address  [default:
                                  localhost]
  --rcon-port INTEGER             RCON Port  [default: 25575]
  --rcon-password TEXT            RCON password  [default: (None)]
  --poll-interval INTEGER         How often to poll Palworld Server (seconds)
                                  [default: 5]
  --listen-address TEXT           Hostname or IP Address for exporter to
                                  listen on  [default: 0.0.0.0]
  --listen-port INTEGER           Port for exporter to listen on  [default:
                                  9877]
  --log-level [NOTSET|DEBUG|INFO|WARNING|ERROR|CRITICAL]
                                  Set logging level  [default: INFO]
  --ignore-logging-in             Ignore players actively logging in that
                                  temporarily have no Player UID
  --help                          Show this message and exit.
```

Environment Variables are also available for each option above:

- `RCON_HOST`
- `RCON_PORT`
- `RCON_PASSWORD`
- `POLL_INTERVAL`
- `LISTEN_ADDRESS`
- `LISTEN_PORT`
- `LOG_LEVEL`
- `IGNORE_LOGGING_IN`

# Run as Container

## Just Docker

Below is the command to run straight with docker (podman works too!). 

*NOTE*: You will need to make sure the exporter can reach the Palworld server you wish to monitor.

```
docker run -e RCON_HOST=palworld -e RCON_PASSWORD=topsecrt --rm -it docker.io/bostrt/palworld-exporter
```

## Docker Compose

Here is an EXAMPLE docker compose file that uses a https://github.com/thijsvanloef/palworld-server-docker great containerization of Palworld:

⚠️ *Note*: PLEASE check the README on https://github.com/thijsvanloef/palworld-server-docker and don't just copy paste this. 

- Notice the `RCON_PASSWORD` and `ADMIN_PASSWORD` match. 
- Notice the exporter references `palworld`, the name of the Docker compose service.
- Notice the `RCON_PORT` in both services match.

```yaml
services:
  exporter:
    image: docker.io/bostrt/palworld-exporter:latest
    restart: unless-stopped
    container_name: exporter
    ports:
      - 9000:9000/tcp
    depends_on:
      - palworld
    environment:
      - RCON_HOST=palworld
      - RCON_PORT=25575
      - RCON_PASSWORD=top-secret
  palworld:
      image: docker.io/thijsvanloef/palworld-server-docker:latest
      container_name: palworld-server
      ports:
        - 8211:8211/udp
        - 27015:27015/udp
      environment:
         - PUID=1000
         - PGID=1000
         - PORT=8211
         - PLAYERS=16
         - MULTITHREADING=true
         - RCON_ENABLED=true
         - RCON_PORT=25575
         - ADMIN_PASSWORD=top-secret
      volumes:
         - ./palworld:/palworld/:z
```

# Visualization (Grafana)

If you already have a Promtheus + Grafana monitoring setup, you can integrate the metris for some pretty graphs. Here is a screenshot of some very basic graphs of each metric using two different Palworld servers:

![Grafana Screenshot](./grafana.png)