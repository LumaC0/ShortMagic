from __future__ import print_function
from os import getenv
from pathlib import Path as pl
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from IPython import paths as ip
from dotenv import load_dotenv

DIR = pl(f"{ip.get_ipython_package_dir()}/extensions/shortcutmagic")

load_dotenv(f"{DIR}/.env")

SEP = getenv("SEP")


class ShortUtil:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def _create_files(self):
        """
        Creates file with an -- {appname}.sct -- naming convention
        where .sct stands for shortcut text

        File is created if not existant. This
        method is run on every Ipython startup.
        """
        for app in self.apps:
            appath = self.scdir.joinpath(f"{app.strip()}.sct")
            if not appath.exists():
                appath.touch()


    def _write_command(self):
        command = input("Command: ")
        description = input("Description: ")
        return f"{command} {SEP} {description}\n"


    def _open_for_read(self, file):
        line_cache = []
        file_path = f"{DIR}/{getenv('SHORTCUT_DIR_NAME')}/{file}"
        with open(file_path, "r") as file:
            for line in file.readlines():
                try:
                    line_cache.append(line)
                except IndexError:
                    pass
        return line_cache


    def _open_for_append(self, file):
        file = f"{DIR}/{getenv('SHORTCUT_DIR_NAME')}/{file}"
        with open(file, "a") as file:
            file.write(self._write_command())


    def _open_for_clean_write(self, file, lines = None: list):
        file = f"{DIR}/{getenv('SHORTCUT_DIR_NAME')}/{file}"
        with open(file, "w") as file:
            file.writelines(lines)


    def _edit_file(self, file: list = None):
        coms = self._open_for_read(file)
        com_dict = {}
        for i in coms:
            k, v = i.split(SEP)
            com_dict[k.strip()] = v
            print(f"{k}   :   {v}")
        while True:
            k = input("Command to edit (typed exactly as seen): ").strip()
            if not com_dict.get(k):
                print("\ncommand is typed incorrectly or does not exist\n")
                continue
            com_dict.pop(k)
            newk, newv = self._write_command().split(SEP)
            com_dict[newk] = newv
            break
        scitems = [f"{k} {SEP} {v}" for k,v in com_dict.items()]
        self._open_for_clean_write(file, scitems)



# Custom ipython magic method documentation at: 
# https://ipython.readthedocs.io/en/stable/config/custommagics.html

@magics_class
class ShortMagic(ShortUtil, Magics):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apps = getenv("APPLICATIONS").split()
        self.scdir = DIR.joinpath(getenv("SHORTCUT_DIR_NAME"))
        self._create_files()


    @line_magic
    def sc(self, line):
        "Get a user defined list of IPython shortcuts"
        app = self._interpret_line(line, self.apps)
        if not app:
           return
        file = f"{app}.sct"
        coms = self._open_for_read(file)
        for i in coms:
            line = i.split(SEP)
            print(f"{line[0]}   :   {line[1]}")


    @line_magic
    def sc_add(self, line):
        "Add to IPython shortcuts file - ishortcuts.txt"
        file = self.ip_file
        self._open_for_append(file)


    @line_magic
    def sc_edit(self,line):
        file = self.ip_file
        self._edit_file(file)


    def _interpret_line(self, line, apps):
        line = line.strip()
        if not line:
            print("\n".join(apps))
            return

        apps = [i for i in apps if line == i[:len(line)]]
        assert apps, "No shortcut file for that application exists"
        if len(apps) == 1:
            return apps[0]
        else:
            return self._interpret_line(line, apps)





