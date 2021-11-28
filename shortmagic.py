from __future__ import print_function
from os import getenv
from pathlib import Path as pl
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic, line_cell_magic)
from IPython import paths as ip
from dotenv import load_dotenv

DIR = pl(f"{ip.get_ipython_package_dir()}/extensions/shortcutmagic")
load_dotenv(f"{DIR}/.env")

# Custom ipython magic method documentation at: 
# https://ipython.readthedocs.io/en/stable/config/custommagics.html

@magics_class
class ShortMagic(Magics):

    def __init__(self, shell):
        super(ShortMagic, self).__init__(shell)
        self.apps = getenv("APPLICATIONS").split()
        self.scdir = DIR.joinpath(getenv("SHORTCUT_DIR_NAME"))
        self._create_files()


    @line_magic
    def sc(self, line):
        "Get a user defined list of IPython shortcuts"
        file = self.ip_file
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


    def _create_files(self):
        for app in self.apps:
            appath = self.scdir.joinpath(f"{app.strip()}.txt")
            if not appath.exists():
                appath.touch()


    def _write_command(self):
        command = input("Command: ")
        description = input("Description: ")
        return f"{command} {SEP} {description}\n"


    def _open_for_read(self, file):
        line_cache = []
        with open(f"{DIR}/{file}", "r") as file:
            for line in file.readlines():
                try:
                    line_cache.append(line)
                except IndexError:
                    pass
        return line_cache


    def _open_for_append(self, file):
        with open(f"{DIR}/{file}", "a") as file:
            file.write(self._write_command())


    def _edit_file(self, file=None):
        coms = self._open_for_read(file)
        com_dict = {}
        for i in coms:
            k, v = i.split(SEP)
            com_dict[k] = v
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

        try:
            fopen_for_write = open(file, "w")
        except:
            print("could not write to file")
        finally:
            fopen_for_write.writelines([f"{k} {SEP} {v}" for k,v in com_dict.items()])
            fopen_for_write.close()


