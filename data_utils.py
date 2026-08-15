import pandas as pd
import re
from typing import Optional, Tuple

# ----------------------
# READ DATA
# ----------------------

def build_dataset_profile(df: pd.DataFrame) -> str:
    profile_sections = []

    profile_sections.append(f"Rows: {len(df)}")
    profile_sections.append(f"Columns: {len(df.columns)}")
    profile_sections.append(f"Column Name: {list(df.columns)}")

    profile_sections.append(
        "\nData Types:\n"
        + df.dtypes.to_string()
    )

    profile_sections.append(
        "\nMissing Values\n"
        + df.isnull().sum().to_string()
    )

    profile_sections.append(
        "\nUnique values per column:\n"
        + df.nunique(dropna= True).to_string()
    )
    
    profile_sections.append(
        f"\nDuplicate Rows: {df.duplicated().sum()}"
    )

    numeric_columns = df.select_dtypes(include = "number").columns

    if len(numeric_columns) > 0:
        numeric_summary = df[numeric_columns].describe().to_string()

        profile_sections.append(
            "\nNumeric summary statistics:\n"
            + numeric_summary
        )

    categorical_columns = df.select_dtypes(
        include = ["object", "category", "bool"]).columns

    for column in categorical_columns:
        cat_value_counts = df[column].value_counts(
            dropna= False
        ).head(10)

        cat_value_percentage = (
            df[column].value_counts(
                normalize = True,
                dropna= False
            )
            .mul(100)
            .round(2)
            .head(10)
        )

        category_summary = pd.DataFrame({
            "count": cat_value_counts,
            "Percentage": cat_value_percentage
        })

        profile_sections.append(
            f"\nTop values for '{column}':\n"
            + category_summary.to_string()
        )

    for column in df.columns:
        if "date" in column.lower():
            converted_dates = pd.to_datetime(
                df[column],
                errors= "coerce"
            )

            if converted_dates.notna().any():
                min_date = converted_dates.min()
                max_date = converted_dates.max()

                profile_sections.append(
                    f"\nDate range for '{column}': "
                    f"{min_date} to {max_date}"

                )

    return "\n".join(profile_sections)

    
# ----------------------
# QUERY DETECTOR
# ----------------------

def detect_query_type(question: str) -> str:
    question = question.lower().strip()
    question_tokens = set(question.split())

    # CORRELATION

    if any(word in question for word in [
        "correlation", "correlated", "relationship"
        ]):
        return "correlation"

    # MISSING VALUES

    if any(word in question for word in [
        "missing", "null", "blank", "incomplete"
        ]):
        return "missing_values"

    # PERCENTILE / QUANTILE

    if (
        "percentile" in question_tokens
        or "quartile" in question_tokens
        or "q1" in question_tokens
        or "q2" in question_tokens
        or "q3" in question_tokens
        ):
        return "percentile"

    # MEDIAN

    if "median" in question_tokens:
        return "median"

    # STANDARD DEVIATION

    if ("standard deviation" in question or "std dev" in question or "std" in question_tokens):
        return "standard_deviation"

    # VARIANCE

    if "variance" in question_tokens:
        return "variance"

    # AVERAGE

    if any(word in question_tokens for word in [
        "average", "mean"
        ]):
        return "average"

    # MAXIMUM

    if any(word in question_tokens for word in [
        "maximum", "highest", "largest", "max"]):
        return "maximum"

    # MINIMUM

    if any(word in question_tokens for word in [
        "minimum", "lowest", "smallest", "min"]):
        return "minimum"

    # SUM / TOTAL

    if is_row_count_question(question):
        return "count"

    if "sum" in question_tokens:
        return "sum"

    if "total" in question_tokens:
        return "sum"

    # COUNT

    if any(word in question for word in [
        "how many", "count", "number of"
        ]):
        return "count"

    # DISTRIBUTION

    if any(word in question for word in [
        "distribution", "frequency", "most common"
        ]):
        return "distribution"

    # RELATIONSHIP

    if any(word in question for word in [
        "correlation", "relationship", "related"
        ]):
        return "correlation"

    # NUMERIC PROFILE / MULTI-STAT ANALYSIS

    if (
        "descriptive statistics" in question
        or "statistical summary" in question
        or "numeric profile" in question
        or "numerical profile" in question
        or question.startswith("analyze ")
        or question.startswith("analyse ")
        or question.startswith("summarize ")
        or question.startswith("summarise ")
        or "analysis of" in question
        ):

        return "numeric_profile"

    # SUMMARY

    if any(word in question for word in [
        "summarize", "summary", "overview", "stand out", "stands out"
        ]):
        return "summary"


    return "general"

# ----------------------
# COLUMN NORMALIZER
# ----------------------

def normalize_text(text: str) -> str:
    # add a space between lowercase/number characters and capital letters
    text = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", " ", text)

    # replace underscores and other separators with a space
    text = re.sub(r"[^a-zA-Z0-9]+", " ", text)

    # normalize capitalization and extra spaces 
    return " ".join(text.lower().split())


def find_column_in_question(df: pd.DataFrame, question: str) -> Optional[str]:
    normalized_question = normalize_text(question)

    for column in df.columns:
        normalized_column = normalize_text(column)

        if normalized_column in normalized_question:
            return column

    return None

# -------------
# AVERAGE
# -------------

def calculate_average(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors= "coerce"
    )

    if numeric_values.notna().sum() == 0:
        return None

    return float(numeric_values.mean())

def build_average_report(df: pd.DataFrame, column: str) -> Optional[str]:
    average_value = calculate_average(df, column)

    if average_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors= "coerce"
    ).notna().sum()

    if normalize_text(column) == "sale price":
        formatted_value = f"${average_value:,.2f}"

    else:
        formatted_value = f"{average_value:,.2f}"

    return build_numeric_report(
        column = column,
        metric_label = "Average",
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label = "Pandas arithmetic mean"
    )

# -------------
# MAX
# -------------

def calculate_maximum(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors="coerce"
    )

    if numeric_values.notna().sum() == 0:
        return None

    return float(numeric_values.max())

def build_maximum_report(df: pd.DataFrame, column: str) -> Optional[str]:
    maximum_value = calculate_maximum(df, column)

    if maximum_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors="coerce"
    ).notna().sum()

    if normalize_text(column) == "sale price":
        formatted_value = f"${maximum_value:,.2f}"
    else:
        formatted_value = f"{maximum_value:,.2f}"

    return build_numeric_report(
        column = column,
        metric_label = "Maximum",
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label = "Pandas maximum"
    )


# -------------
# MIN
# -------------

def calculate_minimum(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None
    
    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    )

    if numeric_values.notna().sum() == 0:
        return None
    
    return float(numeric_values.min())

def build_minimum_report(df: pd.DataFrame, column: str) -> Optional[str]:
    minimum_value = calculate_minimum(df, column)

    if minimum_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors = "coerce"
    ).notna().sum()

    if normalize_text(column) == "sale price":
        formatted_value = f"${minimum_value:,.2f}"
    else:
        formatted_value = f"{minimum_value:,.2f}"

    return build_numeric_report(
        column = column,
        metric_label = "Minimum",
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label = "Pandas minimum"
    )

