#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import CMake, AutoToolsBuildEnvironment, ConanFile, tools


class ZlibNgConan(ConanFile):
    name = "giflib"
    version = "5.1.3"
    ZIP_FOLDER_NAME = "giflib-%s" % version 
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url = "http://github.com/ZaMaZaN4iK/conan-giflib"
    license = "https://sourceforge.net/p/giflib/code/ci/master/tree/COPYING"
    exports = ["FindGIF.cmake", "CMakeLists.txt", "getopt.c", "getopt.h", "unistd.h.in"]
    install = 'gitfil-install'
    description = 'The GIFLIB project maintains the giflib service library, which has been pulling images out of GIFs since 1989'
    # The exported files I took them from https://github.com/bjornblissing/osg-3rdparty-cmake/tree/master/giflib
    
    def config(self):
        del self.settings.compiler.libcxx
        
        if self.settings.os == "Windows":
            try:
                self.options.remove("shared")
                self.options.remove("fPIC")
            except: 
                pass
            # self.ZIP_FOLDER_NAME = "giflib-%s-windows" % self.version

    def source(self):
        zip_name = "%s.tar.gz" % self.ZIP_FOLDER_NAME
        tools.download("http://downloads.sourceforge.net/project/giflib/%s" % zip_name, zip_name)
        tools.unzip(zip_name)
        os.unlink(zip_name)
        if not self.settings.os != "Windows":
            for filename in ["CMakeLists.txt", "getopt.c", "getopt.h", "unistd.h.in"]:
                shutil.copy(filename, os.path.join(self.ZIP_FOLDER_NAME, filename))

    def build_configure(self):
        prefix = os.path.abspath(self.install)
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.fPIC

        args = ['--prefix=%s' % prefix]
        if self.options.shared:
            args.extend(['--disable-static', '--enable-shared'])
        else:
            args.extend(['--enable-static', '--disable-shared'])

        with tools.chdir(self.ZIP_FOLDER_NAME):
            if self.settings.os == "Macos":
                old_str = r'-install_name \$rpath/\$soname'
                new_str = r'-install_name \$soname'
                tools.replace_in_file("configure", old_str, new_str)

            self.run('chmod +x configure')
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

    def build_windows(self):
        cmake = CMake(self.settings)
        self.run("cd %s && mkdir _build" % self.ZIP_FOLDER_NAME)
        cd_build = "cd %s/_build" % self.ZIP_FOLDER_NAME
        self.output.warn('%s && cmake .. %s' % (cd_build, cmake.command_line))
        self.run('%s && cmake .. %s' % (cd_build, cmake.command_line))
        self.output.warn("%s && cmake --build . %s" % (cd_build, cmake.build_config))
        self.run("%s && cmake --build . %s" % (cd_build, cmake.build_config))

    def build(self):
        if self.settings.os == "Windows":
            self.build_windows()
        else:
            self.build_configure()

    def package(self):
        # Copy FindGIF.cmake to package
        self.copy("FindGIF.cmake", ".", ".")
        
        # Copying zlib.h, zutil.h, zconf.h
        self.copy("*.h", "include", "%s" % self.ZIP_FOLDER_NAME, keep_path=False)
        self.copy("*.h", "include", "%s" % "_build", keep_path=False)

        if not self.settings.os == "Windows" and self.options.shared:
            if self.settings.os == "Macos":
                self.copy(pattern="*.dylib", dst="lib", keep_path=False)
                self.copy(pattern="**.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            else:
                self.copy(pattern="*.so*", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
                self.copy(pattern="**.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
        else:
            self.copy(pattern="*.a", dst="lib", src="%s/_build" % self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.a", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=self.ZIP_FOLDER_NAME, keep_path=False)

    def package_info(self):
        if self.settings.os == "Windows":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ['libgifd', 'getargd']
            else:
                self.cpp_info.libs = ['libgif', 'getarg']
        else:
            self.cpp_info.libs = ['gif', 'getarg']
