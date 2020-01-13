import datetime
import time
import requests
from squadclient.squad import *

API = "api"
GROUPS = "groups"
PROJECTS = "projects"
BUILDS = "builds"
TESTRUNS = "testruns"
ENVS = "environment"
ARGS_PIECE = "?"


def urljoiner(*args):
    """
    Joins given arguments into an url. Trailing but not leading slashes are
    stripped for each argument.
    """
    return "/".join(map(lambda x: str(x).rstrip("/"), args))


def args_builder(relation_prefix=None, **kwargs):
    """
    Joins multiple args with '&' for the url args part. If lookup spans
    objects relations, use relations_prefix arg. eg. `relations_prefix='status__'`
    :param relation_prefix:
    :param kwargs:
    :return:
    """
    args = _args_composer(**kwargs)
    if relation_prefix:
        relation_prefix += "{0}"
        return "&".join(map(lambda x: relation_prefix.format(x), args)) + "&"
    else:
        return "&".join(args) + "&"


def _args_composer(**kwargs):
    """
    Constructs kv arg(s) into k=v list. Call this function via args_builder function
    :param kwargs:
    :return:
    """
    return ["=".join([k, str(v)]) for k, v in kwargs.items() if v]


def get_url(url, retries=3):
    r = requests.get(url)
    try:
        r.raise_for_status()
    except:
        if retries <= 0:
            raise
        print("Retrying {}".format(url))
        time.sleep(30)
        return get_url(url, retries=retries - 1)
    return r


def get_objects(url, only_results=False):
    r = get_url(url)
    if only_results:
        for obj in r.json()["results"]:
            yield obj
    else:
        for obj in r.json()["results"]:
            yield get_url(obj["url"])
    if r.json()["next"] is not None:
        yield from get_objects(r.json()["next"])


class Client(object):
    """
    Main class representing reporting client for SQUAD
    """

    def __init__(self, squad_url):
        self.url = squad_url
        self.group_ep = urljoiner(self.url, API, GROUPS, ARGS_PIECE)
        self.projects_ep = urljoiner(self.url, API, PROJECTS, ARGS_PIECE)
        self.builds_ep = urljoiner(self.url, API, BUILDS, ARGS_PIECE)
        self.testruns_ep = urljoiner(self.url, API, TESTRUNS, ARGS_PIECE)
        self.envs_ep = urljoiner(self.url, API, ENVS, ARGS_PIECE)

    @classmethod
    def validate_id(cls, arg):
        try:
            return int(arg)
        except ValueError:
            print("Expected group id but got slug instead!")
            raise

    @classmethod
    def validate_datetime(cls, arg):
        try:
            return datetime.datetime.strptime(arg, "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            raise ValueError(
                "created date must be YYYY-MM-DDTHH:MM:SS fromat: eg. 2018-10-07T00:00:00"
            )

    @classmethod
    def retrieve_testresults(cls):
        pass

    def retrieve_latest_builds(self, count=5, group=None, project=None, **kwargs):
        """
        Retrieves details for last N builds. By default N=5.
        Optional parameters can be provided:
         * group - name of SQUAD group
         * project - name of SQUAD project
        Data is stored in memory.
        Additional filtering parameters can be applied with kwargs.
        Valid parameters are:
         * finished
         * created_at
         * notified
         * approved
         * has_metrics
         * has_tests
        Invalid filtering parameters will be ignored
        """
        url = self.builds_ep
        if group and not project:
            url += args_builder("project__", **{"group": Client.validate_id(group)})
        elif project:
            url += args_builder(**{"project": Client.validate_id(project)})
        if kwargs:
            created_at = kwargs.pop("created_at", None)
            args = args_builder("status__", **kwargs)
            if created_at:
                args += args_builder(Client.validate_datetime(created_at))
            url += args

        counted = 0
        builds = []
        for bld in get_objects(url, True):
            if counted == count:
                break
            bld_status = get_url(bld["status"]).json()
            # TODO add project id->name translation table
            builds.append(
                Build(
                    bld["id"],
                    bld["project"].rsplit("/")[-2],
                    bld["version"],
                    bld["finished"],
                    bld_status["notified"],
                    bld_status["approved"],
                    bld_status["has_tests"],
                    bld_status["has_metrics"],
                )
            )
            bld_trs_url = self.testruns_ep + args_builder(
                **{"build": bld["id"], "completed": "true"}
            )
            # (testruns, tests, metrics) = retrieve_tests_results()
            for tr in get_objects(bld_trs_url):
                tr = tr.json()
                env = get_url(tr["environment"]).json()
                builds[-1].testruns.append(TestRun(tr['id'],
                                                   tr['job_url'],
                                                   Environment(env['id'],
                                                               env['slug'],
                                                               env['name']
                                                               )
                                                   ),

                                           )



            # for testrun in get_objects(build_obj['testruns']):
            #     #add instatiated tr to above obj
            #     for test

            # bldjson = bld.json()
            # testruns = []
            # for tr in get_objects(bldjson["testruns"]):
            #     trjson = tr.json()
            #     tr_env = get_url(trjson["environment"]).json()["name"]
            #     tests = []
            #     metrics = []
            #     for test_obj in _get_tests(trjson["tests"], "t"):
            #         tests.append(Test(*test_obj))
            #     for mtrc_obj in _get_tests(trjson["metrics"], "m"):
            #         metrics.append(Metric(*mtrc_obj))
            #     testruns.append(
            #         TestRun(
            #             tr_env, trjson["completed"], trjson["job_url"], tests, metrics
            #         )
            #     )
            # self.builds.append(
            #     {
            #         "version": bldjson["version"],
            #         "finished": bldjson["finished"],
            #         "testruns": testruns,
            #     }
            # )
            count += 1

    def retrieve_build_results(self, build):
        """
        Retrieves Test and Metric results for given build
        """
        pass

    def retrieve_test_results(self, suite, name, group=None, project=None, history=5):
        """
        Retrieves test results using Suite and Test name
        Optionally accepts following parameters:
         * group - name of SQUAD group
         * project - name of SQUAD project
        Returns list of results. By default results from last 5 builds are
        retrieved.
        """
        pass

    def retrieve_test_regressions(self, suite, name, group, project, history=1):
        """
        Calculates regressions of single test result in a project
        By default looks only 1 build into the history. If it is required
        to search further, parameter 'history' should be provided
        """
        pass

    def retrieve_test_fixes(self, suite, name, group, project, history=1):
        """
        Calculates fixes of single test result in a project
        By default looks only 1 build into the history. If it is required
        to search further, parameter 'history' should be provided
        """
        pass

    def retrieve_metric_results(self, suite, name, group=None, project=None, history=5):
        """
        Retrieves metric results using Suite and Metric name
        Optionally accepts following parameters:
         * group - name of SQUAD group
         * project - name of SQUAD project
        Returns list of metrics. By default data from last 5 builds are
        retrieved.
        """
        pass


if __name__ == "__main__":
    c = Client("http://localhost:8000/")
    kwargs = {
        "has_tests": True,
        "has_metrics": True,
        "notified": True,
        "finished": True,
    }
    c.retrieve_latest_builds(group="3", **kwargs)
