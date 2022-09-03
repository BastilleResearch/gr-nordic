if(NOT PKG_CONFIG_FOUND)
    INCLUDE(FindPkgConfig)
endif()
PKG_CHECK_MODULES(PC_NORDIC nordic)

FIND_PATH(
    NORDIC_INCLUDE_DIRS
    NAMES nordic/api.h
    HINTS $ENV{NORDIC_DIR}/include
        ${PC_NORDIC_INCLUDEDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/include
          /usr/local/include
          /usr/include
)

FIND_LIBRARY(
    NORDIC_LIBRARIES
    NAMES gnuradio-nordic
    HINTS $ENV{NORDIC_DIR}/lib
        ${PC_NORDIC_LIBDIR}
    PATHS ${CMAKE_INSTALL_PREFIX}/lib
          ${CMAKE_INSTALL_PREFIX}/lib64
          /usr/local/lib
          /usr/local/lib64
          /usr/lib
          /usr/lib64
          )

include("${CMAKE_CURRENT_LIST_DIR}/nordicTarget.cmake")

INCLUDE(FindPackageHandleStandardArgs)
FIND_PACKAGE_HANDLE_STANDARD_ARGS(NORDIC DEFAULT_MSG NORDIC_LIBRARIES NORDIC_INCLUDE_DIRS)
MARK_AS_ADVANCED(NORDIC_LIBRARIES NORDIC_INCLUDE_DIRS)
