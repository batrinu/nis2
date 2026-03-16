; =============================================================================
; NIS2 Field Audit Tool - Uncle-Friendly Windows Installer
; =============================================================================
; This installer handles:
;   - Windows version check (Windows 10+ recommended)
;   - Visual C++ Redistributable check and install
;   - Python check (for dev version) OR portable Python extraction
;   - Desktop shortcut creation
;   - Uninstaller creation
; =============================================================================

!include "MUI2.nsh"
!include "LogicLib.nsh"
!include "x64.nsh"

; =============================================================================
; Application Info
; =============================================================================
!define APP_NAME "NIS2 Field Audit Tool"
!define APP_SHORTNAME "NIS2Audit"
!define APP_VERSION "1.0.0"
!define APP_PUBLISHER "NIS2 Audit Team"
!define APP_WEBSITE "https://github.com/batrinu/nis2"
!define INSTALL_DIR "$PROGRAMFILES64\${APP_SHORTNAME}"

; VCRedist info
!define VCREDIST_URL "https://aka.ms/vs/17/release/vc_redist.x64.exe"
!define VCREDIST_EXE "vc_redist.x64.exe"

; Python info (for portable version)
!define PYTHON_VERSION "3.12.3"
!define PYTHON_URL "https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-embed-amd64.zip"

; =============================================================================
; Installer Configuration
; =============================================================================
Name "${APP_NAME}"
OutFile "..\dist\NIS2-Audit-Tool-Setup.exe"
InstallDir "${INSTALL_DIR}"
InstallDirRegKey HKLM "Software\${APP_SHORTNAME}" "InstallDir"
RequestExecutionLevel admin

; Compression
SetCompressor lzma

; =============================================================================
; Interface Settings
; =============================================================================
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page text
!define MUI_WELCOMEPAGE_TITLE "Welcome to the ${APP_NAME} Setup Wizard"
!define MUI_WELCOMEPAGE_TEXT "This wizard will guide you through the installation of ${APP_NAME}.\r\n\r\n\
Before we begin, please ensure:\r\n\
  • You have an internet connection (for dependency downloads)\r\n\
  • You are running Windows 10 or later\r\n\
  • You have administrator rights\r\n\r\n\
Click Next to continue."

; =============================================================================
; Pages
; =============================================================================
!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_LICENSE "..\LICENSE.txt"
Page custom CheckDependenciesPage CheckDependenciesLeave
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!define MUI_FINISHPAGE_RUN "$INSTDIR\launch.bat"
!define MUI_FINISHPAGE_RUN_TEXT "Launch NIS2 Field Audit Tool"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\README.txt"
!define MUI_FINISHPAGE_SHOWREADME_TEXT "Show Readme"
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; =============================================================================
; Languages
; =============================================================================
!insertmacro MUI_LANGUAGE "English"

; =============================================================================
; Variables
; =============================================================================
Var VCRedistInstalled
Var PythonInstalled
Var WindowsVersion
Var InternetAvailable
Var Dialog
Var Label1
Var Label2
Var Checkbox1
Var Checkbox2

; =============================================================================
; Helper Functions
; =============================================================================

; Check if VCRedist is installed
Function CheckVCRedist
    Push $0
    
    ; Check for VCRedist 2015-2022 (x64)
    ReadRegDWORD $0 HKLM "SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64" "Installed"
    StrCmp $0 1 VCRedistFound
    
    ; Check via uninstall registry
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{8bdfe669-9705-4184-b44e-1dbaa9e449b2}" "DisplayName"
    StrCmp $0 "" VCRedistNotFound VCRedistFound
    
VCRedistFound:
    StrCpy $VCRedistInstalled "1"
    Pop $0
    Return
    
VCRedistNotFound:
    StrCpy $VCRedistInstalled "0"
    Pop $0
    Return
FunctionEnd

; Check Python installation
Function CheckPython
    Push $0
    Push $1
    
    nsExec::ExecToStack 'python --version'
    Pop $0
    Pop $1
    
    StrCmp $0 "0" PythonFound
    
    nsExec::ExecToStack 'py --version'
    Pop $0
    Pop $1
    
    StrCmp $0 "0" PythonFound
    
    StrCpy $PythonInstalled "0"
    Pop $1
    Pop $0
    Return
    
PythonFound:
    StrCpy $PythonInstalled "1"
    Pop $1
    Pop $0
    Return
FunctionEnd

; Check Windows version
Function CheckWindowsVersion
    Push $0
    ReadRegStr $0 HKLM "SOFTWARE\Microsoft\Windows NT\CurrentVersion" "CurrentMajorVersionNumber"
    StrCpy $WindowsVersion $0
    Pop $0
