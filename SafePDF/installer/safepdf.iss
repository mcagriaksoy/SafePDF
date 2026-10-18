; Inno Setup script for SafePDF.
;
; Produces a per-user Windows installer (no admin rights required) that matches
; the previous InstallForge configuration: install into
; %LocalAppData%\Programs\SafePDF, create Start Menu shortcuts and an
; optional desktop shortcut, and allow a clean uninstall.
;
; The CI workflow builds the portable executable first, then compiles this
; script, passing the version, source executable and output directory:
;
;   ISCC.exe /DVersion=1.2.3 /DSourceExe=<abs path> /DOutputDir=<abs path> safepdf.iss
;
; Defaults below allow compiling locally from the repository as well.

#ifndef Version
  #define Version "0.0.0"
#endif

#ifndef SourceExe
  #define SourceExe "..\dist\SafePdf_v" + Version + "_portable_win64.exe"
#endif

#ifndef OutputDir
  #define OutputDir "..\dist"
#endif

[Setup]
AppId={{522241A8-95CE-4AF1-A892-1C200DD551FD}
AppName=SafePDF
AppVersion={#Version}
AppVerName=SafePDF {#Version}
AppPublisher=mcagriaksoy
AppPublisherURL=https://safepdf.de
AppSupportURL=https://github.com/mcagriaksoy/SafePDF
AppUpdatesURL=https://github.com/mcagriaksoy/SafePDF/releases
DefaultDirName={localappdata}\Programs\SafePDF
DefaultGroupName=SafePDF
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
OutputDir={#OutputDir}
OutputBaseFilename=SafePdf_v{#Version}_iwin64
SetupIconFile=..\assets\icon.ico
UninstallDisplayIcon={app}\SafePDF.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
LicenseFile=..\..\LICENSE

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "german"; MessagesFile: "compiler:Languages\German.isl"
Name: "turkish"; MessagesFile: "compiler:Languages\Turkish.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "{#SourceExe}"; DestDir: "{app}"; DestName: "SafePDF.exe"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\SafePDF"; Filename: "{app}\SafePDF.exe"
Name: "{autodesktop}\SafePDF"; Filename: "{app}\SafePDF.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\SafePDF.exe"; Description: "{cm:LaunchProgram,SafePDF}"; Flags: nowait postinstall skipifsilent
