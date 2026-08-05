import pandas as pd
import re
from typing import Optional

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

    if any(word in question for word in [
        "summarize", "summary", "overview", "stand out", "stands out"
        ]):
        return "summary"

    if any(word in question for word in [
        "missing", "null", "blank", "incomplete"
        ]):
        return "missing_values"

    if any(word in question for word in [
        "average", "mean"
        ]):
        return "average"

    if any(word in question for word in [
        "maximum", "highest", "largest", "max"
        ]):
        return "maximum"

    if any(word in question for word in [
        "minimum", "lowest", "smallest", "min"
        ]):
        return "minimum"

    if any(word in question for word in [
        "how many", "count", "number of"
        ]):
        return "count"

    if any(word in question for word in [
        "distribution", "frequency", "most common"
        ]):
        return "distribution"

    if any(word in question for word in [
        "correlation", "relationship", "related"
        ]):
        return "correlation"

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
        column=column,
        metric_label="Average",
        formatted_value=formatted_value,
        valid_count=valid_count,
        calculation_label="Pandas arithmetic mean"
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
        column=column,
        metric_label="Maximum",
        formatted_value=formatted_value,
        valid_count=valid_count,
        calculation_label="Pandas maximum"
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
        column=column,
        metric_label="Minimum",
        formatted_value=formatted_value,
        valid_count=valid_count,
        calculation_label="Pandas minimum"
    )


# ----------------------
# GENERIC REPORT BBUILDER
# ----------------------

def build_numeric_report(
    column: str, metric_label: str, formatted_value: str,
    valid_count: int, calculation_label: str
    ) -> str:
    return f"""
    ## Executive Answer

The {metric_label.lower()} **{column}** is **{formatted_value}**.

## Data Evidence

- **Column:** {column}
- **Valid records evaluated:** {valid_count:,}
- **Calculation:** {calculation_label}

## Confidence

- **Level:** High
- **Reason:** The result was calculated directly from the uploaded dataset using Python.
""".strip()




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