from setuptools import setup

version = '1.0.1'

setup(
    name = 'remote_embed',
    version = version,
    py_modules = ['remote_embed'],
    description = "A remote version of code.interact()",
    author = 'pandolia' ,
    author_email = 'pandolia@yeah.net',
    url = 'https://github.com/pandolia/remote_embed/',
    download_url = 'https://github.com/pandolia/remote_embed/archive/%s.tar.gz' % version,
    keywords = ['python debug', 'python debugger', 'remote debug', 'remote debugger',
        'code.interact', 'remote interact', 'interact'],
    classifiers = [],
)