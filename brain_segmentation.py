# -*- coding: utf-8 -*-
# code writting by Rune Brix Lundsgaard Thomsen, University of Copenhagen, Rune.brix0611@gmail.com-
# and Mehmet Ilker Ünsal, University of Copenhagen
pip install dirty_cat

import torch
import torch.nn as nn
import pandas as pd
import numpy as np

from sklearn.model_selection import cross_val_score
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.utils.class_weight import compute_class_weight
from sklearn.model_selection import GridSearchCV
from sklearn import svm
from sklearn.svm import SVC

from pandas.core.construction import is_empty_data
from pandas.core.api import isnull

from sklearn import metrics 
from sklearn.metrics import accuracy_score, confusion_matrix, roc_auc_score, roc_curve
from sklearn.metrics import precision_recall_curve, auc
import matplotlib.pyplot as plt
from sklearn.metrics import make_scorer

from sklearn.decomposition import PCA

import dirty_cat

#For at se alle columns:
#pd.reset_option('display.max_rows')

#For normal igen
pd.reset_option('all')

pd_volumes = pd.read_csv("train_volumes_anonymized.csv")

pd_labels = pd.read_csv("train_labels_final_anonymized.csv")
# Merge the datasets on newID and newPatientID columns
df_BV = pd.merge(pd_labels, pd_volumes, on=['newID'])
df_BV = df_BV[df_BV["BrainSegmentation"] != 2]
df_BV = df_BV[df_BV["Pathology"] != 2]
df_BV = df_BV.drop(["Background"], axis = 1 )
df_BV

print(df_BV["newPatientID"].value_counts())
print(df_BV["BrainSegmentation"].value_counts())
print(df_BV["Pathology"].value_counts())
contingency_table2 = pd.crosstab(df_BV["BrainSegmentation"], df_BV["Pathology"])
print(contingency_table2)

df_pathology = df_BV.loc[:, ~df_BV.columns.isin(["newID", "BrainSegmentation"])]
df_BS = df_BV.loc[:, ~df_BV.columns.isin(["Pathology"])]
df_pathology = df_pathology.dropna(subset=['Pathology'])
df_BS = df_BS.dropna(subset=['BrainSegmentation'])
df_pathology = df_pathology[df_pathology["Pathology"] != 2]
df_BS = df_BS[df_BS["BrainSegmentation"] != 2]
print(df_pathology.shape)
print(df_BS.shape)

P_train_patients, P_test_patients = train_test_split(df_pathology["newPatientID"].unique(), test_size = 0.2, random_state = 42)
P_train_unique_df = df_pathology[df_pathology['newPatientID'].isin(P_train_patients)]
P_test_unique_df = df_pathology[df_pathology['newPatientID'].isin(P_test_patients)]
P_train_df = P_train_unique_df.loc[:, ~P_train_unique_df.columns.isin(["newPatientID"])]
P_test_df = P_test_unique_df.loc[:, ~P_test_unique_df.columns.isin(["newPatientID"])]
P_test_df = P_test_df.drop(["SeriesDescription"], axis = 1 )
P_train_df = P_train_df.drop(["SeriesDescription"], axis = 1 )
print(P_train_df.shape)
print(P_test_df.shape)

P_X_train = P_train_df.drop(["Pathology"], axis = 1 )
P_y_train = P_train_df["Pathology"]
P_X_test= P_test_df.drop(["Pathology"], axis = 1 )
P_y_test = P_test_df["Pathology"]
print("P_X_train " + str(P_X_train.shape))
print("P_y_train " + str(P_y_train.shape))
print("P_X_test " + str(P_X_test.shape))
print("P_y_test " + str(P_y_test.shape))

print(df_BS["BrainSegmentation"].value_counts())

print(P_test_df["Pathology"].value_counts())

"""#Randomforest for Pathology

"""

RFP = RandomForestClassifier(n_estimators=100)

RFP.fit(P_X_train, P_y_train)

RFP_y_pred = RFP.predict(P_X_test)
# Calculate and print accuracy score
RFP_accuracy = accuracy_score(P_y_test, RFP_y_pred)
print("Accuracy:", RFP_accuracy)

#perform 5-fold cross-validation
RF_cv_scores = cross_val_score(RFP, P_X_train, P_y_train, cv=5)

# print the cross-validation scores
print("Cross-validation scores:", RF_cv_scores)
print("Mean cross-validation score:", RF_cv_scores.mean())

# Calculate and print confusion matrix
RFP_tn, RFP_fp, RFP_fn, RFP_tp = confusion_matrix(P_y_test, RFP_y_pred).ravel()
print("Confusion matrix:")
print("TN:", RFP_tn, "\tFP:", RFP_fp)
print("FN:", RFP_fn, "\tTP:", RFP_tp)

# Calculate and print sensitivity and specificity
R_PLR_sensitivity = RFP_tp / (RFP_tp + RFP_fn)
R_PLR_specificity = RFP_tn / (RFP_tn + RFP_fp)
print("Sensitivity:", R_PLR_sensitivity)
print("Specificity:", R_PLR_specificity)

# Calculate and print AUC-ROC score
RFP_y_pred_prob = RFP.predict_proba(P_X_test)[:,1]
RFP_auc_roc = roc_auc_score(P_y_test, RFP_y_pred_prob)
print("AUC-ROC:", RFP_auc_roc)

