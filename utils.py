import logging
import sys
import time
import configparser
import requests
from os.path import isfile
from collections import OrderedDict
import pdb

logger = logging.getLogger()
cp = configparser.ConfigParser()

reports_cfg = 'reports.cfg'
squad = 'https://qa-reports.linaro.org'
api = 'api'
projects = 'projects'
grp_slug_arg = '?group__slug='


def urljoiner(*args):
    '''
        Joins given arguments into an url. Trailing but not leading slashes are
        stripped for each argument.
    '''
    return "/".join(map(lambda x: str(x).rstrip('/'), args))


def get_url(url, retries=3):
    logger.info("retrieving %s" % url)
    r = requests.get(url)
    try:
        r.raise_for_status()
    except:
        if retries <= 0:
            raise
        logger.warn("Retrying {}".format(url))
        lime.sleep(30)
        return get_url(url, retries=retries-1)
    return r


def get_objects(url):
    r = get_url(url)
    for obj in r.json()['results']:
        yield get_url(obj['url'])
    if r.json()['next'] is not None:
        yield from get_objects(r.json()['next'])

def get_proj_slugs(args):
    if not args.group:
        print("group slug/name missing. Exiting")
        sys.exit(1)
    grp_url = urljoiner(squad, api, projects) + grp_slug_arg + args.group
    for res in get_objects(grp_url):
        url = res.json()['url']
        prj_slug = get_url(url).json()['slug']
        print(prj_slug)



#def gen_builds_json(args):
#    if not args.group:
#        logger.error('Missing group. Specify group to generate builds file for. Use -g')
#        sys.exit(1)
#    if not isfile(reports_cfg):
#        logger.error('reports.cfg is missing! Exiting')
#        sys.exit(1)
#    else:
#        try:
#            cp.read(reports_cfg)
#            bld_jsn = cp['settings']['builds_file']
#            token = cp['settings']['token']
#            pdb.set_trace()
#            url = urljoiner(squad, api, projects) + slug_arg + args.group
#            res = query_api(url, token)
#            proj = OrderedDict({args.group: []})
#            build = OrderedDict()
#            for project in res['results']:
#                proj.update(OB
#
#            
#        except ValueError:
#            logger.info(ValueError)
