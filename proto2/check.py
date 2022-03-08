import os
from bioblend.galaxy import GalaxyInstance

galaxy_url = os.getenv('GALAXY_URL')
galaxy_api_key = os.getenv('API_KEY')
galaxy_work = os.getenv('GALAXY_WORKING_DIR')
galaxy_history_id = os.getenv('HISTORY_ID')

gi = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)

jobs = gi.jobs.get_jobs(state='running', tool_id='interactive_tool_proto2', history_id=galaxy_history_id)
#print(jobs)

for job in jobs:
  jid = job['id']
  jinfo = gi.jobs.show_job(jid, full_details=True)
  print(jinfo)

eps = gi.make_get_request(gi.base_url + '/api/entry_points?running=true').json()


print(eps[0]['target'])


