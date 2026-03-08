import great_expectations as gx
import pandas as pd
from pathlib import Path
from great_expectations.expectations import (
    ExpectColumnValuesToBeBetween,
    ExpectColumnValuesToNotBeNull,
    ExpectColumnValuesToBeOfType
)


def validate_data_func():
    root_path = Path(__file__).parent.parent
    data_path = root_path / 'data' / 'raw_data.csv'

    context = gx.get_context()
    df = pd.read_csv(data_path)

    try:
        datasource = context.data_sources.add_pandas(name="my_pandas_datasource")
    except Exception:
        datasource = context.data_sources.get("my_pandas_datasource")

    try:
        data_asset = datasource.add_dataframe_asset(name="raw_data_asset")
    except Exception:
        data_asset = datasource.get_asset("raw_data_asset")

    try:
        batch_definition = data_asset.add_batch_definition_whole_dataframe("batch_def")
    except Exception:
        batch_definition = data_asset.get_batch_definition("batch_def")

    suite = gx.ExpectationSuite(name="my_suite")

    suite.add_expectation(ExpectColumnValuesToBeBetween(column="price", min_value=0))
    suite.add_expectation(ExpectColumnValuesToBeBetween(column="stock", min_value=0, max_value=1000))
    suite.add_expectation(ExpectColumnValuesToBeOfType(column="stock", type_="float64"))
    for col in ["model", "price", "stock"]:
        suite.add_expectation(ExpectColumnValuesToNotBeNull(column=col))

    context.suites.add_or_update(suite)

    validation_def = gx.ValidationDefinition(
        name="validation",
        data=batch_definition,
        suite=suite,
    )
    context.validation_definitions.add_or_update(validation_def)

    checkpoint = gx.Checkpoint(
        name="my_checkpoint",
        validation_definitions=[validation_def],
        result_format="SUMMARY",
    )
    context.checkpoints.add_or_update(checkpoint)

    results = checkpoint.run(batch_parameters={"dataframe": df})

    if results.success:
        print("Data validation passed")
        return True

    print("Data validation failed")
    return False

if __name__ == "__main__":
    validate_data_func()