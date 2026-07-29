import os
import sys
import subprocess
import shutil
import re

def get_version():
    init_path = os.path.join(os.path.dirname(__file__), "__init__.py")
    with open(init_path, 'r', encoding='utf-8') as f:
        content = f.read()
    match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
    if match:
        return match.group(1)
    return "1.0.16" # fallback

def build_executable(version, safe_pdf_dir, dist_dir):
    portable_name = f"SafePdf_v{version}_portable_win64"
    print(f"\n--- COMPILING PORTABLE SINGLE-FILE BUILD (onefile: {portable_name}.exe) ---")
    pyinstaller_onefile_cmd = [
        "pyinstaller",
        "--noconfirm",
        "--windowed",
        "--onefile",
        "--name", portable_name,
        "--icon", os.path.join(safe_pdf_dir, "assets", "icon.ico"),
        "--version-file", os.path.join(safe_pdf_dir, "version.txt"),
        "--add-data", f"{os.path.join(safe_pdf_dir, 'assets')};assets/",
        "--add-data", f"{os.path.join(safe_pdf_dir, 'ui')};ui/",
        "--add-data", f"{os.path.join(safe_pdf_dir, 'ops')};ops/",
        "--add-data", f"{os.path.join(safe_pdf_dir, 'ctrl')};ctrl/",
        "--add-data", f"{os.path.join(safe_pdf_dir, 'logger')};logger/",
        "--add-data", f"{os.path.join(safe_pdf_dir, 'text')};text/",
        "--add-data", f"{os.path.join(safe_pdf_dir, 'keys')};keys/",
        "--exclude-module", "scipy",
        "--exclude-module", "networkx",
        os.path.join(safe_pdf_dir, "safe_pdf_app.py")
    ]
    
    res = subprocess.run(pyinstaller_onefile_cmd, cwd=safe_pdf_dir)
    if res.returncode != 0:
        print("Error: PyInstaller onefile compilation failed.")
        sys.exit(1)
    print("  Portable onefile compilation successful.")
    return os.path.join(dist_dir, f"{portable_name}.exe")

