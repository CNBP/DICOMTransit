# To install, run at command prompt of the Source directory:

# python setup.py intall

from setuptools import setup,find_packages

setup(name='DICOMTransit',
	version='0.21',
	description='Intermediate server to transfer and process DICOM files',
	url='https://github.com/CNBP/DICOMTransit',
	author='Canadian Neonatal Brain Platform',
	author_email='it@cnbp.ca',
	license='MIT',
	packages=find_packages(),
	install_requires=[
        'python-dotenv'
        'python-coveralls'
        'coverage'
        'pydicom'
        'python-dateutil'
        'pytest-cov'
        'heudiconv[all]'
        'tqdm'
        'paramiko'
	],
	zip_safe=False)
