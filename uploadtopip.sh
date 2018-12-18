python setup.py register -r pypi
python setup.py sdist upload -r pypi
rm -r dist
rm -r remote_embed.egg-info