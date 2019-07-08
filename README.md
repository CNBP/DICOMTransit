[![GitHub license](https://img.shields.io/github/license/CNBP/DICOMTransit.svg)](https://github.com/CNBP/DICOMTransit/blob/master/LICENSE) [![Build Status](https://travis-ci.com/CNBP/DICOMTransit.svg?branch=master)](https://travis-ci.com/CNBP/DICOMTransit) [![GitHub issues](https://img.shields.io/github/issues/CNBP/DICOMTransit.svg)](https://github.com/CNBP/DICOMTransit/issues) [![Coverage Status](https://coveralls.io/repos/github/CNBP/DICOMTransit/badge.svg?branch=DICOMAnonimization)](https://coveralls.io/github/CNBP/DICOMTransit?branch=DICOMAnonimization) [![codebeat badge](https://codebeat.co/badges/77d7fbdb-2823-49f2-a311-2eea70d4eb28)](https://codebeat.co/projects/github-com-cnbp-dicomtransit-master) [![Scrutinizer Code Quality](https://scrutinizer-ci.com/g/CNBP/DICOMTransit/badges/quality-score.png?b=master)](https://scrutinizer-ci.com/g/CNBP/DICOMTransit/?branch=master) [![Maintainability](https://api.codeclimate.com/v1/badges/36f48abc2a8c3802914a/maintainability)](https://codeclimate.com/github/CNBP/DICOMTransit/maintainability) [![Codacy Badge](https://api.codacy.com/project/badge/Grade/03a4b7ba72c54989ad8f063693184c04)](https://www.codacy.com/app/dyt811/DICOMTransit?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=CNBP/DICOMTransit&amp;utm_campaign=Badge_Grade) 

![DICOMTranist Logo](https://github.com/CNBP/DICOMTransit/blob/master/logo.png)

An intermediate server that built around Orthanc server to include several commonly used components to serve a variety of functions to facilicate data transport and exchange from the scanner all the way to data storage services such as LORIS or offsite tertiary storage servers. 

## Planned features and other details forthcoming:
- Everything should be containerized in an latest Ubuntu OS.
- Basic Python 3.6 support.

## Incoming:
- Orthanc server for Ubuntu included

## Automated Conversion, DICOM Manipuation:
- All MINCToolkit included.
- All DICOMToolkit included. 
- Basic anonymization routine to guarntee the removal of the NAME and SUBJECT ID.
- Basic SQLite database to store research ID substitution. 
- TODO: HeuDiCom conversion of incoming DICOM files into BIDS compatible format.
- TODO: Automated BIDS validation. 

## Outgoing:
- Remote SSH upload
- Conversation/interaction (e.g LORIS) with remote system substitute and modify DICOM. E.g. obtain an ID remotely, write info into DICOM. 

## Security / Logging:
- Finite State Machine implementation: Sentry.IO remote automated bug report. 
- TODO: Unerasble, auditable trail of all actions taken.
- TODO: Unerasble, auditable record of all settings.

# Funding and Support:
* Currently, Canadian Neonatal Brain Platform, Canada

# Continuous Integration:
- TravisCI
- TODO: Appveyor
