#!/usr/bin/env python3
"""View the project's SQLite DB using pandas.

Usage examples:
  python scripts\view_db_pandas.py --show
  python scripts\view_db_pandas.py --join --limit 50
  python scripts\view_db_pandas.py --to-csv --out-dir .\exports

The script will try to import `biocantinas.backend.app.storage` to obtain the
DB path. If that fails (running outside the package path), it will search for
`biocantinas.db` in the repository root and current directory.
"""
import argparse
import os
import pathlib
import sys

try:
    from biocantinas.backend.app import storage
    DB_PATH = storage.DB_PATH
except Exception:
    # fallback: search for biocantinas.db in repo tree (current dir upward)
    cwd = pathlib.Path.cwd()
    candidate = None
    # search current dir and parents up to root
    for p in [cwd] + list(cwd.parents):
        candidate_path = p / "biocantinas.db"
        if candidate_path.exists():
            candidate = candidate_path
            break
    if candidate is None:
        # also try repo-relative locations
        candidate = pathlib.Path(__file__).resolve().parents[1] / "biocantinas.db"
    DB_PATH = str(candidate)


def find_db_path():
    if DB_PATH and pathlib.Path(DB_PATH).exists():
        return str(pathlib.Path(DB_PATH).resolve())
    raise FileNotFoundError(f"Database file not found at {DB_PATH}")


def main():
    parser = argparse.ArgumentParser(description="View biocantinas SQLite DB with pandas.")
    parser.add_argument("--show", action="store_true", help="Show top rows of tables")
    parser.add_argument("--join", action="store_true", help="Show joined produtos x fornecedores")
    parser.add_argument("--limit", type=int, default=20, help="Number of rows to show")
    parser.add_argument("--to-csv", action="store_true", help="Export tables to CSV")
    parser.add_argument("--out-dir", type=str, default="./exports", help="Output dir for CSVs")
    args = parser.parse_args()

    try:
        import pandas as pd
        import sqlite3
    except Exception as e:
        print("This script requires pandas. Install with: pip install pandas")
        raise

    db = find_db_path()
    print(f"Using DB: {db}")

    conn = sqlite3.connect(db)

    if args.show:
        print("\n--- fornecedores (top) ---")
        df_f = pd.read_sql_query(f"SELECT * FROM fornecedores LIMIT {args.limit}", conn)
        print(df_f.to_string(index=False))

        print("\n--- produtos (top) ---")
        df_p = pd.read_sql_query(f"SELECT * FROM produtos LIMIT {args.limit}", conn)
        print(df_p.to_string(index=False))

    if args.join:
        print("\n--- produtos JOIN fornecedores (top) ---")
        q = (
            "SELECT p.id as produto_id, p.nome as produto, p.capacidade, "
            "f.id as fornecedor_id, f.nome as fornecedor, f.data_inscricao, f.aprovado "
            "FROM produtos p JOIN fornecedores f ON p.fornecedor_id = f.id "
            f"ORDER BY p.nome, f.data_inscricao LIMIT {args.limit}"
        )
        df_j = pd.read_sql_query(q, conn)
        print(df_j.to_string(index=False))

    if args.to_csv:
        out_dir = pathlib.Path(args.out_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        df_f = pd.read_sql_query("SELECT * FROM fornecedores", conn)
        df_p = pd.read_sql_query("SELECT * FROM produtos", conn)
        fpath1 = out_dir / "fornecedores.csv"
        fpath2 = out_dir / "produtos.csv"
        df_f.to_csv(fpath1, index=False)
        df_p.to_csv(fpath2, index=False)
        print(f"Exported fornecedores -> {fpath1}\nExported produtos -> {fpath2}")

    conn.close()


if __name__ == '__main__':
    main()
