from __future__ import absolute_import
import re
tocline_internal_links_re = re.compile(ur'((?:#|\*)+).*\[\[(.*)\]\]')
tocline_external_links_re = re.compile(ur'((?:#|\*)+).*\[(.*)\]')


def parse_tocline(line, tocline_re):

    match = re.match(tocline_re, line.strip())
    # logging.debug("MATCH %s %s " % (line, str(match)))
    list_part, link_part = match.groups()
    depth = len(list_part)
    link_parts = link_part.split(u'|')
    return depth, link_parts


def get_siteurl(site):
    u'''mwclient.Site does not have a "full url" attribute.
        But we need one for expanding relative paths.'''
    scheme = u'https'
    host = site.host
    if isinstance(host, (list, tuple)):
        scheme, host = host
    return u'{scheme}://{host}'.format(scheme=scheme, host=host)


def on_no_errors(meth):
    u'''Decorator for methods in classes with an error attribute.'''
    def inner(*args):
        if not args[0].errors:
            return meth(*args)
    return inner


def parse_template_text(txt):
    txt = txt[txt.find(u'|'):]
    data = {}
    if not txt:
        return data

    while(True):
        next_ = txt.find(u'|')
        keyval = txt[:next_].split(u"=")
        txt = txt[next_ + 1:]
        if len(keyval) == 2:
            k, v = keyval
            data[k.strip()] = v.strip()
        if next_ < 0:
            break

    return data


def template_from_info(info):
    #import pdb; pdb.set_trace()
    t = u"{{Bookinfo\n"
    info = dict([(k.upper(), v) for k,v in info.items()])
    for key in [u'ABSTRACT', u'AUTOREN', u'HERAUSGEBER', u'KONTRIBUTOREN',
                u'STAND', u'DOI']:
        key = key.upper()

        if key in info:
            t += u"|%s = %s\n" % (key, info[key])

    t += u"}}\n"
    return t
