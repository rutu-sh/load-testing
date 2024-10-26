CL_DIR=${CURDIR}/.cloudlab
TOOLS_SRC_DIR=${CURDIR}/setup/cloudlab-tools
BENCHMARK_URL=http://192.168.1.2
JQ_CMD := jq -r '.${TOOL}[] | select(.name == "${EXPERIMENT_NAME}") | .parameters[]' experiments.json

PARAMETERS := $(shell $(JQ_CMD))

include setup/cloudlab-tools/cloudlab_tools.mk

REMOTE_DIR?=~/load-testing
REMOTE_SUBDIR=benchmark-tools/${APP_NAME}
EXPERIMENT_DIR=${CURDIR}/experiments/${TOOL}/${EXPERIMENT_NAME}


copy-results:
	@echo "Copying results from the cloudlab host..."
	mkdir -p ${CURDIR}/results/${APP_NAME} && \
	$(MAKE) cl-scp-from-host REMOTE_DIR=~/load-testing/benchmark-tools/${APP_NAME}/results SCP_DEST=${CURDIR}/results/${APP_NAME} && \
	echo "Results copied from the cloudlab host"


perform-experiment:
	@echo "Performing experiment ${EXPERIMENT_NAME} for tool ${TOOL}..."
	mkdir -p ${EXPERIMENT_DIR} && \
	jq -r '.${TOOL}[] | select(.name == "${EXPERIMENT_NAME}")' experiments.json > ${EXPERIMENT_DIR}/parameters.json
	TOOL=${TOOL} BENCHMARK_URL=${BENCHMARK_URL} EXPRIMENT_DIR=${EXPERIMENT_DIR} ./benchmark.sh $(PARAMETERS) && \
	echo "Experiment done"


install-tool:
	@echo "Installing tool..."
	./install.sh install_$(subst -,_,${TOOL}) && \
	echo "Tool installed"	