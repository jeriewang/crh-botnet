from setuptools import setup

setup(
        name='crh-botnet',
        version='0.0.1',
        packages=['crh_botnet','crh_botnet.server'],
        url='https://github.com/pkqxdd/crh-botnet',
        license='MIT',
        author='Jerry Wang',
        author_email='yrrejkk@gmail.com',
        description='A Robot Networking Library',
        install_requires=[
            'aiohttp',
            'requests',
            'flask'
        ]
)
