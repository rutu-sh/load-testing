URL=http://192.168.1.2
DEVICE=$(ip route get ${URL} | awk '{print $$3}' | head -n 1)

setup:
	${CURDIR}/install.sh install

benchmark:
	echo "Benchmarking..."
	BENCHMARK_URL=${URL} ${CURDIR}/benchmark.sh -z ${DURATION}s --latency-correction --disable-keepalive 
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
		grep "Requests/sec" ${CURDIR}/results/scenario-$$scenario/out.txt | awk '{print $$2}' >> ${CURDIR}/results/scenario-$$scenario/rps; \
		sleep 10; \
	done

clean:
	rm -r results