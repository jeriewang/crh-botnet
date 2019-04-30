from setuptools import setup

setup(
        name='crh-botnet',
        version='0.0.4',
        packages=['crh_botnet','crh_botnet.server'],
        url='https://docs.jerrywang.website/crh-botnet/',
        license='MIT',
        author='Jerry Wang',
        author_email='yrrejkk@gmail.com',
        description='A Robot Networking Library',
        python_requires='>=3.6',
        install_requires=[
            'aiohttp',
            'requests',
            'flask'
        ],
        long_description=open('README.md').read()
)
