from utils import add_periods, create_daily_df, summarize_with_ci


def calculate_subs_metrics(pre_processed_subs_data_df, daily_dive_numbers_df, period):
    daily_subs_data_df = create_daily_df(pre_processed_subs_data_df, "subs")
    daily_subs_data_df = add_periods(daily_subs_data_df, period)

    base_daily = daily_subs_data_df[
        ["Survey_ID", "Date", "Period", "Site"]
    ].drop_duplicates()
    metric_frames = [
        calculate_hard_coral_cover(daily_subs_data_df, daily_dive_numbers_df),
        calculate_soft_coral_cover(daily_subs_data_df, daily_dive_numbers_df),
        calculate_fresh_algae_cover(daily_subs_data_df, daily_dive_numbers_df),
        calculate_rubble_cover(daily_subs_data_df, daily_dive_numbers_df),
        calculate_bleaching(daily_subs_data_df, daily_dive_numbers_df),
    ]

    daily_results_df = base_daily.copy()
    for frame in metric_frames:
        daily_results_df = daily_results_df.merge(
            frame, on=["Survey_ID", "Date", "Period", "Site"], how="left"
        )

    coverage_columns = [
        "Hard Coral Cover",
        "Soft Coral Cover",
        "Fresh Algae Cover",
        "Rubble Cover",
        "Bleaching",
    ]
    for column in coverage_columns:
        if column in daily_results_df.columns:
            daily_results_df[column] = daily_results_df[column].fillna(0)

    value_cols = [c for c in coverage_columns if c in daily_results_df.columns]

    seasonal_summary_df = summarize_with_ci(
        daily_results_df,
        group_cols=["Period", "Site"],
        value_cols=value_cols,
    )

    return seasonal_summary_df


def calculate_hard_coral_cover(daily_subs_data_df, daily_dive_numbers_df):
    hard_coral_daily = (
        daily_subs_data_df[daily_subs_data_df["Group"].str.contains("Hard Coral")]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    hard_coral_daily["Hard Coral Cover"] = hard_coral_daily.apply(
        lambda row: (row["Total"] / daily_dive_numbers_df.loc[row["Survey_ID"]])
        / 120
        * 100,
        axis=1,
    )
    return hard_coral_daily[["Survey_ID", "Date", "Period", "Site", "Hard Coral Cover"]]


def calculate_soft_coral_cover(daily_subs_data_df, daily_dive_numbers_df):
    soft_coral_daily = (
        daily_subs_data_df[daily_subs_data_df["Group"].str.contains("Soft Coral")]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    soft_coral_daily["Soft Coral Cover"] = soft_coral_daily.apply(
        lambda row: (row["Total"] / daily_dive_numbers_df.loc[row["Survey_ID"]])
        / 120
        * 100,
        axis=1,
    )
    return soft_coral_daily[["Survey_ID", "Date", "Period", "Site", "Soft Coral Cover"]]


def calculate_fresh_algae_cover(daily_subs_data_df, daily_dive_numbers_df):
    fresh_algae_categories = ["Algae Turf", "Algae Macro", "Algae Filamentous"]
    fresh_algae_daily = (
        daily_subs_data_df[daily_subs_data_df["Group"].isin(fresh_algae_categories)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    fresh_algae_daily["Fresh Algae Cover"] = fresh_algae_daily.apply(
        lambda row: (row["Total"] / daily_dive_numbers_df.loc[row["Survey_ID"]])
        / 120
        * 100,
        axis=1,
    )
    return fresh_algae_daily[
        ["Survey_ID", "Date", "Period", "Site", "Fresh Algae Cover"]
    ]


def calculate_rubble_cover(daily_subs_data_df, daily_dive_numbers_df):
    rubble_daily = (
        daily_subs_data_df[daily_subs_data_df["Group"].str.contains("Rubble")]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    rubble_daily["Rubble Cover"] = rubble_daily.apply(
        lambda row: (row["Total"] / daily_dive_numbers_df.loc[row["Survey_ID"]])
        / 120
        * 100,
        axis=1,
    )
    return rubble_daily[["Survey_ID", "Date", "Period", "Site", "Rubble Cover"]]


def calculate_bleaching(daily_subs_data_df, daily_dive_numbers_df):
    bleaching_categories = ["Fully Bleaching", "Partially Bleaching"]
    bleaching_daily = (
        daily_subs_data_df[daily_subs_data_df["Status"].isin(bleaching_categories)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    bleaching_daily["Bleaching"] = bleaching_daily.apply(
        lambda row: (row["Total"] / daily_dive_numbers_df.loc[row["Survey_ID"]])
        / 120
        * 100,
        axis=1,
    )
    return bleaching_daily[["Survey_ID", "Date", "Period", "Site", "Bleaching"]]
