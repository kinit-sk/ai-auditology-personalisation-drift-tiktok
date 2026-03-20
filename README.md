# TikTok personalization drift study

This repository documents the data analysis workflow in six files:

- process_data_32_agents_polarizing_only.py
- process_data_US_politics_4_agents_mixed_polarity.py
- process_data_32_agents_polarizing_plus_neutral.py
- process_data_32_agents_polarizing_only.ipynb
- process_data_US_politics_4_agents_mixed_polarity.ipynb
- process_data_32_agents_polarizing_only.ipynb

## process_data_32_agents_polarizing_only.py

A command-line script that runs the full analysis pipeline end-to-end on data collected from 32 agents that are only seeded with a polarizing topic (representing maximum polarity), but interact with a neutral topic during the interaction phase. This script writes the resulting figures to disk and prints results of statistical analyses. It expects path to directory containing the raw data (data_32_agents_polarizing_only_zenodo.csv) and path to directory where figures will be saved to.

## process_data_US_politics_4_agents_mixed_polarity.py

A command-line script that runs the full analysis pipeline end-to-end on data collected from 4 agents seeded with equal polarities on US politics topic. This script writes the resulting figures to disk and prints results of statistical analyses. It expects path to directory containing the raw data (data_US_politics_4_agents_mixed_polarity_zenodo.csv) and path to directory where figures will be saved to.

## process_data_32_agents_polarizing_plus_neutral.py

A command-line script that runs the full analysis pipeline end-to-end on data collected from 32 agents which were seeded with both polarizing and neutral topic. This script writes the resulting figures to disk and prints results of statistical analyses. It expects path to directory containing the raw data (data_US_politics_4_agents_mixed_polarity_zenodo.csv) and path to directory where figures will be saved to.


## process_data_32_agents_polarizing_only.ipynb

An notebook that performs the same analysis as process_data_32_agents_polarizing_only.py.

### Run

Open the notebook in Jupyter or VS Code and execute the cells from top to bottom.

## process_data_US_politics_4_agents_mixed_polarity.ipynb

An notebook that performs the same analysis as process_data_US_politics_4_agents_mixed_polarity.py.

### Run

Open the notebook in Jupyter or VS Code and execute the cells from top to bottom.

## process_data_32_agents_polarizing_only.ipynb

An notebook that performs the same analysis as process_data_32_agents_polarizing_only.py.

### Run

Open the notebook in Jupyter or VS Code and execute the cells from top to bottom.

