#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import CMake, AutoToolsBuildEnvironment, ConanFile, tools


class ZlibNgConan(ConanFile):
    name = "giflib"
    version = "5.1.3"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url = "http://github.com/bincrafters/conan-giflib"
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
        zip_name = "%s-%s" % (self.name, self.version)
        tools.get("http://downloads.sourceforge.net/project/giflib/%s.tar.gz" % zip_name)
        if self.settings.os == "Windows":
            for filename in ["CMakeLists.txt", "getopt.c", "getopt.h", "unistd.h.in"]:
                shutil.copy(filename, os.path.join(zip_name, filename))
        os.rename(zip_name, "sources")

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_windows()
        else:
            self.build_configure()

    def build_windows(self):
        cmake = CMake(self)
        cmake.configure(source_dir="sources")
        self.output.info('Running CMake command: ' + cmake.command_line)
        cmake.build()

    def build_configure(self):
        prefix = os.path.abspath(self.install)
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.fPIC

        args = ['--prefix=%s' % prefix]
        if self.options.shared:
            args.extend(['--disable-static', '--enable-shared'])
        else:
            args.extend(['--enable-static', '--disable-shared'])

        with tools.chdir("sources"):
            if self.settings.os == "Macos":
                old_str = r'-install_name \$rpath/\$soname'
                new_str = r'-install_name \$soname'
                tools.replace_in_file("configure", old_str, new_str)

            self.run('chmod +x configure')
            env_build.configure(args=args)
            env_build.make()
            env_build.make(args=['install'])

            
    def package(self):
        # Copy FindGIF.cmake to package
        self.copy("FindGIF.cmake", ".", ".")
        
        # Copying zlib.h, zutil.h, zconf.h
        self.copy("*.h", "include", "%s" % "sources", keep_path=False)
        self.copy(pattern="libgif.lib", dst="lib", keep_path=False)
        self.copy(pattern="libgif.dylib", dst="lib", keep_path=False)
        self.copy(pattern="libgif.a", dst="lib", keep_path=False)
        self.copy(pattern="libgif.so*", dst="lib", keep_path=False)
        
    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.settings.build_type == "Debug":
                self.cpp_info.libs = ['libgifd', 'getargd']
            else:
                self.cpp_info.libs = ['libgif', 'getarg']
        else:
            self.cpp_info.libs = ['gif', 'getarg']