FunctionEnd

; Check internet connection
Function CheckInternet
    Push $0
    Dialer::GetConnectedState
    Pop $0
    StrCpy $InternetAvailable $0
    Pop $0
FunctionEnd

; =============================================================================
; Custom Dependency Check Page
; =============================================================================
Function CheckDependenciesPage
    !insertmacro MUI_HEADER_TEXT "Checking System Requirements" "Verifying that your system meets all requirements"
    
    nsDialogs::Create 1018
    Pop $Dialog
    
    ${If} $Dialog == error
        Abort
    ${EndIf}
    
    ; Check all dependencies
    Call CheckWindowsVersion
    Call CheckVCRedist
    Call CheckPython
    Call CheckInternet
    
    ; Title
    ${NSD_CreateLabel} 0 0 100% 20u "System Requirements Check:"
    Pop $Label1
    
    ; Windows Version
    ${NSD_CreateLabel} 0 30u 100% 20u ""
    Pop $0
    ${If} $WindowsVersion >= 10
        ${NSD_SetText} $0 "✓ Windows Version: OK (Windows 10 or newer)"
        SetCtlColors $0 008000 transparent
    ${Else}
        ${NSD_SetText} $0 "⚠ Windows Version: Windows 10 or newer recommended"
        SetCtlColors $0 FF8000 transparent
    ${EndIf}
    
    ; VCRedist
    ${NSD_CreateLabel} 0 50u 100% 40u ""
    Pop $Label2
    ${If} $VCRedistInstalled == "1"
        ${NSD_SetText} $Label2 "✓ Visual C++ Redistributable: Installed"
        SetCtlColors $Label2 008000 transparent
    ${Else}
        ${NSD_SetText} $Label2 "✗ Visual C++ Redistributable: NOT INSTALLED$$
The installer will download and install it automatically."
        SetCtlColors $Label2 FF0000 transparent
    ${EndIf}
    
    ; Python status (informational for portable version)
    ${NSD_CreateLabel} 0 90u 100% 30u ""
    Pop $0
    ${NSD_SetText} $0 "Note: This installer includes a portable Python runtime.$\r$\nNo separate Python installation is required."
    SetCtlColors $0 0000FF transparent
    
    ; Internet warning if needed
    ${If} $VCRedistInstalled == "0"
    ${AndIf} $InternetAvailable == "0"
        ${NSD_CreateLabel} 0 130u 100% 40u ""
        Pop $0
        ${NSD_SetText} $0 "⚠ WARNING: No internet connection detected and VCRedist is missing.$\r$\nPlease connect to the internet or install VCRedist manually from:$\r$\nhttps://aka.ms/vs/17/release/vc_redist.x64.exe"
        SetCtlColors $0 FF0000 transparent
    ${EndIf}
    
    nsDialogs::Show
FunctionEnd

Function CheckDependenciesLeave
    ; Allow proceeding even if checks fail - we'll handle it during install
FunctionEnd

; =============================================================================
; Download and Install VCRedist
; =============================================================================
Function InstallVCRedist
    ${If} $VCRedistInstalled == "1"
        DetailPrint "Visual C++ Redistributable already installed"
        Return
    ${EndIf}
    
    DetailPrint "Downloading Visual C++ Redistributable..."
    
    ; Download to temp
    NSISdl::download "${VCREDIST_URL}" "$TEMP\${VCREDIST_EXE}"
    Pop $0
    
    ${If} $0 != "success"
        MessageBox MB_OK "Failed to download Visual C++ Redistributable. Please install it manually from:${VCREDIST_URL}"
        Return
    ${EndIf}
    
    DetailPrint "Installing Visual C++ Redistributable..."
    ExecWait '"$TEMP\${VCREDIST_EXE}" /install /quiet /norestart' $0
    
    ${If} $0 == 0
        DetailPrint "Visual C++ Redistributable installed successfully"
    ${ElseIf} $0 == 3010
        DetailPrint "Visual C++ Redistributable installed (restart required)"
        MessageBox MB_OK "Visual C++ Redistributable was installed successfully. You may need to restart your computer after the installation completes."
    ${Else}
        DetailPrint "Visual C++ Redistributable installation returned: $0"
        MessageBox MB_OK "Visual C++ Redistributable installation may have failed (code: $0). The application might not work correctly."
    ${EndIf}
    
    Delete "$TEMP\${VCREDIST_EXE}"
FunctionEnd

