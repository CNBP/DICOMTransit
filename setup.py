#!/usr/bin/env python




# To install, run at command prompt of the Source directory:

# python setup.py intall

from setuptools import setup, find_packages

setup(name='DICOMTransit',
	version='0.4',
	description='DICOMTransit server as an intermediate step to facilitate transfer, anonymization and upload of data from Orthanc to LORIS instances.',
	url="https://cnbp.ca",
	author='Canadian Neonatal Brain Platform',
	author_email='it@cnbp.ca',
	keywords="mri neonatal CNBP brain imaging",
	project_urls={
		"Source Code": "https://github.com/CNBP/DICOMTransit/"
	},
	python_requires='3.6',
	license='MIT',
	packages=find_packages(),
	install_requires=[
		'python-dotenv'				
		'pydicom'
		'python-dateutil'
		'pytest-cov'
		'tqdm'
		'paramiko'		
		'gevent'
		'pyodbc'
		'requests'
		'config'
		'werkzeug'
		'flask'
		'transitions'
	],
	zip_safe=False)


