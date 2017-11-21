#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
from conans import AutoToolsBuildEnvironment, ConanFile, tools


class GiflibConan(ConanFile):
    name = "giflib"
    version = "5.1.3"
    generators = "cmake"
    settings = "os", "arch", "compiler", "build_type"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = "shared=False", "fPIC=True"
    url = "http://github.com/bincrafters/conan-giflib"
    license = "https://sourceforge.net/p/giflib/code/ci/master/tree/COPYING"
    exports = ["FindGIF.cmake", "getopt.c", "getopt.h", "unistd.h", 'gif_lib.h']
    description = 'The GIFLIB project maintains the giflib service library, ' \
                  'which has been pulling images out of GIFs since 1989'
    # The exported files I took them from https://github.com/bjornblissing/osg-3rdparty-cmake/tree/master/giflib

    def build_requirements(self):
        if self.settings.os == "Windows":
            self.build_requires("cygwin_installer/2.9.0@bincrafters/testing")
    
    def config(self):
        del self.settings.compiler.libcxx
        
        if self.settings.os == "Windows":
            self.options.remove("fPIC")

    def source(self):
        zip_name = "%s-%s" % (self.name, self.version)
        tools.get("http://downloads.sourceforge.net/project/giflib/%s.tar.gz" % zip_name)
        if self.settings.os == "Windows":
            for filename in ["getopt.c", "getopt.h", "unistd.h"]:
                shutil.copy(filename, os.path.join(zip_name, filename))
            if self.options.shared:
                self.output.warn("shared build, overwrite gif_lib.h")
                os.unlink(os.path.join(zip_name, 'lib', 'gif_lib.h'))
                shutil.copy('gif_lib.h', os.path.join(zip_name, 'lib', 'gif_lib.h'))
            else:
                self.output.warn("static build, overwrite gif_lib.h")
        os.rename(zip_name, "sources")

    def build(self):
        if self.settings.compiler == "Visual Studio":
            self.build_windows()
        else:
            self.build_configure()

    def run_in_cygwin(self, command):
        with tools.environment_append({'PATH': [self.deps_env_info['cygwin_installer'].CYGWIN_BIN]}):
            bash = "%CYGWIN_BIN%\\bash"
            vcvars_command = tools.vcvars_command(self.settings)
            self.run("{vcvars_command} && {bash} -c ^'{command}'".format(
                vcvars_command=vcvars_command,
                bash=bash,
                command=command))

    def build_windows(self):
        with tools.chdir("sources"):
            if self.settings.arch == "x86":
                host = "i686-w64-mingw32"
            elif self.settings.arch == "x86_64":
                host = "x86_64-w64-mingw32"
            else:
                raise Exception("unsupported architecture %s" % self.settings.arch)
            if self.options.shared:
                options = '--disable-static --enable-shared'
            else:
                options = '--enable-static --disable-shared'

            self.run_in_cygwin('cl getopt.c -DWIN32 /c -%s' % str(self.settings.compiler.runtime))
            self.run_in_cygwin('lib getopt.obj /OUT:getopt.lib /NODEFAULTLIB:LIBCMT')

            if self.options.shared:
                tools.replace_in_file(os.path.join('util', 'Makefile.in'),
                                      'DEFS = @DEFS@', 'DEFS = @DEFS@ -DUSE_GIF_DLL')

            getopt = os.path.abspath('getopt.lib')
            getopt = tools.unix_path(getopt)
            getopt = '/cygdrive' + getopt

            cflags = ''
            if float(str(self.settings.compiler.version)) < 14.0:
                cflags = '-Dsnprintf=_snprintf'

            prefix = tools.unix_path(os.path.abspath(self.package_folder))
            prefix = '/cygdrive' + prefix
            self.run_in_cygwin('./configure '
                               '{options} '
                               '--host={host} '
                               '--prefix={prefix} '
                               'CC="$PWD/compile cl -nologo" '
                               'CFLAGS="-{runtime} {cflags}" '
                               'CXX="$PWD/compile cl -nologo" '
                               'CXXFLAGS="-{runtime} {cflags}" '
                               'CPPFLAGS="-I{prefix}/include" '
                               'LDFLAGS="-L{prefix}/lib {getopt}" '
                               'LD="link" '
                               'NM="dumpbin -symbols" '
                               'STRIP=":" '
                               'AR="$PWD/ar-lib lib" '
                               'RANLIB=":" '.format(host=host, prefix=prefix, options=options, getopt=getopt,
                                                    runtime=str(self.settings.compiler.runtime), cflags=cflags))
            self.run_in_cygwin('make')
            self.run_in_cygwin('make install')

    def build_configure(self):
        env_build = AutoToolsBuildEnvironment(self)
        env_build.fpic = self.options.fPIC

        args = ['--prefix=%s' % self.package_folder]
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
        self.copy('getarg.h', src=os.path.join('sources', 'util'), dst='include')
        if self.settings.os == "Windows":
            shutil.move(os.path.join('sources', 'util', 'libgetarg.a'),
                        os.path.join('sources', 'util', 'libgetarg.lib'))
            self.copy('libgetarg.lib', src=os.path.join('sources', 'util'), dst='lib')
        else:
            self.copy('libgetarg.a', src=os.path.join('sources', 'util'), dst='lib')
        
    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            if self.options.shared:
                self.cpp_info.libs = ['libgetarg', 'gif.dll.lib']
                self.cpp_info.defines.append('USE_GIF_DLL')
            else:
                self.cpp_info.libs = ['libgetarg', 'gif']
        else:
            self.cpp_info.libs = ['getarg', 'gif']
