import marimo

__generated_with = "0.23.6+alx.1"
app = marimo.App()


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    <div align="center" style=" font-size: 80%; text-align: center; margin: 0 auto">
    <img src="https://raw.githubusercontent.com/Explore-AI/Pictures/refs/heads/master/Python-Notebook-Banners/Code_challenge.png"  style="display: block; margin-left: auto; margin-right: auto;";/>
    </div>
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Understanding and Trusting Data
    Data doesn't lie, but it can hide. When a government audit threatens to freeze the Ministry of Agriculture's funding, the gap between an unverified spreadsheet and a defensible dataset is three weeks of rigorous proof. In this project, you step into an emergency data audit for Maji Ndogo: you profile distributions, break rainfall down by province, weigh each crop's yield, and trace the true drivers of productivity through a Seaborn correlation heatmap. It is exactly the kind of high-stakes, story-driven exploratory data analysis that proves you can trust data under pressure.

    > ⚠️ **Note that this code challenge is graded and will contribute to your overall marks for this module. Submit this notebook for grading.**
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Instructions

    - Do not add or remove cells in this notebook. Do not edit or remove the `### START FUNCTION` or `### END FUNCTION` comments. Do not add any code outside of the functions you are required to edit. Doing any of this will result in a mark of 0%.
    - Answer the questions according to the specifications provided.
    - Use the provided test cells to verify your output before submitting.
    - Do not hard-code answers — your functions must work on unseen inputs.
    - The use of StackOverflow, Google, and other online resources is permitted. The use of Generative AI tools — including ChatGPT, Claude, Copilot, and others — is also allowed and encouraged as a learning partner. However, the code you submit must reflect your own understanding. Copying a fellow student's code is a breach of the honor code. [Read the honor code here](https://drive.google.com/file/d/1atFOPUQRLz5slb4Q1ASXh8QQfKyXVqrw/preview). Submitting code you do not understand is also a breach.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    The letter from the government auditor arrives on a Tuesday.

    It is polite but unmistakable: the Ministry of Agriculture has three weeks to demonstrate that the Maji Ndogo farm survey data is accurate before it can be used to allocate funding. If the data cannot be independently verified, the entire project gets put on hold.

    Sanaa reads the letter twice, puts it face-down on the desk, and turns to you.

    "We have weather stations across the region," she says. "Five of them. They record temperature, rainfall, and pollution independently of our field teams — IoT sensors, real-time data. If our field measurements agree with the station readings, we have a defensible case." She pauses. "If they do not..."

    She does not finish the sentence.

    Your job starts now. The audit clock is running, and the first step is to understand the data as it stands — distribution by distribution, relationship by relationship, pattern by pattern. This notebook is your field report. Every chart you produce, every number you note down, is evidence you can take into that audit. Work carefully.
    """)
    return


@app.cell
def _():
    ### DO NOT CHANGE ANYTHING IN THIS CELL, ONLY EXECUTE IT!

    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    import seaborn as sns
    from sqlalchemy import create_engine, text

    engine = create_engine('sqlite:///Maji_Ndogo_farm_survey_small.db')
    sql_query = """
    SELECT *
    FROM geographic_features
    LEFT JOIN weather_features USING (Field_ID)
    LEFT JOIN soil_and_crop_features USING (Field_ID)
    LEFT JOIN farm_management_features USING (Field_ID)
    """
    with engine.connect() as connection:
        MD_agric_df = pd.read_sql_query(text(sql_query), connection)

    # In this survey, the Crop_type and Annual_yield columns are stored in each
    # other's place. Swap them back so Crop_type holds crop names and Annual_yield
    # holds the numeric tonnage.
    MD_agric_df.rename(columns={'Annual_yield': 'Crop_type_Temp', 'Crop_type': 'Annual_yield'}, inplace=True)
    MD_agric_df.rename(columns={'Crop_type_Temp': 'Crop_type'}, inplace=True)

    # A handful of elevations were logged as negative — fix the sign.
    MD_agric_df['Elevation'] = MD_agric_df['Elevation'].abs()

    # Clean known crop-name typos (e.g. 'cassaval' -> 'cassava').
    corrections = {'cassaval': 'cassava', 'wheatn': 'wheat', 'teaa': 'tea'}
    MD_agric_df['Crop_type'] = MD_agric_df['Crop_type'].apply(
        lambda crop: corrections.get(str(crop).strip(), str(crop).strip())
    )
    print(f'Loaded: {MD_agric_df.shape[0]} rows x {MD_agric_df.shape[1]} columns')
    return (MD_agric_df,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    **Expected output:**
    ```
    Loaded: 5654 rows x 18 columns
    ```
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Data Dictionary

    **Geographic features**

    | Column | Description | Type |
    |--------|-------------|------|
    | Field_ID | Unique identifier for each field | BigInt |
    | Elevation | Elevation above sea level in meters | Float |
    | Latitude / Longitude | Geographic coordinates in degrees | Float |
    | Location | Province the field is in | Text |
    | Slope | Slope of the land in degrees | Float |

    **Weather features**

    | Column | Description | Type |
    |--------|-------------|------|
    | Rainfall | Annual rainfall in mm | Float |
    | Min_temperature_C | Average minimum temperature in degrees C | Float |
    | Max_temperature_C | Average maximum temperature in degrees C | Float |
    | Ave_temps | Average temperature in degrees C | Float |

    **Soil and crop features**

    | Column | Description | Type |
    |--------|-------------|------|
    | Soil_fertility | Normalized fertility index, 0-1 | Float |
    | Soil_type | Categorical soil classification | Text |
    | pH | Soil pH level | Float |
    | Pollution_level | Normalized pollution index, 0-1 | Float |

    **Farm management features**

    | Column | Description | Type |
    |--------|-------------|------|
    | Plot_size | Field area in hectares | Float |
    | Crop_type | Type of crop grown | Text |
    | Annual_yield | Total annual yield in tonnes | Float |
    | Standard_yield | Normalized yield score, 0-1 | Float |
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Challenge 1: Dataset Summary Metrics

    Every analysis starts by understanding what you are working with. Before building complex charts, let's extract the essential dimensions: how many columns the joined survey has, and the average elevation across all fields.

    ### Task
    Write a function `get_dataset_summary` that accepts the dataset and returns a tuple `(number_of_columns, mean_elevation)`, where `number_of_columns` is an `int` and `mean_elevation` is the mean of the `Elevation` column.

    > ⚠️ Do not change the function name `get_dataset_summary`.

    ### Expected Output
    ```
    (18, 637.7907086314113)
    ```
    """)
    return


