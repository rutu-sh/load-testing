APPS=go-wrk k6 wrk wrk2

generate-result-plots:
	echo "Generating result plots..." && \
	mkdir -p ${CURDIR}/plots && \
	for app in $(APPS); do \
		echo "Generating plots for app $$app"; \
		scenarios=$$(ls ../results/$$app/results/ | grep scenario); \
		for scenario in $$scenarios; do \
			echo "Generating plot for scenario $$app/$$scenario"; \
			source ${CURDIR}/.venv/bin/activate && python3 plot_results/main.py -d ../results/$$app/results/$$scenario -o ${CURDIR}/plots/$$app-$$scenario.png -t $$app; \
			echo "Plot for scenario $$app/$$scenario done"; \
		done; \
	done
	