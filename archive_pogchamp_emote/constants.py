
ARROW_DATE_FORMAT = "YYYY-MM-DD"

WPULL_DATABASE_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_database.sqlite3"
WPULL_OUTPUT_FILE_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_output.log"
WPULL_WARC_FILE_FORMAT = "{}_twitch-tv_pogchamp_emote"

WPULL_INPUT_URL_LIST_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_url_list.txt"
WPULL_ARGS_FILE_FORMAT = "{}_twitch-tv_pogchamp_emote_wpull_arguments.txt"
YTDL_ARGS_FILE_FORMAT = "{}_twitch-tv_pogchamp_emote_youtube-dl_arguments.txt"


CONFIG_PATH_ROOT_SECTION = "archive_pogchamp_emote"

CONFIG_PATH_TWITCH_EMOTE_ID = "twitch_emote_id"
CONFIG_PATH_TWITCH_TWITTER_POST_URL = "twitch_twitter_post_url"
CONFIG_PATH_STREAMER_SOCIAL_MEDIA_URL = "streamer_social_media_url"
CONFIG_PATH_STREAMER_TWITCH_URL = "streamer_twitch_url"
CONFIG_PATH_STREAMER_NAME = "streamer_name"
CONFIG_PATH_DATE = "date"
CONFIG_PATH_WARC_HEADERS = "warc_headers"

WPULL_INPUT_URLS_FORMAT_LIST = [
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/dark/1.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/dark/2.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/dark/3.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/light/1.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/light/2.0",
    "https://static-cdn.jtvnw.net/emoticons/v2/{}/default/light/3.0",
]

HTTP_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:86.0) Gecko/20100101 Firefox/86.0"

WAYBACK_ATTEMPT_MAX = 5

YOUTUBE_DL_FILE_TEMPLATE_STR = "%(title)s-%(id)s.%(ext)s"