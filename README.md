# ProTo2

Repository for testing the ProTo v2 concept. Using containers and the "Galaxy Interactive Tools" framework as a basis for running ProTo tools.

Environment setup is fetched from https://stackoverflow.com/questions/70851048/does-it-make-sense-to-use-conda-poetry.


## Creating the environment
```
conda create --name proto2 --file conda-linux-64.lock  # or other OS type as needed
conda activate proto2
poetry install --no-root
```
## Activating the environment
```
conda activate proto2_env
```

## Updating the environment
```
# Re-generate Conda lock file(s) based on environment.yml
conda-lock -k explicit --conda mamba
# Update Conda packages based on re-generated lock file
mamba update --file conda-linux-64.lock
# Update Poetry packages and re-generate poetry.lock
poetry update
```
