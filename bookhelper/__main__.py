import sys
import configparser
import logging
import argparse
import json

from bookhelper import EXPORTKEYS
from  bookhelper.starter import Starter


def merge_config(args):
    '''Parse config and make the values look the same as from argparse.
       Command line arguments will not be overwritten - unless they have a
       default <> None.
    '''
    vargs = vars(args)
    config = configparser.ConfigParser()
    config.read(args.conf)
    d = config['default']
    for k, v in d.items():
        if vargs.get(k, None) is None:
            v = v.replace('"', '')
            s = v.split(' ')
            if len(s) > 1:
                 v = s
            elif k == 'export':
                v = [v]

            if v == "True":
                v = True

            if v == "False":
                v = False

            setattr(args, k, v)


def main():
    parser = argparse.ArgumentParser(prog="BOOKHELPER")
    subparsers = parser.add_subparsers(help='sub-command help', dest="cmd")
    subparsers.required = True
    parser.add_argument(
        "-u", "--user",
        help="Username")
    parser.add_argument(
        "-p", "--password",
        help="Password")
    parser.add_argument(
        "-a", "--api-url",
        help="Api URL")
    parser.add_argument(
        "--no-https", help="Use http", action="store_true")
    parser.add_argument(
        "--queued", help="Run command as asynchronous task", action="store_true")
    parser.add_argument(
        "-l", "--log",
        dest="loglevel",
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help="Set the logging level", default="INFO")
    parser.add_argument(
        "-c", "--conf",
        help="Path to config file", default="")
    #parser.add_argument(
    #    "--tmp-path",
    #    help="path to a tmp dir for file creation and celerydb")

    # shared for subcommands - d.r.y.
    book_args_kwargs = (("book",), {'default': 'Beispielbuch', })
    version_args_kwargs = (
        ("-v", "--version"),
        {'help': 'The version',
         'default': 'live',
         }
    )


    parser_publish = subparsers.add_parser('publish', help='publish --help')
    parser_publish.add_argument(*book_args_kwargs[0], **book_args_kwargs[1])
    parser_publish.add_argument(*version_args_kwargs[0], **version_args_kwargs[1])
    parser_publish.add_argument(
        "-e", "--export",
        choices=EXPORTKEYS+['all'],
        help="Formate", nargs="*", default=['all'])
    parser_publish.add_argument(
        "--printpage-title", help="Title of the printpage",
        default="_Druckversion")
    parser_publish.add_argument(
        "--force-overwrite", help="Overwrite stable book version and files",
        action="store_true", default=False)

    parser_version = subparsers.add_parser('versionize', help='version --help')
    parser_version.add_argument(*book_args_kwargs[0], **book_args_kwargs[1])
    version_args_kwargs[1]['required'] = True
    parser_version.add_argument(*version_args_kwargs[0], **version_args_kwargs[1])
    parser_version.add_argument(
        "--no-doi",
        help="No DOI creation",
        action="store_true", default=False)
    parser_version.add_argument("--dc-symbol", help="Datacite symbol (user)")
    parser_version.add_argument("--dc-password", help="Datacite password")
    parser_version.add_argument("--dc-prefix", help="Datacite prefix")
    parser_version.add_argument("--dc-identifier", help="Datacite identifier")
    parser_version.add_argument("--dc-version", help="Datacite version")

    parser_status = subparsers.add_parser('status', help='status --help')
    parser_status.add_argument("task_id", help="Task id of a queued task")

    args = parser.parse_args()
    if args.conf:
        merge_config(args)

    logging.basicConfig(level=getattr(logging, args.loglevel))
    logging.debug(str(args))
    errors = []
    result = None
    s = Starter(args)
    result = s.start()
    errors += s.errors

    #for err in errors:
        #  print(err, file=sys.stderr) # then we get the logging too
    #    print(err)
    if not result:
        result = int(bool(errors))

    print(json.dumps({'errors': errors, 'result': result}))
    return int(bool(errors))

if __name__ == '__main__':
    sys.exit(main())
