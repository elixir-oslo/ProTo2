import json
import os, shelve, tempfile
from flask import Flask, render_template, request, redirect, url_for, send_file
from flask_mako import MakoTemplates, render_template as render_mako
from bioblend.galaxy import GalaxyInstance

from compat.galaxy import Transaction, get_proto2_url
from proto.config.Config import PROTO_TOOL_SHELVE_FN
from proto.generictool import getController
from proto.ProtoToolRegister import initInstalledProtoTools


def create_app(test_config=None):

    galaxy_url = os.getenv('GALAXY_URL', 'http://localhost.norgene.no:8080')
    galaxy_api_key = os.getenv('API_KEY', '467bf4df60d0985fac4c9d63a7bc1aa3')
    galaxy_output = os.getenv('GALAXY_OUTPUT', tempfile.mkstemp()[1])
    galaxy_work = os.getenv('GALAXY_WORKING_DIR', 'instance/files')
    galaxy_history_id = os.getenv('HISTORY_ID', None)

    gi = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)

    #my_url = get_proto2_url(gi, galaxy_history_id, galaxy_output)
    #static_url_path = os.path.join(my_url, 'static')
    #print(static_url_path)

    app = Flask(__name__, instance_relative_config=True)

    mako = MakoTemplates(app)
    #try:
    #    app.config.from_envvar('APP_CONFIG')
    #except RuntimeError:
    #    app.config.from_pyfile('config/dev.py')


    meta = {
        'title': 'ProTo2 test app'
    }

    tool_list = initInstalledProtoTools()

    @app.route('/', methods=['GET','POST'])
    def index():
        trans = Transaction(gi, app, request)

        if 'tool_id' in trans.request.params:
            tool_controller = getController(trans)
            return render_mako('generictool.mako', control=tool_controller, h=trans)
        else:
            data = {'tools': tool_list}
            return render_template('index.html', meta=meta, data=data)

    @app.route('/tool_runner', methods=['POST'])
    def tool_runner():
        trans = Transaction(gi, app, request)

        if 'tool_id' in request.form:
            tool_controller = getController(trans)
            #tool_controller.jobFile = tempfile.mkstemp(dir=galaxy_work)[1]
            #tool_controller.execute()

            #with open(tool_controller.jobFile) as f:
            #    data = f.read()
            history_id = galaxy_history_id
            if history_id is None:
                hist = gi.histories.get_most_recently_used_history()
                history_id = hist['id']

                #gi.tools.paste_content(data, hist['id'])
                #gi.tools.upload_file(tool_controller.jobFile, hist['id'])
                #os.makedirs(galaxy_work + '/files', exist_ok=True)
                #shutil.copy(tool_controller.jobFile, galaxy_work + '/files/test.txt')

            param_dict = {
                "tool_id": tool_controller.toolId,
                "tool_name": tool_controller.toolId
                #'URL': url_for('result', job=os.path.basename(tool_controller.jobFile), _external=True)
                }
            param_dict.update(trans.request.params)
            for key in ('cached_options', 'cached_params', 'cached_extra', 'old_values', 'mako', 'URL', 'start'):
                param_dict.pop(key)

            try:
                #data = gi.tools.run_tool(history_id,'Test1Tool',params)
                data = gi.tools.run_tool(history_id, param_dict['tool_id'], {
                    "param_dict": json.dumps(param_dict),
                    "interactivetool_id": "xxx",
                    "interactivetool_name": "xxx",
                    "proto_tool_id": tool_controller.toolId
                })
            except Exception as e:
                return str(e)
            #return redirect(galaxy_url)
            return data

    @app.route('/rerun/<dataset_id>')
    def rerun(dataset_id):
        #if id in request.args:
        #    dataset_id = request.args['id']
        dataset = gi.datasets.show_dataset(dataset_id)
        job_id = dataset['creating_job']
        job = gi.jobs.show_job(job_id)
        param_dict = job['params']['param_dict']
        params = json.loads(json.loads(param_dict))
        #return params
        return redirect('./..' + url_for('index', **params))

    @app.route('/log')
    def log():
        logfile = galaxy_output
        #with open(logfile) as f:
        #    data = f.read()
        return send_file(logfile, 'text/plain', cache_timeout=10)

    # @app.route('/result/<path:job>')
    # def result(job):
    #     jobfile = os.path.join(galaxy_work, job)
    #     #with open(jobfile) as f:
    #     #    data = f.read()
    #     #os.unlink(jobfile)
    #     return send_file(jobfile)
    #
    # @app.route('/shutdown')
    # def shutdown():
    #     os.system(app.instance_path + '/shutdown.sh &')
    #     return 'shutting down'

    return app
