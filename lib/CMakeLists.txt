#  Copyright (C) 2016 Bastille Networks
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

########################################################################
# Setup library
########################################################################
include(GrPlatform) #define LIB_SUFFIX

include_directories(${Boost_INCLUDE_DIR})
link_directories(${Boost_LIBRARY_DIRS})
list(APPEND nordic_sources
    nordic_rx_impl.cc
    bit_shifting_byte_vector.cc
    nordic_tx_impl.cc
    enhanced_shockburst_packet.cc )

set(nordic_sources "${nordic_sources}" PARENT_SCOPE)
if(NOT nordic_sources)
	MESSAGE(STATUS "No C++ sources... skipping lib/")
	return()
endif(NOT nordic_sources)

add_library(gnuradio-nordic SHARED ${nordic_sources})
target_link_libraries(gnuradio-nordic ${Boost_LIBRARIES} ${GNURADIO_ALL_LIBRARIES})
set_target_properties(gnuradio-nordic PROPERTIES DEFINE_SYMBOL "gnuradio_nordic_EXPORTS")

if(APPLE)
    set_target_properties(gnuradio-nordic PROPERTIES
        INSTALL_NAME_DIR "${CMAKE_INSTALL_PREFIX}/lib"
    )
endif(APPLE)

########################################################################
# Install built library files
########################################################################
install(TARGETS gnuradio-nordic
    LIBRARY DESTINATION lib${LIB_SUFFIX} # .so/.dylib file
    ARCHIVE DESTINATION lib${LIB_SUFFIX} # .lib file
    RUNTIME DESTINATION bin              # .dll file
)

########################################################################
# Build and register unit test
########################################################################
include(GrTest)

include_directories(${CPPUNIT_INCLUDE_DIRS})

list(APPEND test_nordic_sources
    ${CMAKE_CURRENT_SOURCE_DIR}/test_nordic.cc
    ${CMAKE_CURRENT_SOURCE_DIR}/qa_nordic.cc
)

add_executable(test-nordic ${test_nordic_sources})

target_link_libraries(
  test-nordic
  ${GNURADIO_RUNTIME_LIBRARIES}
  ${Boost_LIBRARIES}
  ${CPPUNIT_LIBRARIES}
  gnuradio-nordic
)

GR_ADD_TEST(test_nordic test-nordic)
