include Makefile.inc

################################################################################
# 							Setup & Validation
################################################################################

# Ensure that critical directories needed here are absolute paths
override PYTHON_BUILD := $(abspath $(PYTHON_BUILD))
override PYTHON_VENV  := $(abspath $(PYTHON_VENV))

# Default target that is executed when none is specified at command line
.DEFAULT_GOAL=summary

###############################################################################
# 						Helper Macros & Targets
###############################################################################
pip_install:
	@echo Installing $(PIP_PACKAGE)...
	$(PYTHON_VENV)/bin/pip install $(PIP_PACKAGE)
	
check_dir:
	@if [ ! -d "$($(DIR))" ] ; then \
		echo "Error: $(DIR) undefined or points to non-existent dir: $($(DIR))" ;\
		false ; \
	fi 

check_var:
	@if [ -z "$($(VAR))" ] ; then \
		echo "Error: You must set $(VAR) makefile variable ... " ; \
		false ; \
	fi

################################################################################
# 									Usage
################################################################################
summary:
	@echo
	@echo The main targets this Makefile provides are:
	@echo "    1. create_venv              Creates a fresh virtual environment"
	@echo "                                in $(PYTHON_VENV)"
	@echo "    2. build_venv               Runs create_env, then "
	@echo "                                install_external_packages and "
	@echo "                                install_src"
	@echo "    3. install_external_pkgs    Standalone target for performing "
	@echo "                                ONLY the second target of build_venv"
	@echo "    4. install_src              Standalone target for performing "
	@echo "                                ONLY the third target of build_venv"
	@echo "    5. test                     Run nosetests. "
	@echo 
	@echo Each of these require that you define PYTHON_BUILD and/or PYTHON_VENV
	@echo variables in Makefile.inc.  
	@echo

###############################################################################
# 							Python Build Targets
###############################################################################
build_venv: python_venv_build install_external_packages install_src
create_venv: python_venv_build

python_venv_build:
	@$(MAKE) check_dir DIR=PYTHON_BUILD
	@$(MAKE) check_var VAR=PYTHON_VENV
	@echo Creating new Python virtual env at $(PYTHON_VENV) from $(PYTHON_BUILD)
	$(PYTHON_BUILD)/bin/virtualenv --system-site-packages $(PYTHON_VENV)
	@echo Installing ipython to virtualenv... ; \
	$(PYTHON_VENV)/bin/pip install -I ipython

install_external_packages:
	@echo Now installing individual external packages ...
	$(MAKE) pip_install PIP_PACKAGE=virtualenv==1.10.1
	#$(MAKE) pip_install PIP_PACKAGE=numpy==1.8.0
	#$(MAKE) pip_install PIP_PACKAGE=scipy==0.13.0
	$(MAKE) pip_install PIP_PACKAGE=pymongo==2.7
	$(MAKE) pip_install PIP_PACKAGE=pyyaml==3.10
	$(MAKE) pip_install PIP_PACKAGE=simplejson==3.3.1
	$(MAKE) pip_install PIP_PACKAGE=Flask==0.10.1
	$(MAKE) pip_install PIP_PACKAGE=tornado==3.2
	$(MAKE) pip_install PIP_PACKAGE=redis==2.9.1
	$(MAKE) pip_install PIP_PACKAGE=suds==0.4
	
install_src:
	@$(MAKE) check_dir DIR=PYTHON_VENV
	@echo Performing $@ to python virtual environment $(PYTHON_VENV)... ; \
	$(PYTHON_VENV)/bin/python setup.py install && \
	rm -fr build dist *.egg-info
	
test:
    @echo Performing $@ in python virtual environment $(PYTHON_VENV)... ; \
    $(PYTHON_VENV)/bin/python setup.py nosetests && \
    rm -fr build dist *.egg-info