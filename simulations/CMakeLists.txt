cmake_minimum_required( VERSION 3.6 )

PROJECT(SketchLab)

MESSAGE(STATUS "Project SketchLab2")
        
SET(CMAKE_CXX_STANDARD 17)
SET(CMAKE_BUILD_TYPE "Debug")
#SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -Wall  -g -ggdb -msse2 -mssse3 -msse4.1 -msse4.2 -mavx -mavx2 -march=native")
#SET(CMAKE_CXX_FLAGS_RELEASE "$ENV{CXXFLAGS} -O3")
SET(CMAKE_CXX_FLAGS_DEBUG "$ENV{CXXFLAGS} -O0 -g -Wnarrowing")
## -pg
### Header files
include_directories(
    ${PROJECT_SOURCE_DIR}/include
    ${PROJECT_SOURCE_DIR}/lib/
)

### Libraries
# BOB HASH
set(LIB_BOBHASH BOBHash)
aux_source_directory(${PROJECT_SOURCE_DIR}/lib/BOBHash/ BOBHASH_SRC)
add_library(${LIB_BOBHASH} STATIC ${BOBHASH_SRC})
link_directories(${BOBHASH_SRC})

# CUCKOO HASH
set(LIB_CUCKOOHASH CuckooHash)
aux_source_directory(${PROJECT_SOURCE_DIR}/lib/CuckooHash/ CUCKOOHASH_SRC)
add_library(${LIB_CUCKOOHASH} STATIC ${CUCKOOHASH_SRC})
link_directories(${BOBHASH_SRC})

# CRC32 HASH
set(LIB_CRC32 CRC32)
aux_source_directory(${PROJECT_SOURCE_DIR}/lib/CRCHash CRCHASH_SRC)
add_library(${LIB_CRC32} STATIC ${CRCHASH_SRC})
link_directories(${CRCHASH_SRC})

# HOWLOG 
set(LIB_HOWLOG HowLog)
aux_source_directory(${PROJECT_SOURCE_DIR}/lib/HowLog/ HOWLOG_SRC)
add_library(${LIB_HOWLOG} STATIC ${HOWLOG_SRC})
link_directories(${HOWLOG_SRC})

# # For Network Related
# find_package(g3logger CONFIG REQUIRED)
# include_directories(
#     ${PROJECT_SOURCE_DIR}/lib/TSP-NS/lib
# )
# link_directories(${PROJECT_SOURCE_DIR}/lib/TSP-NS/build)

# Common functions
set(LIB_COMMON Common)
aux_source_directory(${PROJECT_SOURCE_DIR}/src/Common COMMON_SRC)
add_library(${LIB_COMMON} STATIC ${COMMON_SRC})
# target_link_libraries(${LIB_COMMON} TSP_NS)
link_directories(${COMMON_SRC})


set(LIB_TBC TBC)
aux_source_directory(${PROJECT_SOURCE_DIR}/src/TBC TBC_SRC)
add_library(${LIB_TBC} STATIC ${TBC_SRC})
link_directories(${TBC_SRC})


### Executable Tests
# SET OUTPUT PATH
SET(EXECUTABLE_OUTPUT_PATH ${PROJECT_SOURCE_DIR}/bin)


set(TEST_UNIVMON test_univmon)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/UnivMon TEST_UNIVMON_SRC)
add_executable( ${TEST_UNIVMON} ${TEST_UNIVMON_SRC})
target_link_libraries(${TEST_UNIVMON} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG}) 

# set(TEST_BASIC_NETWORK test_basic_network)
# aux_source_directory(${PROJECT_SOURCE_DIR}/test/NetworkTest TEST_BASIC_NETWORK_SRC)
# add_executable( ${TEST_BASIC_NETWORK} ${TEST_BASIC_NETWORK_SRC})
# target_link_libraries(${TEST_BASIC_NETWORK} ${LIB_CMSKETCH} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG} TSP_NS skiplist  threadpool pthread g3logger) 

set(TEST_TBC_CMSKETCH test_tbc_cmsketch)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_CMSketch TEST_TBC_CMSKETCH_SRC)
add_executable( ${TEST_TBC_CMSKETCH} ${TEST_TBC_CMSKETCH_SRC})
target_link_libraries(${TEST_TBC_CMSKETCH} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG}) 

set(TEST_TBC_CUSKETCH test_tbc_cusketch)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_CUSketch TEST_TBC_CUSKETCH_SRC)
add_executable( ${TEST_TBC_CUSKETCH} ${TEST_TBC_CUSKETCH_SRC})
target_link_libraries(${TEST_TBC_CUSKETCH} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG}) 

