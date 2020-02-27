#!/usr/local/bin/python3
# encoding: utf-8
'''
webcamarch -- get image from cam and ftp it

seeconfiguration file

@author:     werner.fuerst@gmx.at

@copyright:  2020 werner.fuerst

@license:    Free software

@contact:    werner.fuerst@gmx.at
@deffield    updated: Updated
'''

import sys
# import os


from os import listdir, rename
from os.path import isfile, join
import ftplib
# import urllib.request
from datetime import datetime
# import shutil
import configparser
import socket
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter


# import helpers.tools
from helpers import tools



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

        local_config = config['LOCAL']
        picture = local_config.get('picture', 'archive.jpeg')
        picture_annotated = local_config.get('picture_annotated',
                                             'archive_crop.jpeg')
        retrydir = local_config.get('retrydir',
                                    '/home/werner/'
                                    'Dokumente/webcam/retry')

        print(datetime.strftime(datetime.now(None), "%Y-%m-%d--%H-%M-%S - ")
              + "get image from cam")

        if tools.get_image_from_webcam(config['WEBCAM']) == 0:
            print("giving up, did not get an image from cam")
            sys.exit()

        print(datetime.strftime(datetime.now(), "%Y-%m-%d--%H-%M-%S - ")
              + "crop an annotate image")

        tools.annotate_picture(picture, picture_annotated)

        print(datetime.strftime(datetime.now(), "%Y-%m-%d--%H-%M-%S - ") +
              "send image to Webpage")

        filename = (datetime.strftime(datetime.now(), "%Y-%m-%d--%H-%M-%S")
                    + '.jpeg')

        session_is_open = 0

        (session_is_open, session) = tools.send_imge_to_webpage(config['FTP'], filename)

        if session_is_open == 1:
            files = [fil for fil in listdir(retrydir)
                     if (isfile(join(retrydir, fil))
                         and fil.endswith('.jpeg'))]
            if not files:
                session.quit()
            else:
                for file in files:
                    if tools.send_imge_to_webpage_wos(config['FTP'], session, file):
                        rename(join(retrydir, file), join(retrydir, file) + 'xxx')
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
