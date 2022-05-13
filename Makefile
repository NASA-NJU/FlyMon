all: generate compile
configure: configure 

export P4_PATH=${SDE}/2work_dir/FlyMon/p4src/flymon.p4

generate:
	cd p4_templates; python3 flymon_compiler.py; cd -

configure:
	mkdir -p build; cd build; ${SDE}/pkgsrc/p4-build/configure  \
			--prefix=${SDE_INSTALL}   \
			--with-tofino             \
			--with-p4c=p4c            \
			--with-bf-runtime         \
			P4_VERSION=p4-16          \
			P4_PATH=${P4_PATH}        \
			P4_NAME=flymon            \
			P4_ARCHITECTURE=tna       \
			LDFLAGS="-L${SDE_INSTALL}/lib"; cd -
compile:
	cd build; make -j4 && make install; cd -

clean:
	rm -rf build


