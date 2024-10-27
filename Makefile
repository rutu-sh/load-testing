CL_DIR=${CURDIR}/.cloudlab
TOOLS_SRC_DIR=${CURDIR}/setup/cloudlab-tools
BENCHMARK_URL=http://192.168.1.2
TOOL_UNDERSCORE := $(subst -,_,${TOOL})
JQ_CMD := jq -r '."${TOOL}"[] | select(.name == "${EXPERIMENT_NAME}") | .parameters[]' ${CURDIR}/experiments.json

# Cloudlab parameters
LOAD_GEN_NODE=NODE_0
SERVER_NODE=NODE_1

PARAMETERS := $(shell $(JQ_CMD))

include setup/cloudlab-tools/cloudlab_tools.mk

EXPERIMENT_DIR=${CURDIR}/experiments/${TOOL}/${EXPERIMENT_NAME}


sync-code-to-nodes:
	@echo "Syncing code to the nodes..."
	$(MAKE) cl-sync-code NODE=${LOAD_GEN_NODE} && \
	$(MAKE) cl-sync-code NODE=${SERVER_NODE} && \
	echo "Code synced to the nodes"


setup-loadgen-node:
	@echo "Setting up the load generator node..."
	$(MAKE) cl-sync-code NODE=$(LOAD_GEN_NODE) && \
	$(MAKE) cl-run-cmd NODE=$(LOAD_GEN_NODE) COMMAND="cd ${REMOTE_DIR}/load-testing && ./install.sh setup_loadgen" && \
	echo "Load generator node setup done"

setup-server-node:
	@echo "Setting up the server node..."
	$(MAKE) cl-sync-code NODE=${SERVER_NODE} && \
	$(MAKE) cl-run-cmd NODE=${SERVER_NODE} COMMAND="cd ${REMOTE_DIR}/load-testing/server/nginx && make setup" && \
	echo "Server node setup done"

setup-platform:
	@echo "Setting up the environment..."
	$(MAKE) setup-loadgen-node
	$(MAKE) setup-server-node 
	echo "Environment setup done"


copy-experiment-results:
	@echo "Copying experiment results..."
	$(MAKE) cl-scp-from-host NODE=$(LOAD_GEN_NODE) SCP_SRC=${REMOTE_DIR}/load-testing/experiments/${TOOL}/${EXPERIMENT_NAME} SCP_DEST=${CURDIR}/experiments/${TOOL}

copy-results:
	@echo "Copying results from the cloudlab host..."
	$(MAKE) cl-scp-from-host NODE=$(LOAD_GEN_NODE) SCP_SRC=${REMOTE_DIR}/load-testing/experiments SCP_DEST=${CURDIR}


perform-experiment:
	@echo "Performing experiment ${EXPERIMENT_NAME} for tool ${TOOL}..."
	mkdir -p ${EXPERIMENT_DIR} && \
	jq -r '.${TOOL}[] | select(.name == "${EXPERIMENT_NAME}")' ${CURDIR}/experiments.json > ${EXPERIMENT_DIR}/exp_metadata.json
	TOOL=${TOOL} BENCHMARK_URL=${BENCHMARK_URL} EXPERIMENT_DIR=${EXPERIMENT_DIR} ./benchmark.sh $(PARAMETERS) && \
	echo "Experiment done"

reset-server:
	@echo "Resetting the server..."
	$(MAKE) cl-run-cmd NODE=${SERVER_NODE} COMMAND="cd ${REMOTE_DIR}/load-testing/server/nginx && make clean" && \
	echo "Server reset done"


perform-experiment-remote:
	@echo "Performing experiment ${EXPERIMENT_NAME} for tool ${TOOL}... on ${LOAD_GEN_NODE}"
	$(MAKE) cl-sync-code NODE=${LOAD_GEN_NODE} 
	$(MAKE) cl-run-cmd NODE=${LOAD_GEN_NODE} COMMAND="cd ${REMOTE_DIR}/load-testing && TOOL=${TOOL} EXPERIMENT_NAME=${EXPERIMENT_NAME} make perform-experiment" 
	$(MAKE) copy-experiment-results
	$(MAKE) reset-server
	echo "Experiment done"


perform-tool-experiments-remote:
	@echo "Performing experiments for tool ${TOOL}..."
	$(MAKE) sync-code-to-nodes 
	for experiment in $(shell jq -r '.${TOOL}[] | .name' ${CURDIR}/experiments.json); do \
		$(MAKE) cl-run-cmd NODE=${LOAD_GEN_NODE} COMMAND="cd ${REMOTE_DIR}/load-testing && TOOL=${TOOL} EXPERIMENT_NAME=$$experiment make perform-experiment" \
		$(MAKE) reset-server; \
		echo "Experiment $$experiment done"; \
		echo "Waiting for 30 seconds..."; \
		sleep 30; \
	done
	$(MAKE) copy-results


install-tool:
	@echo "Installing tool...$(TOOL_UNDERSCORE)"
	./install.sh install_$(TOOL_UNDERSCORE) && \
	echo "Tool installed"	


install-tool-remote:
	@echo "Installing tool..."
	$(MAKE) cl-sync-code NODE=${LOAD_GEN_NODE} && \
	$(MAKE) cl-run-cmd NODE=${LOAD_GEN_NODE} COMMAND="cd ${REMOTE_DIR}/load-testing && TOOL=${TOOL} make install-tool" && \
	echo "Tool installed remotely"