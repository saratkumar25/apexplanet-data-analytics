import pandas as pd
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, text

def get_db_path(db_path=None):
    """Resolve the path to superstore.db. Defaults to project_root/data/superstore.db."""
    if db_path is not None:
        return Path(db_path).resolve()
    
    # Try relative to CWD first, then script location
    for p in [Path("data/superstore.db"), Path("../data/superstore.db"), Path("../../data/superstore.db")]:
        if p.exists():
            return p.resolve()
            
    # Fallback to resolving relative to this script
    script_dir = Path(__file__).resolve().parent
    return (script_dir.parent / "data" / "superstore.db").resolve()

def get_engine(db_path=None):
    """Return a SQLAlchemy engine connected to the SQLite database."""
    resolved_path = get_db_path(db_path)
    # Ensure parent dir exists
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{resolved_path}")

def get_connection(db_path=None):
    """Return a raw sqlite3 connection object."""
    resolved_path = get_db_path(db_path)
    return sqlite3.connect(str(resolved_path))

def run_query(query, engine=None, params=None):
    """Execute a raw SQL query and return a pandas DataFrame. Uses text() wrapper for SQLAlchemy."""
    if engine is None:
        engine = get_engine()
        
    with engine.connect() as conn:
        df = pd.read_sql(sql=text(query), con=conn, params=params)
    return df

def pretty_print(df):
    """Formatted print of DataFrame."""
    if hasattr(df, 'to_string'):
        print(df.to_string(index=False))
    else:
        print(df)

def list_tables(engine=None):
    """Return a list of all user-defined tables and views in the database."""
    query = """
        SELECT type, name, tbl_name 
        FROM sqlite_master 
        WHERE type IN ('table', 'view') AND name NOT LIKE 'sqlite_%'
        ORDER BY type DESC, name;
    """
    df = run_query(query, engine)
    pretty_print(df)
    return df

def db_summary(engine=None):
    """Print count summaries for the primary database tables."""
    if engine is None:
        engine = get_engine()
        
    tables = ['orders', 'customers', 'products']
    print("Database Row Counts Summary:")
    print("----------------------------")
    for tbl in tables:
        try:
            df = run_query(f"SELECT COUNT(*) AS count FROM {tbl}", engine)
            print(f"Table: {tbl:<10} | Rows: {df['count'].iloc[0]:,}")
        except Exception as e:
            print(f"Table: {tbl:<10} | Error: {str(e)}")
            
    # Views count
    try:
        df_views = run_query("SELECT name FROM sqlite_master WHERE type = 'view'", engine)
        print(f"Views: {len(df_views)}")
        for v in df_views['name']:
            print(f"  - {v}")
    except Exception:
        pass
    print("----------------------------")

def table_info(table_name, engine=None):
    """Return a DataFrame with details about columns in a table or view."""
    query = f"PRAGMA table_info({table_name});"
    return run_query(query, engine)
