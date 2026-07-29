# Copyright (c) 2026 Samuel Gobbi (Ezpeon). Licensed under the MIT License (see LICENSE).

from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
SCF_PATH = BASE_DIR / "scf.csv"

if not SCF_PATH.exists():
    raise FileNotFoundError(
        f"'{SCF_PATH}' not found. Please download the SCF full public dataset (scf.csv) from the Berkeley SDA archive at https://sda.berkeley.edu/sdaweb/analysis/?dataset=scfcomb2022 and place it in the 'local_prep' directory."
    )


def weighted_mean(
    df: pd.DataFrame, value_col: str, weight_col: str = "WGT"
) -> pd.Series:
    return df.groupby("YEAR").apply(
        lambda g: np.average(g[value_col], weights=g[weight_col])
    )


df = pd.read_csv(SCF_PATH, low_memory=False)
df = df[
    df["YEAR"] != 1989
]  # first SCF year, uses a different data structure than later year

df["ALL_ALTERNATIVE"] = (
    df["OTHFIN"] + df["OTHNFIN"] + df["BUS"] + df["NNRESRE"] + df["VEHIC"]
)
df["TOTAL_INVESTED"] = (
    df["FIN"] + df["OTHNFIN"] + df["BUS"] + df["NNRESRE"] + df["VEHIC"]
)
df["ALT_NO_Q"] = df["OTHFIN"] + df["OTHNFIN"]
df["TOT_NO_Q"] = df["FIN"] + df["OTHNFIN"]

hh = (
    df.groupby(["YEAR", "YY1"])
    .agg(
        ALL_ALTERNATIVE=("ALL_ALTERNATIVE", "mean"),
        TOTAL_INVESTED=("TOTAL_INVESTED", "mean"),
        ALT_NO_Q=("ALT_NO_Q", "mean"),
        TOT_NO_Q=("TOT_NO_Q", "mean"),
        WGT=("WGT", "first"),
    )
    .reset_index()
)

mini_df = pd.concat(
    {
        "TOTAL_INVESTED": hh.groupby("YEAR").apply(
            lambda g: np.average(g["TOTAL_INVESTED"], weights=g["WGT"])
        ),
        "ALL_ALTERNATIVE": hh.groupby("YEAR").apply(
            lambda g: np.average(g["ALL_ALTERNATIVE"], weights=g["WGT"])
        ),
    },
    axis=1,
).sort_index()
mini_nq_df = pd.concat(
    {
        "TOTAL_INVESTED": hh.groupby("YEAR").apply(
            lambda g: np.average(g["TOT_NO_Q"], weights=g["WGT"])
        ),
        "ALL_ALTERNATIVE": hh.groupby("YEAR").apply(
            lambda g: np.average(g["ALT_NO_Q"], weights=g["WGT"])
        ),
    },
    axis=1,
).sort_index()

mini_df.to_csv(BASE_DIR / "mini_scf.csv")
mini_nq_df.to_csv(BASE_DIR / "mini_scf_nq.csv")
