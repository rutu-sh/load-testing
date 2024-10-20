CL_DIR=${CURDIR}/.cloudlab
TOOLS_SRC_DIR=${CURDIR}/setup/cloudlab-tools


include setup/cloudlab-tools/cloudlab_tools.mk

REMOTE_DIR?=~/load-testing
REMOTE_SUBDIR=benchmark-tools/${APP_NAME}


copy-results:
	@echo "Copying results from the cloudlab host..."
	mkdir -p ${CURDIR}/results/${APP_NAME} && \
	$(MAKE) cl-scp-from-host REMOTE_DIR=~/load-testing/benchmark-tools/${APP_NAME}/results SCP_DEST=${CURDIR}/results/${APP_NAME} && \
	echo "Results copied from the cloudlab host"