
def on_no_errors(meth):
    '''Decorator for methods in classes with an error attribute.'''
    def inner(*args, **kwargs):
        if not args[0].errors:
            return meth(*args, **kwargs)

    return inner

def  get_fullurl(site, title):
    '''Full url for a mediawiki pagetitle'''
    q = site.api("query", titles=title, prop="info", inprop="url")
    return list(q['query']['pages'].values())[0]['fullurl']


def get_siteurl(site):
    '''mwclient.Site does not have a "full url" attribute.
        But we need one for expanding relative paths.'''
    scheme = 'https'
    host = site.host
    if isinstance(host, (list, tuple)):
        scheme, host = host
    return '{scheme}://{host}'.format(scheme=scheme, host=host)

def template_from_info(info_):
    t = u"{{Bookinfo\n"
    info = dict([(k.upper(), v) for k, v in info_.items()])
    for key in ['ABSTRACT', 'AUTOREN', 'HERAUSGEBER', 'KONTRIBUTOREN',
                'STAND', 'DOI', 'VERSION', 'TITLE']:
        if key in info:
            t += u"|%s = %s\n" % (key, info[key])

    t += "}}\n"
    return t

