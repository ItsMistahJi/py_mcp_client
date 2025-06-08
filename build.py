import os
import sys
import platform
import subprocess
import shutil

def install_requirements():
    print("Installing requirements...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def build_executable():
    print("Building executable...")
    # Create spec file content
    icon_path = 'assets/icon.ico' if platform.system() == 'Windows' else 'assets/icon.icns'
    spec_content = f"""
import platform
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['Py_MCP_Client.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MCP Client',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='{icon_path}',
)

if platform.system() == 'Darwin':
    app = BUNDLE(
        exe,
        name='MCP Client.app',
        icon='{icon_path}',
        bundle_identifier='com.mcp.client',
        info_plist={{
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleVersion': '1.0.0',
            'NSHighResolutionCapable': 'True',
            'LSBackgroundOnly': 'False',
            'NSRequiresAquaSystemAppearance': 'False',
        }},
    )
    """
    
    # Write spec file
    with open("MCP_Client.spec", "w") as f:
        f.write(spec_content)
    
    # Run PyInstaller
    subprocess.check_call(["pyinstaller", "MCP_Client.spec", "--clean"])

def create_windows_installer():
    if platform.system() != "Windows":
        print("Skipping Windows installer creation on non-Windows platform")
        return
    
    print("Creating Windows installer...")
    # Create Inno Setup script
    inno_script = """
#define MyAppName "MCP Client"
#define MyAppVersion "1.0"
#define MyAppPublisher "Your Company"
#define MyAppExeName "MCP Client.exe"

[Setup]
AppId={{YOUR-UNIQUE-APP-ID-HERE}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=installer
OutputBaseFilename=MCP_Client_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\MCP Client\\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{autodesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent
    """
    
    # Write Inno Setup script
    with open("installer_script.iss", "w") as f:
        f.write(inno_script)
    
    # Run Inno Setup Compiler
    subprocess.check_call(["iscc", "installer_script.iss"])

def create_mac_dmg():
    if platform.system() != "Darwin":
        print("Skipping Mac DMG creation on non-Mac platform")
        return
    
    print("Creating Mac DMG...")
    # Create DMG using create-dmg
    subprocess.check_call([
        "create-dmg",
        "--volname", "MCP Client",
        "--volicon", "assets/icon.icns",
        "--window-pos", "200", "120",
        "--window-size", "800", "400",
        "--icon-size", "100",
        "--icon", "MCP Client.app", "200", "190",
        "--hide-extension", "MCP Client.app",
        "--app-drop-link", "600", "185",
        "installer/MCP_Client.dmg",
        "dist/MCP Client.app"
    ])

def main():
    # Create necessary directories
    os.makedirs("assets", exist_ok=True)
    os.makedirs("installer", exist_ok=True)
    
    # Install requirements
    install_requirements()
    
    # Build executable
    build_executable()
    
    # Create platform-specific installers
    if platform.system() == "Windows":
        create_windows_installer()
    elif platform.system() == "Darwin":
        create_mac_dmg()
    
    print("Build process completed!")

if __name__ == "__main__":
    main() 