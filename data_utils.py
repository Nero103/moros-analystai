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

    if any(word in question_tokens for word in [
        "maximum", "highest", "largest", "max"]):
        return "maximum"

    if any(word in question_tokens for word in [
        "minimum", "lowest", "smallest", "min"]):
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
# GENERIC REPORT BUILDER
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

