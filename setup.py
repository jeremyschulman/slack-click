# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['slack_click']

package_data = \
{'': ['*']}

install_requires = \
['click<8',
 'first>=2.0.2,<3.0.0',
 'pyee>=8.1.0,<9.0.0',
 'slack-bolt>=1.6.0,<2.0.0']

setup_kwargs = {
    'name': 'slack-click',
    'version': '1.0.0',
    'description': 'Click support for Slack-Bolt applications',
    'long_description': None,
    'author': 'Jeremy Schulman',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
