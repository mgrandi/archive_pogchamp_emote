import logging
import pathlib
import pprint
import typing
import subprocess

import arrow
import pyhocon
import bfa
import attr
import waybackpy
from waybackpy.exceptions import WaybackError, URLError
import youtube_dl

from archive_pogchamp_emote import constants as constants
from archive_pogchamp_emote import model as model

logger = logging.getLogger(__name__)


def check_completedprocess_for_acceptable_exit_codes(
    completed_process_obj:subprocess.CompletedProcess,
    acceptable_exit_codes:typing.Sequence[int]):
    ''' sees if a `subprocess.CompletedProcess` object has an acceptable exit code
    if not, we call subprocess.CompletedProcess.check_returncode() which will throw an exception

    @param completed_process_obj - the subprocess.CompletedProcess object to check
    @param acceptable_exit_codes - the list of integers of acceptable exit codes
    @throws `subprocess.CalledProcessError` if the exit code is not in the acceptable list
    '''

    logger.debug("checking return code: acceptable: `%s`, CompletedProcess return code: `%s`",
        acceptable_exit_codes, completed_process_obj.returncode)

    # throw an exception if the exit code is not in our acceptble list
    # this assumes that 0 is always a valid exit code, since `check_returncode()` won't
    # throw an exception if the exit code is 0
    if not completed_process_obj.returncode in acceptable_exit_codes:
        completed_process_obj.check_returncode()

def youtube_dl_progress_hook(logger_to_use):
    '''
    returns a downloader hook that logs to a logger we specify

    we have to do this because the default progress uses a carriage return even
    when using youtube-dl as a library and passing in a 'logger' to the
    configuration, which messes up the stdout logging and looks weird in
    file logging

    '''


    def _inner_youtube_dl_progress_hook(dl_progress_dictionary):
        '''

        see https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L230

        If status is one of "downloading", or "finished", the following properties may also be present:
            * filename: The final filename (always present)
            * tmpfilename: The filename we're currently writing to
            * downloaded_bytes: Bytes on disk
            * total_bytes: Size of the whole file, None if unknown
            * total_bytes_estimate: Guess of the eventual file size, None if unavailable.
            * elapsed: The number of seconds since download started.
            * eta: The estimated time in seconds, None if unknown
            * speed: The download speed in bytes/second, None if unknown
            * fragment_index: The counter of the currently downloaded video fragment.
            * fragment_count: The number of fragments (= individual files that will be merged)

        '''

        logger_to_use.info("download progress: `%s`", dl_progress_dictionary)

    return _inner_youtube_dl_progress_hook


def save_video_with_youtube_dl(ytdl_args_dict, url):
    '''
    download a url with youtube-dl, given the arguments and a url to download

    see https://github.com/ytdl-org/youtube-dl#embedding-youtube-dl
    '''


    with youtube_dl.YoutubeDL(ytdl_args_dict) as ydl:
        ydl.download([url])


def save_archive_of_webpage_in_wbm(url):
    '''
    saves a copy of the given URL in the Internet Archive wayback machine
    and returns the archive URL

    '''
    logger.info("saving an archive of the url `%s` in the wayback machine", url)
    error_list = []

    # loop until we get a valid result since it seems to not return a result a lot of
    # the time , probably because it takes too long and is queued?
    # also, do +1 because we start at index 1 here
    for iter_try_idx in range(1, constants.WAYBACK_ATTEMPT_MAX + 1):
        try:
            logger.debug("try `%s/%s` on url `%s`", iter_try_idx, constants.WAYBACK_ATTEMPT_MAX, url)
            wayback_handle_for_url = waybackpy.Url(url, constants.HTTP_USER_AGENT)

            logger.debug("calling save() on wayback handle for url: `%s`", wayback_handle_for_url)

            archive = wayback_handle_for_url.save()
            archive_url = archive.archive_url
            logger.info("archive of url `%s` complete, url: `%s`", url, archive_url)
        except WaybackError as e:
            logger.debug(f"Got WaybackError when trying to save url `{url}`: `{e}`")
            error_list.append(e)
            continue
        except URLError as e:
            # don't continue here, this means we screwed up when providing
            # the url
            logger.debug(f"Got URLError when trying to save url `{url}`")
            raise e

        return archive_url

    # if we get here, then we ran out of tries
    raise Exception("did not get a good result when trying to save the url `%s` in the wayback machine, errors: `%s`",
        url, error_list)


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
    builder = builder.root_output_folder(root_folder_with_date)
    builder = builder.warc_output_folder(root_folder_with_date / "warc")
    builder = builder.youtube_dl_output_folder(root_folder_with_date / "twitter_video")
    builder = builder.warc_tempdir_folder(root_folder_with_date / "warc")
    builder = builder.warc_database_name(constants.WPULL_DATABASE_FORMAT.format(date_str))
    builder = builder.warc_output_file_name(constants.WPULL_OUTPUT_FILE_FORMAT.format(date_str))
    builder = builder.warc_arguments_file_name(constants.WPULL_ARGS_FILE_FORMAT.format(date_str))
    builder = builder.warc_input_url_list_file_name(constants.WPULL_INPUT_URL_LIST_FORMAT.format(date_str))
    builder = builder.warc_file_name(constants.WPULL_WARC_FILE_FORMAT.format(date_str))
    builder = builder.ytdl_arguments_file_name(constants.YTDL_ARGS_FILE_FORMAT.format(date_str))
    builder = builder.emote_date(date_str)

    # stuff that we read from the configuration file


    builder = builder.twitch_emote_id(root_config_section[constants.CONFIG_PATH_TWITCH_EMOTE_ID])
    builder = builder.twitch_twitter_post_url(root_config_section[constants.CONFIG_PATH_TWITCH_TWITTER_POST_URL])
    builder = builder.twitch_twitter_post_is_video(root_config_section[constants.CONFIG_PATH_TWITCH_TWTITER_POST_IS_VIDEO])
    builder = builder.streamer_social_media_url(root_config_section[constants.CONFIG_PATH_STREAMER_SOCIAL_MEDIA_URL])
    builder = builder.streamer_twitch_url(root_config_section[constants.CONFIG_PATH_STREAMER_TWITCH_URL])
    builder = builder.streamer_name(root_config_section[constants.CONFIG_PATH_STREAMER_NAME])

    warc_header_dict = root_config_section[constants.CONFIG_PATH_WARC_HEADERS]

    warc_header_list = []
    for key,value in warc_header_dict.items():
        warc_header_list.append(model.WarcHeader(key=key, value=value))

    builder = builder.warc_headers(warc_header_list)



    logger.debug("building DailyPogchampEmoteConfig object")

    final_config = builder.build()

    logger.debug("DailyPogchampEmoteConfig object built successfully: `%s`", pprint.pformat(attr.asdict(final_config)))

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

def isFileType(strict=True):
    def _isFileType(filePath):
        ''' see if the file path given to us by argparse is a file
        @param filePath - the filepath we get from argparse
        @return the filepath as a pathlib.Path() if it is a file, else we raise a ArgumentTypeError'''

        path_maybe = pathlib.Path(filePath)
        path_resolved = None

        # try and resolve the path
        try:
            path_resolved = path_maybe.resolve(strict=strict).expanduser()

        except Exception as e:
            raise argparse.ArgumentTypeError("Failed to parse `{}` as a path: `{}`".format(filePath, e))

        # double check to see if its a file
        if strict:
            if not path_resolved.is_file():
                raise argparse.ArgumentTypeError("The path `{}` is not a file!".format(path_resolved))

        return path_resolved
    return _isFileType