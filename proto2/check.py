import os
from bioblend.galaxy import GalaxyInstance

galaxy_url = os.getenv('GALAXY_URL')
galaxy_api_key = os.getenv('API_KEY')
galaxy_work = os.getenv('GALAXY_WORKING_DIR')
galaxy_history_id = os.getenv('HISTORY_ID')

gi = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)

eps = gi.make_get_request(gi.base_url + '/api/entrypoints', payload={'key': galaxy_api_key})

print(eps)
