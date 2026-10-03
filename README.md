# MRI Metadata and Downstream Brain-Segmentation Quality

> Status: BSc group project, University of Copenhagen, 2023.

This project investigates whether metadata from structural MRI scans can be used to predict when a separate downstream brain-analysis model is likely to fail. Here, “quality” means suitability for that downstream model; the analysis identifies associations between acquisition metadata and failures, not proven causal relationships.

## Work covered

- merged anonymised scan-volume metadata with labels for brain-segmentation quality and pathology;
- explored scan settings and other metadata associated with downstream outcomes;
- cleaned and represented heterogeneous metadata, including text recorded in inconsistent formats;
- split data at patient level to reduce leakage between training and test sets;
- compared several classification approaches and evaluated them with confusion matrices, sensitivity, specificity, ROC curves, and AUC;
- used Python with pandas, scikit-learn, PyTorch, Keras, Matplotlib, and `dirty-cat` during the exploratory modelling work.

## Repository contents

- `brain_segmentation.py` — a notebook-style export containing data preparation, exploratory analysis, model experiments, and plots;
- `Bachelor_Project_in_Machine_Learning_and_data_science (4).pdf` — the accompanying project report.

## Reproducibility note

The anonymised CSV inputs referenced by the script are not included. The Python file also retains notebook-style installation and display statements, so it is preserved as an analysis artifact rather than a one-command package. Read the report for the project context and interpretation before reusing individual experiments.

## Authorship

The code header credits Rune Brix Lundsgaard Thomsen and Mehmet Ilker Ünsal. This README describes the group project and does not assign unverified individual ownership of every implementation detail.
