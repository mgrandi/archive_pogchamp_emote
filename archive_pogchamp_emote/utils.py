import logging
import pathlib

import arrow
import pyhocon
import bfa

from archive_pogchamp_emote import constants as constants
from archive_pogchamp_emote import model as model

logger = logging.getLogger(__name__)


def build_emote_config_from_argparse_args(args):
    ''' builds and returns the DailyPogchampEmoteConfig object
    from the argparse arguments (and the hocon config that it has)

    '''

    # validate the model
    logger.info("validating HOCON config")

    config = args.config_file

    try:
        validate_hocon(config)
    except Exception as e:
        logger.exception("HOCON config validation failed!")
        raise e

    # now that the HOCON config is validated, build our config object
    # and return it
    class_builder = bfa.builder(for_class=model.DailyPogchampEmoteConfig)
    builder = class_builder

    root_config_section = config[constants.CONFIG_PATH_ROOT_SECTION]


    date_str = root_config_section[constants.CONFIG_PATH_DATE]

    root_folder_with_date = args.root_output_folder / date_str

    # set folder paths that require the date
    builder = builder.warc_output_folder(root_folder_with_date / "warc")
    builder = builder.youtube_dl_output_folder(root_folder_with_date / "twitter_video")
    builder = builder.warc_tempdir_folder(root_folder_with_date / "warc")
    builder = builder.warc_database_name(constants.WPULL_DATABASE_FORMAT.format(date_str))
    builder = builder.warc_output_file_name(constants.WPULL_OUTPUT_FILE_FORMAT.format(date_str))
    builder = builder.warc_input_url_list_file_name(constants.WPULL_INPUT_URL_LIST_FORMAT.format(date_str))
    builder = builder.warc_file_name(constants.WPULL_WARC_FILE_FORMAT.format(date_str))
    builder = builder.emote_date(date_str)

    # stuff that we read from the configuration file


    builder = builder.twitch_emote_id(root_config_section[constants.CONFIG_PATH_TWITCH_EMOTE_ID])
    builder = builder.twitch_twitter_post_url(root_config_section[constants.CONFIG_PATH_TWITCH_TWITTER_POST_URL])
    builder = builder.streamer_social_media_url(root_config_section[constants.CONFIG_PATH_STREAMER_SOCIAL_MEDIA_URL])
    builder = builder.streamer_twitch_url(root_config_section[constants.CONFIG_PATH_STREAMER_TWITCH_URL])
    builder = builder.streamer_name(root_config_section[constants.CONFIG_PATH_STREAMER_NAME])

    warc_header_dict = root_config_section[constants.CONFIG_PATH_WARC_HEADERS]

    warc_header_list = []
    for key,value in warc_header_dict.items():
        warc_header_list.append(model.WarcHeader(key=key, value=value))

    builder = builder.warc_headers(warc_header_list)



    logger.info("building DailyPogchampEmoteConfig object")

    final_config = builder.build()

    import pprint,attr
    logger.info("final DailyPogchampEmoteConfig object: `%s`", pprint.pformat(attr.asdict(final_config)))

    return final_config




def validate_hocon(hocon):
    logger.warning("TODO actually implement HOCON config validation!")
    pass

class ArrowLoggingFormatter(logging.Formatter):
    ''' logging.Formatter subclass that uses arrow, that formats the timestamp
    to the local timezone (but its in ISO format)
    '''

    def formatTime(self, record, datefmt=None):
        return arrow.get("{}".format(record.created), "X").to("local").isoformat()

def hocon_config_file_type(stringArg):
    ''' argparse type method that returns a pyhocon Config object
    or raises an argparse.ArgumentTypeError if this file doesn't exist

    @param stringArg - the argument given to us by argparse
    @return a dict like object containing the configuration or raises ArgumentTypeError
    '''

    resolved_path = pathlib.Path(stringArg).expanduser().resolve()
    if not resolved_path.exists:
        raise argparse.ArgumentTypeError("The path {} doesn't exist!".format(resolved_path))

    conf = None
    try:
        conf = pyhocon.ConfigFactory.parse_file(str(resolved_path))
    except Exception as e:
        raise argparse.ArgumentTypeError(
            "Failed to parse the file `{}` as a HOCON file due to an exception: `{}`".format(resolved_path, e))

    return conf

def isDirectoryType(filePath):
    ''' see if the file path given to us by argparse is a directory
    @param filePath - the filepath we get from argparse
    @return the filepath as a pathlib.Path() if it is a directory, else we raise a ArgumentTypeError'''

    path_maybe = pathlib.Path(filePath)
    path_resolved = None

    # try and resolve the path
    try:
        path_resolved = path_maybe.resolve(strict=True).expanduser()

    except Exception as e:
        raise argparse.ArgumentTypeError("Failed to parse `{}` as a path: `{}`".format(filePath, e))

    # double check to see if its a file
    if not path_resolved.is_dir():
        raise argparse.ArgumentTypeError("The path `{}` is not a file!".format(path_resolved))

    return path_resolved
