# TikTok personalization drift study

This repository documents the data analysis workflow in four files:

- process_umap_paper_results_32_agents_final.py
- process_umap_paper_results_4_agents_final.py
- process_umap_paper_results_32_agents_final.ipynb
- process_umap_paper_results_4_agents_final.ipynb

## process_umap_paper_results_32_agents_final.py

A command-line script that runs the full analysis pipeline end-to-end on data collected from 32 agents seeded with given agents interest. This script writes the resulting figures to disk and prints results of statistical analyses. It expects path to directory containing the raw data (UMAP_data_32_agents_zenodo.csv) and path to directory where figures will be saved to.

## process_umap_paper_results_4_agents_final.py

A command-line script that runs the full analysis pipeline end-to-end on data collected from 4 agents seeded with equal polarities on US politics topic. This script writes the resulting figures to disk and prints results of statistical analyses. It expects path to directory containing the raw data (UMAP_data_US_politics_4_agents_zenodo.csv) and path to directory where figures will be saved to.

## process_umap_paper_results_32_agents_final.ipynb

An notebook that performs the same analysis as process_umap_paper_results_32_agents_final.py.

### Run

Open the notebook in Jupyter or VS Code and execute the cells from top to bottom.

## process_umap_paper_results_4_agents_final.ipynb

An notebook that performs the same analysis as process_umap_paper_results_32_agents_final.py.

### Run

Open the notebook in Jupyter or VS Code and execute the cells from top to bottom.