# -------------
# MEDIAN
# -------------

def calculate_median(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    )

    if numeric_values.notna().sum() == 0:
        return None

    return float(numeric_values.median())

def build_median_report(df: pd.DataFrame, column: str) -> Optional[str]:
    median_value = calculate_median(df, column)

    if median_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors="coerce"
    ).notna().sum()

    if normalize_text(column) == "sale price":
        formatted_value = f"${median_value:,.2f}"
    else:
        formatted_value = f"{median_value:,.2f}"

    return build_numeric_report(
        column = column,
        metric_label = "Median",
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label = "Pandas median"
    )

# -------------
# COUNT
# -------------

def calculate_row_count(df: pd.DataFrame) -> int:
    return len(df)

def build_row_count_report(df: pd.DataFrame) -> str:
    row_count = calculate_row_count(df)

    return f"""
    ## Executive Answer

The dataset contains **{row_count:,}** records.

## Data Evidence

- **Calculation:** Total number of rows in the dataset
- **Rows counted:** {row_count:,}

## Confidence

- **Level:** High
- **Reason:** The result was calculated directly from the uploaded dataset using Python.
""".strip()

def find_value_in_question(df: pd.DataFrame, question: str) -> Optional[Tuple[str, object]]:
    normalized_question = normalize_text(question)
    question_tokens = set(normalized_question.split())

    possible_matches = []

    for column in df.columns:
        unique_values = df[column].dropna().unique()

        for value in unique_values:
            value_text = normalize_text(str(value))

            if not value_text:
                continue

            possible_matches.append(
                (len(value_text), column, value, value_text)
            )

    # Check longer values first, such as "one family",
    # before short values such as "m".
    possible_matches.sort(reverse=True, key=lambda item: item[0])

    for _, column, value, value_text in possible_matches:
        if " " in value_text:
            if value_text in normalized_question:
                return column, value
        else:
            if value_text in question_tokens:
                return column, value

    return None

def calculate_value_count(df: pd.DataFrame, column: str, value: object) -> Optional[int]:
    if column not in df.columns:
        return None

    count = int(
        df[column].eq(value).sum()
    )

    return count

def build_value_count_report(df: pd.DataFrame, column: str, value: object) -> Optional[str]:
    count = calculate_value_count(df, column, value)

    if count is None:
        return None

    total_rows = len(df)
    percentage = (
        (count / total_rows) * 100
        if total_rows > 0
        else 0
    )

    return f"""
    ## Executive Answer

The value **{value}** appears **{count:,}** times in **{column}**.

## Data Evidence

- **Column:** {column}
- **Value counted:** {value}
- **Matching records:** {count:,}
- **Total dataset records:** {total_rows:,}
- **Share of dataset:** {percentage:.2f}%
- **Calculation:** Pandas exact-value count

## Confidence

- **Level:** High
- **Reason:** The result was calculated directly from the uploaded dataset using Python.
""".strip()


# ----------------------
# VALUE ALIAS
# ----------------------

value_aliases = {
    "malignant": "M",
    "benign": "B"
}

def find_alias_value_in_question(df: pd.DataFrame, question: str) -> Optional[Tuple[str, object]]:
    normalized_question = normalize_text(question)

    for alias, target_value in value_aliases.items():
        if alias not in normalized_question:
            continue
        
        for column in df.columns:
            unique_values = df[column].dropna().unique()

            for value in unique_values:
                if str(value).lower() == str(target_value).lower():
                    return column, value

    return None


# ----------------------
# STANDARD DEVIATION
# ----------------------

def calculate_standard_deviation(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    )

    if numeric_values.notna().sum() < 2:
        return None

    return float(numeric_values.std())

def build_standard_deviation_report(df: pd.DataFrame, column: str) -> Optional[str]:
    std_value = calculate_standard_deviation(df, column)

    if std_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors="coerce"
    ).notna().sum()

    if normalize_text(column) == "sale price":
        formatted_value = f"${std_value:,.2f}"
    else:
        formatted_value = f"{std_value:,.2f}"

    return build_numeric_report(
        column = column,
        metric_label = "Standard deviation of",
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label = "Pandas sample standard deviation"
    )


# ----------------------
# VARIANCE
# ----------------------

def calculate_variance(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    )

    if numeric_values.notna().sum() < 2:
        return None
    
    return float(numeric_values.var())

def build_variance_report(df: pd.DataFrame, column: str) -> Optional[str]:
    variance_value = calculate_variance(df, column)

    if variance_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors="coerce"
    ).notna().sum()

    formatted_value = f"{variance_value:,.2f}"

    return build_numeric_report(
        column = column,
        metric_label = "Variance of",
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label="Pandas sample variance"
    )


# ----------------------
# DISTRIBUTION
# ----------------------

def calculate_distribution(df: pd.DataFrame, column: str) -> Optional[pd.Series]:
    if column not in df.columns:
        return None
    
    valid_values = df[column].dropna()

    if len(valid_values) == 0:
        return None

    return valid_values.value_counts()

def build_distribution_report(df: pd.DataFrame, column: str, top_n: int = 10) -> Optional[str]:
    distribution = calculate_distribution(df, column)

    if distribution is None:
        return None

    valid_count = int(distribution.sum())
    unique_count = len(distribution)

    top_values = distribution.head(top_n)

    most_common_value = distribution.index[0]
    most_common_count = int(distribution.iloc[0])

    most_common_percentage = (most_common_count / valid_count) * 100

    distribution_lines = []

    for value, count in top_values.items():
        percentage = (count / valid_count) * 100

        distribution_lines.append(
            f"- **{value}:** {count:,} ({percentage:.2f}%)"
        )

    distribution_text = "\n".join(distribution_lines)

    return f"""
## Executive Answer

The **{column}** distribution contains **{unique_count:,} unique values** across **{valid_count:,} valid records**.

The most common value is **{most_common_value}**, appearing **{most_common_count:,} times** ({most_common_percentage:.2f}%).

## Distribution

{distribution_text}

## Data Evidence

- **Column:** {column}
- **Valid records evaluated:** {valid_count:,}
- **Unique values:** {unique_count:,}
- **Values displayed:** {len(top_values):,}
- **Calculation:** Pandas value counts

## Confidence

- **Level:** High
- **Reason:** The distribution was calculated directly from the uploaded dataset using Python.
""".strip()

# ------------------------
# CORRELATION FIND COLUMNS
# ------------------------

def find_columns_in_question(df: pd.DataFrame, question: str) -> list:
    normalized_question = normalize_text(question)

    matched_columns = []

    for column in df.columns:
        normalized_column = normalize_text(column)

        if normalized_column in normalized_question:
            matched_columns.append(column)

    return matched_columns


# ----------------------
# CORRELATION
# ----------------------

