BENCHMARKING_SCNARIOS=30s-10 30s-20 30s-100

ifndef URL
$(error URL is not set)
endif

setup:
	${CURDIR}/install.sh install

benchmark:
	echo "Benchmarking..."
	${CURDIR}/benchmark.sh --duration $(DURATION) --vus $(VUS) -e URL=${URL} ${CURDIR}/script.js
	echo "Benchmarking done"


run-benchmarking-scenarios:
	for scenario in ${BENCHMARKING_SCNARIOS}; do \
		mkdir -p ${CURDIR}/results/scenario-$$scenario; \
		echo "Running benchmarking scenario: $$scenario"; \
		echo "Scenario $$scenario" > ${CURDIR}/results/scenario-$$scenario/README.md; \
		$(MAKE) benchmark \
			THREADS=$$(echo $$scenario | cut -d '-' -f 1) \
			DURATION=$$(echo $$scenario | cut -d '-' -f 2) \
			CONNECTIONS=$$(echo $$scenario | cut -d '-' -f 3) \
			URL=${URL}; \
		echo "Benchmarking scenario $$scenario done"; \
		mv out.txt ${CURDIR}/results/scenario-$$scenario/out.txt; \
		mv results.csv ${CURDIR}/results/scenario-$$scenario/results.csv; \
		cat ${CURDIR}/results/scenario-$$scenario/out.txt | grep "Requests/sec" >> ${CURDIR}/results/scenario-$$scenario/rps; \
	done