@app.cell
def _():
    ### START FUNCTION
    def get_dataset_summary(df):
        """Return (number_of_columns, mean_elevation) for the given dataset."""
        number_of_columns = df.shape[1]
        mean_elevation = df['Elevation'].mean()
        return (number_of_columns, mean_elevation)
    ### END FUNCTION
    return (get_dataset_summary,)


@app.cell
def _(MD_agric_df, get_dataset_summary):
    print(get_dataset_summary(MD_agric_df))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Challenge 2: Rainfall by Location

    The overall `Rainfall` distribution shows multiple peaks — a sign that different sub-populations are being averaged together. Breaking it down by province reveals the hidden structure, and tells the audit which regions are genuinely dry and which are wet.

    ### Task
    Write a function `get_mean_rainfall_by_location` that calculates the mean `Rainfall` grouped by `Location` and returns it as a pandas Series sorted in **ascending** order of values.

    > ⚠️ Do not change the function name `get_mean_rainfall_by_location`.

    ### Expected Output
    ```
    Location
    Rural_Amanzi       723.628958
    Rural_Kilimani     791.352426
    Rural_Hawassa     1325.941003
    Rural_Akatsi      1584.884457
    Rural_Sokoto      1705.079431
    Name: Rainfall, dtype: float64
    ```
    """)
    return


@app.cell
def _():
    ### START FUNCTION
    def get_mean_rainfall_by_location(df):
        """Return mean Rainfall grouped by Location, sorted ascending."""
        return df.groupby('Location')['Rainfall'].mean().sort_values(ascending=True)
    ### END FUNCTION
    return (get_mean_rainfall_by_location,)


@app.cell
def _(MD_agric_df, get_mean_rainfall_by_location):
    print(get_mean_rainfall_by_location(MD_agric_df))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Amanzi and Kilimani are the dry provinces; Sokoto receives more than twice their rainfall. That spread is exactly what a per-location KDE plot would show as separated peaks.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Challenge 3: Crop Distribution Volume

    Before diving into continuous relationships, it helps to understand the categorical landscape. How many fields are planted with each crop type? This Series drives both a bar chart and a pie chart.

    ### Task
    Write a function `get_crop_counts` that counts the number of fields per `Crop_type` and returns a pandas Series sorted in **descending** order of counts.

    > ⚠️ Do not change the function name `get_crop_counts`.

    ### Expected Output
    ```
    Crop_type
    wheat      1342
    tea         913
    potato      823
    cassava     672
    banana      633
    coffee      607
    maize       399
    rice        265
    Name: count, dtype: int64
    ```
    """)
    return


@app.cell
def _():
    ### START FUNCTION
    def get_crop_counts(df):
        """Return the count of fields per Crop_type, sorted descending."""
        return df['Crop_type'].value_counts()
    ### END FUNCTION
    return (get_crop_counts,)


