import logging
from threading import Event

import click
from click_loglevel import LogLevel
from prometheus_client import (GC_COLLECTOR, PLATFORM_COLLECTOR,
                               PROCESS_COLLECTOR, REGISTRY, start_http_server)

from palworld_exporter.collectors.rcon_collector import (RCONCollector,
                                                         RCONContext)
from palworld_exporter.collectors.save_meta_collector import SaveFileCollector
from palworld_exporter.collectors.util import find_save_directory

# Unregister default/built-in Python collectors
# https://prometheus.github.io/client_python/collector/#disabling-default-collector-metrics
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(GC_COLLECTOR)


@click.command()
@click.option('--rcon-host', default='localhost', help='RCON hostname or IP address', show_default=True, envvar='RCON_HOST')
@click.option('--rcon-port', default=25575, help='RCON Port', show_default=True, envvar='RCON_PORT', type=int)
@click.option('--rcon-password', default='', help='RCON password', show_default='None', envvar='RCON_PASSWORD')
@click.option('--listen-address', default='0.0.0.0', help='Hostname or IP Address for exporter to listen on', envvar='LISTEN_ADDRESS', show_default=True)
@click.option('--listen-port', default=9877, help='Port for exporter to listen on', show_default=True, envvar='LISTEN_PORT', type=int)
@click.option('--save-directory', default=None, envvar='SAVE_DIRECTORY', help='Path to directory contain all .sav files (e.g. Pal/Saved/SaveGames)', show_default='None', type=click.Path(exists=True, dir_okay=True, file_okay=False))
@click.option('--log-level', type=LogLevel(), default='INFO', help='Set logging level', envvar='LOG_LEVEL', show_default=True)
@click.option('--ignore-logging-in', is_flag=True, default=True, envvar='IGNORE_LOGGING_IN', help='Ignore players actively logging in that temporarily have no Player UID')
@click.option('--version', is_flag=True, default=False, help='Print version of palworld-exporter and exit')
def main(rcon_host: str,
         rcon_port: int,
         rcon_password: str,
         listen_address: str,
         listen_port: int,
         save_directory: str,
         log_level: int,
         ignore_logging_in: bool,
         version: bool):

    if version:
        from palworld_exporter import __version__
        click.echo(__version__)
        return

    logging.basicConfig(format='%(asctime)s.%(msecs)03d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s',
                        datefmt='%Y-%m-%d:%H:%M:%S',
                        level=log_level)

    # Register all the collectors
    if save_directory:
        try:
            actual_save_dir = find_save_directory(save_directory)
            REGISTRY.register(SaveFileCollector(actual_save_dir))
        except Exception as e:
            logging.error(e)
            return

    rcon_ctx = RCONContext(rcon_host, rcon_port, rcon_password)
    REGISTRY.register(RCONCollector(rcon_ctx, ignore_logging_in))
    start_http_server(port=listen_port, addr=listen_address)

    logging.info(f'Listening on {listen_address}:{listen_port}')
    # Wait forever
    Event().wait()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("Exiting...")
