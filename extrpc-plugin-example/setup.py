import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='neopython-extrpc-sample-plugin',
    version='0.1.0',
    packages=find_packages(),
    install_requires=['neopython-extended-rpc-server'],
    include_package_data=True,
    license='MIT License',
    description='A neo-python Extended RPC Server sample plugin.',
    entry_points={'neopython.extrpc.plugins': 'example_name = my_extrpc_plugin.ExampleCommand'},
    long_description=README,
    url='https://github.com/ixje/neopython-extended-rpc-server/',
    author='Erik van den Brink',
    author_email='erik@cityofzion.io',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
