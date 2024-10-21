APPS=go-wrk k6 wrk 

setup:
	cd ${CURDIR}/${APP_NAME} && \
	$(MAKE) setup

run-benchmarking-scenarios:
	cd ${CURDIR}/${APP_NAME} && \
	$(MAKE) run-benchmarking-scenarios


run-all-benchmarking-scenarios:
	for app in ${APPS}; do \
		cd ${CURDIR}/$$app && \
		$(MAKE) run-benchmarking-scenarios; \
		echo "Sleeping for 60 seconds..."; \
		sleep 60; \
	done

clean:
	for app in ${APPS}; do \
		cd ${CURDIR}/$$app && \
		$(MAKE) clean; \
	done