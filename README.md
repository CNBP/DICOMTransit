[![Build Status](https://travis-ci.com/CNBP/DICOMTransit.svg?branch=InitialMerge)](https://travis-ci.com/CNBP/DICOMTransit) [![GitHub issues](https://img.shields.io/github/issues/CNBP/DICOMTransit.svg)](https://github.com/CNBP/DICOMTransit/issues) [![GitHub license](https://img.shields.io/github/license/CNBP/DICOMTransit.svg)](https://github.com/CNBP/DICOMTransit/blob/master/LICENSE)

# DICOMTransit
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
- HeuDiCom conversion of incoming DICOM files into BIDS compatible format.
- Automated BIDS validation. 

## Outgoing:
- Remote SSH upload
- Conversation/interaction (e.g LORIS) with remote system substitute and modify DICOM. E.g. obtain an ID remotely, write info into DICOM. 

## Security:
- Unerasble, auditable trail of all actions taken.
- Unerasble, auditable record of all settings.

# Funding and Support:
* Maybe Canadian Neonatal Brain Platform, Canada? TBD
* Maybe Cyclotron Research Centre,  University of Liège, Belgium? TBD
