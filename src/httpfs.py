import os
import click
from lib.httpfs.http import Http

CONTEXT_SETTINGS = dict(help_option_names=["--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("-v", "--verbose", default=False, flag_value=True,
              help="Prints debugging messages")
@click.option("-p", "--port", default=8080,
              help="Specifies the port number that the server will listen and serve at. Default is 8080")
@click.option("-d", "--data-dir", default=".",
              help="Specifies the directory that the server will use to read/write requested files. Default is the "
                   "current directory when launching the application.")
def main(verbose, port, data_dir):
    """
    httpfs is a simple file server.
    """
    validate_port(port)
    validate_data_dir(data_dir)
    Http(verbose, port, data_dir).start()


def validate_port(port):
    if port < 1023 or port > 65535:
        print("Invalid port, must be between 1023 and 65535")
        exit(1)


def validate_data_dir(data_dir):
    try:
        if not os.path.isdir(data_dir):
            print("Path provided is not a directory")
            exit(1)
    except Exception:
        print("Invalid directory")
        exit(1)


if __name__ == "__main__":
    main()
