import setuptools

setuptools.setup(
    name='sacrerouge',
    version='0.0.3',
    author='Daniel Deutsch',
    description='An open-source library for summarization evaluation metrics',
    url='https://github.com/danieldeutsch/sacrerouge',
    packages=setuptools.find_packages(),
    entry_points={'console_scripts': ['sacrerouge=sacrerouge.__main__:main']},
    python_requires='>=3.6',
    install_requires=[
        'googledrivedownloader',
        'jsons',
        'lxml',
        'nltk',
        'numpy',
        'overrides',
        'pytest',
        'requests',
        'scipy'
    ]
)
