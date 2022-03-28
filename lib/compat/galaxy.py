from collections import namedtuple
from werkzeug.datastructures import MultiDict
from flask import url_for
from compat import patch_dict


def get_proto2_url(gi, galaxy_history_id, galaxy_output):
    jobs = gi.jobs.get_jobs(state='running', tool_id='interactive_tool_proto2', history_id=galaxy_history_id)
    #print(jobs)
    for job in jobs:
        job_id = job['id']
        job_info = gi.jobs.show_job(job_id, full_details=True)
        job_cmd = str(job_info['command_line'])
        if job_cmd.find(galaxy_output) != -1:
            break

    eps = gi.make_get_request(gi.base_url + '/api/entry_points?job_id=' + job_id).json()

    target = str(eps[0]['target']).rstrip('/').replace('//', '/')
    return target


class SecurityHelper:
    pass


class GalaxyHistory:
    def __init__(self, gi):
        self.history = gi.histories.get_most_recently_used_history()
        hds = gi.histories.show_history(self.history['id'], contents=True, deleted=False, visible=True)
        self.active_datasets = []
        if len(hds) > 0:
            self.dataset_class = namedtuple('GalaxyHistoryDataset', ['dbkey'] + list(hds[0].keys()))
            for ds in hds:
                self.active_datasets += [self.dataset_class('xxx', *ds.values())]


class Transaction:
    def __init__(self, app, gi, request):
        self.app = app
        self.galaxy = gi
        self.request = request
        params = MultiDict(request.args)
        params.update(request.form)
        if 'proto_tool_id' in params:
            params['tool_id'] = params['proto_tool_id']
        #print(params)
        self.request.params = patch_dict(params)
        self.request.GET = patch_dict(request.args)
        self.request.POST = patch_dict(request.form)

    def css(self, fname):
        html = '<link rel="stylesheet" type="text/css" href="./%s/style/%s.css">' % (self.app.static_url_path, fname)
        return html

    def js(self, fname):
        html = '<script type="text/javascript" src="./%s/%s.js"></script>' % (self.app.static_url_path, fname)
        return html

    def url_for(self, ref):
        ref = ref.lstrip('/')
        url = '.' + url_for(ref)
        return url

    def get_user(self):
        user_dict = self.galaxy.users.get_current_user()
        user = namedtuple('GalaxyUser', user_dict.keys())(*user_dict.values())
        return user

    def get_genome_build_names(self):
        genomes = self.galaxy.genomes.get_genomes()
        #print(genomes)
        return genomes

    def get_history(self):
        return GalaxyHistory(self.galaxy)
