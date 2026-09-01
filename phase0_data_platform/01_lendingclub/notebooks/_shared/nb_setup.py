"""
Shared setup used by every notebook in notebooks/01_ingestion/, notebooks/02_eda/,
and notebooks/03_data_cleaning/.

Why this exists: almost every notebook in this project started with the same
six lines -- connect to the interim DuckDB file, and make sure the two asset
folders (04_assets/tables, 04_assets/plots) exist before anything tries to
save a chart or a CSV into them. Repeating that in 16 places means 16 places
to fix if the path ever changes. This module gives every notebook one call
for it instead.

How to use it, from any notebook that lives two folders under notebooks/
(e.g. notebooks/02_eda/03_....ipynb):

    import sys, os
    sys.path.insert(0, os.path.abspath("../_shared"))
    from nb_setup import connect

    con, ASSETS_TABLES, ASSETS_PLOTS = connect()
    # -> read-only connection, both asset folders created if missing.
    # Every EDA notebook should call it exactly like this: EDA notebooks
    # never write to data/02_interim/.

The one notebook that's different is `01_ingestion/01_raw_to_interim.ipynb`
-- it doesn't connect to an existing interim file, it *builds* one from
scratch (deleting any old copy first). That's a different enough job that it
gets its own function, `create_fresh()`, below -- but it's still one call
from this same shared module, not its own inline copy of the setup logic.

This module does NOT import pandas/numpy for you -- keep those explicit
imports in each notebook, since which of them a given notebook actually
needs varies.
"""
import os
import duckdb

DEFAULT_DUCKDB_FILE = "../../data/02_interim/lendingclub.duckdb"
DEFAULT_ASSETS_TABLES = "../../data/04_assets/tables"
DEFAULT_ASSETS_PLOTS = "../../data/04_assets/plots"


def connect(duckdb_file=DEFAULT_DUCKDB_FILE, read_only=True,
            assets_tables=DEFAULT_ASSETS_TABLES, assets_plots=DEFAULT_ASSETS_PLOTS):
    """Connect to the interim DuckDB file and make sure the asset folders exist.

    Returns (con, ASSETS_TABLES, ASSETS_PLOTS) -- the same three names every
    notebook already used, so swapping the old inline lines for this call
    doesn't require renaming anything else in the notebook.
    """
    os.makedirs(assets_tables, exist_ok=True)
    os.makedirs(assets_plots, exist_ok=True)
    con = duckdb.connect(duckdb_file, read_only=read_only)
    return con, assets_tables, assets_plots


def create_fresh(duckdb_file=DEFAULT_DUCKDB_FILE,
                  assets_tables=DEFAULT_ASSETS_TABLES, assets_plots=DEFAULT_ASSETS_PLOTS):
    """Only for the ingestion notebook: delete any existing interim DuckDB
    file and open a brand-new one, so re-running ingestion always starts
    from a clean slate rather than appending to stale tables.

    Returns (con, ASSETS_TABLES, ASSETS_PLOTS), same as connect().
    """
    os.makedirs(assets_tables, exist_ok=True)
    os.makedirs(assets_plots, exist_ok=True)
    os.makedirs(os.path.dirname(duckdb_file), exist_ok=True)
    if os.path.exists(duckdb_file):
        os.remove(duckdb_file)
    con = duckdb.connect(duckdb_file)
    return con, assets_tables, assets_plots
