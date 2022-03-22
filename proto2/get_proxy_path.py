import os
from bioblend.galaxy import GalaxyInstance
from compat.galaxy import get_proto2_url


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

