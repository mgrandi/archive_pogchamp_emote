import logging

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

        # create folder with the date if it doesn't exist
        if not emote_config.root_output_folder.exists():
            logger.info("making folder `%s`", emote_config.root_output_folder)
            emote_config.root_output_folder.mkdir()

        wpull_url_list_path = emote_config.root_output_folder / emote_config.warc_input_url_list_file_name

        # write wpull url list
        logger.info("writing wpull url list to `%s`", wpull_url_list_path)

        with open(wpull_url_list_path, "w", encoding="utf-8") as f:
            for iter_url in constants.WPULL_INPUT_URLS_FORMAT_LIST:
                url_to_write = iter_url.format(emote_config.twitch_emote_id)
                f.write(f"{url_to_write}\n")
                f.write("\n")

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
            streamer_social_media_link_archive = utils.save_archive_of_webpage_in_wbm(emote_config.streamer_social_media_url)
            f.write("--warc-header\n")
            f.write(f"twitch-tv-pogchamp-streamer-social-media-link:{emote_config.streamer_social_media_url}\n")
            f.write("--warc-header\n")
            f.write(f"twitch-tv-pogchamp-streamer-social-media-link-wbm:{streamer_social_media_link_archive}\n")

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



