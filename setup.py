from setuptools import setup, find_packages, version

with open('README.md') as readme_file:
    readme = readme_file.read()

setup(
    name='fu',
    version='1.0.0',
    description='A fancy tool for managing local files',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Giovanni Aguirre',
    author_email='giovanni.fi05@gmail.com',
    
    packages=find_packages(),
    scripts=['fu/futils.py']
)