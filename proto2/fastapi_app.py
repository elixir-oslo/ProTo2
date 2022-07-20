import os
import tempfile

from bioblend.galaxy import GalaxyInstance
from fastapi import FastAPI
from fastapi_mako import FastAPIMako

from compat.galaxy import get_proto2_url
from compat.galaxy import Transaction
from proto.config.Config import PROTO_TOOL_SHELVE_FN
from proto.generictool import getController
from proto.ProtoToolRegister import initInstalledProtoTools

galaxy_url = os.getenv('GALAXY_URL', '')
galaxy_api_key = os.getenv('API_KEY', '')
galaxy_output = os.getenv('GALAXY_OUTPUT', tempfile.mkstemp()[1])
galaxy_work = os.getenv('GALAXY_WORKING_DIR', 'instance/files')
galaxy_history_id = os.getenv('HISTORY_ID', None)

gi = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)

app = FastAPI()
mako = FastAPIMako(app)


@app.get('/')
async def root():
    return {'message': 'Hello World'}