def calculate_correlation(df: pd.DataFrame, column_x: str, column_y: str) -> Optional[float]:
    if column_x not in df.columns or column_y not in df.columns:
        return None

    numeric_x = pd.to_numeric(
        df[column_x],
        errors = "coerce"
    ) 

    numeric_y = pd.to_numeric(
        df[column_y],
        errors = "coerce"
    )

    valid_pairs = numeric_x.notna() & numeric_y.notna()

    if valid_pairs.sum() < 2:
        return None

    correlation = numeric_x[valid_pairs].corr(
        numeric_y[valid_pairs]
    )

    if pd.isna(correlation):
        return None

    return float(correlation)

# -----------------------
# CORRELATION EXPLAINER
# -----------------------

def explain_correlation(correlation_value: float, column_x: str, column_y: str) -> str:
    if correlation_value > 0:
        return (
            f"Higher values of **{column_x}** tend to be associated "
            f"with higher values of **{column_y}**."
        )

    if correlation_value < 0:
        return (
            f"Higher values of **{column_x}** tend to be associated "
            f"with lower values of **{column_y}**."
        )

    return (
        f"No linear association was detected between "
        f"**{column_x}** and **{column_y}**."
    )


def build_correlation_report(df: pd.DataFrame, column_x: str, column_y: str) -> Optional[str]:
    correlation_value = calculate_correlation(
        df,
        column_x,
        column_y
    )

    if correlation_value is None:
        return None

    numeric_x = pd.to_numeric(
        df[column_x],
        errors="coerce"
    )

    numeric_y = pd.to_numeric(
        df[column_y],
        errors="coerce"
    )

    valid_pairs = numeric_x.notna() & numeric_y.notna()
    valid_count = int(valid_pairs.sum())

    formatted_value = f"{correlation_value:.4f}"

    interpretation = interpret_correlation(correlation_value)

    explanation = explain_correlation(correlation_value,column_x,column_y)

    return f"""
## Executive Answer

The Pearson correlation between **{column_x}** and **{column_y}** is **{formatted_value}**, indicating a **{interpretation}**. {explanation}

## Data Evidence

- **Column 1:** {column_x}
- **Column 2:** {column_y}
- **Valid paired records evaluated:** {valid_count:,}
- **Calculation:** Pandas Pearson correlation

## Confidence

- **Level:** High
- **Reason:** The correlation was calculated directly from paired numeric values in the uploaded dataset using Python.
""".strip()

# -----------------------
# CORRELATION INTERPRETER
# -----------------------

def interpret_correlation(correlation_value: float) -> str:
    absolute_value = abs(correlation_value)

    if absolute_value < 0.30:
        strength = "weak"

    elif absolute_value < 0.70:
        strength = "moderate"

    else:
        strength = "strong"

    if correlation_value > 0:
        direction = "positive"

    elif correlation_value < 0:
        direction = "negative"

    else:
        return "no linear relationship"

    return f"{strength} {direction} linear relationship"


# -----------------------
# MISSING VALUES ANALYSIS
# -----------------------

def calculate_missing_values(df: pd.DataFrame, column: str) -> Optional[int]:
    if column not in df.columns:
        return None

    missing_count = df[column].isna().sum()

    return int(missing_count)

# ALL MISSING VALUES

def calculate_missing_values_all(df: pd.DataFrame) -> pd.Series:
    return df.isna().sum()

def build_missing_values_report(df: pd.DataFrame) -> str:
    missing_counts = calculate_missing_values_all(df)

    total_rows = len(df)
    columns_with_missing = int((missing_counts > 0).sum())
    total_missing = int(missing_counts.sum())

    # find column with the most missing values

    missing_only = missing_counts[missing_counts > 0].sort_values(ascending= False)

    if len(missing_only) > 0:
        worst_column = missing_only.idxmax()
        worst_count = int(missing_only.max())

        worst_percentage = (
            (worst_count / total_rows) * 100
            if total_rows > 0
            else 0
        )
    else:
        worst_column = None
        worst_count = 0
        worst_percentage = 0

    # build executive takeaway
    if worst_column is not None:
        executive_answer = (
            f"The dataset contains **{total_missing:,} missing values** "
            f"across **{columns_with_missing:,} columns**.\n\n"
            f"The largest missing-data issue is **{worst_column}**, with "
            f"**{worst_count:,} missing values** "
            f"({worst_percentage:.2f}% of rows)."
        )
    else:
        executive_answer = (
            "The dataset contains **no missing values**."
        )

    # build individual column lines

    missing_lines = []

    for column, count in missing_only.items():
        percentage = (
            (count / total_rows) * 100
            if total_rows > 0
            else 0
        )

        missing_lines.append(
            f"- **{column}:** {count:,} ({percentage:.2f}%)"
        )

    missing_text = "\n".join(missing_lines)

    return f"""
## Executive Answer

{executive_answer}

## Missing Values by Column

{missing_text}

## Data Evidence

- **Total dataset rows:** {total_rows:,}
- **Columns evaluated:** {len(df.columns):,}
- **Columns with missing values:** {columns_with_missing:,}
- **Total missing values:** {total_missing:,}
- **Calculation:** Pandas missing-value count

## Confidence

- **Level:** High
- **Reason:** Missing values were counted directly from the uploaded dataset using Python.
""".strip()

# ----------------------
# SUM / TOTAL
# ----------------------

def calculate_sum(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    )

    if numeric_values.notna().sum() == 0:
        return None

    return float(numeric_values.sum())

def build_sum_report(df: pd.DataFrame, column: str) -> Optional[str]:
    sum_value = calculate_sum(
        df,
        column
    )

    if sum_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors="coerce"
    ).notna().sum()

    if normalize_text(column) == "sale price":
        formatted_value = f"${sum_value:,.2f}"
    else:
        formatted_value = f"{sum_value:,.2f}"

    return build_numeric_report(
        column = column,
        metric_label = "Total",
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label = "Pandas sum"
    )

# ----------------------
# PERCENTILES / QUANTILES
# ----------------------

def calculate_percentile(df: pd.DataFrame, column: str, percentile: float) -> Optional[float]:
    if column not in df.columns:
        return None

    if percentile < 0 or percentile > 100:
        return None
    
    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    )

    if numeric_values.notna().sum() == 0:
        return None

    quantile_value = percentile / 100

    return float(numeric_values.quantile(quantile_value))

# EXTRACT PERCENTILE

def extract_percentile(question: str) -> Optional[float]:
    question = question.lower().strip()

    if re.search(r"\bq1\b", question) or "first quartile" in question:
        return 25.0

    if re.search(r"\bq2\b", question) or "second quartile" in question:
        return 50.0

    if re.search(r"\bq3\b", question) or "third quartile" in question:
        return 75.0

    match = re.search(
        r"\b(\d+(?:\.\d+)?)\s*(?:st|nd|rd|th)?\s*percentile\b",
        question
    )

    if match:
        percentile = float(match.group(1))

        if 0 <= percentile <= 100:
            return percentile

    return None

