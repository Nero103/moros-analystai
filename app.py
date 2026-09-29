import streamlit as st
import pandas as pd
import time
from ai_engine import analyze_text, analyze_document, format_report
from document_utils import extract_pdf_text, extract_docx_text
from data_utils import load_excel_file, get_excel_sheet_names
from config import MODEL, PDF_LIMIT

st.set_page_config(
    page_title="Moros AnalystAI",
    page_icon="⬢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------
# STRUCTURED DATA ANALYSIS UI
# ---------------------------

def render_structured_analysis(
    df: pd.DataFrame,
    file_type: str,
    user_question: str
):
    analysis_placeholder = st.empty()

    if st.button(
        f"Generate {file_type} Analysis"
    ):
        with st.spinner(
            f"Analyzing {file_type.lower()} data..."
        ):
            start_time = time.perf_counter()

            question = (
                user_question
                if user_question
                else "What stands out in this dataset?"
            )

            brief = analyze_text(
                df,
                question
            )

            processing_time = (
                time.perf_counter() - start_time
            )

        st.subheader("Analysis Brief")
        st.success("✅ Analysis Complete")

        sumcol1, sumcol2, sumcol3, sumcol4, sumcol5 = st.columns(5)

        with sumcol1:
            st.metric("File Type", file_type)

        with sumcol2:
            st.metric("Rows", len(df))

        with sumcol3:
            st.metric("AI Model", MODEL)

        with sumcol4:
            st.metric(
                "Time",
                f"{processing_time:.1f}s"
            )

        with sumcol5:
            st.metric("Status", "Complete")

        with analysis_placeholder.container():

            st.markdown(
                "### 📋 Executive Analysis Report"
            )

            with st.container(border=True):
                st.markdown(
                    format_report(brief)
                )

        st.download_button(
            label="Download Analysis Brief",
            data=brief,
            file_name=(
                f"analystai_{file_type.lower()}_brief.txt"
            ),
            mime="text/plain"
        )

# ------------------
# UI
# ------------------

st.title("⬢ Moros AnalystAI")
st.markdown("## Transform Data into Decisions")
st.caption("AI-Powered Business & Document Intelligence")
st.divider()

st.markdown("""
Upload a **CSV**, **Excel workbook**, **PDF**, or **Word document** ask a question in plain English, and receive structured executive insights from a local AI.

**Built for analysts, business, and decision-making.**
""")

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border= True):
        st.markdown("""
        ### 📈 Business Intelligence\n\nAnalyze CSV datasets to uncover trends, anomalies, and business insights.
        
    Best for:
    - Sales reports
    - Financial data
    - Operational metrics
        """)

with col2:
    with st.container(border= True):
        st.markdown("""
        ### 📄 Document Intelligence\n\nSummarize PDF reports and ask questions using local AI.
        
    Best for:
    - Business reports
    - Research reports
    - Documentation
        """)

with col3:
    with st.container(border= True):
        st.markdown("""
        ### 💾 Executive Reporting\n\nGenerate structured reports that can be downloaded and shared.
        
    Outputs:
    - Executive summary
    - Key findings
    - Recommendations
        """)

# --------------------
# Sidebar for input
# --------------------

with st.sidebar:
    st.title("⬢ Control Center")
    st.caption("Configure your analysis")

    st.divider()

    st.markdown("### 📂 Upload")
    uploaded_file = st.file_uploader(
        "Upload a CSV, Excel, PDF, or Word document",
        type = ["csv", "xlsx", "pdf", "docx"]
    )

    st.divider()

    st.markdown("### ❓ Analysis Question")
    user_question = st.text_input(
            "Ask a question about the data",
            placeholder = "Example: what stands out in this dataset?"
    )

    st.divider()

    st.markdown("### 🤖 model")
    st.info(MODEL)

    st.divider()

    st.caption("⬢ Moros AnalystAI v3.0")

# -----------------
# Main area
# -----------------

