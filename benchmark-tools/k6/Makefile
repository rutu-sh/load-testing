BENCHMARKING_SCNARIOS=30s-10 30s-20 30s-100

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
			DURATION=$$(echo $$scenario | cut -d '-' -f 1) \
			VUS=$$(echo $$scenario | cut -d '-' -f 2) \
			URL=${URL}; \
		echo "Benchmarking scenario $$scenario done"; \
		mv out.txt ${CURDIR}/results/scenario-$$scenario/out.txt; \
		mv results.csv ${CURDIR}/results/scenario-$$scenario/results.csv; \
		grep "http_reqs" ${CURDIR}/results/scenario-$$scenario/out.txt | awk '{print $$3}' | sed 's/\/s//' >> ${CURDIR}/results/scenario-$$scenario/rps; \
	done

clean:
	rm -r results