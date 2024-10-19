setup:
	./${CURDIR}/install.sh install

benchmark:
	echo "Benchmarking..."
	${CURDIR}/benchmark.sh -t ${THREADS} -d ${DURATION} -c ${CONNECTIONS} ${URL}
	echo "Benchmarking done"