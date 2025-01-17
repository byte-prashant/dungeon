from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import subprocess
import sys
class CustomInstallCommand(install):
    def run(self):
        install.run(self)
        post_install_script = os.path.join(os.path.dirname(__file__), 'post_install.py')
        subprocess.call([sys.executable, post_install_script])

setup(
    name='lightYagmi',
    version='0.1',
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'yagmi = app.cli:main',  # 'yagmi' will be the CLI command
        ],
    },
    include_package_data=True,
    description='A simple command-line tool.',
    author='Prashant verma',
    author_email='reachprashantverma@gmail.com',
    url='https://github.com/byte-prashant/dungeon',
    cmdclass={
        'install': CustomInstallCommand,
    }
)
