import numpy as np
import pandas as pd
from scipy import stats


def summarize_with_ci(df, group_cols, value_cols, confidence=0.95):
    records = []
    grouped = df.groupby(group_cols)
    for keys, g in grouped:
        row = dict(zip(group_cols, keys if isinstance(keys, tuple) else (keys,)))
        for col in value_cols:
            data = pd.to_numeric(g[col], errors="coerce").dropna()
            n = data.size
            if n == 0:
                mean = sd = se = ci_low = ci_high = eb_low = eb_high = np.nan
            elif n == 1:
                mean = float(data.iloc[0])
                sd = se = ci_low = ci_high = eb_low = eb_high = np.nan
            else:
                mean = data.mean()
                sd = data.std(ddof=1)
                se = stats.sem(data, nan_policy="omit")
                tcrit = stats.t.ppf((1 + confidence) / 2.0, df=n - 1)
                margin = tcrit * se
                ci_low, ci_high = mean - margin, mean + margin
                eb_low, eb_high = mean - se, mean + se

            if not pd.isna(ci_low):
                ci_low = max(0, ci_low)
            if not pd.isna(eb_low):
                eb_low = max(0, eb_low)

            row[col] = mean
            row[f"{col}_N"] = int(n) if n == n else np.nan
            row[f"{col}_SD"] = sd
            row[f"{col}_SE"] = se
            row[f"{col}_CI_low"] = ci_low
            row[f"{col}_CI_high"] = ci_high
            row[f"{col}_EB_low"] = eb_low
            row[f"{col}_EB_high"] = eb_high
        records.append(row)

    out = pd.DataFrame.from_records(records)
    order = list(group_cols) + [c for c in out.columns if c not in group_cols]
    return out.loc[:, order]