def main():
    safe_pdf_dir = os.path.dirname(os.path.abspath(__file__))
    user_desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
    
    version = get_version()
    print(f"Detected SafePDF version: {version}")
    
    portable_name = f"SafePdf_v{version}_portable_win64"
    dest_portable = os.path.join(user_desktop, f"{portable_name}.exe")
    final_setup_path = os.path.join(user_desktop, f"SafePdf_v{version}_iwin64.exe")
    
    # Check PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: PyInstaller not found.")
        sys.exit(1)
        
    # Clean previous build artifacts
    dist_dir = os.path.join(safe_pdf_dir, "dist")
    build_dir = os.path.join(safe_pdf_dir, "build")
    for folder in [dist_dir, build_dir]:
        if os.path.exists(folder):
            try:
                shutil.rmtree(folder)
            except Exception as e:
                print(f"Warning: Could not delete {folder}: {e}")
                
    os.makedirs(dist_dir, exist_ok=True)
                
    # 1. Build portable executable directly into dist
    src_portable = build_executable(version, safe_pdf_dir, dist_dir)
    
    # Copy standalone portable build to Desktop
    try:
        shutil.copy2(src_portable, dest_portable)
        print(f"Copied portable build to Desktop: {dest_portable}")
    except Exception as e:
        print(f"Warning: Could not copy portable build to Desktop: {e}")
        
    # Name the executable to package as SafePDF.exe
    setup_target_exe = os.path.join(dist_dir, "SafePDF.exe")
    shutil.copy2(src_portable, setup_target_exe)
    
    # 2. Check InstallForge
    ifbuild_exe = r"C:\Program Files (x86)\solicus\InstallForge\bin\ifbuildx86.exe"
    if not os.path.exists(ifbuild_exe):
        print(f"Error: InstallForge compiler not found at: {ifbuild_exe}")
        sys.exit(1)
        
    # 3. Read and adapt script.ifp
    ifp_path = os.path.join(safe_pdf_dir, "installer", "script.ifp")
    with open(ifp_path, 'r', encoding='utf-8') as f:
        ifp_content = f.read()
        
    app_icon_path = os.path.join(safe_pdf_dir, "assets", "icon.ico")
    uninstaller_icon = r"C:\Program Files (x86)\solicus\InstallForge\bin\ifbuildx86.exe" # fallback or standard
    if not os.path.exists(uninstaller_icon):
        uninstaller_icon = app_icon_path
        
    escaped_target_exe = setup_target_exe.replace('\\', '\\\\')
    escaped_output_setup = final_setup_path.replace('\\', '\\\\')
    escaped_app_icon = app_icon_path.replace('\\', '\\\\')
    
    modified_ifp = ifp_content
    # Per-user execution & uninstallation privileges (zero admin rights required)
    if '<Privileges' not in modified_ifp:
        modified_ifp = modified_ifp.replace('<InstallerConfiguration>', '<InstallerConfiguration>\n    <Privileges level="user"/>')
    else:
        modified_ifp = re.sub(r'<Privileges level="[^"]*"/>', '<Privileges level="user"/>', modified_ifp)

    # Per-user installation path (%LocalAppData%\Programs\SafePDF)
    modified_ifp = re.sub(r'defaultInstallationPath="[^"]*"', 'defaultInstallationPath="&lt;LocalAppData&gt;\\\\Programs\\\\SafePDF\\\\"', modified_ifp)
    modified_ifp = re.sub(r'<Version>[^<]*</Version>', f'<Version>v{version}</Version>', modified_ifp)
    modified_ifp = re.sub(r'<HeaderImage filePath="[^"]*"/>', '<HeaderImage filePath="&lt;main&gt;"/>', modified_ifp)
    modified_ifp = re.sub(r'<SplashScreen isDialogEnabled="[^"]*"[^>]*>[\s\S]*?</SplashScreen>',
                          '<SplashScreen isDialogEnabled="false" delayTime="2">\n      <Image filePath="&lt;main&gt;"/>\n      <Sound isEnabled="false" filePath=""/>\n    </SplashScreen>',
                          modified_ifp)
    # Package single executable file directly
    modified_ifp = re.sub(r'<InstallationFile size="[^"]*" type="\[(Folder|File)\]">[^<]*</InstallationFile>',
                          f'<InstallationFile size="N/A" type="[File]">{escaped_target_exe}</InstallationFile>',
                          modified_ifp)
    modified_ifp = re.sub(r'<SetupFilePath>[^<]*</SetupFilePath>', f'<SetupFilePath>{escaped_output_setup}</SetupFilePath>', modified_ifp)
    modified_ifp = re.sub(r'<SetupIconPath>[^<]*</SetupIconPath>', f'<SetupIconPath>{escaped_app_icon}</SetupIconPath>', modified_ifp)
    modified_ifp = re.sub(r'<UninstallerIconPath>[^<]*</UninstallerIconPath>', f'<UninstallerIconPath>{escaped_app_icon}</UninstallerIconPath>', modified_ifp)
    modified_ifp = re.sub(r'<UninstallerConfiguration isPackaged="[^"]*">', '<UninstallerConfiguration isPackaged="true">', modified_ifp)
    # Shortcut points directly to <InstallPath>\SafePDF.exe
    modified_ifp = re.sub(r'targetFile="&lt;InstallPath&gt;\\[^"]*"', 'targetFile="&lt;InstallPath&gt;\\\\SafePDF.exe"', modified_ifp)
    modified_ifp = re.sub(r'executableFilePath="&lt;InstallPath&gt;\\[^"]*"', 'executableFilePath="&lt;InstallPath&gt;\\\\SafePDF.exe"', modified_ifp)
    
    temp_ifp_path = os.path.join(safe_pdf_dir, "installer", "temp_script.ifp")
    with open(temp_ifp_path, 'w', encoding='utf-8') as f:
        f.write(modified_ifp)
        
    print("Compiling installer package with InstallForge...")
    res = subprocess.run([ifbuild_exe, "-i", temp_ifp_path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if os.path.exists(temp_ifp_path):
        os.remove(temp_ifp_path)
        
    if res.returncode != 0 or b"[err]" in res.stdout:
        print("Error: InstallForge compilation failed.")
        print(res.stdout.decode('utf-8', errors='ignore'))
        print(res.stderr.decode('utf-8', errors='ignore'))
        sys.exit(1)
        
    print("\n" + "="*50)
    print("SUCCESS: Installer package and portable build created successfully!")
    print(f"Installer path: {final_setup_path}")
    print(f"Portable path:  {dest_portable}")
    print("="*50)

if __name__ == "__main__":
    main()
