EXTRA_CFLAGS    := -O2
EXTRA_CFLAGS    += -Wall -Wno-unused
#DEFINES         := -DHAVE_DEBUG_CONSOLE -DHAVE_NAME_IN_TOKEN
src-y           := ./core/ ./platform/
inc-y           := ./core ./platform
TARGET_TYPE     := app
TARGET          := pxcc.exe
OBJECT_DIR      := objs
SOURCE_SUFFIXES := c cpp
TARGET_DEPENDS  := core/precedence-matrix.h

include common_Makefile

SCRIPTS_DIR := core/scripts

core/precedence-matrix.h: $(SCRIPTS_DIR)/c_opr.bnf $(SCRIPTS_DIR)/ssymid.cfg ./$(SCRIPTS_DIR)/bnf_parser.sh 
	@echo GEN $@; $(word 3,$^) -m g1_oprmx -s g1_oprset -c $(word 1,$^) $(word 2,$^) >$@ || { rm -rf $@; exit 1; }

.PHONY: run
run: all
	./Run-test
