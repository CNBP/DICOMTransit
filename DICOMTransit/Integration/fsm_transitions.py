#############################
# Transition Naming Variables:
#############################

# Exists purely to ensure IDE can help mis spellings vs strings, which IDE DO NOT CHECK
TR_ZipFiles = "TR_ZipFiles"

# Orthanc handling transitions
TR_CheckLocalDBStudyUID = "TR_CheckLocalDBStudyUID"
TR_UpdateOrthancNewDataStatus = "TR_UpdateOrthancNewDataStatus"
TR_HandlePotentialOrthancData = "TR_HandlePotentialOrthancData"
TR_DownloadNewData = "TR_DownloadNewData"

# File handling transitions
TR_UnpackNewData = "TR_UnpackNewData"
TR_ObtainDICOMMRN = "TR_ObtainDICOMMRN"
TR_UpdateNewMRNStatus = "TR_UpdateNewMRNStatus"
TR_ProcessPatient = "TR_ProcessPatient"

TR_FindInsertionStatus = "TR_FindInsertionStatus"
TR_ProcessNextSubject = "TR_ProcessNextSubject"

# Process Old Subjects transitions
TR_QueryLocalDBForDCCID = "TR_QueryLocalDBForDCCID"
TR_QueryRemoteUID = "TR_QueryRemoteUID"
TR_IncrementRemoteTimepoint = "TR_IncrementRemoteTimepoint"
TR_UpdateLocalRecords = "TR_UpdateLocalRecords"

# Process New Subjects transitions
TR_RetrieveGender = "TR_RetrieveGender"
TR_RetrieveBirthday = "TR_RetrieveBirthday"
TR_RemoteCreateSubject = "TR_RemoteCreateSubject"
TR_LocalDBCreateSubject = "TR_LocalDBCreateSubject"

# Files handling transitions.
TR_AnonymizeFiles = "TR_AnonymizeFiles"
TR_UploadZip = "TR_UploadZip"
TR_InsertSubjectData = "TR_InsertSubjectData"
TR_RecordInsertion = "TR_RecordInsertion"
TR_ResumeMonitoring = "TR_ResumeMonitoring"

# Error handling transitions
TR_reattempt = "TR_reattempt"
TR_DetectedOrthancError = "TR_DetectedOrthancError"
TR_DetectedLORISError = "TR_DetectedLORISError"
TR_DetectedFileError = "TR_DetectedFileError"
TR_DetectedLocalDBError = "TR_DetectedLocalDBError"
TR_DetectedNetworkError = "TR_DetectedNetworkError"
