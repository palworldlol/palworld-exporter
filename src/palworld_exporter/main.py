import logging

import click
from click_loglevel import LogLevel
from prometheus_client import start_http_server

from palworld_exporter.exporter import PalworldMetrics


@click.command()
@click.option('--rcon-host', default='localhost', help='RCON hostname or IP address', show_default=True, envvar='RCON_HOST')
@click.option('--rcon-port', default=25575, help='RCON Port', show_default=True, envvar='RCON_PORT', type=int)
@click.option('--rcon-password', default='', help='RCON password', show_default='None', envvar='RCON_PASSWORD')
@click.option('--poll-interval', default=5, help='How often to poll Palworld Server (seconds)', show_default=True, envvar='POLL_INTERVAL', type=int)
@click.option('--listen-address', default='0.0.0.0', help='Hostname or IP Address for exporter to listen on', envvar='LISTEN_ADDRESS', show_default=True)
@click.option('--listen-port', default=9877, help='Port for exporter to listen on', show_default=True, envvar='LISTEN_PORT', type=int)
@click.option('--save-directory', default=None, envvar='SAVE_DIRECTORY', help='Path to directory contain all .sav files (e.g. Pal/Saved/SaveGames/0/2FCD4.../)', show_default='None', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--log-level', type=LogLevel(), default='INFO', help='Set logging level', envvar='LOG_LEVEL', show_default=True)
@click.option('--ignore-logging-in', is_flag=True, default=True, envvar='IGNORE_LOGGING_IN', help='Ignore players actively logging in that temporarily have no Player UID')
def main(rcon_host: str,
         rcon_port: int,
         rcon_password: str,
         poll_interval: int,
         listen_address: str,
         listen_port: int,
         save_directory: str,
         log_level: int,
         ignore_logging_in: bool):

    app_metrics = PalworldMetrics(
        rcon_host=rcon_host,
        rcon_port=rcon_port,
        rcon_password=rcon_password,
        polling_interval_seconds=poll_interval,
        save_directory=save_directory,
        ignore_logging_in=ignore_logging_in
    )

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=log_level)

    start_http_server(port=listen_port, addr=listen_address)
    app_metrics.run_metrics_loop()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting...")
