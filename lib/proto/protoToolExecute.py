import sys, os

# Adjustment to add the Galaxy "lib" directory to the beginning of PYTHONPATH instead of "lib/proto", for two reasons:
# 1. "lib/proto" should not be in PYTHONPATH in order to not confuse e.g. "lib/proto/config" with "lib/config".
# 2. "lib" should be added in the case when a conda environment is activated, as Galaxy then does not add it.
# See also comment in ProtoTools.requires_galaxy_python_environment() in module "galaxy_tool_classes.py"
lib_dir = os.path.dirname(sys.path[0])
sys.path[0] = lib_dir

from proto.generictool import getController

from proto.ProtoToolRegister import initInstalledProtoTools
initInstalledProtoTools()

#print(sys.argv[1])
#sys.path = sys.path[1:]  # to remove the '/proto' directory from the Python path
toolCtrl = getController(None, sys.argv[1])
toolCtrl.execute()

outName = toolCtrl.prototype.getOutputName(toolCtrl.choices)
outFormat = toolCtrl.prototype.getOutputFormat(toolCtrl.choices)

with open('galaxy.json', 'w') as f:
    f.writelines([
        '{{"type": "dataset", "dataset_id": "{}", "name": "{}", "ext": "{}", "info": "info", "dbkey": "{}"}}'
            .format(sys.argv[2], outName, outFormat, '?')
    ])
