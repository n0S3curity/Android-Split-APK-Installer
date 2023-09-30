import os
import re
import shutil
import subprocess
import sys
import time
import argparse
import pyautogui

# Text cmd colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'
Bold = '\033[1m'
MAGENTA = '\033[35m'
CYAN = '\033[36m'


class Parser:
    logger = None

    def __init__(self):
        parser = argparse.ArgumentParser(
            description='',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
        parser.add_argument("-d", "--dest", required=True, dest="dest", help="Destenation folder with all apks",
                            type=str)
        args = parser.parse_args()
        self.command_lines = vars(args)


pars = Parser()


def get_List_Of_Apks_In_Folder(apk_folder):
    # Get a list of all APK files in the folder
    return sorted([file for file in os.listdir(apk_folder) if file.endswith('.apk')])


def decompile_all_apks(apk_files):
    try:
        if os.path.exists(pars.command_lines['decompiled_folder']):
            print(RED + f"Deleting exists directory: {pars.command_lines['decompiled_folder']}" + RESET)
            shutil.rmtree(pars.command_lines['decompiled_folder'])
        for decompile_apk in apk_files:
            apk_path = os.path.join(pars.command_lines['dest'], decompile_apk)
            decompiled_apk_folder = os.path.join(pars.command_lines['decompiled_folder'],
                                                 decompile_apk.split('.apk')[0])
            print(f"Decompiling {decompile_apk} file..")
            decompile_command = f'apktool d "{apk_path}" -o "{decompiled_apk_folder}"'
            subprocess.call(decompile_command, shell=True)
            time.sleep(2)
        print(GREEN + "Decompiling process finished successfully from base AndroidManifest.xml." + RESET)
    except Exception as e:
        print(RED + "Error in decompile_all_apks Function: " + str(e) + RESET)


def remove_flag_from_manifestXML():
    try:
        manifest_path = os.path.join(pars.command_lines['decompiled_folder'], 'base', 'AndroidManifest.xml')
        if not os.path.exists(manifest_path):
            print(RED + f"Path does not exist: {manifest_path}" + RESET)
            sys.exit(0)
        with open(manifest_path, 'r') as file:
            content = file.read()
        if 'android:isSplitRequired="true"' in content:
            modified_content = re.sub(r'android:isSplitRequired="true"\s*', '', content)
            with open(manifest_path, 'w') as file:
                file.write(modified_content)
            print(GREEN + "[Success] Flag removed successfully." + RESET)
        else:
            print(GREEN + "[Success] Flag not found. No changes made to the file." + RESET)
    except Exception as e:
        print(RED + "Error in remove_flag_from_manifestXML Function: " + str(e) + RESET)


def copy_files_from_splits_to_base():
    try:
        for source_folder in pars.command_lines['decompiled_folder']:
            if "base" in source_folder:
                pass
            else:
                command = f'robocopy /E /XC /XN /XO /NDL /NFL "{source_folder}" "{pars.command_lines["base"]}"'
                subprocess.call(command, shell=True)
        print(GREEN + "All files copied from splits folder to base folder. "+ RESET)

    except Exception as e:
        print(RED + "Error in copy_files_from_splits_to_base Function: " + str(e) + RESET)


try:
    pars.command_lines['apk_files'] = get_List_Of_Apks_In_Folder(pars.command_lines['dest'])
    pars.command_lines['dest'] = pars.command_lines['dest'].replace("\\", "/")
    pars.command_lines['decompiled_folder'] = os.path.join(pars.command_lines['dest'], 'decompiled_apks')
    os.makedirs(pars.command_lines['decompiled_folder'], exist_ok=True)

    decompile_all_apks(pars.command_lines['apk_files'])
    remove_flag_from_manifestXML()
    pars.command_lines['base'] = os.path.join(pars.command_lines['decompiled_folder'], 'base')
    copy_files_from_splits_to_base()



except Exception as e:
    print(RED + "Error in Main:" + str(e) + RESET)

# Install the base APK
# base_apk = apk_files[0]
# base_apk_path = os.path.join(apk_folder, base_apk)
# print("Installing base.apk file first")
# base_command = f'adb install -r "{base_apk_path}"'
# subprocess.call(base_command, shell=True)