@app.cell
def _(MD_agric_df, get_crop_counts):
    print(get_crop_counts(MD_agric_df))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Wheat dominates the survey; rice is rare. An imbalance like this matters later — any model trained on this data will see wheat five times as often as rice.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Challenge 4: Crop Median Yields

    A violin plot shows the full distribution of a continuous variable across categories. Let's isolate the precise median annual yields across crop varieties to locate the performance peaks.

    ### Task
    Write a function `get_median_yield_by_crop` that calculates the median `Annual_yield` grouped by `Crop_type` and returns a pandas Series sorted in **descending** order of median yield.

    > ⚠️ Do not change the function name `get_median_yield_by_crop`.

    ### Expected Output
    ```
    Crop_type
    rice       1.734914
    tea        1.657955
    cassava    1.447799
    maize      1.446741
    coffee     1.405154
    banana     1.391763
    wheat      1.389082
    potato     1.283974
    Name: Annual_yield, dtype: float64
    ```
    """)
    return


@app.cell
def _():
    ### START FUNCTION
    def get_median_yield_by_crop(df):
        """Return median Annual_yield grouped by Crop_type, sorted descending."""
        return df.groupby('Crop_type')['Annual_yield'].median().sort_values(ascending=False)
    ### END FUNCTION
    return (get_median_yield_by_crop,)


@app.cell
def _(MD_agric_df, get_median_yield_by_crop):
    print(get_median_yield_by_crop(MD_agric_df))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    Rice is rare (Challenge 3) but its median yield is the highest — a pattern worth flagging for the audit, since low-volume, high-yield crops are easy to overlook in an averaged view.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## ## Challenge 5: Temperature and Elevation Correlation

    Scatter plots reveal how two continuous variables relate. Let's quantify the linear connection between altitude and average ambient temperature with a single Pearson coefficient.

    ### Task
    Write a function `get_elevation_temp_correlation` that computes the Pearson correlation coefficient between `Elevation` and `Ave_temps`, returned as a `float`.

    > ⚠️ Do not change the function name `get_elevation_temp_correlation`.

    ### Expected Output
    ```
    0.20306114718387722
    ```
    """)
    return


@app.cell
def _():
    ### START FUNCTION
    def get_elevation_temp_correlation(df):
        """Return the Pearson correlation coefficient between Elevation and Ave_temps."""
        return float(df['Elevation'].corr(df['Ave_temps']))
    ### END FUNCTION
    return (get_elevation_temp_correlation,)


@app.cell
def _(MD_agric_df, get_elevation_temp_correlation):
    print(get_elevation_temp_correlation(MD_agric_df))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    A weak positive correlation. One might expect higher elevation to mean *cooler* temperatures, so a mild positive value is itself an audit flag — the kind of "does this make physical sense?" check that validating data against independent sensors is meant to catch.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Challenge 6: Yield Correlations

    A correlation matrix measures how strongly each numerical variable relates to every other. Values close to 1 or -1 indicate a strong linear relationship. Here we ask: what actually drives `Standard_yield`?

    ### Task
    Write a function `get_yield_correlations` that:
    - Considers these feature columns only: `['Elevation', 'Slope', 'Rainfall', 'Min_temperature_C', 'Max_temperature_C', 'Ave_temps', 'Soil_fertility', 'pH', 'Pollution_level', 'Plot_size', 'Annual_yield']`.
    - Computes each feature's Pearson correlation with `Standard_yield`.
    - Returns the result as a pandas Series sorted in **descending order of absolute value** (strongest relationship first).

    > ⚠️ Do not change the function name `get_yield_correlations`.

    ### Expected Output
    ```
    Pollution_level     -0.285761
    Annual_yield         0.220812
    pH                  -0.196613
    Min_temperature_C    0.144233
    Elevation            0.129248
    Max_temperature_C   -0.111649
    Soil_fertility       0.070205
    Slope                0.056991
    Rainfall             0.039217
    Plot_size           -0.017014
    Ave_temps            0.006786
    Name: Standard_yield, dtype: float64
    ```
    """)
    return


@app.cell
def _():
    ### START FUNCTION
    def get_yield_correlations(df):
        """Return each feature's Pearson correlation with Standard_yield,
        sorted by descending absolute value."""
        feature_columns = [
            'Elevation', 'Slope', 'Rainfall', 'Min_temperature_C', 'Max_temperature_C',
            'Ave_temps', 'Soil_fertility', 'pH', 'Pollution_level', 'Plot_size', 'Annual_yield'
        ]
        correlations = df[feature_columns].corrwith(df['Standard_yield'])
        correlations = correlations.reindex(correlations.abs().sort_values(ascending=False).index)
        correlations.name = 'Standard_yield'
        return correlations
    ### END FUNCTION
    return (get_yield_correlations,)


@app.cell
def _(MD_agric_df, get_yield_correlations):
    print(get_yield_correlations(MD_agric_df))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    `Pollution_level` is the strongest single correlate of standardized yield (negative — more pollution, lower yield), ahead of soil and weather. None of the relationships is especially strong, which tells the audit that yield is multi-causal: no single field measurement explains it, so the data must be trusted as a whole, not by any one column.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ---

    ## Wrap Up

    You have completed the exploratory analysis of the Maji Ndogo farm survey dataset.

    Six challenges have mapped out a growing picture of what the data actually contains — which provinces are dry (Amanzi, Kilimani) and which are wet (Sokoto), which crops dominate (wheat) and which are rare-but-productive (rice), and which variables move together (pollution and yield) versus on their own. Each result is a line in the field report you can take into the audit: independently checkable, reproducible from the database, and honest about how strong — or weak — each relationship really is.

    That last point is the heart of *trusting* data: an analyst who reports a weak correlation as weak is worth more than one who oversells it. Ensure all unit tests pass before final submission — then walk into that audit with evidence you can defend line by line.
    """)
    return




