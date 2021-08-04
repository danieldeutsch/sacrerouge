import setuptools


# version.py defines the VERSION variable.
# We use exec here so we don't import sacrerouge whilst setting up.
VERSION = {}
with open('sacrerouge/version.py', 'r') as version_file:
    exec(version_file.read(), VERSION)


# Load requirements so we can keep them in a single file
requirements = open('requirements.txt', 'r').read().splitlines()


setuptools.setup(
    name='sacrerouge',
    version=VERSION['VERSION'],
    author='Daniel Deutsch',
    description='An open-source library for summarization evaluation metrics',
    url='https://github.com/danieldeutsch/sacrerouge',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': ['sacrerouge=sacrerouge.__main__:main']},
    python_requires='>=3.6',
    install_requires=requirements,
)