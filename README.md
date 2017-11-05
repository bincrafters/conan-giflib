[![Build Status](https://travis-ci.org/lasote/conan-giflib.svg)](https://travis-ci.org/lasote/conan-giflib)


# conan-giflib

[Conan.io](https://conan.io) package for giflib library

The packages generated with this **conanfile** can be found in [conan.io](https://conan.io/source/giflib/5.1.2/lasote/stable).
Sources from giflib repository: https://sourceforge.net/p/giflib/code/ci/master/tree/build.asc

## Build packages

    $ pip install conan_package_tools
    $ python build.py
    
## Upload packages to server

    $ conan upload giflib/5.1.2@lasote/stable --all
    
## Reuse the packages

### Basic setup

    $ conan install giflib/5.1.2@lasote/stable
    
### Project setup

If you handle multiple dependencies in your project is better to add a *conanfile.txt*
    
    [requires]
    giflib/5.1.2@lasote/stable

    [options]
    giflib:shared=true # false
    
    [generators]
    txt
    cmake

Complete the installation of requirements for your project running:</small></span>

    conan install . 

Project setup installs the library (and all his dependencies) and generates the files *conanbuildinfo.txt* and *conanbuildinfo.cmake* with all the paths and variables that you need to link with your dependencies.
