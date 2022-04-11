import click
from urllib.parse import urlparse
from lib.httpc.http import Http


CONTEXT_SETTINGS = dict(help_option_names=["--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.argument("command")
@click.argument("URL")
@click.option("-v", "--verbose", default=False, flag_value=True,
              help="Prints the detail of the response such as protocol, status, and headers")
@click.option("-h", "--headers", default=None, multiple=True,
              help="Associates headers to HTTP Request with the format 'key:value'")
@click.option("-d", "--data", default=None, help="Associates an inline data to the body HTTP POST request")
@click.option("-f", "--file", default=None, help="Associates the content of a file to the body HTTP POST request.")
@click.option("-o", "--output", default=None, help="Outputs response to file")
def main(command, url, verbose, headers, data, file, output):
    """
    httpc is a curl-like application but supports HTTP protocol only.

    The commands are:

    - get executes an HTTP GET request and prints the response.

    - post executes an HTTP POST request and prints the response.
    """

    # Validate command
    validate_command(command)

    # Validate url
    validate_url(url)

    # Validate header
    parsed_headers = validate_headers(headers)

    # Validate input file
    parsed_file = validate_input_file(file)

    if file is not None and data is not None:
        print("Cannot provide body data using both -d and -f")
        exit(1)

    if command == "get" and (file is not None or data is not None):
        print("Cannot pass body data using get")
        exit(1)

    try:
        if command == "get":
            response = Http().get(url, parsed_headers)
        else:
            if file is not None:
                response = Http().post(url, parsed_headers, parsed_file)
            else:
                response = Http().post(url, parsed_headers, data)

        if verbose:
            if output is not None:
                write_output(output, response.get_formatted_response())
            else:
                print(response.get_formatted_response())
        else:
            if output is not None:
                write_output(output, response.get_body())
            else:
                print(response.get_body())

    except Exception as e:
        print(e)
        exit(1)


def validate_input_file(file):
    """Reads and validates input file"""
    if file is not None:
        try:
            with open(file, "r") as f:
                return f.read().strip()
        except Exception as e:
            print("Unable to read file: " + file)
            exit(1)


def validate_output_file(file):
    """Validates output file"""
    if file is not None:
        return None


def validate_command(command):
    """Validates incoming command"""
    if command.lower() != "get" and command.lower() != "post":
        print("Invalid command provided, must be either 'get' or 'post'")
        exit(1)


def validate_url(url):
    """Validates incoming url"""
    parsed_url = urlparse(url)
    if parsed_url.scheme != "http":
        print("Invalid scheme provided in url, must be 'http'")
        exit(1)
    elif parsed_url.hostname is None:
        print("Invalid url provided")


def validate_headers(headers):
    """Validates and parses incoming headers"""
    parsed_headers = []
    if headers is not None:
        for header in headers:
            parsed_header = header.split(":")
            if len(parsed_header) == 1:
                print("Invalid header: " + header)
                exit(1)
            else:
                parsed_headers.append((parsed_header[0], parsed_header[1]))
    return parsed_headers


def write_output(file, data):
    try:
        with open(file, "w") as f:
            f.write(data)
    except Exception as e:
        print("Unable to write to file: " + file)
        exit(1)


if __name__ == "__main__":
    main()
