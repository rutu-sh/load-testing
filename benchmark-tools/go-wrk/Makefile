BENCHMARKING_SCNARIOS=60-200 60-400

setup:
	cd ../../setup/cloudlab-tools/tools/generic && \
	$(MAKE) install-go
	${CURDIR}/install.sh install

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
			DURATION=$$(echo $$scenario | cut -d '-' -f 1) \
			CONNECTIONS=$$(echo $$scenario | cut -d '-' -f 2) \
			URL=${URL}; \
		echo "Benchmarking scenario $$scenario done"; \
		mv out.txt ${CURDIR}/results/scenario-$$scenario/out.txt; \
		mv results.csv ${CURDIR}/results/scenario-$$scenario/results.csv; \
		grep "^Requests/sec:" ${CURDIR}/results/scenario-$$scenario/out.txt | awk '{print $$2}' >> ${CURDIR}/results/scenario-$$scenario/rps; \
	done

clean:
	rm -r results