# Plot ROC curve
RFP_fpr, RFP_tpr, _ = roc_curve(P_y_test , RFP_y_pred_prob)
plt.plot(RFP_fpr, RFP_tpr)
plt.plot([0, 1], [0, 1], '--')
plt.title("ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.show()

"""##LogisticRegression for Pathology"""

# Fit the model on training data
PLR = LogisticRegression(random_state=0, solver='liblinear',  max_iter=1000)
PLR.fit(P_X_train, P_y_train)

# Make predictions on validation data
PLR_y_pred = PLR.predict(P_X_test)

# Calculate and print accuracy score
PLR_accuracy = accuracy_score(P_y_test, PLR_y_pred)
print("Accuracy:", PLR_accuracy)

#perform 5-fold cross-validation
PLR_cv_scores = cross_val_score(PLR, P_X_train, P_y_train, cv=5)

# print the cross-validation scores
print("Cross-validation scores:", PLR_cv_scores)
print("Mean cross-validation score:", PLR_cv_scores.mean())

# Calculate and print confusion matrix
PLR_tn, PLR_fp, PLR_fn, PLR_tp = confusion_matrix(P_y_test, PLR_y_pred).ravel()
print("Confusion matrix:")
print("TN:", PLR_tn, "\tFP:", PLR_fp)
print("FN:", PLR_fn, "\tTP:", PLR_tp)
#use build in library for scores. 

# Calculate and print sensitivity and specificity
PLR_sensitivity = PLR_tp / (PLR_tp + PLR_fn)
PLR_specificity = PLR_tn / (PLR_tn + PLR_fp)
print("Sensitivity:", PLR_sensitivity)
print("Specificity:", PLR_specificity)

# Calculate and print AUC-ROC score
PLR_y_pred_prob = PLR.predict_proba(P_X_test)[:,1]
PLR_auc_roc = roc_auc_score(P_y_test, PLR_y_pred_prob)
print("AUC-ROC:", PLR_auc_roc)

# Plot ROC curve
PLR_fpr, PLR_tpr, _ = roc_curve(P_y_test, PLR_y_pred_prob)
plt.plot(PLR_fpr, PLR_tpr)
plt.plot([0, 1], [0, 1], '--')
plt.title("ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.show()

"""##Neural network for Pathology"""

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.regularizers import l2
from keras.optimizers import Adam
from keras.utils import to_categorical
from sklearn.metrics import accuracy_score, roc_curve, confusion_matrix
from sklearn.preprocessing import StandardScaler

# Normalize the input data
scaler = StandardScaler()
P_X_train_scaled = scaler.fit_transform(P_X_train)
P_X_test_scaled = scaler.transform(P_X_test)

# Define the neural network architecture
model = Sequential()
model.add(Dense(32, input_dim=P_X_train_scaled.shape[1], activation='relu'))
model.add(Dropout(0.5))
model.add(Dense(16, activation='relu', kernel_regularizer=l2(0.01)))
model.add(Dense(1, activation='sigmoid'))
model.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

# Train the model on the training data
model.fit(P_X_train_scaled, P_y_train, epochs=100, batch_size=32, verbose=0)

# Evaluate the model on the testing data
P_NN_y_pred_prob = model.predict(P_X_test_scaled)
P_NN_y_pred = (P_NN_y_pred_prob > 0.5).astype(int)
P_NN_accuracy = accuracy_score(P_y_test, P_NN_y_pred)
fpr, tpr, thresholds = roc_curve(P_y_test, P_NN_y_pred_prob)
tn, fp, fn, tp = confusion_matrix(P_y_test, P_NN_y_pred).ravel()
P_NN_sensitivity = tp / (tp + fn)
P_NN_specificity = tn / (tn + fp)

# Plot the ROC curve
import matplotlib.pyplot as plt
plt.plot(fpr, tpr, label='ROC Curve')
plt.plot([0, 1], [0, 1], linestyle='--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.show()

# Print the results
print("Accuracy:", P_NN_accuracy)
print("Sensitivity:", P_NN_sensitivity)
print("Specificity:", P_NN_specificity)

P_NN_auc_roc = roc_auc_score(P_y_test, P_NN_y_pred_prob)
print("AUC-ROC:", P_NN_auc_roc)

"""#BrainSegementation Classifiers

##BrainSegmentation Data seperation
"""

BS_train_patients, BS_test_patients = train_test_split(df_BS["newPatientID"].unique(), test_size = 0.2, random_state = 42)
BS_unique_train_df = df_BS[df_BS['newPatientID'].isin(BS_train_patients)]
BS_unique_test_df = df_BS[df_BS['newPatientID'].isin(BS_test_patients)]
BS_test_df = BS_unique_test_df.drop(["SeriesDescription"], axis = 1 )
BS_train_df = BS_unique_train_df.drop(["SeriesDescription"], axis = 1 )
BS_X_train = BS_train_df.drop(["BrainSegmentation"], axis = 1 )
BS_y_train = BS_train_df["BrainSegmentation"]
BS_X_test= BS_test_df.drop(["BrainSegmentation"], axis = 1 )
BS_y_test = BS_test_df["BrainSegmentation"]
BS_X_train["newPatientID"]

print(BS_test_df["BrainSegmentation"].value_counts())
print(BS_train_df["BrainSegmentation"].value_counts())
print(BS_test_df.shape)
print(BS_train_df.shape)

"""###Randomforest for BrainSegmentation"""

bsrf = RandomForestClassifier(n_estimators=100)

bsrf.fit(BS_X_train, BS_y_train)

BS_y_predRF = bsrf.predict(BS_X_test)
# Calculate and print accuracy score
BS_RF_accuracy = accuracy_score(BS_y_test, BS_y_predRF)
print("Accuracy:", BS_RF_accuracy)

#perform 5-fold cross-validation
BS_RF_cv_scores = cross_val_score(bsrf, BS_X_train, BS_y_train, cv=5)

# print the cross-validation scores
print("Cross-validation scores:", BS_RF_cv_scores)
print("Mean cross-validation score:", BS_RF_cv_scores.mean())

# Calculate and print confusion matrix
BS_RF_tn, BS_RF_fp, BS_RF_fn, BS_RF_tp = confusion_matrix(BS_y_test, BS_y_predRF).ravel()
print("Confusion matrix:")
print("TN:", BS_RF_tn, "\tFP:", BS_RF_fp)
print("FN:", BS_RF_fn, "\tTP:", BS_RF_tp)

# Calculate and print sensitivity and specificity
BS_RF_sensitivity = BS_RF_tp / (BS_RF_tp + BS_RF_fn)
BS_RF_specificity = BS_RF_tn / (BS_RF_tn + BS_RF_fp)
print("Sensitivity:", BS_RF_sensitivity)
print("Specificity:", BS_RF_specificity)

# Calculate and print AUC-ROC score
BS_RF_y_pred_prob = bsrf.predict_proba(BS_X_test)[:,1]
BS_RF_auc_roc = roc_auc_score(BS_y_test, BS_RF_y_pred_prob)
print("AUC-ROC:", BS_RF_auc_roc)

# compute the PR-AUC score
BS_RF_precision, BS_RF_recall, _ = precision_recall_curve(BS_y_test, BS_RF_y_pred_prob)
BS_RF_auc_pr = auc(BS_RF_recall, BS_RF_precision)
print(f"BS_RF PR-AUC: {BS_RF_auc_pr}")

# plot the precision-recall curve
plt.plot(BS_RF_recall, BS_RF_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {BS_RF_auc_pr:.2f})')
plt.show()

# Plot ROC curve
BS_RF_fpr, BS_RF_tpr, _ = roc_curve(BS_y_test , BS_RF_y_pred_prob)
plt.plot(BS_RF_fpr, BS_RF_tpr)
plt.plot([0, 1], [0, 1], '--')
plt.title("ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.show()

"""## XGBoost for BrainSegmentation"""

import xgboost as xgb
import pandas as pd
from xgboost import plot_importance
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score


# train the XGBoost model with class balance
xgb_classifier = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, random_state=42)
xgb_classifier.fit(BS_X_train, BS_y_train)

# make predictions on the test set
y_pred = xgb_classifier.predict(BS_X_test)

# compute the accuracy score
XGB_accuracy = accuracy_score(BS_y_test, y_pred)
print(f"Accuracy: {XGB_accuracy}")

# compute the cross-validation scores
cv_scores = cross_val_score(xgb_classifier, BS_X_train, BS_y_train, cv=5)
print("Cross-validation scores:")
print(cv_scores)
print(f"Mean cross-validation score: {cv_scores.mean()}")

# compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(BS_y_test, y_pred).ravel()
print("Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# compute the sensitivity and specificity
XGB_sensitivity = tp / (tp + fn)
XGB_specificity = tn / (tn + fp)
print(f"Sensitivity: {XGB_sensitivity}")
print(f"Specificity: {XGB_specificity}")

# compute the AUC-ROC score
y_pred_prob = xgb_classifier.predict_proba(BS_X_test)[:, 1]
XGB_auc_roc = roc_auc_score(BS_y_test, y_pred_prob)
print(f"AUC-ROC: {XGB_auc_roc}")
    
# compute the PR-AUC score
XGB_precision, XGB_recall, _ = precision_recall_curve(BS_y_test, y_pred_prob)
XGB_auc_pr = auc(XGB_recall, XGB_precision)
print(f"XGBoost PR-AUC: {XGB_auc_pr}")


# plot the precision-recall curve
plt.plot(XGB_recall, XGB_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {XGB_auc_pr:.2f})')
plt.show()

# Plot ROC curve
XGB_fpr, XGB_tpr, _ = roc_curve(BS_y_test , y_pred_prob)
plt.plot(XGB_fpr, XGB_tpr)
plt.plot([0, 1], [0, 1], '--')
plt.title("ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.show()

"""##KNN for Brain Segmentation"""

knn_classifier = KNeighborsClassifier(n_neighbors=5)
knn_classifier.fit(BS_X_train, BS_y_train)

# make predictions on the test set
y_pred = knn_classifier.predict(BS_X_test)

# compute the accuracy score
knn_accuracy = accuracy_score(BS_y_test, y_pred)
print(f"KNN Accuracy: {knn_accuracy}")

# compute the cross-validation scores
cv_scores = cross_val_score(knn_classifier, BS_X_train, BS_y_train, cv=5)
print("KNN Cross-validation scores:")
print(cv_scores)
print(f"KNN Mean cross-validation score: {cv_scores.mean()}")
knn_std_score = cv_scores.std()
print(f"KNN standard deviation cross-validation score: {knn_std_score}")

# compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(BS_y_test, y_pred).ravel()
print("KNN Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# compute the sensitivity and specificity
knn_sensitivity = tp / (tp + fn)
knn_specificity = tn / (tn + fp)
print(f"KNN Sensitivity: {knn_sensitivity}")
print(f"KNN Specificity: {knn_specificity}")

# compute the AUC-ROC score
y_pred_prob = knn_classifier.predict_proba(BS_X_test)[:,1]
knn_auc_roc = roc_auc_score(BS_y_test, y_pred_prob)
print(f"AUC-ROC: {knn_auc_roc}")

# compute the PR-AUC score
knn_precision, knn_recall, _ = precision_recall_curve(BS_y_test, y_pred_prob)
knn_auc_pr = auc(knn_recall, knn_precision)
print(f"NN PR-AUC: {knn_auc_pr}")

# Plot ROC curve
knn_fpr, knn_tpr, _ = roc_curve(BS_y_test , y_pred_prob)
plt.plot(knn_fpr, knn_tpr)
plt.plot([0, 1], [0, 1], '--')
plt.title("ROC Curve")
plt.xlabel("False Positive Rate")
plt.ylabel("True Positive Rate")
plt.show()

# plot the precision-recall curve
plt.plot(knn_recall, knn_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {knn_auc_pr:.2f})')
plt.show()

"""##Neural network for BrainSegmentation"""

from sklearn.model_selection import KFold
# Normalize the input data
scaler = StandardScaler()
BS_X_train_scaled = scaler.fit_transform(BS_X_train)
BS_X_test_scaled = scaler.transform(BS_X_test)

# Define the neural network architecture
model_BV = Sequential()
model_BV.add(Dense(32, input_dim=BS_X_train_scaled.shape[1], activation='relu'))
model_BV.add(Dropout(0.5))
model_BV.add(Dense(16, activation='relu', kernel_regularizer=l2(0.01)))
model_BV.add(Dense(1, activation='sigmoid'))
model_BV.compile(loss='binary_crossentropy', optimizer=Adam(learning_rate=0.001), metrics=['accuracy'])

# Train the model on the training data
model_BV.fit(BS_X_train_scaled, BS_y_train, epochs=100, batch_size=32, verbose=0)

# Evaluate the model on the testing data
BS_y_pred_prob = model_BV.predict(BS_X_test_scaled)
BS_y_pred = (BS_y_pred_prob > 0.5).astype(int)
BS_NN_accuracy = accuracy_score(BS_y_test, BS_y_pred)
fpr, tpr, thresholds = roc_curve(BS_y_test, BS_y_pred_prob)
tn, fp, fn, tp = confusion_matrix(BS_y_test, BS_y_pred).ravel()
print("KNN Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")
BS_NN_sensitivity = tp / (tp + fn)
BS_NN_specificity = tn / (tn + fp)

# compute the PR-AUC score
BS_NN_precision, BS_NN_recall, _ = precision_recall_curve(BS_y_test, BS_y_pred_prob)
BS_NN_auc_pr = auc(BS_NN_recall, BS_NN_precision)
print(f"NN PR-AUC: {BS_NN_auc_pr}")

# Plot the ROC curve
import matplotlib.pyplot as plt
plt.plot(fpr, tpr, label='ROC Curve')
plt.plot([0, 1], [0, 1], linestyle='--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.show()

# plot the precision-recall curve
plt.plot(BS_NN_recall, BS_NN_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {BS_NN_auc_pr:.2f})')
plt.show()

# Print the results
print("Accuracy:", BS_NN_accuracy)
print("Sensitivity:", BS_NN_sensitivity)
print("Specificity:", BS_NN_specificity)

BS_NN_auc_roc = roc_auc_score(BS_y_test, BS_y_pred_prob)
print("AUC-ROC:", BS_NN_auc_roc)

df_BS_table = pd.DataFrame({"Accuracy" : [round(BS_RF_accuracy,2), round(BS_NN_accuracy,2), round(XGB_accuracy,2), round(knn_accuracy,2)], 
                   "ROC-Curve" : [round(BS_RF_auc_roc,2), round(BS_NN_auc_roc,2), round(XGB_auc_roc,2), round(knn_auc_roc,2)],
                   "PR-AUC" : [round(BS_RF_auc_pr,2), round(BS_NN_auc_pr,2), round(XGB_auc_roc,2), round(knn_auc_pr,2)],
                   "Sensitivity": [round(BS_RF_sensitivity,2), round(BS_NN_sensitivity,2), round(XGB_sensitivity,2), round(knn_sensitivity,2)],
                   "Specificity": [round(BS_RF_specificity,2), round(BS_NN_specificity,2), round(XGB_specificity,2), round(knn_specificity,2)]},
                   index= ["RandomForest", "Neural Network", "XGBoost", "KNN"] )
df_BS_table

"""#Scan parameters


"""

pd_labels = pd.read_csv("train_labels_final_anonymized.csv")
pd_labels

label_counts = pd_labels['BrainSegmentation'].value_counts()

# Display the count of each label value
print(label_counts)

pd_scans = pd.read_csv("train_scan_params_anonymized.csv")
pd_scans

print(pd_scans["newPatientID"].value_counts())

pd_volumes = pd.read_csv("train_volumes_anonymized.csv")

# Merge the datasets on newID and newPatientID columns
merged_df = pd.merge(pd_labels, pd_scans, on=['newID', "newPatientID"])
merged_df = merged_df[merged_df["BrainSegmentation"] != 2]
merged_df = merged_df[merged_df["Pathology"] != 2]
merged_df = merged_df.drop("SeriesDescription_y", axis=1)

merged_df

print(merged_df["BrainSegmentation"].value_counts())
print(merged_df["Pathology"].value_counts())

contingency_table = pd.crosstab(merged_df["BrainSegmentation"], merged_df["Pathology"])
print(contingency_table)

na_percentage = merged_df.isna().sum() / len(merged_df)
# select columns with NaN values greater than 50%
na_cols = na_percentage[na_percentage > 0.50].index.tolist()
# drop selected columns
merged_df = merged_df.drop(na_cols, axis=1)
# display the updated dataframe
print(merged_df.shape)

Klar_df = merged_df[["newID", "newPatientID", "AcquisitionDuration", "dBdt" , "EchoTime", "EchoTrainLength", "EchoNumbers", "FlipAngle", "ImagingFrequency", "MagneticFieldStrength", "RepetitionTime", "Rows", "Columns", "SliceThickness", "SpacingBetweenSlices", "RowSpacing", "ColumnSpacing", "DistanceBetweenSlices", "NumberOfSlices"]]
Ikkeklar_df = merged_df[["newID", "newPatientID", "SeriesDescription_x", "ImageType", "ScanningSequence", "SequenceVariant", "ScanOptions", "Sequence", "PatientPosition"]]

"""##Filling out columns with NaN values"""

dbdtmedian = Klar_df["dBdt"].median()
Klar_df["dBdt"] = Klar_df["dBdt"].fillna(dbdtmedian)

ADmean = Klar_df["AcquisitionDuration"].mean()
print(ADmean)
Klar_df["AcquisitionDuration"] = Klar_df["AcquisitionDuration"].fillna(ADmean)

SBSmedian = Klar_df["SpacingBetweenSlices"].median()
SBSmean = Klar_df["SpacingBetweenSlices"].mean()
print(SBSmedian)
print(SBSmean)
Klar_df["SpacingBetweenSlices"] = Klar_df["SpacingBetweenSlices"].fillna(SBSmedian)

ENmedian = Klar_df["EchoNumbers"].median()
ENmean = Klar_df["EchoNumbers"].mean()
print(ENmedian)
print(ENmean)
Klar_df["EchoNumbers"] = Klar_df["EchoNumbers"].fillna(ENmedian)

DBSmedian = Klar_df["DistanceBetweenSlices"].median()
DBSmean = Klar_df["DistanceBetweenSlices"].mean()
print(DBSmedian)
print(DBSmean)
Klar_df["DistanceBetweenSlices"] = Klar_df["DistanceBetweenSlices"].fillna(DBSmedian)

print(Klar_df.isna().any())

Klar_df
Klar_df.shape

Klar_df_train, Klar_df_test = train_test_split(Klar_df["newPatientID"].unique(), test_size = 0.2, random_state = 42)
klar_train_unique_df = Klar_df[Klar_df['newPatientID'].isin(Klar_df_train)]
klar_test_unique_df = Klar_df[Klar_df['newPatientID'].isin(Klar_df_test)]
klar_train_df = klar_train_unique_df.loc[:, ~klar_train_unique_df.columns.isin(["newPatientID"])]
klar_test_df = klar_test_unique_df.loc[:, ~klar_test_unique_df.columns.isin(["newPatientID"])]
print(klar_train_df.shape)
print(klar_test_df.shape)

"""##Encoding string columns

"""

print(Ikkeklar_df.shape)
Ikkeklar_df
#MultilabeBinarizer::: SeriesDescription_x, ScanningSequence, SequenceVariant, ImageType, ScanOptions
#label encode:::Sequence, PatientPosition

#filling empty values in "ScanOptions"
Ikkeklar_df.loc[:, 'ScanOptions'] = Ikkeklar_df['ScanOptions'].fillna('NaN')
Ikkeklar_df.loc[:, 'ScanOptions'] = Ikkeklar_df['ScanOptions'].replace('NaN', "['NaN']")

print(Ikkeklar_df.nunique())
print(Ikkeklar_df.isna().any())

"""###Imagetype encoding"""

from sklearn.preprocessing import MultiLabelBinarizer

mlb = MultiLabelBinarizer()

encoded_labels_imagetype = mlb.fit_transform(Ikkeklar_df["ImageType"].apply(eval))
# Print the classes produced by the binarizer
print("Classes:", mlb.classes_)

# Get the classes produced by the binarizer
classes = mlb.classes_

# Create new columns for each class and add them to the dataframe
for i, cls in enumerate(classes):
    col_name = f"ImageType_{cls}"
    Ikkeklar_df.loc[:, col_name] = encoded_labels_imagetype[:, i].copy()

# Iterate over the column pairs and check if they always have the same value
for i in range(len(classes)):
    for j in range(i + 1, len(classes)):
        col1 = f"ImageType_{classes[i]}"
        col2 = f"ImageType_{classes[j]}"
        
        if col1 not in Ikkeklar_df.columns or col2 not in Ikkeklar_df.columns: 
          continue

        # Check if the columns always have the same value
        if Ikkeklar_df[col1].equals(Ikkeklar_df[col2]):
            
            # Combine the columns and name the new column after the two classes
            new_col = f"ImageType_{classes[i]}_{classes[j]}"
            Ikkeklar_df.loc[:, new_col] = Ikkeklar_df[col1]
            
            # Drop the original columns
            Ikkeklar_df.drop(columns=[col1, col2], inplace=True)

            # Insert the new class after col2 in the classes list
            col2_idx = np.where(classes == classes[j])[0][0]
            classes = np.insert(classes, col2_idx + 1, f"{classes[i]}_{classes[j]}")
            
            

image_type_cols = [col for col in Ikkeklar_df.columns if col.startswith("ImageType_")]
print("Columns starting with 'ImageType_':", image_type_cols)

"""
# Reduce dimensionality of encoded labels using PCA
pca = PCA(n_components=4)
encoded_labels_imagetype_pca = pca.fit_transform(encoded_labels_imagetype)
# Add the encoded labels as new columns in the dataframe
encoded_labels_df = pd.DataFrame(encoded_labels_imagetype_pca, columns=['ImageType_encoded_1', 'ImageType_encoded_2', 'ImageType_encoded_3', 'ImageType_encoded_4'])
Ikkeklar_df = Ikkeklar_df.reset_index(drop=True)
encoded_labels_df = encoded_labels_df.reset_index(drop=True)
Ikkeklar_df = pd.concat([Ikkeklar_df, encoded_labels_df], axis=1)
"""

"""###ScanningSequence encoding"""

print(Ikkeklar_df.nunique())

encoded_labels_SS = mlb.fit_transform(Ikkeklar_df["ScanningSequence"].apply(eval))

# Print the classes produced by the binarizer
print("Classes:", mlb.classes_)

# Get the classes produced by the binarizer
classes = mlb.classes_

# Create new columns for each class and add them to the dataframe
for i, cls in enumerate(classes):
    col_name = f"ScanningSequence_{cls}"
    Ikkeklar_df[col_name] = encoded_labels_SS[:, i]

# Iterate over the column pairs and check if they always have the same value
for i in range(len(classes)):
    for j in range(i + 1, len(classes)):
        col1 = f"ScanningSequence_{classes[i]}"
        col2 = f"ScanningSequence_{classes[j]}"
        
        if col1 not in Ikkeklar_df.columns or col2 not in Ikkeklar_df.columns: 
          continue

        # Check if the columns always have the same value
        if Ikkeklar_df[col1].equals(Ikkeklar_df[col2]):
            
            # Combine the columns and name the new column after the two classes
            new_col = f"ScanningSequence_{classes[i]}_{classes[j]}"
            Ikkeklar_df.loc[:, new_col] = Ikkeklar_df[col1]
            
            # Drop the original columns
            Ikkeklar_df.drop(columns=[col1, col2], inplace=True)

            # Insert the new class after col2 in the classes list
            col2_idx = np.where(classes == classes[j])[0][0]
            classes = np.insert(classes, col2_idx + 1, f"{classes[i]}_{classes[j]}")
            
            

ScanningSequence_cols = [col for col in Ikkeklar_df.columns if col.startswith("ScanningSequence_")]
print("Columns starting with 'ScanningSequence_':", ScanningSequence_cols)
"""
encoded_labels_SS_df = pd.DataFrame(encoded_labels_SS, columns=['ScanningSequence_encoded_1', 'ScanningSequence_encoded_2', 'ScanningSequence_encoded_3'])
Ikkeklar_df = pd.concat([Ikkeklar_df, encoded_labels_SS_df], axis=1)
"""

print(Ikkeklar_df.nunique())

"""###SequenceVariant encoding"""

# Fit and transform the SequenceVariant column
encoded_labels_SV = mlb.fit_transform(Ikkeklar_df["SequenceVariant"].apply(eval))

# Print the classes produced by the binarizer
print("Classes:", mlb.classes_)

# Get the classes produced by the binarizer
classes = mlb.classes_

# Create new columns for each class and add them to the dataframe
for i, cls in enumerate(classes):
    col_name = f"SequenceVariant_{cls}"
    Ikkeklar_df[col_name] = encoded_labels_SV[:, i]

# Iterate over the column pairs and check if they always have the same value
for i in range(len(classes)):
    for j in range(i + 1, len(classes)):
        col1 = f"SequenceVariant_{classes[i]}"
        col2 = f"SequenceVariant_{classes[j]}"
        
        if col1 not in Ikkeklar_df.columns or col2 not in Ikkeklar_df.columns: 
          continue

        # Check if the columns always have the same value
        if Ikkeklar_df[col1].equals(Ikkeklar_df[col2]):
            
            # Combine the columns and name the new column after the two classes
            new_col = f"SequenceVariant_{classes[i]}_{classes[j]}"
            Ikkeklar_df.loc[:, new_col] = Ikkeklar_df[col1]
            
            # Drop the original columns
            Ikkeklar_df.drop(columns=[col1, col2], inplace=True)

            # Insert the new class after col2 in the classes list
            col2_idx = np.where(classes == classes[j])[0][0]
            classes = np.insert(classes, col2_idx + 1, f"{classes[i]}_{classes[j]}")
            
            

SequenceVariant_cols = [col for col in Ikkeklar_df.columns if col.startswith("SequenceVariant_")]
print("Columns starting with 'SequenceVariant_':", SequenceVariant_cols)
"""
# Reduce dimensionality of encoded labels using PCA
pca = PCA(n_components=4)
encoded_labels_SV_pca = pca.fit_transform(encoded_labels_SV)

# Add the encoded labels as new columns in the dataframe
encoded_labels_df = pd.DataFrame(encoded_labels_SV_pca, columns=['SequenceVariant_encoded_1', 'SequenceVariant_encoded_2', 'SequenceVariant_encoded_3', 'SequenceVariant_encoded_4'])
Ikkeklar_df = Ikkeklar_df.reset_index(drop=True)
encoded_labels_df = encoded_labels_df.reset_index(drop=True)
Ikkeklar_df = pd.concat([Ikkeklar_df, encoded_labels_df], axis=1)
"""

"""###ScanOptions encoding"""

encoded_labels_SO = mlb.fit_transform(Ikkeklar_df["ScanOptions"].apply(eval))

# Print the classes produced by the binarizer
print("Classes:", mlb.classes_)

# Get the classes produced by the binarizer
classes = mlb.classes_

# Create new columns for each class and add them to the dataframe
for i, cls in enumerate(classes):
    col_name = f"ScanOptions_{cls}"
    Ikkeklar_df[col_name] = encoded_labels_SO[:, i]

# Iterate over the column pairs and check if they always have the same value
for i in range(len(classes)):
    for j in range(i + 1, len(classes)):
        col1 = f"ScanOptions_{classes[i]}"
        col2 = f"ScanOptions_{classes[j]}"
        
        if col1 not in Ikkeklar_df.columns or col2 not in Ikkeklar_df.columns: 
          continue

        # Check if the columns always have the same value
        if Ikkeklar_df[col1].equals(Ikkeklar_df[col2]):
            
            # Combine the columns and name the new column after the two classes
            new_col = f"ScanOptions_{classes[i]}_{classes[j]}"
            Ikkeklar_df.loc[:, new_col] = Ikkeklar_df[col1]
            
            # Drop the original columns
            Ikkeklar_df.drop(columns=[col1, col2], inplace=True)

            # Insert the new class after col2 in the classes list
            col2_idx = np.where(classes == classes[j])[0][0]
            classes = np.insert(classes, col2_idx + 1, f"{classes[i]}_{classes[j]}")
            
            

ScanOptions_cols = [col for col in Ikkeklar_df.columns if col.startswith("ScanOptions_")]
print("Columns starting with 'ScanOptions_':", ScanOptions_cols)
"""
# Reduce dimensionality of encoded labels using PCA
encoded_labels_SO_pca = pca.fit_transform(encoded_labels_SO)

# Add the encoded labels as new columns in the dataframe
encoded_labels_df = pd.DataFrame(encoded_labels_SO_pca, columns=['ScanOptions_encoded_1', 'ScanOptions_encoded_2', 'ScanOptions_encoded_3', 'ScanOptions_encoded_4'])
Ikkeklar_df = Ikkeklar_df.reset_index(drop=True)
encoded_labels_df = encoded_labels_df.reset_index(drop=True)
Ikkeklar_df = pd.concat([Ikkeklar_df, encoded_labels_df], axis=1)
"""

Ikkeklar_df

"""###SeriesDescription encoding"""

print(Ikkeklar_df["Sequence"].value_counts())

"""
# Initialize the encoder with default parameters
encoder = dirty_cat.SimilarityEncoder()

# Fit the encoder on your column
encoder.fit(Ikkeklar_df['SeriesDescription_x'].values.reshape(-1, 1))

# Encode the column
encoded_column = encoder.transform(Ikkeklar_df['SeriesDescription_x'].values.reshape(-1, 1))

# Replace the original column with the encoded one
Ikkeklar_df['SeriesDescription_x'] = encoded_column
"""

Ikkeklar_df

"""
encoded_labels_SDX = mlb.fit_transform(Ikkeklar_df["SeriesDescription_x"].apply(eval))

# Print the classes produced by the binarizer
print("Classes:", mlb.classes_)

# Reduce dimensionality of encoded labels using PCA
pca = PCA(n_components=20)
encoded_labels_SDX_pca = pca.fit_transform(encoded_labels_SDX)

# Add the encoded labels as new columns in the dataframe
encoded_labels_df = pd.DataFrame(encoded_labels_SDX_pca, columns=['SeriesDescription_encoded_1', 'SeriesDescription_encoded_2', 'SeriesDescription_encoded_3', 'SeriesDescription_encoded_4', 'SeriesDescription_encoded_5', 'SeriesDescription_encoded_6', 'SeriesDescription_encoded_7', 'SeriesDescription_encoded_8', 'SeriesDescription_encoded_9', 'SeriesDescription_encoded_10', 'SeriesDescription_encoded_11', 'SeriesDescription_encoded_12', 'SeriesDescription_encoded_13', 'SeriesDescription_encoded_14', 'SeriesDescription_encoded_15', 'SeriesDescription_encoded_16', 'SeriesDescription_encoded_17', 'SeriesDescription_encoded_18', 'SeriesDescription_encoded_19', 'SeriesDescription_encoded_20'])
Ikkeklar_df = Ikkeklar_df.reset_index(drop=True)
encoded_labels_df = encoded_labels_df.reset_index(drop=True)
Ikkeklar_df = pd.concat([Ikkeklar_df, encoded_labels_df], axis=1)
"""
import re
# Define regular expression pattern for splitting the strings
pattern = r'(\s+|\_|\-|\+)'

# Define a function to split a string using the regex pattern
def split_string(s):
    s = str(s).lower()
    return re.findall(r'\w+', re.sub(pattern, ' ', s))

Ikkeklar_df['SeriesDescription_x'] = Ikkeklar_df['SeriesDescription_x'].apply(split_string)

Ikkeklar_df['SeriesDescription_x'] = Ikkeklar_df['SeriesDescription_x'].apply(lambda x: f'{x}') 

encoded_labels_SDX = mlb.fit_transform(Ikkeklar_df["SeriesDescription_x"].apply(eval))

# Print the classes produced by the binarizer
print("Classes:", mlb.classes_)

# Get the classes produced by the binarizer
classes = mlb.classes_

# Create new columns for each class and add them to the dataframe
for i, cls in enumerate(classes):
    col_name = f"SeriesDescription_x_{cls}"
    Ikkeklar_df[col_name] = encoded_labels_SDX[:, i]

# Iterate over the column pairs and check if they always have the same value
for i in range(len(classes)):
    for j in range(i + 1, len(classes)):
        col1 = f"SeriesDescription_x_{classes[i]}"
        col2 = f"SeriesDescription_x_{classes[j]}"
        
        if col1 not in Ikkeklar_df.columns or col2 not in Ikkeklar_df.columns: 
          continue

        # Check if the columns always have the same value
        if Ikkeklar_df[col1].equals(Ikkeklar_df[col2]):
            
            # Combine the columns and name the new column after the two classes
            new_col = f"SeriesDescription_x_{classes[i]}_{classes[j]}"
            Ikkeklar_df.loc[:, new_col] = Ikkeklar_df[col1]
            
            # Drop the original columns
            Ikkeklar_df.drop(columns=[col1, col2], inplace=True)

            # Insert the new class after col2 in the classes list
            col2_idx = np.where(classes == classes[j])[0][0]
            classes = np.insert(classes, col2_idx + 1, f"{classes[i]}_{classes[j]}")
            
            

SeriesDescription_x_cols = [col for col in Ikkeklar_df.columns if col.startswith("SeriesDescription_x_")]
print("Columns starting with 'SeriesDescription_x_':", SeriesDescription_x_cols)

Ikkeklar_df.drop("SeriesDescription_x", axis=1, inplace=True)

print(Ikkeklar_df.nunique())

"""###Sequence encoding"""

from sklearn.preprocessing import LabelEncoder
# Create a LabelEncoder object
le = LabelEncoder()
# Fit and transform the "Sequence" column of the DataFrame
Ikkeklar_df['Sequence'] = le.fit_transform(Ikkeklar_df['Sequence'])

"""###PatientPosition Encoding"""

# Fit and transform the "PatientPosition" column of the DataFrame
Ikkeklar_df['PatientPosition'] = le.fit_transform(Ikkeklar_df['PatientPosition'])

Ikkeklar_df

columns_to_count = ['Sequence', 'PatientPosition', 'ImageType_DIS3D', 'ImageType_MFSPLIT', 'ImageType_M_SE_SE', 'ScanningSequence_GR', 'ScanningSequence_SE', 'ScanOptions_FS', 'ScanOptions_IR_GEMS', 'ScanOptions_NaN', 'ScanOptions_CG_PER_RG']

for column in columns_to_count:
    print(column + " value count:")
    print(Ikkeklar_df[column].value_counts())
    print()

# Get the number of rows in the DataFrame
n_rows = len(Ikkeklar_df.index)

# Calculate the threshold value for removing columns
threshold = 0.99 * n_rows

# Initialize an empty list to keep track of the columns that are deleted
deleted_columns = []

# Loop through each column in the DataFrame
for column in Ikkeklar_df.columns:

    # Get the value counts for the column
    value_counts = Ikkeklar_df[column].value_counts()

    # Check if the most common value appears in more than 99% of the rows
    if value_counts.iloc[0] >= threshold:
        
        # Delete the column from the DataFrame
        Ikkeklar_df.drop(column, axis=1, inplace=True)
        
        # Add the column name to the deleted_columns list
        deleted_columns.append(column)

# Print the list of deleted columns
print("Deleted columns:", deleted_columns)

cols_to_drop = ['ScanningSequence', 'SequenceVariant', 'ImageType', 'ScanOptions']
Ikkeklar_df.drop(cols_to_drop, axis=1, inplace=True)

"""###Merging the two Klar_df and Ikkeklar_df after encoding and removing Nan values"""

encodedmerged_df = pd.merge(Klar_df, Ikkeklar_df, on=["newID", "newPatientID"])
encodedmerged_df

"""###Mergin the new dataframe with labels"""

Finalmerged_df = pd.merge(encodedmerged_df, pd_labels, on = ["newID", "newPatientID"])
Finalmerged_df.drop('SeriesDescription', axis=1, inplace=True)
print(Finalmerged_df.shape)
Finalmerged_df

"""##Trying to evaluate feature importance"""

X = Finalmerged_df.drop(['Pathology', 'BrainSegmentation', "newID", "newPatientID"], axis=1)
y = Finalmerged_df['BrainSegmentation']
rf = RandomForestClassifier()
rf.fit(X, y)
feature_importances = pd.DataFrame(rf.feature_importances_, index=X.columns, columns=['importance']).sort_values('importance', ascending=False)
print(feature_importances)
print("X shape \n", X.shape)
print("y shape \n", y.shape)

"""##Which scan parameters are to blame when no pathology but brain segmentation fails

"""

scanmerged_df = pd.merge(Ikkeklar_df, pd_labels, on = ["newID", "newPatientID"])
scanmerged_df.drop('SeriesDescription', axis=1, inplace=True)
scanmerged_df

print(scanmerged_df.nunique())

label_counts = scanmerged_df['BrainSegmentation'].value_counts()

# Display the count of each label value
print(label_counts)

"""##Autoencoding"""

from keras.models import Model
from keras.layers import Input, Dense

# filter out the rows where Pathology = 1
df = scanmerged_df[(scanmerged_df["Pathology"] == 0)]

# separate the features and labels
X = df.drop(['Pathology', 'BrainSegmentation', 'newID', 'newPatientID'], axis=1)
y = df['BrainSegmentation']

# split the data into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Define the input layer
input_layer = Input(shape=(67,))

# Define the encoder layers
encoded_layer1 = Dense(64, activation='relu')(input_layer)
encoded_layer2 = Dense(32, activation='relu')(encoded_layer1)

# Define the decoder layers
decoded_layer1 = Dense(64, activation='relu')(encoded_layer2)
decoded_layer2 = Dense(67, activation='sigmoid')(decoded_layer1)

# Define the autoencoder model
autoencoder = Model(input_layer, decoded_layer2)

# Compile the model
autoencoder.compile(optimizer='adam', loss='mse')

# Train the model
autoencoder.fit(X_train, X_train, epochs=100, batch_size=32, validation_split=0.2)

# Extract the encoder part of the model
encoder = Model(input_layer, encoded_layer2)

# Encode the data
X_train_encoded = encoder.predict(X_train)
X_test_encoded = encoder.predict(X_test)

"""##XGBoost Baseline"""

import xgboost as xgb
import pandas as pd
from xgboost import plot_importance
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report, roc_auc_score, roc_curve

# calculate the class balance ratio
neg_class_samples = len(y_train) - sum(y_train)
pos_class_samples = sum(y_train)
class_balance_ratio = neg_class_samples / pos_class_samples

# train the XGBoost model with class balance
xgb_classifier = xgb.XGBClassifier(n_estimators=100, max_depth=3, learning_rate=0.1, scale_pos_weight=class_balance_ratio, random_state=42)
xgb_classifier.fit(X_train, y_train)

# make predictions on the test set
y_pred = xgb_classifier.predict(X_test)

# compute the accuracy score
XGB_accuracy = accuracy_score(y_test, y_pred)
print(f"Accuracy: {XGB_accuracy}")

# compute the cross-validation scores
cv_scores = cross_val_score(xgb_classifier, X, y, cv=5)
print("Cross-validation scores:")
print(cv_scores)
print(f"Mean cross-validation score: {cv_scores.mean()}")

# compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
print("Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# compute the sensitivity and specificity
XGB_sensitivity = tp / (tp + fn)
XGB_specificity = tn / (tn + fp)
print(f"Sensitivity: {XGB_sensitivity}")
print(f"Specificity: {XGB_specificity}")

# compute the AUC-ROC score
y_pred_prob = xgb_classifier.predict_proba(X_test)[:, 1]
XGB_auc_roc = roc_auc_score(y_test, y_pred_prob)
fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
print(f"AUC-ROC: {XGB_auc_roc}")

#feature importances
importance_scores = xgb_classifier.feature_importances_
feature_names = X_train.columns

# Create a dictionary of feature names and their importance scores
feature_importances = dict(zip(feature_names, importance_scores))

# Sort the feature importances by their scores in descending order
sorted_importances = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)

# Print the top 5 most important features and their scores
print("\n Top 5 most important features:")
for feature, score in sorted_importances[:5]:
    print(f"{feature}: {score}")
    
# compute the PR-AUC score
XGB_precision, XGB_recall, _ = precision_recall_curve(y_test, y_pred_prob)
XGB_auc_pr = auc(XGB_recall, XGB_precision)
print(f"XGBoost PR-AUC: {XGB_auc_pr}")

# plot the precision-recall curve
plt.plot(XGB_recall, XGB_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {XGB_auc_pr:.2f})')
plt.show()

# Plot the ROC curve
plt.plot(fpr, tpr, label='ROC Curve')
plt.plot([0, 1], [0, 1], linestyle='--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.show()

# Set the figure size and width of the bars
fig, ax = plt.subplots(figsize=(12, 6))
bar_width = 0.6

# Plot the feature importances using a vertical bar plot
plt.bar(range(len(sorted_importances)), [val[1] for val in sorted_importances], align='center', width=bar_width)
plt.xticks(range(len(sorted_importances)), [val[0] for val in sorted_importances], rotation=45, fontsize=10, ha='right')
plt.ylabel('Feature Importance Score')
plt.xlabel('Feature')
plt.title('Feature Importances')

# Adjust the spacing between the bars
plt.subplots_adjust(bottom=0.2)

plt.show()

"""##Random Forest Baseline"""

# compute the class weights
class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)

# create a Random Forest classifier and fit the model on the scaled training data
rf_classifier = RandomForestClassifier(random_state=42, class_weight=dict(enumerate(class_weights)))
rf_classifier.fit(X_train, y_train)

# make predictions on the scaled test set
y_pred = rf_classifier.predict(X_test)

# compute the accuracy score
rf_accuracy = accuracy_score(y_test, y_pred)
print(f"Random Forest Accuracy: {rf_accuracy}")

print(class_weights.shape)
print()
print(X_train.shape)
print(y_train.shape)
print(X_test.shape)
print(y_test.shape)
print(y_pred.shape)


# compute the cross-validation scores on the scaled data
cv_scores = cross_val_score(rf_classifier, X, y, cv=5)
print("Random Forest Cross-validation scores:")
print(cv_scores)
print(f"Random Forest Mean cross-validation score: {cv_scores.mean()}")

# compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
print("Random Forest Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# compute the sensitivity and specificity
rf_sensitivity = tp / (tp + fn)
rf_specificity = tn / (tn + fp)
print(f"Random Forest Sensitivity: {rf_sensitivity}")
print(f"Random Forest Specificity: {rf_specificity}")

# compute the AUC-ROC score
y_pred_prob = rf_classifier.predict_proba(X_test)[:, 1]
rf_auc_roc = roc_auc_score(y_test, y_pred_prob)
fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
print(f"Random Forest AUC-ROC: {rf_auc_roc}")

# feature importances
importance_scores = rf_classifier.feature_importances_
feature_names = X_train.columns

# Create a dictionary of feature names and their importance scores
feature_importances = dict(zip(feature_names, importance_scores))

# Sort the feature importances by their scores in descending order
sorted_importances = sorted(feature_importances.items(), key=lambda x: x[1], reverse=True)

# Print the top 5 most important features and their scores
print("\nRandom Forest Top 5 most important features:")
for feature, score in sorted_importances[:5]:
    print(f"{feature}: {score}")

# compute the PR-AUC score
rf_precision, rf_recall, _ = precision_recall_curve(y_test, y_pred_prob)
rf_auc_pr = auc(rf_recall, rf_precision)
print(f"Random Forest PR-AUC: {rf_auc_pr}")

# plot the precision-recall curve
plt.plot(rf_recall, rf_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {rf_auc_pr:.2f})')
plt.show()

# Plot the ROC curve
plt.plot(fpr, tpr, label='ROC Curve')
plt.plot([0, 1], [0, 1], linestyle='--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.show()

"""##Voting classifer (Not used)"""

# import the necessary libraries
from sklearn.ensemble import VotingClassifier

# define the ensemble model
ensemble_classifier = VotingClassifier(estimators=[('XGB', xgb_classifier), ('RF', rf_classifier)], voting='soft')

# fit the ensemble model on the scaled training data
ensemble_classifier.fit(X_train, y_train)

# make predictions on the scaled test set
y_pred = ensemble_classifier.predict(X_test)

# compute the accuracy score
ensemble_accuracy = accuracy_score(y_test, y_pred)
print(f"Ensemble Accuracy: {ensemble_accuracy}")

# compute the cross-validation scores on the scaled data
cv_scores = cross_val_score(ensemble_classifier, X, y, cv=5)
print("Ensemble Cross-validation scores:")
print(cv_scores)
print(f"Ensemble Mean cross-validation score: {cv_scores.mean()}")

# compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
print("Ensemble Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# compute the sensitivity and specificity
ensemble_sensitivity = tp / (tp + fn)
ensemble_specificity = tn / (tn + fp)
print(f"Ensemble Sensitivity: {ensemble_sensitivity}")
print(f"Ensemble Specificity: {ensemble_specificity}")

# compute the AUC-ROC score
y_pred_prob = ensemble_classifier.predict_proba(X_test)[:, 1]
ensemble_auc_roc = roc_auc_score(y_test, y_pred_prob)
print(f"Ensemble AUC-ROC: {ensemble_auc_roc}")

# compute the PR-AUC score
rf_precision, rf_recall, _ = precision_recall_curve(y_test, y_pred_prob)
rf_auc_pr = auc(rf_recall, rf_precision)
print(f"Random Forest PR-AUC: {rf_auc_pr}")

# compute the accuracy at 95% sensitivity level
fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
sensitivity_95 = tpr[np.argmin(np.abs(tpr - 0.95))] # find the sensitivity at 95% specificity level
threshold_95 = thresholds[np.argmin(np.abs(tpr - 0.95))] # find the threshold for 95% sensitivity level
y_pred_95 = [1 if x >= threshold_95 else 0 for x in y_pred_prob] # apply the threshold to the predictions
accuracy_95 = accuracy_score(y_test, y_pred_95)
print(f"Random Forest Accuracy at 95% Sensitivity: {accuracy_95}")

# compute the specificity at 95% sensitivity level
tn, fp, fn, tp = confusion_matrix(y_test, y_pred_95).ravel()
specificity_95 = tn / (tn + fp)
print(f"Random Forest Specificity at 95% Sensitivity: {specificity_95}")

df_RF_table = pd.DataFrame({"Accuracy" : [round(rf_accuracy,2)], 
                   "ROC-Curve" : [round(rf_auc_roc,2)],
                   "PR-AUC": [round(rf_auc_pr,2)],
                   "Specificity at 95% sensitivity": [round(specificity_95,2)]},
                   index= ["Random Forest"] )

df_RF_table

fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)

threshold_idx = np.argmin(np.abs(tpr - 0.95))
threshold_95 = thresholds[threshold_idx]

y_pred_95 = (y_pred_prob >= threshold_95).astype(int)
accuracy_95 = accuracy_score(y_test, y_pred_95)
specificity_95 = 1 - fpr[threshold_idx]

print(f"Accuracy at 95% sensitivity: {accuracy_95}")
print(f"Specificity at 95% sensitivity: {specificity_95}")

"""##Neural Network Baseline"""

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.regularizers import l2
from keras.optimizers import Adam
from keras.utils import to_categorical
from sklearn.metrics import accuracy_score, roc_curve, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
from sklearn.utils.class_weight import compute_class_weight
# Compute the class weights
class_weights = {i: weight for i, weight in enumerate(compute_class_weight('balanced', classes=np.unique(y_train), y=y_train))}

# Define the classification model
model = Sequential()
model.add(Dense(64, activation='relu', input_shape=(67,)))
model.add(Dropout(0.5))
model.add(Dense(1, activation='sigmoid'))

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X_train, y_train, epochs=100, batch_size=32, validation_split=0.2, class_weight=class_weights)

# Evaluate the model on the testing data
NN_y_pred_prob = model.predict(X_test)
NN_y_pred = (NN_y_pred_prob > 0.5).astype(int)
NN_accuracy = accuracy_score(y_test, NN_y_pred)
fpr, tpr, thresholds = roc_curve(y_test, NN_y_pred_prob)
tn, fp, fn, tp = confusion_matrix(y_test, NN_y_pred).ravel()
NN_sensitivity = tp / (tp + fn)
NN_specificity = tn / (tn + fp)

# Plot the ROC curve
plt.plot(fpr, tpr, label='ROC Curve')
plt.plot([0, 1], [0, 1], linestyle='--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.show()

# compute the PR-AUC score
NN_precision, NN_recall, _ = precision_recall_curve(y_test, y_pred_prob)
NN_auc_pr = auc(NN_recall, NN_precision)
print(f"NN PR-AUC: {NN_auc_pr}")

# plot the precision-recall curve
plt.plot(NN_recall, NN_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {NN_auc_pr:.2f})')
plt.show()

# Print the results
print("Accuracy:", NN_accuracy)
print("Sensitivity:", NN_sensitivity)
print("Specificity:", NN_specificity)

NN_auc_roc = roc_auc_score(y_test, NN_y_pred_prob)
print("AUC-ROC:", NN_auc_roc)
print("NN Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# Get predicted probabilities from the model
NN_y_pred_prob = model.predict(X_test)

# Create a grid of threshold values to test
thresholds = np.linspace(0, 1, 1000)

# Initialize arrays to store sensitivity and specificity values
sensitivities = np.zeros_like(thresholds)
specificities = np.zeros_like(thresholds)

# Compute sensitivity and specificity for each threshold value
for i, thresh in enumerate(thresholds):
    NN_y_pred = (NN_y_pred_prob > thresh).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, NN_y_pred).ravel()
    sensitivity = tp / (tp + fn)
    specificity = tn / (tn + fp)
    sensitivities[i] = sensitivity
    specificities[i] = specificity

# Find the threshold corresponding to 95% specificity
specificity_threshold = 0.95
closest_fpr_index = np.argmin(np.abs(specificities - specificity_threshold))
sensitivity = sensitivities[closest_fpr_index]
threshold = thresholds[closest_fpr_index]
print(f"Sensitivity at {specificity_threshold:.0%} specificity: {sensitivity:.2%}")
print(f"Threshold: {threshold:.4f}")

# Compute PR-AOC
precision, recall, _ = precision_recall_curve(y_test, NN_y_pred_prob)
pr_auc = auc(recall, precision)
print(f"PR-AOC: {pr_auc:.4f}")

# Compute ROC-AUC
roc_auc = roc_auc_score(y_test, NN_y_pred_prob)
print(f"ROC-AUC: {roc_auc:.4f}")

# Compute accuracy
NN_y_pred = (NN_y_pred_prob > threshold).astype(int)
accuracy = accuracy_score(y_test, NN_y_pred)
print(f"Accuracy: {accuracy:.4f}")

# Display size of train/test set
print(f"Size of train/test set: {X_train.shape[0]}/{X_test.shape[0]}")

# Make predictions on the training set
y_pred = model.predict(X)

# Convert predictions to binary labels
y_pred_labels = (y_pred > 0.5).astype(int)

# Create dataframes for 1 predictions and 0 predictions
df_1_predictions = df[y_pred_labels.flatten() == 1]
df_0_predictions = df[y_pred_labels.flatten() == 0]

# Compute confusion matrix
cm = confusion_matrix(y, y_pred_labels)

# Extract values from confusion matrix
TN, FP, FN, TP = cm.ravel()

# Compute accuracy
accuracy = accuracy_score(y, y_pred_labels)

# Print confusion matrix and accuracy
print("NN Confusion matrix:")
print(f"TN: {TN}\tFP: {FP}")
print(f"FN: {FN}\tTP: {TP}")
print("Accuracy:", accuracy)

""" we get an approximation of feature importance by analyzing the weights of the connections between the input layer and the first hidden layer. We take the absolute values of these weights and compute the mean along each row to obtain the feature importances."""

# Get the weights of the connections between the input layer and the first hidden layer
weights = model.layers[0].get_weights()[0]

# Compute the feature importances
feature_importances = np.abs(weights).mean(axis=1)

# Normalize the feature importances
normalized_importances = feature_importances / np.sum(feature_importances)

# Create a dataframe to display the feature importances
importance_df = pd.DataFrame({'Feature': X.columns, 'Importance': normalized_importances})

# Sort the dataframe by importance values in descending order
importance_df = importance_df.sort_values(by='Importance', ascending=False)

# Get the top 5 features
top_5_features = importance_df.head(5)['Feature']

# Print the top 5 features and their normalized importances
print(importance_df.head(5))

df_1_predictions

# Calculate the percentage of each feature that contains the same value within df_1_predictions
same_value_percentages_pred_1 = df_1_predictions[top_5_features].apply(lambda column: (column.value_counts().max() / len(column) * 100, column.value_counts().idxmax()))

# Print the percentages and corresponding values
for feature, (percentage, value) in same_value_percentages_pred_1.items():
    print(f"{feature}: {percentage}% (Value: {value})")

df_0_predictions

# Calculate the percentage of each feature that contains the same value within df_1_predictions
same_value_percentages_pred_0 = df_0_predictions[top_5_features].apply(lambda column: (column.value_counts().max() / len(column) * 100, column.value_counts().idxmax()))

# Print the percentages and corresponding values
for feature, (percentage, value) in same_value_percentages_pred_0 .items():
    print(f"{feature}: {percentage}% (Value: {value})")

# Ensure both dataframes have the same column labels
df_1_predictions.columns = df_0_predictions.columns

# List of columns to exclude
exclude_columns = ['Pathology', 'BrainSegmentation', 'newPatientID', 'newID']

# Calculate the percentage of each value within df_1_predictions, excluding the specified columns
df_1_value_percentages = df_1_predictions.drop(exclude_columns, axis=1).apply(lambda column: column.value_counts(normalize=True) * 100)

# Calculate the percentage of each value within df_0_predictions, excluding the specified columns
df_0_value_percentages = df_0_predictions.drop(exclude_columns, axis=1).apply(lambda column: column.value_counts(normalize=True) * 100)

df_value_percentage = pd.DataFrame()
for i in range(len(df_1_value_percentages.columns)):
    if df_1_value_percentages.iloc[0][i] > 70 and df_0_value_percentages.iloc[1][i] > 70:
        percentage = df_1_value_percentages.iloc[0][i] + df_0_value_percentages.iloc[1][i]
        column_header = df_1_value_percentages.columns[i]
        df_value_percentage[column_header] = [percentage]
    if df_1_value_percentages.iloc[1][i] > 70 and df_0_value_percentages.iloc[0][i] > 70:
        percentage = df_1_value_percentages.iloc[1][i] + df_0_value_percentages.iloc[0][i]
        column_header = df_1_value_percentages.columns[i]
        df_value_percentage[column_header] = [percentage]


df_value_percentage = df_value_percentage.reset_index(drop=True)    
df_value_percentage.shape

print(df_1_value_percentages.iloc[1])

df_0_value_percentages

"""##SVM Baseline"""

# train the SVM model
svm_classifier = SVC(kernel='linear', C=1.0, random_state=42, class_weight = class_weights)
svm_classifier.fit(X_train, y_train)

# make predictions on the test set
y_pred = svm_classifier.predict(X_test)

# Calculate feature importance
feature_importance = np.abs(svm_classifier.coef_[0])
normalized_importance = feature_importance / np.sum(feature_importance)

# Display feature importance
for feature_name, importance_score in zip(X_train.columns, normalized_importance):
    print(f"Feature: {feature_name}, Importance: {importance_score}")
    
# compute the accuracy score
svm_accuracy = accuracy_score(y_test, y_pred)
print(f"SVM Accuracy: {svm_accuracy}")

# compute the cross-validation scores
cv_scores = cross_val_score(svm_classifier, X, y, cv=5)
print("SVM Cross-validation scores:")
print(cv_scores)
print(f"SVM Mean cross-validation score: {cv_scores.mean()}")

# compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
print("SVM Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# compute the sensitivity and specificity
svm_sensitivity = tp / (tp + fn)
svm_specificity = tn / (tn + fp)
print(f"SVM Sensitivity: {svm_sensitivity}")
print(f"SVM Specificity: {svm_specificity}")

# compute the AUC-ROC score
y_pred_prob = svm_classifier.decision_function(X_test)
svm_auc_roc = roc_auc_score(y_test, y_pred_prob)
print(f"AUC-ROC: {svm_auc_roc}")

# compute the PR-AUC score
svm_precision, svm_recall, _ = precision_recall_curve(y_test, y_pred_prob)
svm_auc_pr = auc(svm_recall, svm_precision)
print(f"svm PR-AUC: {svm_auc_pr}")

# plot the precision-recall curve
plt.plot(svm_recall, svm_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {svm_auc_pr:.2f})')
plt.show()

df_baseline_table = pd.DataFrame({"Accuracy" : [round(XGB_accuracy,2), round(rf_accuracy,2), round(NN_accuracy,2), round(svm_accuracy,2)], 
                   "ROC-Curve" : [round(XGB_auc_roc,2),round(rf_auc_roc,2), round(NN_auc_roc,2), round(svm_auc_roc,2)],
                   "Sensitivity": [round(XGB_sensitivity,2),round(rf_sensitivity,2), round(NN_sensitivity,2), round(svm_sensitivity,2)],
                   "Specificity": [round(XGB_specificity,2),round(rf_specificity,2), round(NN_specificity,2), round(svm_specificity,2)]},
                   index= ["XGBoost", "Random Forest", "Neural Network", "SVM"] )
df_baseline_table

from sklearn.inspection import permutation_importance
knn_classifier = KNeighborsClassifier(n_neighbors=5)
knn_classifier.fit(X_train, y_train)

# Make predictions on the test set
y_pred = knn_classifier.predict(X_test)

# compute the accuracy score
knn_accuracy = accuracy_score(y_test, y_pred)
print(f"KNN Accuracy: {knn_accuracy}")

# Calculate feature importance
result = permutation_importance(knn_classifier, X_test, y_test, n_repeats=10, random_state=42)

# Get feature importance scores
importance_scores = result.importances_mean

# Sort the features based on importance scores
sorted_indices = np.argsort(importance_scores)[::-1]
sorted_features = X_test.columns[sorted_indices]

# Print feature importance scores
for feature, importance_score in zip(sorted_features, importance_scores[sorted_indices]):
    print(f"{feature}: {importance_score}")

# compute the cross-validation scores
cv_scores = cross_val_score(knn_classifier, X, y, cv=5)
print("KNN Cross-validation scores:")
print(cv_scores)
print(f"KNN Mean cross-validation score: {cv_scores.mean()}")
knn_std_score = cv_scores.std()
print(f"KNN standard deviation cross-validation score: {knn_std_score}")

# compute the confusion matrix
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
print("KNN Confusion matrix:")
print(f"TN: {tn}\tFP: {fp}\nFN: {fn}\tTP: {tp}")

# compute the sensitivity and specificity
knn_sensitivity = tp / (tp + fn)
knn_specificity = tn / (tn + fp)
print(f"KNN Sensitivity: {knn_sensitivity}")
print(f"KNN Specificity: {knn_specificity}")

# compute the AUC-ROC score
y_pred_prob = knn_classifier.predict_proba(X_test)[:,1]
knn_auc_roc = roc_auc_score(y_test, y_pred_prob)
print(f"AUC-ROC: {knn_auc_roc}")
fpr, tpr, thresholds = roc_curve(y_test, NN_y_pred_prob)

# Plot the ROC curve
plt.plot(fpr, tpr, label='ROC Curve')
plt.plot([0, 1], [0, 1], linestyle='--', label='Random Guess')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) Curve')
plt.legend()
plt.show()

# compute the PR-AUC score
knn_precision, knn_recall, _ = precision_recall_curve(y_test, y_pred_prob)
knn_auc_pr = auc(knn_recall, knn_precision)
print(f"NN PR-AUC: {knn_auc_pr}")

# plot the precision-recall curve
plt.plot(knn_recall, knn_precision, lw=2)
plt.xlabel('Recall')
plt.ylabel('Precision')
plt.ylim([0.0, 1.05])
plt.xlim([0.0, 1.0])
plt.title(f'Precision-Recall Curve (PR-AUC = {knn_auc_pr:.2f})')
plt.show()

df_knn_table = pd.DataFrame({"cross validation std" : [round(knn_std_score,2)],
                            "Accuracy" : [round(knn_accuracy,2)], 
                            "ROC-Curve" : [round(knn_auc_roc,2)],
                            "Sensitivity": [round(knn_sensitivity,2)],
                            "Specificity": [round(knn_specificity,2)]},
                            index= ["KNN"])
df_knn_table

df_total_table = pd.DataFrame({
    "Accuracy" : [round(XGB_accuracy,2), round(rf_accuracy,2), round(NN_accuracy,2), round(knn_accuracy,2)], 
    "ROC-AUC" : [round(XGB_auc_roc,2),round(rf_auc_roc,2), round(NN_auc_roc,2), round(knn_auc_roc,2)],
    "PR-AUC" : [round(XGB_auc_roc,2),round(rf_auc_pr,2), round(NN_auc_pr,2), round(knn_auc_pr,2)],
    "Sensitivity": [round(XGB_sensitivity,2),round(rf_sensitivity,2), round(NN_sensitivity,2), round(knn_sensitivity,2)],
    "Specificity": [round(XGB_specificity,2),round(rf_specificity,2), round(NN_specificity,2), round(knn_specificity,2)]
    
    },
    index= ["XGBoost", "Random Forest", "Neural Network", "KNN"] )
print(f"Total negatives are: {tn + fp} ")
print(f"Total positives are: {tp + fn} ")
df_total_table

"""Bland-Altman plot (testing)"""

# Filter out the rows where Pathology = 1
df = scanmerged_df[scanmerged_df["Pathology"] == 0].copy()

# Separate the features and labels
X = df.drop(['Pathology', 'BrainSegmentation', 'newID', 'newPatientID'], axis=1)
y = df['BrainSegmentation']

# Make predictions
predictions = model.predict(X)

# Apply threshold
binary_predictions = (predictions >= 0.5).astype(int)

# Add binary predictions to DataFrame
df.loc[:, 'Predictions'] = binary_predictions

df

# Make a copy of df_BV
df_BV_new = df_BV.copy()

# Filter out rows where Pathology is 1
df_BV_new = df_BV_new[df_BV_new["Pathology"] == 0].copy()

# Drop columns
df_BV_new = df_BV_new.drop(['Pathology', 'SeriesDescription'], axis=1)

# Add binary predictions to DataFrame
df_BV_new = df_BV_new.merge(df[['newID', 'Predictions']], on='newID', how='left')

# Remove rows where prediction is 1
df_BV_new = df_BV_new[df_BV_new['Predictions'] == 0]

df_BV_new

# Make a copy of df_BV
df_BV_origin = df_BV.copy()

# Drop columns
df_BV_origin = df_BV_origin.drop(['Pathology', 'SeriesDescription'], axis=1)

# Add binary predictions to DataFrame
df_BV_origin= df_BV_origin.merge(df[['newID', 'Predictions']], on='newID', how='left')
df_BV_origin

# Select one random scan per patient from df_BV
df_BV_sample = df_BV.groupby('newPatientID').apply(lambda x: x.sample(n=1)).reset_index(drop=True)

# Select one random scan per patient from df_BV_new
df_BV_new_sample = df_BV_new.groupby('newPatientID').apply(lambda x: x.sample(n=1)).reset_index(drop=True)

# Only include patients that have at least one scan in both datasets
common_patients = set(df_BV_sample['newPatientID']).intersection(set(df_BV_new_sample['newPatientID']))
df_BV_sample = df_BV_sample[df_BV_sample['newPatientID'].isin(common_patients)]
df_BV_new_sample = df_BV_new_sample[df_BV_new_sample['newPatientID'].isin(common_patients)]

# Calculate total brain volume for each scan in df_BV_sample
volume_columns = [col for col in df_BV_sample.columns if col not in ['newID', 'BrainSegmentation', 'newPatientID', 'Pathology']]
volumes1 = df_BV_sample[volume_columns].sum(axis=1).values

# Calculate total brain volume for each scan in df_BV_new_sample
volume_columns = [col for col in df_BV_new_sample.columns if col not in ['newID', 'BrainSegmentation', 'newPatientID', 'Predictions']]
volumes2 = df_BV_new_sample[volume_columns].sum(axis=1).values

# Calculate mean and difference of volumes
mean_volumes1 = (volumes1 + volumes2) / 2
diff_volumes1 = volumes1 - volumes2

# Calculate mean and standard deviation of differences
mean_diff1 = np.mean(diff_volumes1)
std_diff1 = np.std(diff_volumes1)

# Select one random scan per patient from df_BV_origin
df_BV_origin_sample = df_BV_origin.groupby('newPatientID').apply(lambda x: x.sample(n=1)).reset_index(drop=True)

# Only include patients that have at least one scan in both datasets
common_patients = set(df_BV_sample['newPatientID']).intersection(set(df_BV_origin_sample['newPatientID']))
df_BV_sample = df_BV_sample[df_BV_sample['newPatientID'].isin(common_patients)]
df_BV_origin_sample = df_BV_origin_sample[df_BV_origin_sample['newPatientID'].isin(common_patients)]

# Calculate total brain volume for each scan in df_BV_sample
volume_columns = [col for col in df_BV_sample.columns if col not in ['newID', 'BrainSegmentation', 'newPatientID', 'Pathology']]
volumes3 = df_BV_sample[volume_columns].sum(axis=1).values

# Calculate total brain volume for each scan in df_BV_origin_sample
volume_columns = [col for col in df_BV_origin_sample.columns if col not in ['newID', 'BrainSegmentation', 'newPatientID', 'Predictions']]
volumes4 = df_BV_origin_sample[volume_columns].sum(axis=1).values

# Calculate mean and difference of volumes
mean_volumes2 = (volumes3 + volumes4) / 2
diff_volumes2 = volumes3 - volumes4

# Calculate mean and standard deviation of differences
mean_diff2 = np.mean(diff_volumes2)
std_diff2 = np.std(diff_volumes2)

print(mean_diff1)
print(mean_diff2)
# Create Bland-Altman plot
plt.scatter(mean_volumes1, diff_volumes1, color='blue', label='Filtered brain volumes')
plt.scatter(mean_volumes2, diff_volumes2, color='red', label='Non-filtered brain volumes')
plt.axhline(mean_diff1, color='gray', linestyle='--')
plt.axhline(mean_diff1 + 1.96 * std_diff1, color='gray', linestyle='--')
plt.axhline(mean_diff1 - 1.96 * std_diff1, color='gray', linestyle='--')
plt.axhline(mean_diff2, color='black', linestyle='--')
plt.axhline(mean_diff2 + 1.96 * std_diff2, color='black', linestyle='--')
plt.axhline(mean_diff2 - 1.96 * std_diff2, color='black', linestyle='--')
plt.xlabel('Mean Volume')
plt.ylabel('Difference in Volume')
plt.title('Bland-Altman Plot')
plt.legend()
plt.show()