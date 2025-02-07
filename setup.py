from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import subprocess
import sys



# Read dependencies from requirements.txt
def parse_requirements(filename):

    with open(filename, 'r') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

class CustomInstallCommand(install):

    def install_requirements(self):

        # Install dependencies from requirements.txt
        try:
            requirements_file = "requirements.txt"
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", requirements_file])
            print(f"All requirements from {requirements_file} have been installed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while installing dependencies: {e}")


    def run(self):
        self.install_requirements()
        install.run(self)
        post_install_script = os.path.join(os.path.dirname(__file__), 'post_install.py')
        subprocess.call([sys.executable, post_install_script])




setup(
    name='lightYagmi',
    version='0.1',
    packages=find_packages(),
    install_requires=parse_requirements("requirements.txt"),
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
