class SquadObject(object):
    pass


class Group(SquadObject):
    pass


class Project(SquadObject):
    pass


class Environment(SquadObject):
    def __init__(self, env_id, slug, name):
        self.id = env_id
        self.slug = slug
        self.name = name


class Build(SquadObject):
    def __init__(self, build_id, project_id, version, finished, notified,
                 approved, has_tests, has_metrics):
        self.id = build_id
        self.project = project_id
        self.version = version
        self.finished = finished
        self.notified = notified
        self.approved = approved
        self.has_tests = has_tests
        self.has_metrics = has_metrics
        self.testruns = []


class TestRun(SquadObject):
    def __init__(self, tr_id, job_url, env_id):
        self.id = tr_id
        self.job_url = job_url
        self.env = env_id
        self.test_results = {'tests': [], 'metrics': []}


class TestSuite(SquadObject):
    def __init__(self, slug, project):
        self.slug = slug
        self.project = project


class Test(SquadObject):
    def __init__(self, name, suite, status, has_ki):
        self.name = name
        self.suite = suite
        self.status = status
        self.has_ki = has_ki


class Metric(SquadObject):
    def __init__(self, name, suite, result, is_ol):
        self.name = name
        self.suite = suite
        self.result = result
        self.is_ol = is_ol
