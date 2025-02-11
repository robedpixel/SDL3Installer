# SDL2 Installer

Because people are too lazy to make an installer for SDL2

Currently doesn't show any UI, but this installs to the Program Files folder under `SDL2` and sets the path to include that folder

## How to Use

1. Download the binaries from https://github.com/libsdl-org/SDL
2. Create a folder in the root folder named `install`
3. Unzip the sdl binaries to the `install` folder
4. Run `dotnet build` on the root folder
5. The finished installer will be in `/bin/Debug`