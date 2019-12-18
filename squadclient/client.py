SQUAD_API_PREFIX = "api"
SQUAD_GROUPS_ENDPOINT = "%s/groups" % SQUAD_API_PREFIX
SQUAD_PROJECTS_ENDPOINT = "%s/projects" % SQUAD_API_PREFIX
SQUAD_BUILDS_ENDPOINT = "%s/builds" % SQUAD_API_PREFIX
SQUAD_ENVIRONMENTS_ENDPOINT = "%s/environments" % SQUAD_API_PREFIX


class Client(object):
    """
    Main class representing reporting client for SQUAD
    """

    def __init__(self, squad_url):
        self.url = squad_url


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
        pass

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