if uploaded_file is not None:
    #st.success(f"Uploaded: {uploaded_file.name}")

    # ------------------
    # CSV
    # ------------------

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)

        st.success("✅ CSV uploaded successfully")
        st.caption(f"File: {uploaded_file.name}")

        st.divider()

        left_col, right_col = st.columns([1, 1])

        with left_col:

            st.subheader("CSV Preview")
            st.dataframe(df.head(3))

        with right_col:

            st.subheader("🤖 AI Workspace")

            render_structured_analysis(
                df,
                "CSV",
                user_question
            )

    # --------------------
    # Excel Area
    #---------------------  

    elif uploaded_file.name.endswith(".xlsx"):

        sheet_names = get_excel_sheet_names(
            uploaded_file
        )

        if sheet_names is None:
            st.error("Unable to read this Excel workbook.")

        else:
            st.success("✅ Excel workbook uploaded successfully")
            st.caption(f"File: {uploaded_file.name}")

        selected_sheet = st.selectbox(
                "Select worksheet",
                sheet_names
        )

        df = load_excel_file(
            uploaded_file,
            sheet_name=selected_sheet
        )

        if df is None:
            st.error(
                "Unable to load the selected worksheet."
            )

        else:
            st.caption(
                f"Worksheet: {selected_sheet}"
            )

            st.divider()

            left_col, right_col = st.columns([1, 1])

            with left_col:
                st.subheader("Excel Preview")

                st.dataframe(
                    df.head(3)
                )

            with right_col:
                st.subheader("🤖 AI Workspace")

                render_structured_analysis(
                    df,
                    "Excel",
                    user_question
                )

    # --------------------
    # PDF Area
    #---------------------

    elif uploaded_file.name.endswith(".pdf"):

        st.success("✅ PDF uploaded successfully")
        st.caption(f"File: {uploaded_file.name}")
        

        pdf_text = extract_pdf_text(uploaded_file)

        st.divider()

        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.subheader("📄 PDF Preview")
            st.text(pdf_text[:2000])

            #pdf_question = st.text_input(
            #    "Ask a question about this PDF",
            #    placeholder ="Example: What are the key findings?"
            #)

        with right_col:

            st.subheader("🤖 AI Workspace")

            analysis_placeholder = st.empty()

            if st.button("Generate PDF Analysis"):
                with st.spinner("Analyzing PDF..."):
                    start_time = time.perf_counter()

                    question = (
                        user_question
                        if user_question 
                        else "Summarize the key points in this PDF."
                    )

                    pdf_brief = analyze_document(pdf_text, question)

                    processing_time = time.perf_counter() - start_time

                st.success("✅ Analysis Complete")

                sumcol1, sumcol2, sumcol3, sumcol4, sumcol5 = st.columns(5)

                with sumcol1:
                    st.metric("File Type", "PDF")

                with sumcol2:
                    st.metric("Characters", len(pdf_text))

                with sumcol3:
                    st.metric("AI Model", MODEL)

                with sumcol4:
                    st.metric("Time", f"{processing_time:.1f}s")

                with sumcol5:
                    st.metric("Status", "Complete")    

                with analysis_placeholder.container():

                    st.markdown("### 📋 Executive Analysis Report")    
                    
                    with st.container(border= True):
                        st.markdown(format_report(pdf_brief))

                st.download_button(
                    label = "Download PDF Analysis",
                    data = pdf_brief,
                    file_name = "analystai_pdf_analysis.txt",
                    mime = "text/plain"
                )

    # --------------------
    # Word Area
    #---------------------

    elif uploaded_file.name.endswith(".docx"):

        st.success("✅ Word document uploaded successfully")
        st.caption(f"File: {uploaded_file.name}")

        docx_text = extract_docx_text(uploaded_file)

        if docx_text is None:
            st.error(
                "Unable to read this Word document or the document is empty."
            )

        else:
            st.divider()

            left_col, right_col = st.columns([1, 1])

            with left_col:
                st.subheader("📄 Word Preview")
                st.text(docx_text[:2000])

            with right_col:
                st.subheader("🤖 AI Workspace")

                analysis_placeholder = st.empty()

                if st.button("Generate Word Analysis"):
                    with st.spinner("Analyzing Word document..."):
                        start_time = time.perf_counter()

                        question = (
                            user_question
                            if user_question
                            else "Summarize the key points in this Word document."
                        )

                        word_brief = analyze_document(
                            docx_text,
                            question
                        )

                        processing_time = (
                            time.perf_counter() - start_time
                        )

                    st.success("✅ Analysis Complete")

                    sumcol1, sumcol2, sumcol3, sumcol4, sumcol5 = st.columns(5)

                    with sumcol1:
                        st.metric("File Type", "Word")

                    with sumcol2:
                        st.metric("Characters", len(docx_text))

                    with sumcol3:
                        st.metric("AI Model", MODEL)

                    with sumcol4:
                        st.metric(
                            "Time",
                            f"{processing_time:.1f}s"
                        )

                    with sumcol5:
                        st.metric("Status", "Complete")

                    with analysis_placeholder.container():

                        st.markdown(
                            "### 📋 Executive Analysis Report"
                        )

                        with st.container(border=True):
                            st.markdown(
                                format_report(word_brief)
                            )

                    st.download_button(
                        label="Download Word Analysis",
                        data=word_brief,
                        file_name="analystai_word_analysis.txt",
                        mime="text/plain"
                    )

else:
    st.info("Upload a CSV, Excel, PDF file, or Word document to begin analysis")

    st.markdown("""
    ### What Moros AnalystAI can do:
    - Analyze CSV datasets
    - Read Excel workbooks and worksheets
    - Summarize PDF documents
    - Evaluate Word documents
    - Answer natural language questions
    - Generate analyst-style reports
    - Download results as text files
    - Run locally using Ollama
    """)

# ----------------
# Footer
# ----------------

st.divider()
st.caption(
    "⬢ Moros AnalystAI v3.0  •  Powered by Python, Streamlit, Pandas, and Ollama  •  Local AI Processing"
)


