#!/usr/bin/env python
# -*- coding: utf-8 -*-


from bincrafters import build_template_default
import platform
import copy

if __name__ == "__main__":

    builder = build_template_default.get_builder()

    items = []
    for item in builder.items:
        # skip mingw cross-builds
        if not (platform.system() == "Windows" and item.settings["compiler"] == "gcc" and
                item.settings["arch"] == "x86"):
            new_build_requires = copy.copy(item.build_requires)
            if platform.system() == "Windows" and item.settings["compiler"] == "gcc":
                # add msys2 and mingw as a build requirement for mingw builds
                new_build_requires["*"] = new_build_requires.get("*", []) + \
                    ["mingw_installer/1.0@conan/stable",
                     "msys2_installer/latest@bincrafters/stable"]
                items.append([item.settings, item.options, item.env_vars,
                              new_build_requires, item.reference])
            elif platform.system() == "Windows" and item.settings["compiler"] != "gcc":
                # add cygwin build requirement
                new_build_requires["*"] = new_build_requires.get("*", []) + \
                    ["cygwin_installer/2.9.0@bincrafters/stable"]
                items.append([item.settings, item.options, item.env_vars,
                              new_build_requires, item.reference])
            else:
                # or just add build
                items.append(item)
    builder.items = items

    builder.run()
