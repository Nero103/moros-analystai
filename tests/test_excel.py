import pandas as pd

from data_utils import (
    load_excel_file,
    get_excel_sheet_names,
)


def test_load_excel_file(tmp_path):
    file_path = tmp_path / "test.xlsx"

    source_df = pd.DataFrame({
        "SalePrice": [100000, 200000, 300000],
        "PropertyType": [
            "ONE FAMILY",
            "CONDO",
            "TWO FAMILY"
        ]
    })

    source_df.to_excel(
        file_path,
        index=False
    )

    loaded_df = load_excel_file(
        file_path
    )

    assert loaded_df is not None
    assert len(loaded_df) == 3
    assert list(loaded_df.columns) == [
        "SalePrice",
        "PropertyType"
    ]

    assert loaded_df["SalePrice"].tolist() == [
        100000,
        200000,
        300000
    ]


def test_get_excel_sheet_names(tmp_path):
    file_path = tmp_path / "multi_sheet.xlsx"

    with pd.ExcelWriter(file_path) as writer:
        pd.DataFrame({
            "Sales": [100, 200, 300]
        }).to_excel(
            writer,
            sheet_name="Sales",
            index=False
        )

        pd.DataFrame({
            "Customers": [10, 20, 30]
        }).to_excel(
            writer,
            sheet_name="Customers",
            index=False
        )

    sheet_names = get_excel_sheet_names(
        file_path
    )

    assert sheet_names == [
        "Sales",
        "Customers"
    ]


def test_load_specific_excel_sheet(tmp_path):
    file_path = tmp_path / "multi_sheet.xlsx"

    with pd.ExcelWriter(file_path) as writer:
        pd.DataFrame({
            "Sales": [100, 200]
        }).to_excel(
            writer,
            sheet_name="Sales",
            index=False
        )

        pd.DataFrame({
            "Region": ["North", "South"],
            "Customers": [25, 30]
        }).to_excel(
            writer,
            sheet_name="Customers",
            index=False
        )

    loaded_df = load_excel_file(
        file_path,
        sheet_name="Customers"
    )

    assert loaded_df is not None
    assert list(loaded_df.columns) == [
        "Region",
        "Customers"
    ]

    assert loaded_df["Customers"].tolist() == [
        25,
        30
    ]


def test_invalid_excel_file_returns_none(tmp_path):
    file_path = tmp_path / "not_excel.xlsx"

    file_path.write_text(
        "This is not a real Excel workbook."
    )

    result = load_excel_file(
        file_path
    )

    assert result is None