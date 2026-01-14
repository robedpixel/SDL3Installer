# SDL3 Installer

Because people are too lazy to make an installer for SDL3

By default, this installs to the Program Files folder under `SDL3` and sets the path to include that folder

## Required Software
- Python
- .NET SDK
  - WixToolset.UI.wixext package

## How to Use

1. Fill out the license.rtf file in the license folder with your end-user license agreement
2. Run DownloadSDLAndGenerateInstaller.py
3. The finished installer will be in `/bin/debug`

Or if you want to manually install:

1. Download the SDL3 binaries from https://github.com/libsdl-org/SDL
2. Create a folder in the root folder named `install`
3. Unzip the sdl binaries to the `install` folder
4. Fill out the license.rtf file in the license folder with your end-user license agreement
5. Run `dotnet build` on the root folder
6. The finished installer will be in `/bin/Debug`

## Relevant Generated MSI Variables
- `INSTALLDIR`
  - Folder where SDL3 files will be installed in