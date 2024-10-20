BENCHMARKING_SCNARIOS=30-200 30-400

setup:
	cd ${CURDIR}/../../setup/cloudlab-tools/tools/generic && \
	$(MAKE) install-go
	./${CURDIR}/install.sh install

benchmark:
	echo "Benchmarking..."
	${CURDIR}/benchmark.sh -d ${DURATION} -c ${CONNECTIONS} ${URL}
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