set(TBC_HYPERLOGLOG test_tbc_hyperloglog)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_HYPERLOGLOG TBC_HYPERLOGLOG_SRC)
add_executable( ${TBC_HYPERLOGLOG} ${TBC_HYPERLOGLOG_SRC})
target_link_libraries(${TBC_HYPERLOGLOG} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})

# set(TBC_MEM_TEST test_tbc_mem_test)
# aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_MEM_TEST TBC_MEM_TEST_SRC)
# add_executable( ${TBC_MEM_TEST} ${TBC_MEM_TEST_SRC})
# target_link_libraries(${TBC_MEM_TEST} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})
set(TBC_MRAC test_tbc_mrac)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_MRAC TBC_MRAC_SRC)
add_executable( ${TBC_MRAC} ${TBC_MRAC_SRC})
target_link_libraries(${TBC_MRAC} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})


set(TBC_DISTRIBUTION test_tbc_distribution)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_DISTRIBUTION TBC_DISTRIBUTION_SRC)
add_executable( ${TBC_DISTRIBUTION} ${TBC_DISTRIBUTION_SRC})
target_link_libraries(${TBC_DISTRIBUTION} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})

set(TEST_TBC_DDOS_VICTIM test_tbc_ddos_victim)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TEST_TBC_DDOS_VICTIM TEST_TBC_DDOS_VICTIM_SRC)
add_executable( ${TEST_TBC_DDOS_VICTIM} ${TEST_TBC_DDOS_VICTIM_SRC})
target_link_libraries(${TEST_TBC_DDOS_VICTIM} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})

set(TBC_CARDINALITY test_tbc_cardinality)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_CARDINALITY TBC_CARDINALITY_SRC)
add_executable( ${TBC_CARDINALITY} ${TBC_CARDINALITY_SRC})
target_link_libraries(${TBC_CARDINALITY} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})

set(BEAUCOUP test_beaucoup)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/BEAUCOUP BEAUCOUP_SRC)
add_executable( ${BEAUCOUP} ${BEAUCOUP_SRC})
target_link_libraries(${BEAUCOUP} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})

# set(SECONDARY_HASH test_secondary_hash)
# aux_source_directory(${PROJECT_SOURCE_DIR}/test/SECONDARY_HASH SECONDARY_HASH_SRC)
# add_executable( ${SECONDARY_HASH} ${SECONDARY_HASH_SRC})
# target_link_libraries(${SECONDARY_HASH}  ${LIB_CMSKETCH} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})

set(TBC_MAX_TABLE test_tbc_max_table)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_MAX_TABLE TBC_MAX_TABLE_SRC)
add_executable( ${TBC_MAX_TABLE} ${TBC_MAX_TABLE_SRC})
target_link_libraries(${TBC_MAX_TABLE} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})
set(TBC_BLOOMFILTER test_tbc_bloomfilter)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_BLOOMFILTER TBC_BLOOMFILTER_SRC)
add_executable( ${TBC_BLOOMFILTER} ${TBC_BLOOMFILTER_SRC})
target_link_libraries(${TBC_BLOOMFILTER} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})
set(TBC_BLOOMFILTER_WO_OPTM test_tbc_bloomfilter_wo_optm)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_BLOOMFILTER_WO_OPTM TBC_BLOOMFILTER_WO_OPTM_SRC)
add_executable( ${TBC_BLOOMFILTER_WO_OPTM} ${TBC_BLOOMFILTER_WO_OPTM_SRC})
target_link_libraries(${TBC_BLOOMFILTER_WO_OPTM} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})
set(TBC_BEAUCOUP_HH test_tbc_beaucoup_hh)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_BEAUCOUP_HH TBC_BEAUCOUP_HH_SRC)
add_executable( ${TBC_BEAUCOUP_HH} ${TBC_BEAUCOUP_HH_SRC})
target_link_libraries(${TBC_BEAUCOUP_HH} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})

set(TBC_BEAUCOUP_DDOS test_tbc_beaucoup_ddos)
aux_source_directory(${PROJECT_SOURCE_DIR}/test/TBC_BEAUCOUP_DDOS TBC_BEAUCOUP_DDOS_SRC_A)
add_executable( ${TBC_BEAUCOUP_DDOS} ${TBC_BEAUCOUP_DDOS_SRC_A})
target_link_libraries(${TBC_BEAUCOUP_DDOS} ${LIB_TBC} ${LIB_BOBHASH} ${LIB_COMMON} ${LIB_HOWLOG})