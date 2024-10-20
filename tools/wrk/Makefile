BENCHMARKING_SCNARIOS=5-30-200 10-30-200

setup:
	./${CURDIR}/install.sh install

benchmark:
	echo "Benchmarking..."
	${CURDIR}/benchmark.sh --latency -t $(THREADS) -d $(DURATION) -c $(CONNECTIONS) ${URL}
	echo "Benchmarking done"


run-benchmarking-scenarios:
	for scenario in ${BENCHMARKING_SCNARIOS}; do \
		mkdir -p ${CURDIR}/results/scenario-$$scenario; \
		echo "Running benchmarking scenario: $$scenario"; \
		echo "Scenario $$scenario" > ${CURDIR}/results/scenario-$$scenario/README.md; \
		$(MAKE) benchmark \
			THREADS=$$(echo $$scenario | cut -d '-' -f 1) \
			CONNECTIONS=$$(echo $$scenario | cut -d '-' -f 2) \
			DURATION=$$(echo $$scenario | cut -d '-' -f 3) \
			URL=${URL}; \	
		echo "Benchmarking scenario $$scenario done"; \
		mv out.txt ${CURDIR}/results/scenario-$$scenario/out.txt; \
		mv results.csv ${CURDIR}/results/scenario-$$scenario/results.csv; \
	done
