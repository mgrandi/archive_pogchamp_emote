#!/usr/bin/env python3

# library imports
import argparse
import logging
import sys

# third party imports
import arrow
import attr
import requests
import logging_tree

# lirary imports
from archive_pogchamp_emote import application as application
from archive_pogchamp_emote import utils as utils

def main():
    # if we are being run as a real program

    parser = argparse.ArgumentParser(
        description="Tool to automate the archival of the daily twitch.tv PogChamp emotes each day",
        epilog="Copyright 2021-01-13 - Mark Grandi",
        fromfile_prefix_chars="@")



    # optional arguments, if specified these are the input and output files, if not specified, it uses stdin and stdout
    parser.add_argument("--config-file",
        dest="config_file",
        type=utils.hocon_config_file_type,
        required=True,
        help="the HOCON configuration file")
    parser.add_argument("--root-output-folder",
        dest="root_output_folder",
        type=utils.isDirectoryType,
        required=True,
        help="the root folder that we put everything else in ")
    parser.add_argument("--wpull-pex-path",
        dest="wpull_pex_path",
        type=utils.isFileType(True),
        required=True,
        help="the path to the wpull PEX that we will be executing to archive the emote")
    parser.add_argument("--log-to-file",
        dest="log_to_file",
        type=utils.isFileType(False),
        help="save the application log to a file as well as print to stdout")
    parser.add_argument("--no-wbm-save",
        dest="no_wbm_save",
        action="store_true",
        help="use this to not save URLs in the wayback machine (for testing)")
    parser.add_argument("--no-youtube-dl",
        dest="no_youtube_dl",
        action="store_true",
        help="use this to not save videos with youtube-dl (for testing)")
    parser.add_argument("--verbose", action="store_true", help="Increase logging verbosity")


    try:
        root_logger = logging.getLogger()

        parsed_args = parser.parse_args()


        # set up logging stuff
        logging.captureWarnings(True) # capture warnings with the logging infrastructure
        logging_formatter = utils.ArrowLoggingFormatter("%(asctime)s %(threadName)-10s %(name)-40s %(levelname)-8s: %(message)s")
        logging_handler = logging.StreamHandler(sys.stdout)
        logging_handler.setFormatter(logging_formatter)
        root_logger.addHandler(logging_handler)


        # silence urllib3 (requests) logger because its noisy
        # requests_packages_urllib_logger = logging.getLogger("requests.packages.urllib3")
        # requests_packages_urllib_logger.setLevel("INFO")
        # urllib_logger = logging.getLogger("urllib3")
        # urllib_logger.setLevel("INFO")

        # set logging level based on arguments
        if parsed_args.verbose:
            root_logger.setLevel("DEBUG")
        else:
            root_logger.setLevel("INFO")

        if parsed_args.log_to_file:
            file_handler = logging.FileHandler(parsed_args.log_to_file, mode='a', encoding="utf-8")
            file_handler.setFormatter(logging_formatter)
            root_logger.addHandler(file_handler)

        root_logger.debug("argv: `%s`", sys.argv)
        root_logger.debug("Parsed arguments: %s", parsed_args)
        root_logger.debug("Logger hierarchy:\n%s", logging_tree.format.build_description(node=None))

        # run the application
        app = application.Application(parsed_args)
        app.run()

        root_logger.info("Done!")

    except Exception as e:
        root_logger.exception("Something went wrong!")
        sys.exit(1)