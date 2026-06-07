import time
from pathlib import Path

import numpy as np
import pandas as pd


FEE_BPS = 0.0010
LONG_ONLY_CAP = 1_000_000.0
LONG_SHORT_CAP = 2_000_000.0

# White-box signal:
# TICKER_02 and TICKER_38 define the active regime.
# Inside that regime, TICKER_01 supplies next-bar direction for TICKER_00.
LONG_ONLY_R01_THRESHOLD = 0.0016
LONG_ONLY_R00_ABS_THRESHOLD = 0.0036
LONG_ONLY_V02_THRESHOLD = 2500.0
LONG_ONLY_R38_MAX_RETURN = 0.0050
LONG_SHORT_R01_THRESHOLD = 0.0026
LONG_SHORT_R00_ABS_THRESHOLD = 0.0034
LONG_SHORT_V02_THRESHOLD = 2500.0
LONG_SHORT_R38_MAX_RETURN = 0.00425

LONG_ONLY_EXPOSURE_FRACTION = 0.10
LONG_SHORT_EXPOSURE_FRACTION = 0.10

LONG_SHORT_LONG_EXPOSURE_FRACTION = 0.10
LONG_SHORT_SHORT_EXPOSURE_FRACTION = 0.60

def load_market_data(
    csv_path: Path,
) -> tuple[pd.Index, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Return timestamps, target close, self/lead returns, and regime data."""
    usecols = ["Timestamp", "Ticker", "Close", "Volume"]
    df = pd.read_csv(csv_path, usecols=usecols)
    required = {"TICKER_00", "TICKER_01", "TICKER_02", "TICKER_38"}
    df = df[df["Ticker"].isin(required)]

    close = (
        df.pivot(index="Timestamp", columns="Ticker", values="Close")
        .sort_index()
    )
    volume = (
        df.pivot(index="Timestamp", columns="Ticker", values="Volume")
        .reindex(close.index)
    )

    missing = required.difference(close.columns).union(required.difference(volume.columns))
    if missing:
        raise ValueError(f"Input CSV is missing required tickers: {sorted(missing)}")

    px00 = close["TICKER_00"].to_numpy(dtype=np.float64)
    px01 = close["TICKER_01"].to_numpy(dtype=np.float64)
    px38 = close["TICKER_38"].to_numpy(dtype=np.float64)
    vol02 = volume["TICKER_02"].to_numpy(dtype=np.float64)

    r00 = np.empty_like(px00)
    r00[0] = np.nan
    r00[1:] = px00[1:] / px00[:-1] - 1.0

    r01 = np.empty_like(px01)
    r01[0] = np.nan
    r01[1:] = px01[1:] / px01[:-1] - 1.0

    r38 = np.empty_like(px38)
    r38[0] = np.nan
    r38[1:] = px38[1:] / px38[:-1] - 1.0

    return close.index, px00, r00, r01, vol02, r38


def run_strategy(
    timestamps: pd.Index,
    px00: np.ndarray,
    r00: np.ndarray,
    r01: np.ndarray,
    vol02: np.ndarray,
    r38: np.ndarray,
    *,
    strategy: str,
) -> pd.DataFrame:
    if strategy == "longonly":
        starting_cash = LONG_ONLY_CAP
        exposure_fraction = LONG_ONLY_EXPOSURE_FRACTION
        max_exposure = LONG_ONLY_CAP * exposure_fraction
        r_threshold = LONG_ONLY_R01_THRESHOLD
        r00_abs_threshold = LONG_ONLY_R00_ABS_THRESHOLD
        v_threshold = LONG_ONLY_V02_THRESHOLD
        r38_max = LONG_ONLY_R38_MAX_RETURN
    elif strategy == "longshort":
        starting_cash = LONG_SHORT_CAP
        exposure_fraction = LONG_SHORT_EXPOSURE_FRACTION
        max_exposure = LONG_SHORT_CAP * exposure_fraction
        r_threshold = LONG_SHORT_R01_THRESHOLD
        r00_abs_threshold = LONG_SHORT_R00_ABS_THRESHOLD
        v_threshold = LONG_SHORT_V02_THRESHOLD
        r38_max = LONG_SHORT_R38_MAX_RETURN
    else:
        raise ValueError(f"Unknown strategy: {strategy}")

    n = len(px00)
    gross_exposure = np.zeros(n, dtype=np.float64)
    cash_balance = np.zeros(n, dtype=np.float64)
    interval_turnover = np.zeros(n, dtype=np.float64)
    gross_nav = np.zeros(n, dtype=np.float64)

    cash = starting_cash
    shares = 0.0

    for i in range(n):
        price = px00[i]
        nav_before_trade = cash + shares * price

        signal = 0
        active_regime = (
            vol02[i] >= v_threshold
            and np.isfinite(r38[i])
            and r38[i] < r38_max
            and np.isfinite(r00[i])
            and abs(r00[i]) >= r00_abs_threshold
        )
        if 0 < i < n - 1 and active_regime and np.isfinite(r01[i]):
            if r01[i] >= r_threshold:
                signal = 1
            elif strategy == "longshort" and r01[i] <= -r_threshold:
                signal = -1
        
        if i == n-1:
            signal = 0
        if signal == 0:
            target_shares = 0.0
        else:
            if signal > 0:
                # Long Sizing
                fraction = LONG_ONLY_EXPOSURE_FRACTION if strategy == "longonly" else LONG_SHORT_LONG_EXPOSURE_FRACTION
                target_exposure = min(max_exposure, max(0.0, nav_before_trade) * fraction)
            else:
                # Short Sizing - Uses the heavy asymmetric fraction safely!
                target_exposure = min(max_exposure, max(0.0, nav_before_trade) * LONG_SHORT_SHORT_EXPOSURE_FRACTION)
            target_shares = signal * target_exposure / price

        delta_shares = target_shares - shares
        turnover = abs(delta_shares) * price
        cash -= delta_shares * price
        shares = target_shares

        position_value = shares * price
        gross_exposure[i] = abs(position_value)
        cash_balance[i] = cash
        interval_turnover[i] = turnover
        gross_nav[i] = cash + position_value

    return pd.DataFrame(
        {
            "Timestamp": timestamps.astype(str),
            "Gross_Exposure": gross_exposure,
            "Cash_Balance": cash_balance,
            "Interval_Turnover": interval_turnover,
            "Gross_NAV": gross_nav,
        }
    )


def grader_sharpe(df: pd.DataFrame) -> float:
    net_nav = df["Gross_NAV"] - df["Interval_Turnover"].cumsum() * FEE_BPS
    returns = net_nav.pct_change().fillna(0).replace([np.inf, -np.inf], np.nan).dropna()
    std = returns.std()
    if std == 0 or np.isnan(std):
        return 0.0
    return float((returns.mean() / std) * np.sqrt(75 * 252))


def main() -> None:

    input_file = Path("judging_out_of_sample_dataset.csv") 
    
    team_name = "blackjacks" 
    output_dir = Path("submissions")


    started = time.perf_counter()
    
    timestamps, px00, r00, r01, vol02, r38 = load_market_data(input_file)
    output_dir.mkdir(parents=True, exist_ok=True)

    for strategy in ("longonly", "longshort"):
        result = run_strategy(timestamps, px00, r00, r01, vol02, r38, strategy=strategy)
        output_path = output_dir / f"{team_name}_{strategy}_results.csv"
        result.to_csv(output_path, index=False)
        print(
            f"{strategy}: rows={len(result)} "
            f"sharpe={grader_sharpe(result):.4f} "
            f"min_cash={result['Cash_Balance'].min():.2f} "
            f"max_exposure={result['Gross_Exposure'].max():.2f} "
            f"file={output_path}"
        )

    print(f"elapsed_seconds={time.perf_counter() - started:.2f}")

if __name__ == "__main__":
    main()
