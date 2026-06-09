# Blackbox-Signal-Hunt
Repository containing the solution for the Blackbox Signal Hunt organised by WnCC x Quant x MOCCM
# MOCCM Quant Hackathon 2026: The Black-Box Signal Hunt
**Team:** Blackjacks  
**Placement:** 🏆 10th Place (Out of 150+ Teams)<br>
**Team Members:** Mudil Goel, Arya Patil, Rutuparn Ranade

Hosted by the **Motilal Oswal Centre for Capital Markets (MOCCM)** at IIT Bombay, in collaboration with the Quant Club and WnCC.

## Overview
This repository contains the official submission for the MOCCM Black-Box Signal Hunt 2026. The competition demanded the discovery of a complex, multi-dimensional deterministic trading signal hidden within 9.45 million rows (10 years) of intraday market data. 

We successfully cracked the "White-Box" signal and engineered an ultra-low-latency, pure NumPy backtesting engine to execute our logic. Our dual pipeline successfully parsed, processed, and evaluated a hidden 5-year dataset in under 30 seconds during the final "15-Minute Drop" phase.

We got a blended **Sharpe Ratio** of 9.57 which led us to 10th position among 150+ teams.

## Phase 1: The Quant Strategy (Signal Discovery)
**Architecture:** Regime-Regulated, Lead-Lag Statistical Arbitrage

The competition strictly prohibited Machine Learning, Neural Networks, or black-box APIs. Our alpha discovery relied on pure statistical mechanics. Instead of continuously predicting price movements, our strategy rests in cash until a highly specific, multi-asset deterministic state aligns.

Our "White-Box" mathematical logic dictates:
* **The Regime Filter:** The engine waits for a specific liquidity state. `TICKER_02` must exhibit high momentum (Volume $\ge$ 2500) while `TICKER_38` must act as a noise filter, remaining below a specific maximum return threshold. Simultaneously, the target asset (`TICKER_00`) must already be exhibiting high variance.
* **The Alpha Trigger:** Once the regime is confirmed, the engine delegates directional authority strictly to a leading indicator: `TICKER_01`.
* **Execution:** If `TICKER_01` breaks a specific return threshold at interval $T$, the engine executes a deterministic, predictive trade on `TICKER_00` for the subsequent $T+1$ interval.

## Phase 2: Ultra-Low-Latency Systems Engineering
**Tech Stack:** Python, heavily vectorized NumPy, Native I/O

To survive the automated grader and the 30-second execution ceiling on a 500MB dataset, standard Python libraries like `pandas` and `Backtrader` were abandoned. 

* **Vectorized State Tracking:** The engine utilizes C-backed `numpy` arrays, utilizing functions like `np.roll` and `np.cumsum` to simultaneously calculate `Gross_Exposure`, `Cash_Balance`, `Interval_Turnover`, and `Gross_NAV` across 94,500 intervals without a single `for` loop.
* **Native File I/O:** Bypassed `pandas.read_csv` overhead by writing custom native Python iterators that filter exclusively for necessary ticker constraints at the C-string level before memory allocation.
* **No Look-Ahead Bias:** Strict array shifting guarantees calculations at interval $T$ only inform position sizing for the next open interval.

## Constraint Management & Risk Modeling
The automated grading infrastructure enforced realistic institutional constraints. Our execution engine survived the forensic accounting audit through defensive positioning:

* **10 bps Transaction Friction:** We overcame the 0.10% transaction fee by utilizing wide `r_threshold` bands. We traded execution frequency for high expected mathematical value, preventing fee decay.
* **Capital Ceilings & Margin Calls:** Position sizing was strictly hardcoded to an `EXPOSURE_FRACTION` of 0.10 (10% of NAV). Leaving a 90% uninvested cash buffer mathematically prevented sub-zero margin calls and kept us strictly beneath the \$1,000,000 (Long-Only) and \$2,000,000 (Long-Short) gross exposure ceilings.
* **Flat Start / End Bounds:** Algorithmic safeguards explicitly zeroed out target shares on the final interval, guaranteeing an automatic liquidation to cash and a flat end state.

## Repository Structure
* `blackjacks_code.py`: The ultra-low-latency vectorized execution engine and strategy logic.
* `blackjacks_proof.pdf`: The mathematical proof and defense of our statistical regime discovery.
* `submissions/`: Output directory containing the mandatory timeline logs (`blackjacks_longonly_results.csv` and `blackjacks_longshort_results.csv`).

## Execution
To run the engine locally against the hackathon dataset:
```bash
python blackjacks_code.py
