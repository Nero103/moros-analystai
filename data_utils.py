import pandas as pd

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

    
