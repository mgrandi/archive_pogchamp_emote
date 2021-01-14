import pathlib
import typing

import attr
import arrow


@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class WarcHeader:
    key:str = attr.ib()
    value:str = attr.ib()

@attr.s(auto_attribs=True, frozen=True, kw_only=True)
class DailyPogchampEmoteConfig:

    warc_output_folder:pathlib.Path = attr.ib()
    youtube_dl_output_folder:pathlib.Path = attr.ib()
    warc_tempdir_folder:pathlib.Path = attr.ib()
    warc_database_name:str = attr.ib()
    warc_output_file_name:str = attr.ib()
    warc_input_url_list_file_name:str = attr.ib()
    warc_file_name:str = attr.ib()
    emote_date:arrow.arrow.Arrow = attr.ib()

    twitch_emote_id:int = attr.ib()
    twitch_twitter_post_url:str = attr.ib()
    streamer_social_media_url:str = attr.ib()
    streamer_twitch_url:str = attr.ib()
    streamer_name:str = attr.ib()

    warc_headers:typing.Sequence[WarcHeader] = attr.ib()

