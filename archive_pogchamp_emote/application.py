import logging
import pprint
import subprocess
import sys

from archive_pogchamp_emote import model as model
from archive_pogchamp_emote import utils as utils
from archive_pogchamp_emote import constants as constants


logger = logging.getLogger(__name__)

class Application:
    '''
    main application
    '''

    def __init__(self, args):
        ''' constructor
        @param logger the Logger instance
        @param args - the namespace object we get from argparse.parse_args()
        '''

        self.args = args

    def run(self):

        emote_config = utils.build_emote_config_from_argparse_args(self.args)

        wpull_pex_path = self.args.wpull_pex_path

        folders_to_create_if_they_dont_exist = [
            emote_config.root_output_folder,
            emote_config.youtube_dl_output_folder,
            emote_config.warc_output_folder
        ]

        for iter_folder_path in folders_to_create_if_they_dont_exist:
            if not iter_folder_path.exists():
                logger.info("creating folder `%s` because it doesn't exist yet", iter_folder_path)
                iter_folder_path.mkdir()
                logger.info("folder creation was successful")
            else:
                logger.info("folder `%s` already exists, don't need to recreate it", iter_folder_path)

        wpull_url_list_path = emote_config.root_output_folder / emote_config.warc_input_url_list_file_name

        # write wpull url list
        logger.info("writing wpull url list to `%s`", wpull_url_list_path)

        with open(wpull_url_list_path, "w", encoding="utf-8") as f:

            # write the base twitch emote URLs
            for iter_url in constants.WPULL_INPUT_URLS_FORMAT_LIST:
                url_to_write = iter_url.format(emote_config.twitch_emote_id)
                f.write(f"{url_to_write}\n")

            # write any additional urls the user may have provided in the configuration
            for iter_url in emote_config.additional_urls:
                f.write(f"{iter_url}\n")

        logger.info("writing wpull url list was successful")

        # write wpull arguments file
        wpull_arguments_path = emote_config.root_output_folder / emote_config.warc_arguments_file_name
        logger.info("writing wpull arguments to `%s`", wpull_arguments_path)

        with open(wpull_arguments_path, "w", encoding="utf-8") as f:

            f.write("--database\n")
            f.write(f"{emote_config.warc_output_folder / emote_config.warc_database_name}\n")
            f.write("--output-file\n")
            f.write(f"{emote_config.warc_output_folder / emote_config.warc_output_file_name}\n")
            f.write("--input-file\n")
            f.write(f"{emote_config.root_output_folder / emote_config.warc_input_url_list_file_name}\n")
            f.write("--warc-file\n")
            f.write(f"{emote_config.warc_output_folder / emote_config.warc_file_name}\n")
            f.write("--warc-tempdir\n")
            f.write(f"{emote_config.warc_tempdir_folder}\n")

            #########################################################################
            # WARC headers that always get included
            ##########################################################################
            f.write("--warc-header\n")
            f.write(f"description:twitch.tv PogChamp emote for {emote_config.emote_date.format(constants.ARROW_DATE_FORMAT)}\n")
            f.write("--warc-header\n")
            f.write(f"twitch-tv-pogchamp-streamer-name:{emote_config.streamer_name}\n")

            # link to the streamer's twitch page
            f.write("--warc-header\n")
            f.write(f"twitch-tv-pogchamp-streamer-twitch-link:{emote_config.streamer_twitch_url}\n")
            # f.write("--warc-header\n")
            # f.write(f"twitch-tv-pogchamp-streamer-twitch-link-wbm:{test}\n")

            # link to the streamer's social media page
            for idx, iter_social_media_url in enumerate(emote_config.streamer_social_media_urls):
                streamer_social_media_link_archive = utils.save_archive_of_webpage_in_wbm(iter_social_media_url)
                f.write("--warc-header\n")
                f.write(f"twitch-tv-pogchamp-streamer-social-media-link-id-{idx:03d}:{iter_social_media_url}\n")
                f.write("--warc-header\n")
                f.write(f"twitch-tv-pogchamp-streamer-social-media-link-wbm-id-{idx:03d}:{streamer_social_media_link_archive}\n")

            # link to the twitter.com post by the Twitch user account announcing the emote of the day
            twitch_twitter_post_url_archive = utils.save_archive_of_webpage_in_wbm(emote_config.twitch_twitter_post_url)
            f.write("--warc-header\n")
            f.write(f"twitch-tv-pogchamp-twitch-tweet-link:{emote_config.twitch_twitter_post_url}\n")
            f.write("--warc-header\n")
            f.write(f"twitch-tv-pogchamp-twitch-tweet-link-wbm:{twitch_twitter_post_url_archive}\n")


            f.write("--warc-header\n")
            f.write(f"date:{emote_config.emote_date.format(constants.ARROW_DATE_FORMAT)}\n")

            ##############################################################################
            # custom warc headers, provided by the configuration file
            ##############################################################################
            for iter_header in emote_config.warc_headers:

                f.write("--warc-header\n")
                f.write(f"{iter_header.key}:{iter_header.value}\n")

            #########################################################
            # rest of the wpull arguments
            ########################################################
            f.write("--waitretry\n")
            f.write("30\n")
            f.write("--no-robots\n")
            f.write("--warc-max-size\n")
            f.write("5368709000\n")
            f.write("--html-parser\n")
            f.write("libxml2-lxml\n")
            f.write("--page-requisites\n")
            f.write("--delete-after\n")
            f.write("--warc-append\n")
            f.write("--recursive\n")
            f.write("--verbose\n")

        logger.info("writing wpull arguments was successful")

        if emote_config.twitch_twitter_post_is_video:
            # create youtube-dl arguments
            ytdl_logger = logger.getChild("ytdl")

            # see https://github.com/ytdl-org/youtube-dl/blob/3e4cedf9e8cd3157df2457df7274d0c842421945/youtube_dl/YoutubeDL.py#L137-L312
            ytdl_arguments_dict = {
                "write_all_thumbnails": True,
                "writesubtitles": True,
                "allsubtitles": True, # YoutubeDL.py says that we need "writesubtitles" in order for this to work
                "writeinfojson": True,
                "writeannotations": True,
                "writedescription": True,
                "keepvideo": True,
                "format": "bestvideo+bestaudio/best", # this should be default but lets explicitly set it just in case,
                "newline": True,
                "outtmpl": f"{emote_config.youtube_dl_output_folder}/{constants.YOUTUBE_DL_FILE_TEMPLATE_STR}",
                # set because the progress outputs use carriage returns so it kinda messes up the stdout logging
                # and looks weird in the file logging. So adding this supresses the default console progress
                # logging, but doesn't prevent youtube-dl from calling the progress hooks it seems.
                "noprogress": True,
                "progress_hooks": [utils.youtube_dl_progress_hook(ytdl_logger)],
                "logger": ytdl_logger,
                # this seems to output extra stuff to both stdout and the ytdl logger, should report a bug about this...
                # "verbose": True,
            }

            logger.debug("youtube-dl arguments: `%s`", ytdl_arguments_dict)

            # write youtube-dl arguments file (for reference, we are just using youtube-dl as a library here)
            ytl_arguments_path = emote_config.root_output_folder / emote_config.ytdl_arguments_file_name
            logger.info("writing youtube-dl arguments to `%s`", ytl_arguments_path)

            with open(ytl_arguments_path, "w", encoding="utf-8") as f:

                f.write(pprint.pformat(ytdl_arguments_dict))

            logger.info("writing youtube-dl arguments was successful")

            # now download the twitter video

            logger.info("Downloading any twitter videos to `%s`", emote_config.youtube_dl_output_folder)
            utils.save_video_with_youtube_dl(ytdl_arguments_dict, emote_config.twitch_twitter_post_url)
            logger.info("video download successful")

        else:
            logger.info("config has marked that the Twitch twitter post was not a video, not calling youtube-dl")

            no_video_txt_path = emote_config.youtube_dl_output_folder / "no_video.txt"
            logger.info("writing `%s`", no_video_txt_path)

            with open(no_video_txt_path, "w", encoding="utf-8") as f:
                f.write(f"no video because the configuration file specified that the twitter post `{emote_config.twitch_twitter_post_url}` had no video, so we skipped downloading it")

            logger.info("writing no_video.txt was successful")


        # now call wpull
        wpull_argument_list = [
            sys.executable,
            wpull_pex_path,
            f"@{wpull_arguments_path}"
        ]

        logger.info("executing wpull with the arguments: `%s`", wpull_argument_list)
        try:
            # don't use `check=True` cause we need to check the status codes , and subprocess.run() doesn't have a built in
            # mechanism to do that
            wpull_result = subprocess.run(wpull_argument_list, capture_output=True)
            utils.check_completedprocess_for_acceptable_exit_codes(wpull_result, constants.ACCEPTABLE_WPULL_EXIT_CODES)
        except subprocess.CalledProcessError as e:
            logger.error("error running wpull: Exception: `%s`, output: `%s`, stderr: `%s`",
                e, e.output, e.stderr)
            raise e

        logger.info("executing wpull was successful")
