import re

from archive_pogchamp_emote import __version__ as __version__


ARROW_DATE_FORMAT = "YYYY-MM-DD"

WPULL_DATABASE_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_database.sqlite3"
WPULL_OUTPUT_FILE_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_output.log"
WPULL_WARC_FILE_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_warc"

WPULL_INPUT_URL_LIST_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_url_list.txt"
WPULL_ARGS_FILE_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_arguments.txt"
YTDL_ARGS_FILE_FORMAT = "youtube_dl_args.txt"
APPLICATION_VERSION_FILE_FORMAT = "{}_archive_pogchamp_emote_version_info.json"


CONFIG_PATH_ROOT_SECTION = "archive_pogchamp_emote"

CONFIG_PATH_TWITCH_EMOTE_ID = "twitch_emote_id"
CONFIG_PATH_TWITCH_TWITTER_POST_URL = "twitch_twitter_post_url"
CONFIG_PATH_TWITCH_TWTITER_POST_IS_VIDEO = "twitch_twitter_post_is_video"
CONFIG_PATH_STREAMER_SOCIAL_MEDIA_URL = "streamer_social_media_url" # deprecated, should  use the plural form instead (as a list)
CONFIG_PATH_STREAMER_SOCIAL_MEDIA_URLS = "streamer_social_media_urls"
CONFIG_PATH_STREAMER_TWITCH_URL = "streamer_twitch_url"
CONFIG_PATH_STREAMER_NAME = "streamer_name"
CONFIG_PATH_DATE = "date"
CONFIG_PATH_EXTRA_WARC_HEADERS = "extra_warc_headers"
CONFIG_PATH_ADDITIONAL_URLS_SAVE_WARC = "additional_urls_to_include_in_warc"
CONFIG_PATH_ADDITIONAL_URLS_SAVE_WBM = "additional_urls_to_save_via_wbm"
CONFIG_PATH_ADDITIONAL_URLS_SAVE_YTDL = "additional_urls_to_save_via_youtube_dl"


WPULL_INPUT_URLS_FORMAT_LIST = [
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/dark/1.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/dark/2.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/dark/3.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/light/1.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/light/2.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/light/3.0",
]

HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"

WAYBACK_ATTEMPT_MAX = 6

YOUTUBE_DL_FILE_TEMPLATE_STR = "%(id)s.%(ext)s"

ACCEPTABLE_WPULL_EXIT_CODES = [0, 4, 5, 8]

# https://pbs.twimg.com/hashflag/config-2021-01-15-01.json
TWITTER_HASHFLAGS_REGEX = re.compile("^.*hashflag/config-.*$")

WAYBACK_MACHINE_BACKOFF_TIME_SECONDS = 5 * 60


WPULL_ARGUMENT_WARC_HEADER = "--warc-header"
WPULL_ARGUMENT_DATABASE = "--database"
WPULL_ARGUMENT_OUTPUT_FILE = "--output-file"
WPULL_ARGUMENT_INPUT_FILE_URL_LIST = "--input-file"
WPULL_ARGUMENT_WARC_FILE = "--warc-file"
WPULL_ARGUMENT_WARC_TEMPDIR = "--warc-tempdir"
WPULL_ARGUMENT_WAITRETRY = "--waitretry"
WPULL_ARGUMENT_NO_ROBOTS = "--no-robots"
WPULL_ARGUMENT_WARC_MAX_SIZE = "--warc-max-size"
WPULL_ARGUMENT_HTML_PARSER = "--html-parser"
WPULL_ARGUMENT_PAGE_REQUISITES = "--page-requisites"
WPULL_ARGUMENT_DELETE_AFTER = "--delete-after"
WPULL_ARGUMENT_WARC_APPEND = "--warc-append"
WPULL_ARGUMENT_RECURSIVE = "--recursive"
WPULL_ARGUMENT_VERBOSE = "--verbose"

################
# WARC headers
################

WARC_HEADER_DATE = "date"
WARC_HEADER_DESCRIPTION = "description"

# Custom headers

# use .format() here becaues we need to put some format string markers in the string to put in numeric instances later
WARC_CUSTOM_HEADER_PREFIX = "X-twitch-daily-pogchamp-emote-"

WARC_HEADER_KEY_APPLICATION_NAME = "{}application-name".format(WARC_CUSTOM_HEADER_PREFIX)
WARC_HEADER_VALUE_APPLICATION_NAME = "archive_pogchamp_emote".format(WARC_CUSTOM_HEADER_PREFIX)

WARC_HEADER_KEY_APPLICATION_VERSION = "{}application-version".format(WARC_CUSTOM_HEADER_PREFIX)
WARC_HEADER_VALUE_APPLICATION_VERSION = f"{__version__}"

WARC_HEADER_KEY_APPLICATION_GITHUB_LINK = "{}application-github-link".format(WARC_CUSTOM_HEADER_PREFIX)
WARC_HEADER_VALUE_APPLICATION_GITHUB_LINK= "https://github.com/mgrandi/archive_pogchamp_emote"

WARC_HEADER_KEY_APPLICATION_GIT_HASH = "{}application-git-hash".format(WARC_CUSTOM_HEADER_PREFIX)

WARC_HEADER_STREAMER_TWITCH_LINK = "{}streamer-twitch-link".format(WARC_CUSTOM_HEADER_PREFIX)
WARC_HEADER_STREAMER_SOCIAL_MEDIA_URL_FORMAT = "{}streamer-social-media-link-{}".format(WARC_CUSTOM_HEADER_PREFIX, "{:03d}")
WARC_HEADER_STREAMER_SOCIAL_MEDIA_URL_WBM_FORMAT = "{}social-media-link-wbm-{}".format(WARC_CUSTOM_HEADER_PREFIX, "{:03d}")

WARC_HEADER_STREAMER_TWICH_TWEET_URL = "{}twitch-tweet-link".format(WARC_CUSTOM_HEADER_PREFIX)
WARC_HEADER_STREAMER_TWICH_TWEET_URL_WBM = "{}twitch-tweet-link-wbm".format(WARC_CUSTOM_HEADER_PREFIX)

WARC_HEADER_ADDITIONAL_URL_FORMAT = "{}additional-url-{}".format(WARC_CUSTOM_HEADER_PREFIX, "{:03d}")
WARC_HEADER_ADDITIONAL_URL_WBM_FORMAT = "{}additional-url-wbm-{}".format(WARC_CUSTOM_HEADER_PREFIX, "{:03d}")

WARC_HEADER_STREAMER_NAME = "{}streamer-name".format(WARC_CUSTOM_HEADER_PREFIX)




