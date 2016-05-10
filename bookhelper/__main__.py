from __future__ import absolute_import
import sys
import ConfigParser
import logging
import argparse
import json

from bookhelper import EXPORTKEYS
from bookhelper.starter import Starter


def merge_config(args):
    u'''Parse config and make the values look the same as from argparse.
       Command line arguments will not be overwritten - unless they have a
       default <> None.
    '''
    vargs = vars(args)
    config = ConfigParser.ConfigParser()
    config.read(args.conf)
    d = config[u'default']
    for k, v in d.items():
        if vargs.get(k, None) is None:
            v = v.replace(u'"', u'')
            s = v.split(u' ')
            if len(s) > 1:
                v = s
            elif k == u'export':
                v = [v]

            if v == u"True":
                v = True

            if v == u"False":
                v = False

            setattr(args, k, v)


def main():
    parser = argparse.ArgumentParser(prog=u"BOOKHELPER")
    subparsers = parser.add_subparsers(help=u'sub-command help', dest=u"cmd")
    subparsers.required = True
    parser.add_argument(
        u"-u", u"--user",
        help=u"Username")
    parser.add_argument(
        u"-p", u"--password",
        help=u"Password")
    parser.add_argument(
        u"-a", u"--api-url",
        help=u"Api URL")
    parser.add_argument(
        u"--no-https", help=u"Use http", action=u"store_true")
    parser.add_argument(
        u"--queued", help=u"Run command as asynchronous task", action=u"store_true")
    parser.add_argument(
        u"-l", u"--log",
        dest=u"loglevel",
        choices=[u'DEBUG', u'INFO', u'WARNING', u'ERROR', u'CRITICAL'],
        help=u"Set the logging level", default=u"INFO")
    parser.add_argument(
        u"-c", u"--conf",
        help=u"Path to config file", default=u"")
    # parser.add_argument(
    #    "--tmp-path",
    #    help="path to a tmp dir for file creation and celerydb")

    # shared for subcommands - d.r.y.
    book_args_kwargs = ((u"book",), {u'default': u'Beispielbuch', })
    version_args_kwargs = (
        (u"-v", u"--version"),
        {u'help': u'The version',
         u'default': u'live',
         }
    )

    parser_publish = subparsers.add_parser(u'publish', help=u'publish --help')
    parser_publish.add_argument(*book_args_kwargs[0], **book_args_kwargs[1])
    parser_publish.add_argument(*version_args_kwargs[0], **version_args_kwargs[1])
    parser_publish.add_argument(
        u"-e", u"--export",
        choices=EXPORTKEYS+[u'all'],
        help=u"Formate", nargs=u"*", default=[u'all'])
    parser_publish.add_argument(
        u"--printpage-title", help=u"Title of the printpage",
        default=u"_Druckversion")
    parser_publish.add_argument(
        u"--force-overwrite", help=u"Overwrite stable book version and files",
        action=u"store_true", default=False)

    parser_version = subparsers.add_parser(u'versionize', help=u'version --help')
    parser_version.add_argument(*book_args_kwargs[0], **book_args_kwargs[1])
    version_args_kwargs[1][u'required'] = True
    parser_version.add_argument(*version_args_kwargs[0], **version_args_kwargs[1])
    parser_version.add_argument(
        u"--no-doi",
        help=u"No DOI creation",
        action=u"store_true", default=False)
    parser_version.add_argument(u"--dc-symbol", help=u"Datacite symbol (user)")
    parser_version.add_argument(u"--dc-password", help=u"Datacite password")
    parser_version.add_argument(u"--dc-prefix", help=u"Datacite prefix")
    parser_version.add_argument(u"--dc-identifier", help=u"Datacite identifier")
    parser_version.add_argument(u"--dc-version", help=u"Datacite version")

    parser_status = subparsers.add_parser(u'status', help=u'status --help')
    parser_status.add_argument(u"task_id", help=u"Task id of a queued task")

    args = parser.parse_args()
    if args.conf:
        merge_config(args)

    logging.basicConfig(level=getattr(logging, args.loglevel))
    logging.debug(unicode(args))
    errors = []
    result = None
    s = Starter(args)
    result = s.start()
    errors += s.errors

    if not result:
        result = int(bool(errors))

    print json.dumps({u'errors': errors, u'result': result})
    return int(bool(errors))

if __name__ == u'__main__':
    sys.exit(main())