def build_percentile_report(df: pd.DataFrame, column: str, percentile: float) -> Optional[str]:
    percentile_value = calculate_percentile(
        df,
        column,
        percentile
    )

    if percentile_value is None:
        return None

    valid_count = pd.to_numeric(
        df[column],
        errors="coerce"
    ).notna().sum()

    if normalize_text(column) == "sale price":
        formatted_value = f"${percentile_value:,.2f}"
    else:
        formatted_value = f"{percentile_value:,.2f}"

    percentile_explanation = (
        f"Approximately **{percentile:g}%** of valid "
        f"**{column}** values are at or below "
        f"**{formatted_value}**."
        )

    if percentile == 25:
        metric_label = "25th percentile (Q1)"
    elif percentile == 50:
        metric_label = "50th percentile (Q2)"
    elif percentile == 75:
        metric_label = "75th percentile (Q3)"
    else:
        metric_label = f"{percentile:g}th percentile"

    return build_numeric_report(
        column = column,
        metric_label = metric_label,
        formatted_value = formatted_value,
        valid_count = valid_count,
        calculation_label = "Pandas quantile",
        interpretation = percentile_explanation
    )

# ----------------------
# SKEWNESS
# ----------------------

def calculate_skewness(df: pd.DataFrame, column: str) -> Optional[float]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    ).dropna()

    if len(numeric_values) < 3:
        return None

    skewness = numeric_values.skew()

    if pd.isna(skewness):
        return None

    return float(skewness)

def interpret_skewness(skewness_value: float) -> str:
    absolute_skew = abs(skewness_value)

    if absolute_skew < 0.5:
        strength = "approximately symmetric"

    elif absolute_skew < 1.0:
        strength = "moderately skewed"
    else:
        strength = "strongly skewed"

    if absolute_skew < 0.5:
        return strength

    if skewness_value > 0:
        direction = "right"
    else:
        direction = "left"

    return f"{strength} to the {direction}"

# ---------------------------
# IQR
# ---------------------------

def calculate_iqr_outliers(df: pd.DataFrame, column: str) -> Optional[dict]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    ).dropna()

    if len(numeric_values) < 4:
        return None

    q1 = numeric_values.quantile(0.25)
    q3 = numeric_values.quantile(0.75)

    iqr = q3 - q1

    lower_bound = q1 - (1.5 * iqr)
    upper_bound = q3 + (1.5 * iqr)

    outliers = numeric_values[
        (numeric_values < lower_bound) |
        (numeric_values > upper_bound)
    ]

    outlier_count = int(len(outliers))
    valid_count = int(len(numeric_values))

    outlier_percentage = (
        outlier_count / valid_count
        ) * 100

    return {
        "iqr": float(iqr),
        "lower_bound": float(lower_bound),
        "upper_bound": float(upper_bound),
        "outlier_count": outlier_count,
        "outlier_percentage": float(outlier_percentage),
    }

def interpret_iqr_outliers(outlier_result: dict) -> str:
    outlier_count = outlier_result["outlier_count"]
    outlier_percentage = outlier_result["outlier_percentage"]

    if outlier_count == 0:
        return (
            "No statistical outliers were detected using "
            "the 1.5 x IQR rule."
        )

    if outlier_count == 1:
        return (
            f"**1 statistical outlier** was detected "
            f"({outlier_percentage:.2f}% of valid values) using the "
            f"1.5 x IQR rule."
        )

    return (
        f"**{outlier_count:,} statistical outliers** were detected "
        f"({outlier_percentage:.2f}% of valid values) using the "
        f"1.5 x IQR rule."
    )





# ----------------------
# NUMERIC PROFILE
# ----------------------

def calculate_numeric_profile(df: pd.DataFrame, column: str) -> Optional[dict]:
    if column not in df.columns:
        return None

    numeric_values = pd.to_numeric(
        df[column],
        errors = "coerce"
    )

    valid_count = int(numeric_values.notna().sum())

    if valid_count == 0:
        return None
    
    missing_count = int(df[column].isna().sum())

    outlier_result = calculate_iqr_outliers(df, column)

    return {
        "count": valid_count,
        "missing": missing_count,
        "mean": calculate_average(df, column),
        "median": calculate_median(df, column),
        "minimum": calculate_minimum(df, column),
        "maximum": calculate_maximum(df, column),
        "std_dev": calculate_standard_deviation(df, column),
        "q1": calculate_percentile(df, column, 25),
        "q3": calculate_percentile(df, column, 75),
        "skewness": calculate_skewness(df, column),
        "outliers": outlier_result,
    }

# --------------------------
# NUMERIC REPORT INTERPRETER
# --------------------------

def interpret_numeric_profile(profile: dict, formatter = None) -> list:
    if formatter is None:
        formatter = lambda value: f"{value:,.2f}"

    insights = []

    mean_value = profile["mean"]
    median_value = profile["median"]
    minimum = profile["minimum"]
    maximum = profile["maximum"]
    std_dev = profile["std_dev"]
    q1 = profile["q1"]
    q3 = profile["q3"]
    skewness = profile.get("skewness")
    outlier_result = profile.get("outliers")

    # Measured skewness
    if skewness is not None:
        skew_interpretation = interpret_skewness(
            skewness
        )

        insights.append(
            f"The distribution is **{skew_interpretation}** "
            f"(skewness = **{skewness:.2f}**)."
        )

    # IQR-based outlier interpretation
    if outlier_result is not None:
        outlier_interpretation = interpret_iqr_outliers(
            outlier_result
        )

        insights.append(
            outlier_interpretation
        )

    
    # Middle 50%
    if q1 is not None and q3 is not None:
        insights.append(
            f"The middle 50% of values fall between "
            f"{formatter(q1)} and {formatter(q3)}."
        )

    # Overall range
    if minimum is not None and maximum is not None:
        insights.append(
            f"Values range from {formatter(minimum)} "
            f"to {formatter(maximum)}."
        )

    # Standard deviation
    if std_dev is not None and mean_value not in (None, 0):
        coefficient_of_variation = abs(
            std_dev / mean_value
        )

        if coefficient_of_variation >= 1:
            insights.append(
                "The standard deviation is large relative to the mean, "
                "indicating substantial variability."
            )

    return insights

# ----------------------
# NUMERIC REPORT BUILDER
# ----------------------

