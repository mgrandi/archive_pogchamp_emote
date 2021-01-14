import logging

from archive_pogchamp_emote import model as model
from archive_pogchamp_emote import utils as utils

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

