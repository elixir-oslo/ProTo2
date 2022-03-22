import os
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


def main():
    galaxy_url = os.getenv('GALAXY_URL')
    galaxy_api_key = os.getenv('API_KEY')
    galaxy_work = os.getenv('GALAXY_WORKING_DIR')
    galaxy_history_id = os.getenv('HISTORY_ID')
    galaxy_output = os.getenv('GALAXY_OUTPUT')

    gi = GalaxyInstance(url=galaxy_url, key=galaxy_api_key)
    print(get_proto2_url(gi, galaxy_history_id, galaxy_output))


if __name__ == "__main__":
    main()

