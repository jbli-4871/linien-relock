import setuptools

import linien
assert linien.__version__ != 'dev'

setuptools.setup(
    name="linien-server",
    version=linien.__version__,
    author="Jeffrey Li",
    author_email="jeffreyli@g.harvard.edu",
    description="Modified linien server",
    long_description="Have a look at the \"linien\" package for installation instructions.",
    long_description_content_type="text/x-rst",
    url="https://github.com/jbli-4871/linien-0.3.2-jeff-revision",
    packages=['linien', 'linien.server', 'linien.server.optimization'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'rpyc==4.1.5', 'myhdl==0.11', 'click==7.1.2', 'cma==3.0.3', 'plumbum==1.6.9'
    ],
    scripts=[
        'linien/server/linien_start_server',
        'linien/server/linien_stop_server',
        'linien/server/linien_install_requirements'
    ],
    package_data={
        '': ['linien.bin', 'linien_start_server', 'linien_stop_server',
             'linien_install_requirements', 'VERSION']
    }
)