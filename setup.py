import os
from setuptools import find_packages, setup
import aadiscordbot
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='allianceauth-discordbot',
    version=aadiscordbot.__version__,
    packages=find_packages(),
    include_package_data=True,
    license='GNU General Public License v3 (GPLv3)',
    description='Alliance Auth Discord Bot',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/pvyParts/allianceauth-discordbot',
    author='ak',
    author_email='ak@ak.auth',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    python_requires='>=3.8',
    install_requires=[
        "allianceauth>=2.8.0,<3.0.0",
        "py-cord @ git+https://github.com/Pycord-Development/pycord.git#egg=py-cord",
        "pendulum>=2.1.2,<3.0.0",
        "aioredis<2.0.0",
        "aiohttp>=3.8.1,<4.0.0"
    ],

)
