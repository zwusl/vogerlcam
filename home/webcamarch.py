#!/usr/local/bin/python3
# encoding: utf-8
'''
webcamarch -- get image from cam and ftp it

see configuration file

@author:     werner.fuerst@gmx.at

@copyright:  2020 werner.fuerst

@license:    Free software

@contact:    werner.fuerst@gmx.at
@deffield    updated: Updated
'''

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import configparser
from datetime import datetime
from os import listdir, rename
from os.path import isfile, join
import sys
import logging

from helpers import tools


# create logger
logger = logging.getLogger('webcam')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages #
# fh = logging.FileHandler('spam.log')
# fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
# logger.addHandler(fh)
logger.addHandler(ch)

logger.info('starting')


# import os
# import ftplib
# import urllib.request
# import shutil
# import socket
# import helpers.tools
__all__ = []
__version__ = 0.1
__date__ = '2020-02-21'
__updated__ = '2020-02-21'

DEBUG = 0
TESTRUN = 0
PROFILE = 0


class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg

    def __str__(self):
        return self.msg

    def __unicode__(self):
        return self.msg


def main(argv=None):  # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)

#     program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version,
                                                     program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2020 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    # helpers.tools.test1()
    logger.info('log1')
    tools.test1()
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license,
                                formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument("-v", "--verbose", dest="verbose",
                            action="count",
                            help="set verbosity level "
                            "[default: %(default)s]")
        parser.add_argument('-V', '--version', action='version',
                            version=program_version_message)
        parser.add_argument("-c", "--config", dest="configfile",
                            help="config file. [default: "
                            "%(default)s]", metavar="FILE")

        # Process arguments
        args = parser.parse_args()

        verbose = args.verbose

        configfile = args.configfile

        if verbose is not None and verbose > 0:
            print("Verbose mode on")

        config = configparser.ConfigParser()
        config.read(configfile)

        local_config = config['DEFAULT']
        ftp_config = config['FTP']
        picture = local_config.get('picture_arch', 'archive.jpeg')
        picture_annotated = local_config.get('picture_arch_annotated',
                                             'archive_crop.jpeg')
        retrydir = local_config.get('retrydir',
                                    '/home/werner/'
                                    'Dokumente/webcam/retry')

        logger.info("get image from cam")

        if tools.get_image_from_webcam(config['WEBCAM'],
                                       picture) == 0:
            logger.critical("giving up, did not get an image from cam")
            sys.exit()

        logger.info("crop an annotate image")

        tools.annotate_picture(picture, picture_annotated)

        logger.info("send image to Webpage")

        filename = (datetime.strftime(datetime.now(), "%Y-%m-%d--%H-%M-%S")
                    + '.jpeg')

        session_is_open = 0

        (session_is_open, session) = tools.send_imge_to_webpage(
            config['FTP'], ftp_config.get('dirarch'), filename, picture_annotated)

        if session_is_open == 1:
            files = [fil for fil in listdir(retrydir)
                     if (isfile(join(retrydir, fil))
                         and fil.endswith('.jpeg'))]
            if not files:
                session.quit()
            else:
                for file in files:
                    if tools.send_imge_to_webpage_wos(config['FTP'],
                                                      session, file):
                        rename(join(retrydir, file),
                               join(retrydir, file) + 'xxx')
                session.quit()
        return 0
    except KeyboardInterrupt:
        # handle keyboard interrupt #
        return 0
#     except Exception as ex_all:
#         if DEBUG or TESTRUN:
#             raise ex_all
#         indent = len(program_name) * " "
#         sys.stderr.write(program_name + ": " + repr(ex_all) + "\n")
#         sys.stderr.write(indent + "  for help use --help")
#         return 2


if __name__ == "__main__":
    if DEBUG:
        sys.argv.append("-h")
        sys.argv.append("-v")
        sys.argv.append("-r")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        profile_filename = 't1.w2_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        ps_prof = pstats.Stats(profile_filename, stream=statsfile)
        stats = ps_prof.strip_dirs().sort_stats('cumulative')
        stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
