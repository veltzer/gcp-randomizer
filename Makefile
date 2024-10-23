##############
# parameters #
##############
# do you want to see the commands executed ?
DO_MKDBG:=0
# do you want dependency on the makefile itself ?
DO_ALLDEP:=1
# do you want to check the javascript code?
DO_CHECKJS:=1
# do you want to validate html?
DO_CHECKHTML:=1
# do you want to validate css?
DO_CHECKCSS:=1

########
# code #
########
ALL:=
CLEAN:=

ifeq ($(DO_CHECKJS),1)
ALL+=$(JSCHECK)
all: $(ALL)
CLEAN+=$(JSCHECK)
endif # DO_CHECKJS

ifeq ($(DO_CHECKHTML),1)
ALL+=$(HTMLCHECK)
all: $(ALL)
CLEAN+=$(HTMLCHECK)
endif # DO_CHECKHTML

ifeq ($(DO_CHECKCSS),1)
ALL+=$(CSSCHECK)
all: $(ALL)
CLEAN+=$(CSSCHECK)
endif # DO_CHECKCSS

# silent stuff
ifeq ($(DO_MKDBG),1)
Q:=
# we are not silent in this branch
else # DO_MKDBG
Q:=@
#.SILENT:
endif # DO_MKDBG

SOURCES_JS:=$(shell find static/js -type f -and -name "*.js" 2> /dev/null)
SOURCES_HTML:=$(shell find static/html -type f -and -name "*.html" 2> /dev/null)
SOURCES_CSS:=$(shell find static/css -type f -and -name "*.css" 2> /dev/null)

#########
# rules #
#########
.PHONY: all
all: $(ALL)
	@true

.PHONY: debug
debug:
	$(info doing [$@])
.PHONY: clean
clean:
	$(info doing [$@])
	$(Q)-rm -f $(CLEAN)
.PHONY: clean_hard
clean_hard:
	$(info doing [$@])
	$(Q)git clean -qffxd

############
# patterns #
############
$(JSCHECK): $(SOURCES_JS)
	$(info doing [$@])
	$(Q)pymakehelper touch_mkdir $@
$(HTMLCHECK): $(SOURCES_HTML)
	$(info doing [$@])
	$(Q)pymakehelper only_print_on_error node_modules/.bin/htmlhint $<
	$(Q)tidy -errors -q -utf8 $<
	$(Q)pymakehelper touch_mkdir $@
$(CSSCHECK): $(SOURCES_CSS)
	$(info doing [$@])
	$(Q)pymakehelper only_print_on_error node_modules/.bin/stylelint $<
	$(Q)pymakehelper touch_mkdir $@

##########
# alldep #
##########
ifeq ($(DO_ALLDEP),1)
.EXTRA_PREREQS+=$(foreach mk, ${MAKEFILE_LIST},$(abspath ${mk}))
endif # DO_ALLDEP
