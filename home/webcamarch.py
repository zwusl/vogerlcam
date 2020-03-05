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

__all__ = []
__version__ = 0.1
__date__ = '2020-02-21'
__updated__ = '2020-02-21'

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


DEBUG = 0
TESTRUN = 0


def main(argv=None):
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

        tools.annotate_picture(picture, picture_annotated, 0, 1)

        logger.info("send image to Webpage")

        filename = (datetime.strftime(datetime.now(), "%Y-%m-%d--%H-%M-%S")
                    + '_sm.jpg')

        session_is_open = 0


        (session_is_open, session) = tools.send_image_to_webpage(
            config['FTPARCH'],
            filename, picture_annotated)

        if session_is_open == 1:
            files = [fil for fil in listdir(retrydir)
                     if (isfile(join(retrydir, fil))
                         and fil.endswith('_sm.jpg'))]
            if not files:
                session.quit()
            else:
                for file in files:
                    if tools.send_image_to_webpage_wos(config['FTPARCH'],
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
    sys.exit(main())