def build_numeric_profile_report(df: pd.DataFrame, column: str) -> Optional[str]:
    profile = calculate_numeric_profile(df, column)

    if profile is None:
        return None

    # Currency Formatter
    def format_value(value: float) -> str:
        if abs(value) < 0.005:
            value = 0.0

        if normalize_text(column) == "sale price":
            if value < 0:
                return f"-\\${abs(value):,.2f}"

            return f"\\${value:,.2f}"

        return f"{value:,.2f}"

    insights = interpret_numeric_profile(
        profile,
        formatter=format_value
    )

    mean_value = format_value(profile["mean"])
    median_value = format_value(profile["median"])
    minimum = format_value(profile["minimum"])
    maximum = format_value(profile["maximum"])
    std_dev = format_value(profile["std_dev"])
    q1 = format_value(profile["q1"])
    q3 = format_value(profile["q3"])
    skewness = profile.get("skewness")
    outlier_result = profile.get("outliers")


    if skewness is not None:
        skewness_display = f"{skewness:.2f}"
    else:
        skewness_display = "N/A"

    if insights:
        insight_text = "\n".join(
            f"- {insight}"
            for insight in insights
        )
    else:
        insight_text = (
            "- No additional deterministic interpretation "
            "was generated."
        )

    if outlier_result is not None:
        iqr_display = format_value(
            outlier_result["iqr"]
        )

        lower_bound_display = format_value(
            outlier_result["lower_bound"]
        )

        upper_bound_display = format_value(
            outlier_result["upper_bound"]
        )

        outlier_count = outlier_result[
            "outlier_count"
        ]

        outlier_percentage = outlier_result[
            "outlier_percentage"
        ]

        outlier_section = f"""

## Outlier Analysis

- **IQR:** {iqr_display}
- **Lower fence:** {lower_bound_display}
- **Upper fence:** {upper_bound_display}
- **Statistical outliers:** {outlier_count:,}
- **Outlier percentage:** {outlier_percentage:.2f}%
"""
    else:
        outlier_section = ""

    return f"""
## Executive Answer

The numeric profile for **{column}** was calculated from **{profile["count"]:,} valid records**.

## Key Insights

{insight_text}

## Descriptive Statistics

- **Mean:** {mean_value}
- **Median:** {median_value}
- **Minimum:** {minimum}
- **Q1 (25th percentile):** {q1}
- **Q3 (75th percentile):** {q3}
- **Maximum:** {maximum}
- **Standard deviation:** {std_dev}
- **Skewness:** {skewness_display}
- **Missing values:** {profile["missing"]:,}
{outlier_section}

## Data Evidence

- **Column:** {column}
- **Valid records evaluated:** {profile["count"]:,}
- **Calculation:** Deterministic Pandas descriptive statistics

## Confidence

- **Level:** High
- **Reason:** All statistics and interpretations were generated from deterministic Python calculations on the uploaded dataset.
""".strip()


# ----------------------
# GENERIC REPORT BUILDER
# ----------------------

def build_numeric_report(
    column: str, metric_label: str, formatted_value: str,
    valid_count: int, calculation_label: str, interpretation: Optional[str] = None
    ) -> str:

    interpretation_text = ""

    if interpretation:
        interpretation_text = f"\n\n{interpretation}"

    return f"""
    ## Executive Answer

The {metric_label.lower()} **{column}** is **{formatted_value}**. {interpretation_text}

## Data Evidence

- **Column:** {column}
- **Valid records evaluated:** {valid_count:,}
- **Calculation:** {calculation_label}

## Confidence

- **Level:** High
- **Reason:** The result was calculated directly from the uploaded dataset using Python.
""".strip()

# ----------------------
# QUERY IDENTIFIER
# ----------------------

def is_row_count_question(question: str) -> bool:
    normalized_question = normalize_text(question)

    row_words = [
        "record",
        "records",
        "row",
        "rows",
        "entry",
        "entries",
        "observation",
        "observations",
    ]

    count_words = [
        "how many",
        "total",
        "number",
        "count",
    ]

    return (
        any(word in normalized_question for word in row_words)
        and
        any(word in normalized_question for word in count_words)
    )



# ----------------------
# TESTING
# ----------------------

