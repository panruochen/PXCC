CFLAGS          := $(COMMON_CFLAGS) -ggdb ##-O3
WD              := cl
CFLAGS          += -Wall -Wno-unused-result #-Wno-format
DEFINES         := -DSANITY_CHECK
#SRCS            := ./$(WD)/ ./$(WD)/support/ ./common/ ./$(WD)//.////support . ./././$(WD)///support//./
SRCS            := ./$(WD)/ ./$(WD)/support/ ./$(WD)//.////support . ./././$(WD)///support//./
INCS            := $(SRCS) ./common
EXCLUDE_FILES   := common/got_error.cpp
TARGET          := $(WD).exe
LIBS            := -lpthread
OBJ_DIR         := .objs-cl
SRC_EXTS        := cpp c cc
DEPENDENT_LIBS  := lib/libcommon.a
TARGET_DEPENDS  := $(WD)/precedence-matrix.h $(WD)/help.h

SCRIPTS_DIR := $(WD)/scripts

$(WD)/precedence-matrix.h: $(SCRIPTS_DIR)/c_opr.bnf $(SCRIPTS_DIR)/ssymid.cfg ./$(SCRIPTS_DIR)/bnf_parser.sh
	@echo GEN $@; if test ! -x "$(word 3,$^)" ; then chmod +x "$(word 3,$^)"; fi; \
	$(word 3,$^) -m g1_oprmx -s g1_oprset -c $(word 1,$^) $(word 2,$^) >$@ || { rm -rf $@; exit 1; }

$(WD)/help.h: $(WD)/help.txt
	@ { echo '#ifndef __HELP_H'; \
		echo '#define __HELP_H'; \
		echo 'static const char help_msg[] ='; \
		sed -e 's/^/"/' -e 's/$$/\\n"/' $<; \
		echo -e ';\n#endif'; } > $@

$(call BUILD_EXECUTABLE)
$(call CLEAN_VARS)

