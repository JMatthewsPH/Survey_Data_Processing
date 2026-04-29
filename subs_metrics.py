from utils import prepare_survey_df, summarize_with_ci


def calculate_subs_metrics(pre_processed_subs_data_df, period):
    survey_df = prepare_survey_df(pre_processed_subs_data_df, "subs", period)

    base_survey = survey_df[["Survey_ID", "Date", "Site", "Period"]].drop_duplicates()

    metric_frames = [
        calculate_hard_coral_cover(survey_df),
        calculate_soft_coral_cover(survey_df),
        calculate_fresh_algae_cover(survey_df),
        calculate_rubble_cover(survey_df),
        calculate_bleaching(survey_df),
    ]

    survey_results_df = base_survey.copy()
    for frame in metric_frames:
        survey_results_df = survey_results_df.merge(
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
        if column in survey_results_df.columns:
            survey_results_df[column] = survey_results_df[column].fillna(0)

    value_cols = [c for c in coverage_columns if c in survey_results_df.columns]

    seasonal_summary_df = summarize_with_ci(
        survey_results_df,
        group_cols=["Period", "Site"],
        value_cols=value_cols,
    )

    return seasonal_summary_df


def calculate_hard_coral_cover(survey_df):
    hard_coral_survey = (
        survey_df[survey_df["Group"].str.contains("Hard Coral")]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    hard_coral_survey["Hard Coral Cover"] = hard_coral_survey["Total"] / 120 * 100
    return hard_coral_survey[
        ["Survey_ID", "Date", "Period", "Site", "Hard Coral Cover"]
    ]


def calculate_soft_coral_cover(survey_df):
    soft_coral_survey = (
        survey_df[survey_df["Group"].str.contains("Soft Coral")]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    soft_coral_survey["Soft Coral Cover"] = soft_coral_survey["Total"] / 120 * 100
    return soft_coral_survey[
        ["Survey_ID", "Date", "Period", "Site", "Soft Coral Cover"]
    ]


def calculate_fresh_algae_cover(survey_df):
    fresh_algae_categories = ["Algae Turf", "Algae Macro", "Algae Filamentous"]
    fresh_algae_survey = (
        survey_df[survey_df["Group"].isin(fresh_algae_categories)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    fresh_algae_survey["Fresh Algae Cover"] = fresh_algae_survey["Total"] / 120 * 100
    return fresh_algae_survey[
        ["Survey_ID", "Date", "Period", "Site", "Fresh Algae Cover"]
    ]


def calculate_rubble_cover(survey_df):
    rubble_survey = (
        survey_df[survey_df["Group"].str.contains("Rubble")]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    rubble_survey["Rubble Cover"] = rubble_survey["Total"] / 120 * 100
    return rubble_survey[["Survey_ID", "Date", "Period", "Site", "Rubble Cover"]]


def calculate_bleaching(survey_df):
    bleaching_categories = ["Fully Bleaching", "Partially Bleaching"]
    bleaching_survey = (
        survey_df[survey_df["Status"].isin(bleaching_categories)]
        .groupby(["Survey_ID", "Date", "Period", "Site"])["Total"]
        .sum()
        .reset_index()
    )
    bleaching_survey["Bleaching"] = bleaching_survey["Total"] / 120 * 100
    return bleaching_survey[["Survey_ID", "Date", "Period", "Site", "Bleaching"]]
