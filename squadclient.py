import sys
import logging
import sys
import time
import configparser
import requests
from os.path import isfile
import pdb

logger = logging.getLogger()
cp = configparser.ConfigParser()

reports_cfg = "reports.cfg"
squad = "https://qa-reports.linaro.org"
api = "api"
projects = "projects"
grp_slug_arg = "?group__slug="
proj_slug = "?slug="


def urljoiner(*args):
    """
        Joins given arguments into an url. Trailing but not leading slashes are
        stripped for each argument.
    """
    return "/".join(map(lambda x: str(x).rstrip("/"), args))


def get_url(url, retries=3):
    logger.info("retrieving %s" % url)
    r = requests.get(url)
    try:
        r.raise_for_status()
    except:
        if retries <= 0:
            raise
        logger.warn("Retrying {}".format(url))
        time.sleep(30)
        return get_url(url, retries=retries - 1)
    return r


def get_objects(url):
    r = get_url(url)
    for obj in r.json()["results"]:
        yield get_url(obj["url"])
    if r.json()["next"] is not None:
        yield from get_objects(r.json()["next"])


def _get_tests(url, t_or_m):
    if t_or_m == "m":
        keyword = "result"
    else:
        keyword = "status"
    r = get_url(url)
    for test in r.json()["results"]:
        sliced_name = test["name"].rsplit("/")
        yield (sliced_name[0], sliced_name[1], test[keyword])
    if r.json()["next"] is not None:
        yield from _get_tests(r.json()["next"], keyword)


def get_proj_slugs(args):
    if not args.group:
        print("group slug/name missing. Exiting")
        sys.exit(1)
    grp_url = urljoiner(squad, api, projects) + grp_slug_arg + args.group
    for res in get_objects(grp_url):
        url = res.json()["url"]
        prj_slug = get_url(url).json()["slug"]
        print(prj_slug)


class TestRun:
    def __init__(self, env, completed, job_url, tests, metrics):
        self.env = env
        self.completed = completed
        self.job_url = job_url
        self.tests = tests
        self.metrics = metrics


class Test:
    def __init__(self, suite, name, status):
        self.suite = suite
        self.name = name
        self.status = status


class Metric:
    def __init__(self, suite, name, result):
        self.suite = suite
        self.name = name
        self.result = result


class Client:
    """Class aimed to represent a squad client """

    token = None
    api_url = urljoiner(squad, api, projects)

    def __init__(self, target_proj, num_builds=1):
        """Client object is tied to one project for now. """
        self.project_url = Client.api_url + proj_slug + target_proj
        self.num_builds = num_builds
        self.builds = []

        # self.__init_cache()

    #    def __init_cache(self):
    #        """init cache for the project"""
    #        #TODO enable_diable cache func
    #        req_cache.install_cache(self.project)
    def get_data(self):
        builds_url = get_url(self.project_url).json()["results"][0]["builds"]
        i = 0
        for bld in get_objects(builds_url):
            if i == self.num_builds:
                break
            bldjson = bld.json()
            testruns = []
            for tr in get_objects(bldjson["testruns"]):
                trjson = tr.json()
                tr_env = get_url(trjson["environment"]).json()["name"]
                tests = []
                metrics = []
                for test_obj in _get_tests(trjson["tests"], "t"):
                    tests.append(Test(*test_obj))
                for mtrc_obj in _get_tests(trjson["metrics"], "m"):
                    metrics.append(Metric(*mtrc_obj))
                testruns.append(
                    TestRun(
                        tr_env, trjson["completed"], trjson["job_url"], tests, metrics
                    )
                )
            self.builds.append(
                {
                    "version": bldjson["version"],
                    "finished": bldjson["finished"],
                    "testruns": testruns,
                }
            )
            i += 1
