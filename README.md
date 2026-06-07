# Blackbox-Signal-Hunt
Repository containing the solution for the Blackbox Signal Hunt organised by WnCC x Quant x MOCCM
# 🚧 PPE Compliance Annotation Calibration

> **🏆 Hackathon / Case Competition Achievement:** 
> **Placed 10th out of 150+ teams!**

## 📖 Project Overview
This repository contains the solution for the **Unloq AI Training Role Case Study**[cite: 1]. The project focuses on a critical aspect of the Machine Learning lifecycle: **Data Quality and Pipeline Management**. 

The task was to step into the role of a Senior Annotator on a construction-site Personal Protective Equipment (PPE) compliance project[cite: 1]. The underlying computer vision model requires high-quality, consistent bounding-box/classification data to learn effectively, making annotator alignment absolutely essential.

## ⚠️ The Challenge
The project tracks four classes per worker: **hard hat, hi-vis vest, safety glasses, and gloves**[cite: 1]. 

* **Target Inter-Annotator Agreement (IAA):** > 92%[cite: 1]
* **Current IAA:** Dropped to 78%[cite: 1]
* **Impending Deadline:** A new batch of 20,000 images is scheduled for labeling[cite: 1].

The objective was to lead a calibration round to rescue the IAA metric before the new batch is processed, preventing noisy data from poisoning the model's training set[cite: 1].

## 📂 Repository Contents (Deliverables)

This repository includes the three core deliverables required to solve the IAA bottleneck[cite: 1]:

1. **`Calibration_Document.md`** 
   * A comprehensive rulebook covering eight highly ambiguous edge cases (e.g., partial occlusions, distant workers, look-alike items, low-light conditions)[cite: 1]. 
   * It provides strict, explicit decision rules to eliminate subjective guessing among the labeling team[cite: 1].

2. **`Diagnosis_Note.md`**
   * A strategic memo addressed to the Applied AI Engineer / Project Lead[cite: 1].
   * Outlines the top three hypotheses for why the IAA degraded to 78%[cite: 1].
   * Proposes three concrete, impact-ranked process changes to stabilize team consensus[cite: 1].

3. **`Annotator_Decision_Tree.md`**
   * A MECE (Mutually Exclusive, Collectively Exhaustive) flowchart[cite: 1].
   * Guides annotators step-by-step through the visual logic required to accurately classify an item as `Present`, `Absent`, or `Skip`[cite: 1].

## 🧠 Key Data Science Concepts Demonstrated
* **Data Quality Assurance:** Understanding that "garbage in, garbage out" is the golden rule of ML. Model convergence relies entirely on consistent ground-truth labels.
* **Handling Class Ambiguity:** Differentiating between negative training data (`Absent` - the feature is visible and missing) and null data (`Skip` - the feature is occluded or out of frame).
* **Process Engineering:** Designing systematic interventions (like daily consensus syncs and pre-batch calibration gates) to manage human-in-the-loop ML pipelines.

---
*Built with a focus on robust data pipelines and model-centric AI principles.*
