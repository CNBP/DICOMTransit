#This script will ask for USER name input and then automatically generate the files by copying from template folder.
#By Yang Ding
#On 2017-11-07_T145725_EST


$startTime=(Get-Date);

$ScriptIntro = @"


   ____   _   _   ____    ____      ____    ___    ____    ___    __  __                                  
  / ___| | \ | | | __ )  |  _ \    |  _ \  |_ _|  / ___|  / _ \  |  \/  |                                 
 | |     |  \| | |  _ \  | |_) |   | | | |  | |  | |     | | | | | |\/| |                                 
 | |___  | |\  | | |_) | |  __/    | |_| |  | |  | |___  | |_| | | |  | |                                 
  \____| |_| \_| |____/  |_|       |____/  |___|  \____|  \___/  |_|  |_|                                 
                                                                                                          
  _____                                 __                   ____                    _                    
 |_   _|  _ __    __ _   _ __    ___   / _|   ___   _ __    / ___|   _   _   _ __   | |_    __ _  __  __  
   | |   | '__|  / _` | | '_ \  / __| | |_   / _ \ | '__|   \___ \  | | | | | '_ \  | __|  / _` | \ \/ /  
   | |   | |    | (_| | | | | | \__ \ |  _| |  __/ | |       ___) | | |_| | | | | | | |_  | (_| |  >  <   
   |_|   |_|     \__,_| |_| |_| |___/ |_|    \___| |_|      |____/   \__, | |_| |_|  \__|  \__,_| /_/\_\  
                                                                     |___/                                
   ____                                         _                                                         
  / ___|   ___    _ __   __   __   ___   _ __  | |_    ___   _ __                                         
 | |      / _ \  | '_ \  \ \ / /  / _ \ | '__| | __|  / _ \ | '__|                                        
 | |___  | (_) | | | | |  \ V /  |  __/ | |    | |_  |  __/ | |                                           
  \____|  \___/  |_| |_|   \_/    \___| |_|     \__|  \___| |_|                                           
                                                                                                          


"@

Write-Host $ScriptIntro

#=============================
#Configurations:
$DCMTKFolder = "C:\DICOMTools\DCMTK\bin\"
$Verbose = $FALSE

$DICOMFolder = "C:\Users\dyt81\Desktop\Artefact\DICOMOBJ"

$DCMDJPEG_Executable = "dcmdjpeg.exe"
$DCMDUMP_Executable = "dcmdump.exe"
$DCMDUPM_Param1 = '+P'
$DCMDUPM_Param2 = 'TransferSyntaxUID'

#=============================

#Record Parent Folder: 
$ParentFolder = Split-Path -Parent $DICOMFolder
cd($ParentFolder)
$OldFolderName = Split-Path -Path $DICOMFolder -Leaf -Resolve
$newFolderName = 'TSF-' + $OldFolderName


Write-Host "Copying File (might take a while)"
copy -Recurse $OldFolderName $newFolderName
Write-Host "Done copying file!"
Write-host ""
Write-Host "Started the processing. This might take 20 to 30 mins per 10,000 DICOM files."
Write-Host "Conversion Speed is about:"
Write-Host "10s per 100 files when verbose OFF OR"
Write-Host "12s per 100 files when verbose ON"
Write-Host "Turn on Verbose=True if you need more update."




#Get a list all files in the folder.
cd($newFolderName)
$SourceDCMFiles = Get-ChildItem -Recurse -File | Select-Object -ExpandProperty Fullname 

#Track the conversion total.
$FileCount = 0;

#Form commands:

#Endian Check Command:
$Cmd1 = $DCMTKFolder + $DCMDUMP_Executable
$Cmd2 = $DCMTKFolder + $DCMDJPEG_Executable

#Validate if they are truly DICOM files, for now, assume they all ARE!

#Copy all PDFs from the source folder.
foreach ($TargetFile in $SourceDCMFiles){

        if($Verbose){Write-Host -NoNewline "Currently processing:"}
        if($Verbose){Write-Host $TargetFile}

        $Cmd1_prm = $DCMDUPM_Param1, $DCMDUPM_Param2, $TargetFile
        $TransferSyntaxStatus = & $Cmd1 $Cmd1_prm

        if($Verbose){Write-Host -NoNewline "TransferSyntax detected as:"}
        if($Verbose){Write-Host $TransferSyntaxStatus}

        #Check transfer Syntax
        if ($TransferSyntaxStatus.Contains('JPEGLossless')){

            #If not little ENDIAN, convert.

            #Make new name for these files.
            #$OldFileName =  Split-Path -Path $TargetFile -Leaf -Resolve
            #$OldFilePath =  Split-Path -Path $TargetFile
            #$FixedFileName = 'TSF-' + $OldFileName
            #$NewFileNamePath = $OldFilePath + '\' + $FixedFileName


            if($Verbose){Write-Host -NoNewline "Existing (copied) files will be updated at: "}
            if($Verbose){Write-Host $TargetFile}

            #Call command to convert.
            & $Cmd2 $TargetFile $TargetFile

            $FileCount = $FileCount + 1


        }ElseIf($TransferSyntaxStatus.Contains('LittleEndianExplicit')){
            if($Verbose){write-host "LEE format detected. No JPEG conversion required. Moving along."}

        }Else {
            write-Error "Yo. The TransferSyntax neither contain JPEGLossLess OR LittleEndianExplicit"
            write-Error "Where the hell did you get these weirdos?"
            Write-Error "Not working"
            #return
        }

        #Space between files. 
        if($Verbose){Write-Host ""}
}

$End = @"

   ___                                       _                   ___                        _         _
  / __|  ___   _ _   __ __  ___   _ _   ___ (_)  ___   _ _      / __|  ___   _ __    _ __  | |  ___  | |_   ___
 | (__  / _ \ | ' \  \ V / / -_) | '_| (_-< | | / _ \ | ' \    | (__  / _ \ | '  \  | '_ \ | | / -_) |  _| / -_)  _
  \___| \___/ |_||_|  \_/  \___| |_|   /__/ |_| \___/ |_||_|    \___| \___/ |_|_|_| | .__/ |_| \___|  \__| \___| (_)
                                                                                    |_|

"@

Write-Host $End
Write-Host -NoNewline "Total Files Convertered: "
Write-Host $FileCount


Write-Host "Total Execution Time:"
$Elapsed=(Get-Date)-$startTime; 
$Elapsed
