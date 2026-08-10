import ollama
import pandas as pd
from config import MODEL
from data_utils import (
    build_dataset_profile, detect_query_type, 
    find_column_in_question, build_average_report,
    build_maximum_report, build_minimum_report,
    build_median_report, build_row_count_report, 
    is_row_count_question, find_value_in_question, 
    build_value_count_report, find_alias_value_in_question,
    build_standard_deviation_report, build_variance_report,
    build_distribution_report, find_columns_in_question,
    build_correlation_report, build_missing_values_report,
    build_sum_report, extract_percentile, 
    build_percentile_report,
    )

# ------------------------
# CSV ANALSIS PROMPT
# ------------------------

def analyze_text(df, question):

    query_type = detect_query_type(question)

    if query_type == "count" and is_row_count_question(question):
        return build_row_count_report(df)

    matched_column = find_column_in_question(df, question)

    # CORRELATION

    if query_type == "correlation":
        matched_columns = find_columns_in_question(
            df,
            question
        )

        if len(matched_columns) != 2:
            return (
                "I detected a correlation question, but I need exactly "
                "two dataset columns to calculate the correlation."
            )

        column_x, column_y = matched_columns

        correlation_report = build_correlation_report(
            df,
            column_x,
            column_y
        )

        if correlation_report is None:
            return (
                f"I found the columns '{column_x}' and '{column_y}', "
                "but they do not contain enough paired numeric values "
                "for a correlation calculation."
            )

        return correlation_report

    # STANDARD DEVIATION

    if query_type == "standard_deviation":
        if matched_column is None:
            return (
                "I detected a standard deviation question, but I could not "
                "identify the requested dataset column."
            )

        std_report = build_standard_deviation_report(
            df,
            matched_column
        )

        if std_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain enough usable numeric values."
            )

        return std_report

    # VARIANCE

    if query_type == "variance":
        if matched_column is None:
            return (
                "I detected a variance question, but I could not "
                "identify the requested dataset column."
            )

        variance_report = build_variance_report(
            df,
            matched_column
        )

        if variance_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain enough usable numeric values."
            )

        return variance_report

    # DISTRIBUTION

    if query_type == "distribution":
        if matched_column is None:
            return (
                "I detected a distribution question, but I could not "
                "identify the requested dataset column."
            )

        distribution_report = build_distribution_report(
            df,
            matched_column
        )

        if distribution_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain usable values for a distribution."
            )

        return distribution_report

    # PERCENTILE / QUANTILE

    if query_type == "percentile":
        if matched_column is None:
            return (
                "I detected a percentile question, but I could not "
                "identify the requested dataset column."
            )

        percentile = extract_percentile(question)

        if percentile is None:
            return (
                "I detected a percentile question, but I could not "
                "identify the requested percentile."
            )

        percentile_report = build_percentile_report(
            df,
            matched_column,
            percentile
        )

        if percentile_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain usable numeric values for a percentile calculation."
            )

        return percentile_report

    # MEDIAN

    if query_type == "median":
        if matched_column is None:
            return (
                "I detected a median question, but I could not "
                "identify the requested dataset column."
            )

        median_report = build_median_report(
            df,
            matched_column
        )

        if median_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain usable numeric values."
            )

        return median_report

    # AVERAGE

    if query_type == "average":
        if matched_column is None:
            return (
                "I detected an average question, but I could not identify "
                "which dataset column to calculate."
            )

        average_report = build_average_report(
            df, matched_column
        )

        if average_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain usable numeric values for an average."
            )

        return average_report

    # MAXIMUM    

    if query_type == "maximum":
        if matched_column is None:
            return (
                "I detected a maximum value question, but I could not "
                "identify the requested dataset column."
            )

        maximum_report = build_maximum_report(
            df, matched_column
        )

        if maximum_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain numeric values."
            )

        return maximum_report

    # MINIMUM    

    if query_type == "minimum":
        if matched_column is None:
            return (
                "I detected a minimum-value question, but I could not "
                "identify the requested dataset column."
            )

        minimum_report = build_minimum_report(
            df,
            matched_column
        )

        if minimum_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain usable numeric values."
            )

        return minimum_report

    # COUNT    

    if query_type == "count":
        matched_value = find_value_in_question(
            df,
            question
        )

        if matched_value is None:
            matched_value = find_alias_value_in_question(
                df,
                question
            )

        if matched_value is not None:
            matched_value_column, matched_value_value = matched_value

            value_count_report = build_value_count_report(
                df,
                matched_value_column,
                matched_value_value
            )

            if value_count_report is not None:
                return value_count_report

    # MISSING VALUES

    if query_type == "missing_values":
        return build_missing_values_report(df)

    # SUM / TOTAL

    if query_type == "sum":
        if matched_column is None:
            return (
                "I detected a sum question, but I could not "
                "identify the requested dataset column."
            )

        sum_report = build_sum_report(
            df,
            matched_column
        )

        if sum_report is None:
            return (
                f"I found the column '{matched_column}', but it does not "
                "contain usable numeric values for a sum."
            )

        return sum_report


    dataset_profile = build_dataset_profile(df)
    
    prompt = f"""
    You are a senior data analyst working for a Fortune 500 company.

    Your job is to analyze datasets and produce execuitve-level summaries.

    RULES:
    - Strictly use ONLY the uploaded dataset
    - Strictly never invnt facts, values, trends, or conclusions.
    - If the data cannot answer the question, clearly state that.
    - Distinguish observed facts from interpretations.
    - Every interpretation must strictly be supported by evidence from the dataset.
    - Keep explanation concise and executuve-friendly.
    - Strctly do not exaggerate certainty.
    - For every major conclusion, strictly identify the supporting column, value, statistic, or sample row.
    - Strictly do not claim causation unless the dataset directly supports it.
    - Strictly label unsupported possibilities as hypotheses, not facts.
    - Use the exact row count stated in the verified profile.
    - Never estimate or approximate unique counts.
    - Never describe a date range unless the verified profile explicitly provides minimum and maximum dates.
    - Do not invent sample rows. Only discuss rows if actual row data is provided.
    - When discussing missing data, cite the exact missing-value counts from the profile.
    - Do not recommend collecting additional fields unless the user specifically asks for recommendations about data collection.
    - Do not make geographic, temporal, or business-scope claims that are not directly present in the verified profile.

    VERIFIED DATASET PROFILE:

    {dataset_profile}

    Detected Query Type
    {query_type}
    
    User Question:
    {question}

    OUTPUT FORMAT:

    1. Executive Answer (direct response to question)
    2. Key Insights (bullet points)
    3. Data Evidence (what supports your answer)
        - Supporting columns:
        - Supporting values/statistics:
        - Relevant sample rows, if available
    4. Confidence
        - Level: High / Medium / Low
        - Reason:
    5. Risks / Concerns
    6. Recommended Next Actions
    """

    try:
        response = ollama.chat(
            model = MODEL,
            messages = [{"role": "user", "content": prompt}],
            options = {"temperature": 0.2}
        )

        return response["message"]["content"]

    except Exception as e:
        return f"AI analysis failed. Error: {e}"

