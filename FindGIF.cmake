#.rst:
# FindGIF
# -------
#
#
#
# This module searches giflib and defines GIF_LIBRARIES - libraries to
# link to in order to use GIF GIF_FOUND, if false, do not try to link
# GIF_INCLUDE_DIR, where to find the headers GIF_VERSION, reports either
# version 4 or 3 (for everything before version 4)
#
# The minimum required version of giflib can be specified using the
# standard syntax, e.g.  find_package(GIF 4)
#
# $GIF_DIR is an environment variable that would correspond to the
# ./configure --prefix=$GIF_DIR

#=============================================================================
# Copyright 2007-2009 Kitware, Inc.
#
# Distributed under the OSI-approved BSD License (the "License");
# see accompanying file Copyright.txt for details.
#
# This software is distributed WITHOUT ANY WARRANTY; without even the
# implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the License for more information.
#=============================================================================
# (To distribute this file outside of CMake, substitute the full
#  License text for the above reference.)

# Created by Eric Wing.
# Modifications by Alexander Neundorf

find_path(GIF_INCLUDE_DIR NAMES gif_lib.h PATHS ${CONAN_INCLUDE_DIRS_GIFLIB})
find_library(GIF_LIBRARY NAMES ${CONAN_LIBS_GIFLIB} PATHS ${CONAN_LIB_DIRS_GIFLIB})

SET(GIF_FOUND TRUE)
MESSAGE(STATUS " giflib found by conan!")
MESSAGE(STATUS ${GIF_LIBRARY})
MESSAGE(STATUS ${GIF_INCLUDE_DIR})

set(GIF_INCLUDE_DIRS ${GIF_INCLUDE_DIR})
set(GIF_LIBRARIES ${GIF_LIBRARY})

mark_as_advanced(GIF_LIBRARY GIF_INCLUDE_DIR)

set(GIF_VERSION 5)
