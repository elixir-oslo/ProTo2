import codecs
import json, os, requests
import sys
from collections import namedtuple

from Crypto.Cipher import Blowfish
from werkzeug.datastructures import MultiDict
from flask import url_for, current_app
from compat import patch_dict
from bioblend.galaxy import GalaxyInstance

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
    def __init__(self, gi):
        self.history = gi.histories.get_most_recently_used_history()
        hds = gi.histories.show_history(self.history['id'], contents=True, deleted=False, visible=True, details='all')
        #hds = gi.datasets.get_datasets(history_id=self.history['id'], deleted=False, visible=True) # no details
        self.active_datasets = [GalaxyHistoryDataset(ds) for ds in hds]


class GalaxyConnection:
    galaxy = None

    def __init__(self, galaxy_instance=None):
        if self.galaxy is None:
            if galaxy_instance is None:
                galaxy_url = os.getenv('GALAXY_URL')
                galaxy_api_key = os.getenv('API_KEY')
                self.galaxy = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)
            else:
                self.galaxy = galaxy_instance

    def get_user(self):
        user_dict = self.galaxy.users.get_current_user()
        user = namedtuple('GalaxyUser', user_dict.keys())(*user_dict.values())
        return user

    def get_genome_build_names(self):
        genomes = self.galaxy.genomes.get_genomes()
        #print(genomes)
        return genomes

    def get_history(self):
        try:
            return GalaxyHistory(self.galaxy)
        except Exception as e:
            raise e
            return None

    def get_dataset_path(self, dataset_id):
        #ds = self.galaxy.datasets.show_dataset(dataset_id)
        #url = self.galaxy.base_url + ds['download_url']
        #data = self.galaxy.make_get_request(url)
        file_name = os.getcwd() + '/dataset_' + dataset_id + '.dat'
        #data_file = open(file_name, 'wb')
        #data_file.write(data.content)
        #data_file.close()
        self.galaxy.datasets.download_dataset(dataset_id, file_name, use_default_filename=False)
        #data = requests.get(url)
        return file_name


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
        html = '<link rel="stylesheet" type="text/css" href="./%s/style/%s.css">' % (self.app.static_url_path, fname)
        return html

    def js(self, fname):
        html = '<script type="text/javascript" src="./%s/%s.js"></script>' % (self.app.static_url_path, fname)
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
        s = (b"!" * (8 - len(session_key) % 8)) + session_key
        # Encrypt
        return codecs.encode(self.id_cipher.encrypt(s), 'hex')