# ------------------------
# PDF ANALSIS PROMPT
# ------------------------

def analyze_pdf(pdf_text, question):
    prompt = f"""
    You are a senior reseach and business analyst.

    Analyze the PDF content below and answer the user's questions.

    RULES:
    - Strictly use ONLY the uploaded PDF.
    - Strictly never invent facts.
    - If the answer cannot be determined from the document, explicitly say so.
    - Separate observed facts from interpretations.
    - Every conclusion must strictly reference evidence from the document.
    - Keep explanations concise and executive-friendly.
    - Strictly do not exaggerate certainty.
    - For every major conclusion, strictly quote or closely paraphrase the supporting passage.
    - Strictly identify the page number when page information is available.
    - Strictly do not treat interpretation as a directly stated fact.

    PDF CONTENT:
    {pdf_text[:8000]}

    USER QUESTION:
    {question}

    OUTPUT:
    1. Executive Summary
    2. Evidence
        - Supporting passage:
        - Page number, if available:
    3. Key Findings
    4. Confidence
        - Level: High / Medium / Low
        - Reason:
    5. Risks / Concerns
    6. Recommeneded Next Actions
    """

    try:
        response = ollama.chat(
            model = MODEL,
            messages = [{"role": "user", "content": prompt}],
            options = {"temperature": 0.2}
        )

        return response["message"]["content"]

    except Exception as e:
        return f"PDF analysis failed. Error: {e}"

# ----------------------
# Report Formatting
#-----------------------

def format_report(report):
    heading_replacements = {
        "1. Executive Answer": "## Executive Answer",
        "1. Executive Summary": "## Executive Summary",
        "2. Evidence": "## Evidence",
        "3. Confidence": "## Confidence",
        "4. Key Insights": "## Key Insights",
        "4. Key Findings": "## Key Findings",
        "5. Risks / Concerns": "## Risks / Concerns",
        "6. Recommended Next Actions": "## Recommended Next Actions"
    }

    for old_heading, new_heading in heading_replacements.items():
        report = report.replace(old_heading, new_heading)
    
    return report