if __name__ == "__main__":
    test_questions = [
        "Summarize this dataset",
        "What is the average sale price?",
        "How many malignant tumors are there?",
        "Which category is most common?",
        "Are radius and texture correlated?",
        "Show me the missing values",
        "What is the highest sale price?",
        "What is the lowest risk score?",
        "What stands out here?"
    ]

    for question in test_questions:
        query_type = detect_query_type(question)
        print(f"{question} -> {query_type}")


    test_df = pd.DataFrame(
    columns=[
        "SalePrice",
        "radius_mean",
        "diagnosis"
        ]
    )

    column_questions = [
        "What is the average sale price?",
        "What is the average radius mean?",
        "How many malignant tumors are there?"
    ]

    for question in column_questions:
        matched_column = find_column_in_question(
            test_df,
            question
        )
        print(f"{question} -> {matched_column}")

    # AVERAGE TEST

    average_test_df = pd.DataFrame({
        "SalePrice": [100000, 200000, 300000, None],
        "Category": ["A", "B", "A", "B"]
    })

    sale_price_average = calculate_average(
        average_test_df,
        "SalePrice"
    )

    category_average = calculate_average(
        average_test_df,
        "Category"
    )

    print(f"SalePrice average -> {sale_price_average}")
    print(f"Category average -> {category_average}")

    average_report_test_df = pd.DataFrame({
    "SalePrice": [100000, 200000, 300000, None]
    })

    average_report = build_average_report(
        average_report_test_df,
        "SalePrice"
    )

    print("\nAverage report test:\n")
    print(average_report)

    # MAXIMUM TEST

    maximum_test_df = pd.DataFrame({
    "SalePrice": [100000, 450000, 300000, None],
    "Category": ["A", "B", "A", "B"]
    })

    sale_price_maximum = calculate_maximum(
        maximum_test_df,
        "SalePrice"
    )

    category_maximum = calculate_maximum(
        maximum_test_df,
        "Category"
    )

    print(f"SalePrice maximum -> {sale_price_maximum}")
    print(f"Category maximum -> {category_maximum}")
    
    maximum_report = build_maximum_report(
    maximum_test_df,
    "SalePrice"
    )

    print("\nMaximum report test:\n")
    print(maximum_report)

    # MINIMUM TEST

    minimum_test_df = pd.DataFrame({
    "SalePrice": [100000, 450000, 300000, None],
    "Category": ["A", "B", "A", "B"]
    })

    sale_price_minimum = calculate_minimum(
        minimum_test_df,
        "SalePrice"
    )

    category_minimum = calculate_minimum(
        minimum_test_df,
        "Category"
    )

    print(f"SalePrice minimum -> {sale_price_minimum}")
    print(f"Category minimum -> {category_minimum}")

    minimum_report = build_minimum_report(
    minimum_test_df,
    "SalePrice"
    )

    print("\nMinimum report test:\n")
    print(minimum_report)

    # COUNT TEST

    count_test_df = pd.DataFrame({
    "Category": ["A", "B", "A", "C"]
    })

    row_count = calculate_row_count(count_test_df)

    print(f"Row count -> {row_count}")

    row_count_report = build_row_count_report(count_test_df)

    print("\nRow Count Report:\n")
    print(row_count_report)

    row_count_questions = [
    "How many records are in this dataset?",
    "What is the total number of rows?",
    "How many malignant tumors are there?"
    ]

    for question in row_count_questions:
        result = is_row_count_question(question)
        print(f"{question} -> {result}")

    value_test_df = pd.DataFrame({
    "diagnosis": ["B", "M", "B", "M"],
    "AssrLandUse": [
        "ONE FAMILY",
        "CONDOMINIMUM",
        "ONE FAMILY",
        "THREE FAMILY"
        ]
    })

    value_questions = [
        "How many ONE FAMILY properties are there?",
        "How many CONDOMINIMUM properties are there?",
        "How many M records are there?"
    ]

    for question in value_questions:
        matched_value = find_value_in_question(
            value_test_df,
            question
        )
        print(f"{question} -> {matched_value}")

    one_family_count = calculate_value_count(
    value_test_df,
    "AssrLandUse",
    "ONE FAMILY"
    )

    malignant_code_count = calculate_value_count(
        value_test_df,
        "diagnosis",
        "M"
    )

    missing_column_count = calculate_value_count(
        value_test_df,
        "NotAColumn",
        "M"
    )

    print(f"ONE FAMILY count -> {one_family_count}")
    print(f"M diagnosis count -> {malignant_code_count}")
    print(f"Missing column count -> {missing_column_count}")

    one_family_report = build_value_count_report(
    value_test_df,
    "AssrLandUse",
    "ONE FAMILY"
    )

    print("\nValue Count Report:\n")
    #print(one_family_report)
    print(detect_query_type("How many CONDOMINIMUM properties are there?"))

    # ALIAS COUNT TEST

    alias_test_df = pd.DataFrame({
        "diagnosis": ["B", "M", "B", "M"]
    })

    alias_questions = [
        "How many malignant tumors are there?",
        "How many benign tumors are there?",
        "How many aggressive tumors are there?"
    ]

    for question in alias_questions:
        result = find_alias_value_in_question(
            alias_test_df,
            question
        )
        print(f"{question} -> {result}")

    # MEDIAN TEST

    median_test_df = pd.DataFrame({
    "SalePrice": [100000, 200000, 300000, 400000, 500000],
    "Category": ["A", "B", "C", "D", "E"]
    })

    sale_price_median = calculate_median(
        median_test_df,
        "SalePrice"
    )

    category_median = calculate_median(
        median_test_df,
        "Category"
    )

    missing_median = calculate_median(
        median_test_df,
        "NotAColumn"
    )

    print(f"SalePrice median -> {sale_price_median}")
    print(f"Category median -> {category_median}")
    print(f"Missing column median -> {missing_median}")

    median_questions = [
    "What is the median sale price?",
    "Calculate the median radius mean",
    "What is the average sale price?"
    ]

    for question in median_questions:
        result = detect_query_type(question)
        print(f"{question} -> {result}")

    median_report = build_median_report(
    median_test_df,
    "SalePrice"
    )

    print("\nMedian Report:\n")
    print(median_report)

    # STANDARD DEVIATION TEST

    std_test_df = pd.DataFrame({
    "SalePrice": [100000, 200000, 300000, 400000, 500000],
    "Category": ["A", "B", "C", "D", "E"],
    "SingleValue": [100000, None, None, None, None]
    })

    sale_price_std = calculate_standard_deviation(
        std_test_df,
        "SalePrice"
    )

    category_std = calculate_standard_deviation(
        std_test_df,
        "Category"
    )

    single_value_std = calculate_standard_deviation(
        std_test_df,
        "SingleValue"
    )

    missing_std = calculate_standard_deviation(
        std_test_df,
        "NotAColumn"
    )

    print(f"SalePrice standard deviation -> {sale_price_std}")
    print(f"Category standard deviation -> {category_std}")
    print(f"Single value standard deviation -> {single_value_std}")
    print(f"Missing column standard deviation -> {missing_std}")

    std_questions = [
    "What is the standard deviation of sale price?",
    "Calculate the standard deviation of radius mean",
    "What is the std dev of sale price?",
    "What is the std of sale price?",
    "What is the average sale price?"
    ]

    for question in std_questions:
        result = detect_query_type(question)
        print(f"{question} -> {result}")

    std_report = build_standard_deviation_report(
    std_test_df,
    "SalePrice"
    )

    print("\nStandard Deviation Report:\n")
    print(std_report)

    # VARIANCE TEST

    variance_test_df = pd.DataFrame({
    "SalePrice": [100000, 200000, 300000, 400000, 500000],
    "Category": ["A", "B", "C", "D", "E"],
    "SingleValue": [100000, None, None, None, None]
    })

    sale_price_variance = calculate_variance(
        variance_test_df,
        "SalePrice"
    )

    category_variance = calculate_variance(
        variance_test_df,
        "Category"
    )

    single_value_variance = calculate_variance(
        variance_test_df,
        "SingleValue"
    )

    missing_variance = calculate_variance(
        variance_test_df,
        "NotAColumn"
    )

    print(f"SalePrice variance -> {sale_price_variance}")
    print(f"Category variance -> {category_variance}")
    print(f"Single value variance -> {single_value_variance}")
    print(f"Missing column variance -> {missing_variance}")

    variance_questions = [
    "What is the variance of sale price?",
    "Calculate the variance of radius mean",
    "What is the standard deviation of sale price?",
    "What is the average sale price?"
    ]

    for question in variance_questions:
        result = detect_query_type(question)
        print(f"{question} -> {result}")

    variance_report = build_variance_report(
    variance_test_df,
    "SalePrice"
    )

    print("\nVariance Report:\n")
    print(variance_report)

    # DISTRIBUTIO TEST

    distribution_test_df = pd.DataFrame({
    "PropertyType": [
        "ONE FAMILY",
        "CONDOMINIMUM",
        "ONE FAMILY",
        "TWO FAMILY",
        "ONE FAMILY",
        None
    ],
    "EmptyColumn": [
        None,
        None,
        None,
        None,
        None,
        None
        ]
    })

    property_distribution = calculate_distribution(
        distribution_test_df,
        "PropertyType"
    )

    empty_distribution = calculate_distribution(
        distribution_test_df,
        "EmptyColumn"
    )

    missing_distribution = calculate_distribution(
        distribution_test_df,
        "NotAColumn"
    )

    print("PropertyType distribution:")
    print(property_distribution)

    print("\nEmpty column distribution:")
    print(empty_distribution)

    print("\nMissing column distribution:")
    print(missing_distribution)

    distribution_questions = [
    "What is the distribution of property type?",
    "Show me the frequency of property type",
    "Which property type is most common?",
    "What is the average sale price?"
    ]

    for question in distribution_questions:
        result = detect_query_type(question)
        print(f"{question} -> {result}")

    distribution_report = build_distribution_report(
    distribution_test_df,
    "PropertyType"
    )

    print("\nDistribution Report:\n")
    print(distribution_report)

    # CORRELATION TEST

    correlation_test_df = pd.DataFrame({
    "Advertising": [10, 20, 30, 40, 50],
    "Sales": [100, 200, 300, 400, 500],
    "Random": [4, 8, 2, 9, 1],
    "Category": ["A", "B", "C", "D", "E"]
    })

    sales_correlation = calculate_correlation(
        correlation_test_df,
        "Advertising",
        "Sales"
    )

    random_correlation = calculate_correlation(
        correlation_test_df,
        "Advertising",
        "Random"
    )

    category_correlation = calculate_correlation(
        correlation_test_df,
        "Advertising",
        "Category"
    )

    missing_correlation = calculate_correlation(
        correlation_test_df,
        "Advertising",
        "NotAColumn"
    )

    print(
        f"Advertising vs Sales correlation -> "
        f"{sales_correlation}"
    )

    print(
        f"Advertising vs Random correlation -> "
        f"{random_correlation}"
    )

    print(
        f"Advertising vs Category correlation -> "
        f"{category_correlation}"
    )

    print(
        f"Missing column correlation -> "
        f"{missing_correlation}"
    )

    column_match_test_df = pd.DataFrame({
    "Advertising": [10, 20, 30],
    "Sales": [100, 200, 300],
    "radius_mean": [11.2, 13.5, 15.1],
    "texture_mean": [14.0, 18.2, 20.1]
    })

    correlation_questions = [
        "What is the correlation between Advertising and Sales?",
        "Are radius mean and texture mean correlated?",
        "What is the correlation of Sales?"
    ]

    for question in correlation_questions:
        result = find_columns_in_question(
            column_match_test_df,
            question
        )
        print(f"{question} -> {result}")

    correlation_report = build_correlation_report(
    correlation_test_df,
    "Advertising",
    "Sales"
    )

    random_report = build_correlation_report(
        correlation_test_df,
        "Advertising",
        "Random"
    )

    print("\nCorrelation Report:\n")
    print(correlation_report)

    print("\nRandom Correlation Report:\n")
    print(random_report)

    correlation_classifier_tests = [
    "Are radius mean and texture mean correlated?",
    "What is the correlation between radius_mean and texture_mean?",
    "What is the average radius mean?"
    ]

    for question in correlation_classifier_tests:
        print(
            f"{question} -> "
            f"{detect_query_type(question)}"
        )

   # MISSING VALUES ANALYSIS
   
    missing_test_df = pd.DataFrame({
        "SalePrice": [100000, 200000, None, 400000, None],
        "PropertyType": [
            "ONE FAMILY",
            None,
            "CONDOMINIMUM",
            "ONE FAMILY",
            None
        ],
        "CompleteColumn": ["A", "B", "C", "D", "E"]
    })

    sale_price_missing = calculate_missing_values(
        missing_test_df,
        "SalePrice"
    )

    property_type_missing = calculate_missing_values(
        missing_test_df,
        "PropertyType"
    )

    complete_missing = calculate_missing_values(
        missing_test_df,
        "CompleteColumn"
    )

    missing_column = calculate_missing_values(
        missing_test_df,
        "NotAColumn"
    )

    print(f"SalePrice missing -> {sale_price_missing}")
    print(f"PropertyType missing -> {property_type_missing}")
    print(f"Complete column missing -> {complete_missing}")
    print(f"Missing column -> {missing_column}")

    all_missing = calculate_missing_values_all(
    missing_test_df
    )

    print("\nMissing values by column:")
    print(all_missing)

    missing_report = build_missing_values_report(
    missing_test_df
    )

    print("\nMissing Values Report:\n")
    print(missing_report)

    # SUM / TOTAL

    sum_test_df = pd.DataFrame({
    "SalePrice": [100000, 200000, 300000, None],
    "Category": ["A", "B", "C", "D"]
    })

    sale_price_sum = calculate_sum(
        sum_test_df,
        "SalePrice"
    )

    category_sum = calculate_sum(
        sum_test_df,
        "Category"
    )

    missing_sum = calculate_sum(
        sum_test_df,
        "NotAColumn"
    )

    print(f"SalePrice sum -> {sale_price_sum}")
    print(f"Category sum -> {category_sum}")
    print(f"Missing column sum -> {missing_sum}")

    sum_questions = [
    "What is the sum of sale price?",
    "What is the total sale price?",
    "What is the total number of rows?",
    "How many records are in this dataset?"
    ]

    for question in sum_questions:
        result = detect_query_type(question)
        print(f"{question} -> {result}")

    sum_report = build_sum_report(
    sum_test_df,
    "SalePrice"
    )

    print("\nSum Report:\n")
    print(sum_report)

    # PERCENTILE / QUANTILE

    percentile_test_df = pd.DataFrame({
        "SalePrice": [
            100000,
            200000,
            300000,
            400000,
            500000
        ],
        "Category": ["A", "B", "C", "D", "E"]
    })

    q1 = calculate_percentile(
        percentile_test_df,
        "SalePrice",
        25
    )

    median_percentile = calculate_percentile(
        percentile_test_df,
        "SalePrice",
        50
    )

    q3 = calculate_percentile(
        percentile_test_df,
        "SalePrice",
        75
    )

    invalid_percentile = calculate_percentile(
        percentile_test_df,
        "SalePrice",
        120
    )

    category_percentile = calculate_percentile(
        percentile_test_df,
        "Category",
        75
    )

    print(f"25th percentile -> {q1}")
    print(f"50th percentile -> {median_percentile}")
    print(f"75th percentile -> {q3}")
    print(f"Invalid percentile -> {invalid_percentile}")
    print(f"Category percentile -> {category_percentile}")

    percentile_questions = [
    "What is the 25th percentile of sale price?",
    "What is the 75th percentile of SalePrice?",
    "Calculate the 90 percentile of radius mean",
    "What is the 99.5th percentile of SalePrice?",
    "What is the 120th percentile of SalePrice?",
    "What is the average SalePrice?"
    ]

    for question in percentile_questions:
        result = extract_percentile(question)

        print(
            f"{question} -> {result}"
        )

    quartile_questions = [
    "What is Q1 for sale price?",
    "What is the first quartile of sale price?",
    "What is Q2 for sale price?",
    "What is the second quartile of sale price?",
    "What is Q3 for sale price?",
    "What is the third quartile of sale price?",
    "What is the 75th percentile of sale price?"
    ]

    for question in quartile_questions:
        result = extract_percentile(question)
        print(f"{question} -> {result}")

    percentile_type_questions = [
    "What is the 75th percentile of sale price?",
    "What is Q1 for sale price?",
    "What is the first quartile of sale price?",
    "What is Q2 of radius mean?",
    "What is the median sale price?",
    "What is the average radius mean?"
    ]

    for question in percentile_type_questions:
        result = detect_query_type(question)
        print(f"{question} -> {result}")

    q1_report = build_percentile_report(
    percentile_test_df,
    "SalePrice",
    25
    )

    q3_report = build_percentile_report(
        percentile_test_df,
        "SalePrice",
        75
    )

    p90_report = build_percentile_report(
        percentile_test_df,
        "SalePrice",
        90
    )

    print("\nQ1 Report:\n")
    print(q1_report)

    print("\nQ3 Report:\n")
    print(q3_report)

    print("\n90th Percentile Report:\n")
    print(p90_report)

    # CORRELATION INTERPRETER TEST

    correlation_interpretation_tests = [
    0.2963,
    0.6861,
    -0.2218,
    0.8200,
    -0.7500,
    0.0
    ]

    for value in correlation_interpretation_tests:
        result = interpret_correlation(value)
        print(f"{value} -> {result}")

    # NUMERIC PROFILE

    profile_test_df = pd.DataFrame({
        "SalePrice": [
            100000,
            200000,
            300000,
            400000,
            500000,
            None
        ],
        "Category": [
            "A",
            "B",
            "C",
            "D",
            "E",
            "F"
        ]
    })

    sale_price_profile = calculate_numeric_profile(
        profile_test_df,
        "SalePrice"
    )

    category_profile = calculate_numeric_profile(
        profile_test_df,
        "Category"
    )

    missing_profile = calculate_numeric_profile(
        profile_test_df,
        "NotAColumn"
    )

    print("SalePrice profile:")
    print(sale_price_profile)

    print("\nCategory profile:")
    print(category_profile)

    print("\nMissing column profile:")
    print(missing_profile)

    profile_insights = interpret_numeric_profile(
    sale_price_profile
    )

    print("Profile insights:")

    for insight in profile_insights:
        print(f"- {insight}")

    profile_report = build_numeric_profile_report(
    profile_test_df,
    "SalePrice"
    )

    print("\nNumeric Profile Report:\n")
    print(profile_report)

    skewed_test_df = pd.DataFrame({
        "SalePrice": [
            100000,
            110000,
            120000,
            130000,
            140000,
            150000,
            160000,
            2000000
        ]
    })

    skewed_profile = calculate_numeric_profile(
        skewed_test_df,
        "SalePrice"
    )

    print("\nSkewed Profile:")
    print(skewed_profile)

    print("\nSkewed Profile Insights:")

    skewed_insights = interpret_numeric_profile(
        skewed_profile
    )

    for insight in skewed_insights:
        print(f"- {insight}")

    skewed_report = build_numeric_profile_report(
    skewed_test_df,
    "SalePrice"
    )

    print(skewed_report)

    profile_type_questions = [
    "Analyze SalePrice",
    "Give me an analysis of SalePrice",
    "Summarize SalePrice",
    "Give me a statistical summary of SalePrice",
    "Show me descriptive statistics for SalePrice",
    "Give me a numeric profile of SalePrice",
    "What is the average SalePrice?",
    "What is the median SalePrice?",
    "What is the standard deviation of SalePrice?",
    "What is the 75th percentile of SalePrice?"
    ]

    for question in profile_type_questions:
        result = detect_query_type(question)
        print(f"{question} -> {result}")

    # SKEWNESS

    skewness_test_df = pd.DataFrame({
    "Symmetric": [
        1, 2, 3, 4, 5
    ],
    "RightSkewed": [
        1, 1, 2, 2, 10
    ],
    "LeftSkewed": [
        1, 9, 9, 10, 10
    ],
    "Category": [
        "A", "B", "C", "D", "E"
    ]
    })

    symmetric_skew = calculate_skewness(
        skewness_test_df,
        "Symmetric"
    )

    right_skew = calculate_skewness(
        skewness_test_df,
        "RightSkewed"
    )

    left_skew = calculate_skewness(
        skewness_test_df,
        "LeftSkewed"
    )

    category_skew = calculate_skewness(
        skewness_test_df,
        "Category"
    )

    missing_skew = calculate_skewness(
        skewness_test_df,
        "NotAColumn"
    )

    print(f"Symmetric skewness -> {symmetric_skew}")
    print(f"Right-skewed skewness -> {right_skew}")
    print(f"Left-skewed skewness -> {left_skew}")
    print(f"Category skewness -> {category_skew}")
    print(f"Missing column skewness -> {missing_skew}")

    # SKEWNESS CLASIFY

    skewness_interpretation_tests = [
    0.0,
    0.30,
    -0.30,
    0.70,
    -0.70,
    2.1416,
    -2.1416
    ]

    for value in skewness_interpretation_tests:
        result = interpret_skewness(value)
        print(f"{value} -> {result}")

    # SKEWNESS PROFILE TEST

    right_skewed_profile = calculate_numeric_profile(
    skewness_test_df,
    "RightSkewed"
    )

    print("\nRight-skewed profile:")
    print(right_skewed_profile)

    # SKEWNESS TEST ON INTRPRETER

    right_skewed_profile = calculate_numeric_profile(
    skewness_test_df,
    "RightSkewed"
    )

    right_skewed_insights = interpret_numeric_profile(
        right_skewed_profile
    )

    for insight in right_skewed_insights:
        print(f"- {insight}")

    # SKEWNESS REPORT TEST

    skewed_report = build_numeric_profile_report(
    skewness_test_df,
    "RightSkewed"
    )

    print(skewed_report)

    # IQR TEST

    outlier_test_df = pd.DataFrame({
    "Normal": [
        10, 11, 12, 13, 14,
        15, 16, 17, 18, 19
    ],
    "WithOutlier": [
        10, 11, 12, 13, 14,
        15, 16, 17, 18, 100
    ],
    "Category": [
        "A", "B", "C", "D", "E",
        "F", "G", "H", "I", "J"
        ]
    })

    normal_outliers = calculate_iqr_outliers(
        outlier_test_df,
        "Normal"
    )

    detected_outliers = calculate_iqr_outliers(
        outlier_test_df,
        "WithOutlier"
    )

    category_outliers = calculate_iqr_outliers(
        outlier_test_df,
        "Category"
    )

    missing_outliers = calculate_iqr_outliers(
        outlier_test_df,
        "NotAColumn"
    )

    print(f"Normal -> {normal_outliers}")
    print(f"With outlier -> {detected_outliers}")
    print(f"Category -> {category_outliers}")
    print(f"Missing column -> {missing_outliers}")

    # IQR INTRPRETER

    normal_interpretation = interpret_iqr_outliers(
    normal_outliers
    )

    outlier_interpretation = interpret_iqr_outliers(
        detected_outliers
    )

    print(f"Normal -> {normal_interpretation}")
    print(f"With outlier -> {outlier_interpretation}")

    # IQR RESULT TEST

    normal_profile = calculate_numeric_profile(
    outlier_test_df,
    "Normal"
    )

    print("\nNormal profile:")
    print(normal_profile)

    # OUTLIER TEST

    normal_insights = interpret_numeric_profile(
    normal_profile
    )

    print("Normal insights:")

    for insight in normal_insights:
        print(f"- {insight}")

    # OUTLIER COLUMN

    outlier_profile = calculate_numeric_profile(
    outlier_test_df,
    "WithOutlier"
    )

    outlier_insights = interpret_numeric_profile(
        outlier_profile
    )

    print("\nOutlier insights:")

    for insight in outlier_insights:
        print(f"- {insight}")

    # OUTLIER REPORT TEST

    outlier_report = build_numeric_profile_report(
    outlier_test_df,
    "WithOutlier"
    )

    print(outlier_report)