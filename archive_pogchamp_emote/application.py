import logging
import pprint
import subprocess
import sys
import json

import attr

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

        logger.info("starting, version `%s`, git hash `%s`", constants.WARC_HEADER_VALUE_APPLICATION_VERSION, utils.get_git_hash())

        emote_config = utils.build_emote_config_from_argparse_args(self.args)

        wpull_pex_path = self.args.wpull_pex_path

        folders_to_create_if_they_dont_exist = [
            emote_config.root_output_folder,
            emote_config.youtube_dl_output_folder,
            emote_config.warc_output_folder
        ]

        #########################################################################
        # creating folders
        #########################################################################
        for iter_folder_path in folders_to_create_if_they_dont_exist:
            if not iter_folder_path.exists():
                logger.info("creating folder `%s` because it doesn't exist yet", iter_folder_path)
                iter_folder_path.mkdir()
                logger.info("folder creation was successful")
            else:
                logger.info("folder `%s` already exists, don't need to recreate it", iter_folder_path)

        wpull_url_list_path = emote_config.root_output_folder / emote_config.warc_input_url_list_file_name

        #########################################################################
        # write version info file
        #########################################################################
        ver_info_path = emote_config.root_output_folder / emote_config.application_version_info_name
        logger.info("writing app version info file to `%s`", ver_info_path)

        with open(ver_info_path, "w", encoding="utf-8") as f:

            appversion = utils.get_app_version_info()
            appversion_dict = attr.asdict(appversion)
            json_to_write = json.dumps(appversion_dict, indent=4)
            f.write(json_to_write)

        logger.info("writing of app version info file was successful")

        #########################################################################
        # write wpull url list
        #########################################################################
        logger.info("writing wpull url list to `%s`", wpull_url_list_path)

        with open(wpull_url_list_path, "w", encoding="utf-8") as f:

            # write the base twitch emote URLs
            for iter_url in constants.WPULL_INPUT_URLS_FORMAT_LIST:
                url_to_write = iter_url.format(emote_config.twitch_emote_id)
                f.write(f"{url_to_write}\n")

            # write any additional urls the user may have provided in the configuration
            logger.info("including `%s` additional urls to save in the WARC",
                len(emote_config.additional_urls_to_include_in_warc))
            for iter_url in emote_config.additional_urls_to_include_in_warc:
                f.write(f"{iter_url}\n")

        logger.info("writing wpull url list was successful")

        #########################################################################
        # write wpull arguments file
        #########################################################################
        wpull_arguments_path = emote_config.root_output_folder / emote_config.warc_arguments_file_name
        logger.info("writing wpull arguments to `%s`", wpull_arguments_path)

        with open(wpull_arguments_path, "w", encoding="utf-8") as f:

            f.write(f"{constants.WPULL_ARGUMENT_DATABASE}\n")
            f.write(f"{emote_config.warc_output_folder / emote_config.warc_database_name}\n")
            f.write(f"{constants.WPULL_ARGUMENT_OUTPUT_FILE}\n")
            f.write(f"{emote_config.warc_output_folder / emote_config.warc_output_file_name}\n")
            f.write(f"{constants.WPULL_ARGUMENT_INPUT_FILE_URL_LIST}\n")
            f.write(f"{emote_config.root_output_folder / emote_config.warc_input_url_list_file_name}\n")
            f.write(f"{constants.WPULL_ARGUMENT_WARC_FILE}\n")
            f.write(f"{emote_config.warc_output_folder / emote_config.warc_file_name}\n")
            f.write(f"{constants.WPULL_ARGUMENT_WARC_TEMPDIR}\n")
            f.write(f"{emote_config.warc_tempdir_folder}\n")

            #########################################################################
            # WARC headers that always get included
            ##########################################################################
            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_DESCRIPTION}:Daily https://twitch.tv PogChamp emote for {emote_config.emote_date.format(constants.ARROW_DATE_FORMAT)}\n")
            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_STREAMER_NAME}:{emote_config.streamer_name}\n")

            # link to the streamer's twitch page
            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_STREAMER_TWITCH_LINK}:{emote_config.streamer_twitch_url}\n")


            #########################################################################
            # link to the streamer's social media page + WBM save
            #########################################################################
            logger.info("saving `%s` streamer social media pages via the Wayback Machine",
                len(emote_config.streamer_social_media_urls))
            for idx, iter_social_media_url in enumerate(emote_config.streamer_social_media_urls):

                streamer_social_media_link_archive = utils.save_archive_of_webpage_in_wbm(iter_social_media_url, self.args.no_wbm_save)

                f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
                f.write(f"{constants.WARC_HEADER_STREAMER_SOCIAL_MEDIA_URL_FORMAT.format(idx)}:{iter_social_media_url}\n")

                f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
                f.write(f"{constants.WARC_HEADER_STREAMER_SOCIAL_MEDIA_URL_WBM_FORMAT.format(idx)}:{streamer_social_media_link_archive}\n")

            #########################################################################
            # link to the twitter.com post by the Twitch user account announcing the emote of the day
            #########################################################################
            logger.info("saving the announcement twitter.com/twitch post via the Wayback Machine")
            twitch_twitter_post_url_archive = utils.save_archive_of_webpage_in_wbm(emote_config.twitch_twitter_post_url, self.args.no_wbm_save)

            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_STREAMER_TWICH_TWEET_URL}:{emote_config.twitch_twitter_post_url}\n")

            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_STREAMER_TWICH_TWEET_URL_WBM}:{twitch_twitter_post_url_archive}\n")

            #########################################################################
            # any other links the configuration file says to include as headers (plus the WBM backup)
            #########################################################################
            logger.info("saving `%s` additional url(s) via the Wayback Machine",
                len(emote_config.additional_urls_to_save_via_wbm))

            for idx, iter_additional_url in enumerate(emote_config.additional_urls_to_save_via_wbm):

                iter_additional_url_archive = utils.save_archive_of_webpage_in_wbm(iter_additional_url, self.args.no_wbm_save)

                f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
                f.write(f"{constants.WARC_HEADER_ADDITIONAL_URL_FORMAT.format(idx)}:{iter_additional_url}\n")

                f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
                f.write(f"{constants.WARC_HEADER_ADDITIONAL_URL_WBM_FORMAT.format(idx)}:{iter_additional_url_archive}\n")

            # date
            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_DATE}:{emote_config.emote_date.format(constants.ARROW_DATE_FORMAT)}\n")


            ##############################################################################
            # custom warc headers, provided by the configuration file
            ##############################################################################
            for iter_header in emote_config.extra_warc_headers:

                f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
                f.write(f"{iter_header.key}:{iter_header.value}\n")

            #########################################################
            # warc headers for this application
            #########################################################
            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_KEY_APPLICATION_NAME}:{constants.WARC_HEADER_VALUE_APPLICATION_NAME}\n")

            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_KEY_APPLICATION_VERSION}:{constants.WARC_HEADER_VALUE_APPLICATION_VERSION}\n")

            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_KEY_APPLICATION_GITHUB_LINK}:{constants.WARC_HEADER_VALUE_APPLICATION_GITHUB_LINK}\n")

            f.write(f"{constants.WPULL_ARGUMENT_WARC_HEADER}\n")
            f.write(f"{constants.WARC_HEADER_KEY_APPLICATION_GIT_HASH}:{utils.get_git_hash()}\n")

            #########################################################
            # rest of the wpull arguments
            ########################################################
            f.write(f"{constants.WPULL_ARGUMENT_WAITRETRY}\n")
            f.write("30\n")
            f.write(f"{constants.WPULL_ARGUMENT_NO_ROBOTS}\n")
            f.write(f"{constants.WPULL_ARGUMENT_WARC_MAX_SIZE}\n")
            f.write("5368709000\n")
            f.write(f"{constants.WPULL_ARGUMENT_HTML_PARSER}\n")
            f.write("libxml2-lxml\n")
            f.write(f"{constants.WPULL_ARGUMENT_PAGE_REQUISITES}\n")
            f.write(f"{constants.WPULL_ARGUMENT_DELETE_AFTER}\n")
            f.write(f"{constants.WPULL_ARGUMENT_WARC_APPEND}\n")
            f.write(f"{constants.WPULL_ARGUMENT_RECURSIVE}\n")
            f.write(f"{constants.WPULL_ARGUMENT_VERBOSE}\n")

        logger.info("writing wpull arguments was successful")

        #########################################################################
        # save twitter.com/twitch twitter post with youtube-dl
        #########################################################################
        if emote_config.twitch_twitter_post_is_video:


            logger.info("Downloading the twitter.com/twitch announcement video")

            utils.save_video_with_youtube_dl(emote_config.youtube_dl_output_folder,
                emote_config.twitch_twitter_post_url,
                emote_config.ytdl_arguments_file_name,
                self.args.no_youtube_dl)

            logger.info("video download successful")

        else:
            logger.info("config has marked that the Twitch twitter post was not a video, not calling youtube-dl")

            filename = "no_twitch.com_twitter_announcement_video.txt"
            no_video_txt_path = emote_config.youtube_dl_output_folder / "no_twitch.com_twitter_announcement_video.txt"
            logger.info("writing `%s`", no_video_txt_path)

            with open(no_video_txt_path, "w", encoding="utf-8") as f:
                f.write(f"no video because the configuration file specified that the twitter post `{emote_config.twitch_twitter_post_url}` had no video, so we skipped downloading it")

            logger.info("writing `%s` was successful", filename)


        #########################################################################
        # save any other videos in the additional_urls_to_save_via_youtube_dl config
        #########################################################################
        logger.info("saving `%s` additional video(s) with youtube-dl",
            len(emote_config.additional_urls_to_save_via_youtube_dl))

        for iter_video_url in emote_config.additional_urls_to_save_via_youtube_dl:
            utils.save_video_with_youtube_dl(emote_config.youtube_dl_output_folder,
                iter_video_url,
                emote_config.ytdl_arguments_file_name,
                self.args.no_youtube_dl)


        #########################################################################
        # call wpull
        #########################################################################

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
