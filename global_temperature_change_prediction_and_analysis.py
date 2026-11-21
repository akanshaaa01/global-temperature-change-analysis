import pandas as pd

df = pd.read_csv("FAOSTAT_temperature_raw.csv", low_memory=False)

df.columns = [
    col.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")
    for col in df.columns
]

df["unit"] = "°C"
df["domain"] = "Temperature change on land"

df["months"] = (
    df["months"]
    .astype(str)
    .str.replace("\x96", "-", regex=False)
    .str.replace("–", "-", regex=False)
    .str.replace("?", "-", regex=False)
    .str.strip()
)

df["area"] = df["area"].astype(str).str.strip()

df = df[df["element"] == "Temperature change"].copy()
df = df[df["iso3_code"].notna()].copy()

df["value"] = pd.to_numeric(df["value"], errors="coerce")
df = df.dropna(subset=["value"])

for int_col in ["year", "months_code", "m49_code", "area_code_fao"]:
    df[int_col] = pd.to_numeric(df[int_col], errors="coerce").round().astype("Int64")

source_priority = {
    "FAOSTAT_data_en_11-1-2024.csv": 1,
    "FAOSTAT_data_1-10-2022.csv": 2,
    "Environment_Temperature_change_E_All_Data_NOFLAG.csv": 3
}
df["source_priority"] = df["source_file"].map(source_priority).fillna(4)

df = (
    df.sort_values(by=["iso3_code", "year", "months_code", "source_priority"])
    .drop_duplicates(subset=["iso3_code", "year", "months_code"], keep="first")
)

df["flag"] = df["flag"].fillna("Unflagged")
df["flag_description"] = df["flag_description"].fillna("No flag recorded")

cols_to_keep = [
    "iso3_code", "iso2_code", "m49_code", "area_code_fao", "area",
    "year", "months_code", "months", "value", "unit", "flag", "flag_description"
]
df_clean = df[cols_to_keep].sort_values(by=["area", "year", "months_code"]).reset_index(drop=True)

df_clean.to_csv("cleaned_FAOSTAT_temperature.csv", index=False, encoding="utf-8-sig")