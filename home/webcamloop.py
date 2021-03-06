#!/usr/local/bin/python3
# encoding: utf-8
'''
webcamloop -- get image from cam and ftp it, loop

see configuration file

@author:     werner.fuerst@gmx.at

@copyright:  2020 werner.fuerst

@license:    CC0

@contact:    werner.fuerst@gmx.at
@deffield    updated: Updated
'''

__all__ = []
__version__ = 0.1
__date__ = '2020-02-21'
__updated__ = '2020-03-07'

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
import configparser
import sys
import logging
import time

from helpers import tools


# create logger
logger = logging.getLogger('webcam')
logger.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
# logger.addHandler(fh)
logger.addHandler(ch)


DEBUG = 0
TESTRUN = 0


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

  Created by wf on %s.
  Copyright 2020 wf. All rights reserved.

  Free Software

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    # helpers.tools.test1()
    logger.info('starting')

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
        image_file = local_config.get('image_loop', 'loop.jpeg')
        image_file_annotated = local_config.get('image_loop_annotated',
                                                'loop_annotated.jpeg')
        while True:

            logger.info("get image from cam")

            if not tools.get_image_from_webcam(config['WEBCAM'],
                                               image_file):
                logger.critical(
                    "giving up, did not get an image from cam")
                time.sleep(4)
                continue

            logger.info("crop and annotate image %s %s",
                        image_file, image_file_annotated)

            tools.annotate_image(image_file, image_file_annotated,
                                 do_crop=True)

            logger.info("send image to Webpage")

            tools.send_image_to_webpage(
                config['FTPLOOP'],
                image_file_annotated)

            time.sleep(4)
            for cnt in range(74):
                logger.info("in loop %s", cnt)
                if tools.is_there_anybody_out_there(
                        config['SEMAPHORE']):
                    break
                time.sleep(4)

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
    if TESTRUN:
        import doctest
        doctest.testmod()
    sys.exit(main())
