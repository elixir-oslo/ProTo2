import os, shelve, types, tempfile, signal, shutil, requests
from flask import Flask, render_template, request, Response, session, redirect, url_for, escape, send_file
from flask_mako import MakoTemplates, render_template as render_mako
from bioblend.galaxy import GalaxyInstance

from proto2.compat.galaxy import Transaction
from proto.config.Config import PROTO_TOOL_SHELVE_FN, PROTO_TOOL_DIR
from proto.generictool import getController, GenericToolController
from proto.ProtoToolRegister import getProtoToolList, getInstalledProtoTools


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    mako = MakoTemplates(app)
    #try:
    #    app.config.from_envvar('APP_CONFIG')
    #except RuntimeError:
    #    app.config.from_pyfile('config/dev.py')

    galaxy_url = os.getenv('GALAXY_URL', 'http://localhost.norgene.no:8080')
    galaxy_api_key = os.getenv('API_KEY', '467bf4df60d0985fac4c9d63a7bc1aa3')
    galaxy_output = os.getenv('GALAXY_OUTPUT', tempfile.mkstemp()[1])
    galaxy_work = os.getenv('GALAXY_WORKING_DIR', os.path.join(app.instance_path, 'files'))
    galaxy_history_id = os.getenv('HISTORY_ID', None)

    gi = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)

    meta = {
        'title': 'ProTo2 test app'
    }

    #tool_list = getProtoToolList(PROTO_TOOL_DIR, False)
    #tool_list = getInstalledProtoTools()
    #print(PROTO_TOOL_DIR, repr(tool_list))

    tool_register = shelve.open(PROTO_TOOL_SHELVE_FN, 'n')
    tool_register['Test1Tool'] = ('proto.tools.mojo.Test1Tool', 'Test1Tool', None)
    tool_register['proto_proto_gui_test_tool1'] = ('proto.tools.guitest.ProtoGuiTestTool1', 'ProtoGuiTestTool1', None)
    tool_register['proto_proto_gui_test_tool2'] = ('proto.tools.guitest.ProtoGuiTestTool2', 'ProtoGuiTestTool2', None)
    tool_register['proto_proto_gui_test_tool3'] = ('proto.tools.guitest.ProtoGuiTestTool3', 'ProtoGuiTestTool3', None)
    tool_register['proto_proto_gui_test_tool4'] = ('proto.tools.guitest.ProtoGuiTestTool4', 'ProtoGuiTestTool4', None)
    tool_register['proto_proto_gui_test_tool5'] = ('proto.tools.guitest.ProtoGuiTestTool5', 'ProtoGuiTestTool5', None)
    tool_register['proto_proto_gui_test_tool6'] = ('proto.tools.guitest.ProtoGuiTestTool6', 'ProtoGuiTestTool6', None)
    tool_register['proto_proto_gui_test_tool7'] = ('proto.tools.guitest.ProtoGuiTestTool7', 'ProtoGuiTestTool7', None)
    tool_list = dict(tool_register)
    tool_register.close()

    @app.route('/', methods=['GET','POST'])
    def index():

        trans = Transaction(app, gi, request)

        if 'tool_id' in trans.request.params:
            tool_controller = getController(trans)
            return render_mako('generictool.mako', control=tool_controller, h=trans)
        else:
            data = {'tools': tool_list}
            return render_template('index.html', meta=meta, data=data)

    @app.route('/tool_runner', methods=['POST'])
    def tool_runner():
        trans = Transaction(app, gi, request)

        if 'tool_id' in request.form:
            tool_controller = getController(job=trans.request.params)
            tool_controller.jobFile = tempfile.mkstemp(dir=galaxy_work)[1]
            tool_controller.execute()

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

            params={
                'tool_id': tool_controller.toolId,
                'URL': url_for('result', job=os.path.basename(tool_controller.jobFile), _external=True)
                }
            try:
                data = gi.tools.run_tool(history_id,'Test1Tool',params)
            except Exception as e:
                return str(e)
            return redirect(galaxy_url)

    @app.route('/result/<path:job>')
    def result(job):
        jobfile = os.path.join(galaxy_work, job)
        #with open(jobfile) as f:
        #    data = f.read()
        #os.unlink(jobfile)
        return send_file(jobfile)

    @app.route('/shutdown')
    def shutdown():
        os.system(app.instance_path + '/shutdown.sh &')
        return 'shutting down'

    return app
