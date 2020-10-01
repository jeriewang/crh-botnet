from setuptools import setup
from crh_botnet import __version__, __author__, __license__

setup(
        name='crh-botnet',
        version=__version__,
        packages=['crh_botnet', 'crh_botnet.server'],
        url='https://docs.jerie.wang/crh-botnet/',
        license=__license__,
        author=__author__,
        author_email='mail@jerie.wang',
        description='A Robot Networking Library',
        python_requires='>=3.6',
        install_requires=[
            'aiohttp',
            'requests',
            'flask',
            'gpiozero'
        ],
        long_description=open('README.md').read()
)