# ════════════════════════════════════════════════════════════════════════
# Pre-submission readiness check
#
# This cell has NO declared dependencies — it runs even when other cells
# have not. It uses dynamic name lookup (eval + try/except) so the learner
# always gets actionable feedback, including a "run all cells first" hint
# when nothing has been defined yet.
#
# The spec below is auto-generated at conversion time from the test_suite
# (which functions pytest references) and the model solution (the canonical
# parameter names + body characteristics).
# ════════════════════════════════════════════════════════════════════════

@app.cell
def cell_readiness():
    import inspect as _inspect
    import ast as _ast
    _spec = {'get_crop_counts': {'expected_params': ['df']}, 'get_dataset_summary': {'expected_params': ['df']}, 'get_elevation_temp_correlation': {'expected_params': ['df']}, 'get_mean_rainfall_by_location': {'expected_params': ['df']}, 'get_median_yield_by_crop': {'expected_params': ['df']}, 'get_yield_correlations': {'expected_params': ['df']}}
    _msgs = []
    _missing = 0
    _stubs = 0
    _mismatches = 0
    for _name, _checks in _spec.items():
        try:
            _fn = eval(_name)
        except NameError:
            _msgs.append(f"❌ `{_name}` — not defined yet")
            _missing += 1
            continue
        if not callable(_fn):
            _msgs.append(f"❌ `{_name}` — exists but is not callable")
            _missing += 1
            continue
        try:
            _sig = _inspect.signature(_fn)
            _actual_params = list(_sig.parameters.keys())
        except (ValueError, TypeError):
            _msgs.append(f"✓ `{_name}` — defined (signature unavailable)")
            continue
        _expected = _checks.get("expected_params")
        if _expected and _actual_params != _expected:
            _msgs.append(
                f"⚠️ `{_name}` — parameter mismatch: expected {_expected}, got {_actual_params}"
            )
            _mismatches += 1
            continue
        # AST check — flag empty stubs (function body is just `pass` or `return None`)
        _is_stub = False
        try:
            import textwrap as _textwrap
            _src = _textwrap.dedent(_inspect.getsource(_fn))
            _tree = _ast.parse(_src)
            _body = _tree.body[0].body if _tree.body else []
            # Strip any leading docstring (an Expr with a Constant str)
            _real_body = [
                _stmt for _stmt in _body
                if not (
                    isinstance(_stmt, _ast.Expr)
                    and isinstance(_stmt.value, _ast.Constant)
                    and isinstance(_stmt.value.value, str)
                )
            ]
            _is_stub = (
                not _real_body
                or (
                    len(_real_body) == 1
                    and (
                        isinstance(_real_body[0], _ast.Pass)
                        or (isinstance(_real_body[0], _ast.Return) and _real_body[0].value is None)
                    )
                )
            )
        except (OSError, TypeError, SyntaxError, IndexError):
            pass  # source unavailable; skip stub check
        if _is_stub:
            _msgs.append(
                f"⚠️ `{_name}` — body looks empty (just `pass` or bare `return`). Did you implement it?"
            )
            _stubs += 1
            continue
        _msgs.append(f"✓ `{_name}` — defined with parameters {_actual_params}")
    print("Readiness check:")
    for _m in _msgs:
        print(f"  {_m}")
    print()
    if _missing == len(_spec):
        print("It looks like none of the required functions are defined yet.")
        print("Click 'Run all cells' (the ▶▶ button at the top of the page),")
        print("or run each function-defining cell individually first.")
    elif _missing > 0:
        print(f"{_missing} function(s) not yet defined — run the cells that define them and re-run this check.")
    elif _stubs > 0 or _mismatches > 0:
        print(f"Some functions need fixing before submitting ({_stubs} stub(s), {_mismatches} signature mismatch(es)).")
    else:
        print("All required functions are present and ready. You can submit.")
    return


if __name__ == "__main__":
    app.run()

