import codecs
from collections import namedtuple
import json
import os
import sys

from bioblend.galaxy import GalaxyInstance
from Crypto.Cipher import Blowfish
from flask import current_app
from flask import url_for
import requests
from werkzeug.datastructures import MultiDict

from compat import patch_dict


def get_proto2_url(gi, galaxy_history_id, galaxy_output):
    jobs = gi.jobs.get_jobs(
        state='running', tool_id='interactive_tool_proto2', history_id=galaxy_history_id)
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


class GalaxyHistoryDataset:
    def __init__(self, dataset):
        self.name = dataset['name']
        self.hid = dataset['hid']
        self.visible = dataset['visible']
        self.state = dataset['state']
        self.extension = dataset['file_ext']
        self.dataset_id = dataset['dataset_id']
        self.datatype = dataset['data_type']
        self.dbkey = dataset['genome_build']
        self.url = dataset['download_url']


class GalaxyHistory:
    _cache = {}

    def __init__(self, gi):
        history = gi.histories.get_most_recently_used_history()
        hid = history['id']
        if hid not in self._cache or self._cache[hid]['update_time'] != history['update_time']:
            self._cache[hid] = history
            hds = gi.histories.show_history(
                hid, contents=True, deleted=False, visible=True, details='all')
            #hds = gi.datasets.get_datasets(history_id=self.history['id'], deleted=False, visible=True) # no details
            if 'active_datasets' in self._cache[hid]:
                self._cache[hid]['active_datasets'] = [GalaxyHistoryDataset(ds) for ds in hds]
        self.active_datasets = self._cache[hid]['active_datasets']


class GalaxyConnection:
    galaxy = None
    genomes = None

    def __init__(self, galaxy_instance=None):
        if self.galaxy is None:
            if galaxy_instance is None:
                galaxy_url = os.getenv('GALAXY_URL')
                galaxy_api_key = os.getenv('API_KEY')

                self.galaxy = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)
            else:
                self.galaxy = galaxy_instance
            self.history_id = os.getenv('HISTORY_ID')

    def get_user(self):
        user_dict = self.galaxy.users.get_current_user()
        user = namedtuple('GalaxyUser', user_dict.keys())(*user_dict.values())
        return user

    def get_genome_build_names(self):
        if self.genomes is None:
            self.genomes = self.galaxy.genomes.get_genomes()
        #print(genomes)
        return self.genomes

    def get_history(self):
        try:
            return GalaxyHistory(self.galaxy)
        except Exception as e:
            raise e
            return None

    def get_dataset_path(self, dataset_id):
        ds = self.galaxy.datasets.show_dataset(dataset_id)
        file_name = os.path.join(os.getcwd(), 'dataset_' + dataset_id + '.dat')
        if not os.path.exists(file_name):
            self.galaxy.datasets.download_dataset(dataset_id, file_name, use_default_filename=False)
        return file_name

    def get_new_dataset_path(self):
        return os.path.join(os.getenv('GALAXY_WORKING_DIR'), 'dataset_files')

    def get_extra_files_path(self):
        return os.getenv('GALAXY_OUTPUT_FILES_PATH')


class Transaction(GalaxyConnection):
    def __init__(self, gi, app=None, request=None):
        super().__init__(gi)
        self.app = app
        #self.galaxy = gi if gi is not None else getGalaxyInstance()
        self.request = request
        if request is not None:
            params = MultiDict(request.args)
            params.update(request.form)
            if 'proto_tool_id' in params:
                params['tool_id'] = params['proto_tool_id']
            if 'param_dict' in params:
                try:
                    params.update(json.loads(params['param_dict']))
                except json.JSONDecodeError as e:
                    print(e)
        #print(params)
            self.request.params = patch_dict(params)
            self.request.GET = patch_dict(request.args)
            self.request.POST = patch_dict(request.form)

    def css(self, fname):
        html = '<link rel="stylesheet" type="text/css" href="./%s/style/%s.css">' % (
            self.app.static_url_path, fname)
        return html

    def js(self, fname):
        html = '<script type="text/javascript" src="./%s/%s.js"></script>' % (
            self.app.static_url_path, fname)
        return html

    def url_for(self, ref):
        ref = ref.lstrip('/')
        url = '.' + url_for(ref)
        return url


class SecurityHelper:
    def __init__(self, id_secret):
        self.id_secret = id_secret.encode()
        self.id_cipher = Blowfish.new(self.id_secret, mode=Blowfish.MODE_ECB)

    def encode_guid(self, session_key):
        # Session keys are strings
        # Pad to a multiple of 8 with leading "!"
        if isinstance(session_key, str):
            session_key = session_key.encode()
        s = (b'!' * (8 - len(session_key) % 8)) + session_key
        # Encrypt
        return codecs.encode(self.id_cipher.encrypt(s), 'hex')
