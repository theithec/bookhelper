import os
import os.path
# from fabric.api import run
from fabric.api import settings
from fabric.context_managers import lcd
from fabric.operations import local


MW_REPO = "https://gerrit.wikimedia.org/r/p/mediawiki"
DEV_REPO = '/home/lotek/workspaces/php/booksprint2/src'
DEFAULT_BRANCH = 'REL1_26'
DEV_BRANCH_PREFIX = 'booksprint_'
DEV_LOCAL_BRANCH_PREFIX = 'booksprint_local_'
DEFAULT_MW_PATH = '/home/lotek/workspaces/php/booksprint2/w'
extensions = [
    'Annotator', 'Cite', 'FlaggedRevs', 'ParserFunctions',
    'Renameuser', 'SyntaxHighlight_GeSHi', 'Gadgets', 'Poem',
    'SpamBlacklist', 'VisualEditor', 'Widgets', 'WikiEditor',
    'ConfirmAccount'
]
dev_extensions = ['Bookmaker', ]
skins = ['Vector', ]
dev_skins = ['Handbuchio2', ]


def _do_mod(branch, mw_path, mods_name, mod, dev):
    mods_path = os.path.join(mw_path, mods_name)
    repo_path =  None
    if dev:
        repo_path = "{repo}/{path}".format(
            repo=DEV_REPO,
            path=mod)
    else:
        repo_path = "{repo}/{mods_name}/{mod}.git".format(
            repo=MW_REPO, mods_name=mods_name, mod=mod)

    with settings(warn_only=True), lcd(mods_path):
        print("In %s" % mods_path)
        mod_path = os.path.join(mods_path, mod)
        if not os.path.exists(mod_path):
            res = local('git submodule add %s' %  repo_path)

        local('git submodule update %s' %  mod)
        if dev:
            branch = "%s%s" % (DEV_BRANCH_PREFIX, branch)
        res = None
        with settings(warn_only=True), lcd(mod):
            print("\n%s %s:" % (mods_name, mod))
            res = local("git checkout -b {branch} origin/{branch}".format(
                branch=branch))

            if res.failed:
                local("git checkout {branch}".format(branch=branch))

            local("git pull")


def _do_mods(branch, mw_path, mods_name, mods, dev):
    mods_path = os.path.join(mw_path, mods_name)
    with lcd(mods_path):
        local('echo "" > .gitignore')
        for mod in mods:
            _do_mod(branch, mw_path, mods_name, mod, dev)


def install(branch=DEFAULT_BRANCH, mw_path=DEFAULT_MW_PATH):
    with lcd(mw_path):
        local("git pull")
        org_branch = branch
        with settings(warn_only=True):
            res = local("git checkout {branch}".format(
                branch=DEV_LOCAL_BRANCH_PREFIX + org_branch))
            if res.failed:
                res = local("git checkout {branch}".format(
                    branch=DEV_BRANCH_PREFIX + org_branch))

        if res.failed:
            local("git checkout -b {branch} origin/{org}".format(
                branch=DEV_BRANCH_PREFIX + org_branch, org=org_branch))
        else:
            local("git merge origin/{org}".format(org=org_branch))

    mods = (
        ("skins", skins, False),
        ("skins", dev_skins, True),
        ("extensions", extensions, False),
        ("extensions", dev_extensions, True),
    )
    for m in mods:
        _do_mods(branch, mw_path, mods_name=m[0], mods=m[1], dev=m[2])
