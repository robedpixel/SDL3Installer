# STEPS
# Download latest windows x64 zip file from sdl repo (use regex?) to temp folder
# Record downloaded version number
# unzip contents to install
# Modify wxs version to downloaded version
# Run wix

import requests
import zipfile
import io
import re
import json
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    github_sdl_repo_path = "/libsdl-org/SDL"
    # Regex to find version number, currently not needed
    # version_regex = "([0-9]+[.]){2}[0-9]"

    windows_regex = "win32-x64"
    file_blacklist = ["INSTALL.md"]

    # Download latest windows x64 zip file from sdl repo

    github_sdl_repo_abs_path = (
        "https://api.github.com/repos" + github_sdl_repo_path + "/releases/latest"
    )
    response_json = requests.get(url=github_sdl_repo_abs_path).json()

    # Grab version

    library_version = response_json["name"]

    # Iterate through assets and find x86_64 zip

    asset_list = response_json["assets"]
    for asset in asset_list:
        if re.search(windows_regex, asset["name"]):
            dirname = os.path.dirname(__file__)
            temp_folder = os.path.join(dirname, "temp")
            install_folder = os.path.join(dirname, "install")

            Path(temp_folder).mkdir(parents=True, exist_ok=True)
            # Download contents into temp

            download_url = asset["browser_download_url"]
            r = requests.get(download_url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            z.extractall(temp_folder)

            # move contents to install unless it's in blacklist

            temp_directory = os.fsencode(temp_folder)
            for file in os.listdir(temp_directory):
                filename = os.fsdecode(file)
                if filename in file_blacklist:
                    continue
                else:
                    os.replace(
                        temp_folder + "\\" + filename, install_folder + "\\" + filename
                    )
            # TODO: edit wxs file with new version

            wxs_file = os.path.join(dirname, "Package.wxs")
            ET.register_namespace("", "http://wixtoolset.org/schemas/v4/wxs")
            ET.register_namespace("ui", "http://wixtoolset.org/schemas/v4/wxs/ui")
            tree = ET.parse(wxs_file)
            root = tree.getroot()
            for elem in root:
                if elem.tag == "{http://wixtoolset.org/schemas/v4/wxs}Package":
                    elem.attrib["Version"] = library_version
                    break
            tree.write(wxs_file)
            try:
                shutil.rmtree(temp_folder)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
            # Build Installer

            os.chdir(dirname)
            os.system("dotnet build")


if __name__ == "__main__":
    main()
