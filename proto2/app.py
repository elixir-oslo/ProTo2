import os, shelve, types
from collections import namedtuple
from flask import Flask, render_template, request, Response, session, redirect, url_for, escape
from werkzeug.datastructures import MultiDict
from flask_mako import MakoTemplates, render_template as render_mako
from bioblend.galaxy import GalaxyInstance

from compat import patch_dict
from proto.config.Config import PROTO_TOOL_SHELVE_FN
from proto.generictool import getController, GenericToolController

app = Flask(__name__)
mako = MakoTemplates(app)
#try:
#    app.config.from_envvar('APP_CONFIG')
#except RuntimeError:
#    app.config.from_pyfile('config/dev.py')

galaxy_url = os.getenv('GALAXY_URL', 'http://localhost.norgene.no:8080')
galaxy_api_key = os.getenv('API_KEY', '467bf4df60d0985fac4c9d63a7bc1aa3')

gi = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)

meta = {
    'title': 'ProTo2 test app'
}

tool_register = shelve.open(PROTO_TOOL_SHELVE_FN, 'n')
tool_register['Test1Tool'] = ('proto.tools.mojo.Test1Tool', 'Test1Tool', None)
tool_register['proto_proto_gui_test_tool1'] = ('proto.tools.guitest.ProtoGuiTestTool1', 'ProtoGuiTestTool1', None)
tools = dict(tool_register)
tool_register.close();


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
    def __init__(self, request):
        self.request = request
        params = MultiDict(request.args)
        params.update(request.form)
        #print(params)
        self.request.params = patch_dict(params)
        self.request.GET = patch_dict(request.args)
        self.request.POST = patch_dict(request.form)

    def css(self, fname):
        html = '<link rel="stylesheet" type="text/css" href="%s/style/%s.css">' % (app.static_url_path, fname)
        return html

    def js(self, fname):
        html = '<script type="text/javascript" src="%s/%s.js"></script>' % (app.static_url_path, fname)
        return html

    def url_for(self, ref):
        ref = ref.lstrip('/')
        url = url_for(ref)
        return url

    def get_user(self):
        user_dict = gi.users.get_current_user()
        user = namedtuple('GalaxyUser', user_dict.keys())(*user_dict.values())
        return user

    def get_genome_build_names(self):
        genomes = gi.genomes.get_genomes()
        #print(genomes)
        return genomes

    def get_history(self):
        return GalaxyHistory(gi)



@app.route('/', methods=['GET','POST'])
def index():

    trans = Transaction(request)

    if 'tool_id' in trans.request.params:
        tool_controller = getController(trans)
        return render_mako('generictool.mako', control=tool_controller, h=trans)
    else:
        data = {'tools': tools}
        return render_template('index.html', meta=meta, data=data)


@app.route('/tool_runner', methods=['POST'])
def tool_runner():
    pass