; =============================================================================
; Installation Section
; =============================================================================
Section "Install Application" SecApp
    SectionIn RO
    
    SetOutPath "$INSTDIR"
    
    ; Install VCRedist if needed
    Call InstallVCRedist
    
    ; Create directories
    CreateDirectory "$INSTDIR\python"
    CreateDirectory "$INSTDIR\lib"
    CreateDirectory "$INSTDIR\data"
    
    ; Extract portable Python
    DetailPrint "Extracting portable Python..."
    File "..\dist\portable\python\*"  ; These files should be included in the installer
    
    ; Copy application files
    DetailPrint "Installing application files..."
    File /r "..\nis2-audit-app\app"
    File "..\nis2-audit-app\launch.bat"
    File "..\README.md"
    File "..\LICENSE.txt"
    
    ; Create README for user
    FileOpen $0 "$INSTDIR\README.txt" w
    FileWrite $0 "NIS2 Field Audit Tool$$
$$
Getting Started:$$
1. Double-click 'launch.bat' to start the application$$
2. Or use the Desktop shortcut$$
$$
Requirements:$$
- Windows 10 or later$$
- Visual C++ Redistributable (will be installed automatically)$$
$$
For help, visit: ${APP_WEBSITE}"
    FileClose $0
    
    ; Write registry for uninstall
    WriteRegStr HKLM "Software\${APP_SHORTNAME}" "InstallDir" "$INSTDIR"
    WriteRegStr HKLM "Software\${APP_SHORTNAME}" "Version" "${APP_VERSION}"
    
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "DisplayName" "${APP_NAME}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "UninstallString" "$\"$INSTDIR\uninstall.exe$\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "QuietUninstallString" "$\"$INSTDIR\uninstall.exe$\" /S"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "InstallLocation" "$\"$INSTDIR\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "DisplayIcon" "$\"$INSTDIR\launch.bat\""
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "Publisher" "${APP_PUBLISHER}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "HelpLink" "${APP_WEBSITE}"
    WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}" \
        "DisplayVersion" "${APP_VERSION}"
    
    ; Create uninstaller
    WriteUninstaller "$INSTDIR\uninstall.exe"
    
    ; Create shortcuts
    CreateDirectory "$SMPROGRAMS\${APP_SHORTNAME}"
    CreateShortcut "$SMPROGRAMS\${APP_SHORTNAME}\${APP_NAME}.lnk" "$INSTDIR\launch.bat"
    CreateShortcut "$SMPROGRAMS\${APP_SHORTNAME}\Uninstall.lnk" "$INSTDIR\uninstall.exe"
    CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\launch.bat"
    
    ; Success message
    MessageBox MB_OK "${APP_NAME} has been installed successfully!$$
$$
You can launch it from:$$
- Desktop shortcut$$
- Start Menu > ${APP_SHORTNAME}$$
- $INSTDIR\launch.bat"
SectionEnd

; =============================================================================
; Uninstaller
; =============================================================================
Section "Uninstall"
    ; Remove files
    RMDir /r "$INSTDIR\app"
    RMDir /r "$INSTDIR\python"
    RMDir /r "$INSTDIR\lib"
    RMDir /r "$INSTDIR\data"
    Delete "$INSTDIR\launch.bat"
    Delete "$INSTDIR\README.txt"
    Delete "$INSTDIR\README.md"
    Delete "$INSTDIR\LICENSE.txt"
    Delete "$INSTDIR\uninstall.exe"
    
    ; Remove directory
    RMDir "$INSTDIR"
    
    ; Remove shortcuts
    Delete "$DESKTOP\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_SHORTNAME}\${APP_NAME}.lnk"
    Delete "$SMPROGRAMS\${APP_SHORTNAME}\Uninstall.lnk"
    RMDir "$SMPROGRAMS\${APP_SHORTNAME}"
    
    ; Remove registry entries
    DeleteRegKey HKLM "Software\${APP_SHORTNAME}"
    DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APP_SHORTNAME}"
    
    MessageBox MB_OK "${APP_NAME} has been uninstalled."
SectionEnd

; =============================================================================
; Version Info (for the installer itself)
; =============================================================================
VIProductVersion "${APP_VERSION}.0"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductName" "${APP_NAME}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "ProductVersion" "${APP_VERSION}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "CompanyName" "${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "LegalCopyright" "© 2026 ${APP_PUBLISHER}"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileDescription" "${APP_NAME} Setup"
VIAddVersionKey /LANG=${LANG_ENGLISH} "FileVersion" "${APP_VERSION}"
