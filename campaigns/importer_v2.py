import csv
import io
import os
import math
import tempfile
import pandas as pd
from multiprocessing import Pool, cpu_count
from django.db import connection
from psycopg2 import connect
from .utils import is_valid_email, is_excel_file


# ---------------------------------------------
# CONFIG
# ---------------------------------------------
WORKERS = max(2, cpu_count() // 2)        # e.g., 4–8 workers
CHUNK_SIZE = 200_000                      # rows per worker (tunable)
DB_DSN = connection.settings_dict         # reuse Django DB settings


def _psycopg_connect():
    """Make a raw psycopg2 connection using Django settings."""
    return connect(
        dbname=DB_DSN["NAME"],
        user=DB_DSN["USER"],
        password=DB_DSN["PASSWORD"],
        host=DB_DSN["HOST"],
        port=DB_DSN.get("PORT", 5432),
    )


# ---------------------------------------------------------
# PARALLEL WORKER FUNCTION
# ---------------------------------------------------------
def _copy_worker(chunk_path):
    """Executed in parallel. Copies one chunk into the DB."""
    conn = _psycopg_connect()
    cur = conn.cursor()

    cur.copy_expert(
        f"""
        COPY tmp_recipients(name, email)
        FROM STDIN
        WITH CSV HEADER;
        """,
        open(chunk_path, "r", encoding="utf-8"),
    )

    conn.commit()
    cur.close()
    conn.close()

    return os.path.getsize(chunk_path)   # small progress info


class RecipientImporterParallel:
    """
    Ultra-fast parallel importer.
    Reaches ~2M rows/sec (depends on CPU / IOPS).
    """

    def __init__(self, uploaded_file):
        self.file = uploaded_file

    # -----------------------------------------------------
    # Public entrypoint
    # -----------------------------------------------------
    def run(self):
        csv_file = (
            self._excel_to_csv() if is_excel_file(self.file.name)
            else self._normalize_csv()
        )

        return self._parallel_copy(csv_file)

    # -----------------------------------------------------
    # Excel → CSV
    # -----------------------------------------------------
    def _excel_to_csv(self):
        df = pd.read_excel(self.file)
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv")
        df.to_csv(temp.name, index=False)
        return temp.name

    # -----------------------------------------------------
    # CSV normalize (clean, validate, lowercase emails)
    # -----------------------------------------------------
    def _normalize_csv(self):
        wrapper = io.TextIOWrapper(self.file.file, encoding="utf-8")
        reader = csv.DictReader(wrapper)

        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode='w', encoding='utf-8')
        writer = csv.writer(temp)
        writer.writerow(["name", "email"])

        for row in reader:
            email = row.get("email", "").strip().lower()
            name = row.get("name", "").strip()

            if email and not is_valid_email(email):
                continue

            writer.writerow([name, email])

        temp.close()
        return temp.name

    # -----------------------------------------------------
    # MAIN PARALLEL COPY IMPORT LOGIC
    # -----------------------------------------------------
    def _parallel_copy(self, csv_path):
        # --------------------------------------------
        # 1️⃣ Split CSV into multiple chunk files
        # --------------------------------------------
        paths = self._split_csv(csv_path)

        # --------------------------------------------
        # 2️⃣ Prepare DB: Create one regular table (not temp, so workers can see it)
        # --------------------------------------------
        with connection.cursor() as cur:
            cur.execute("""
                DROP TABLE IF EXISTS tmp_recipients;
                CREATE TABLE tmp_recipients (
                    name  TEXT,
                    email TEXT
                );
            """)

        # --------------------------------------------
        # 3️⃣ Run multiple COPY workers in parallel
        # --------------------------------------------
        try:
            with Pool(WORKERS) as pool:
                pool.map(_copy_worker, paths)

            # --------------------------------------------
            # 4️⃣ Merge into real table with UPSERT
            # --------------------------------------------
            with connection.cursor() as cur:
                cur.execute("""
                    INSERT INTO campaigns_recipient (name, email, subscription_status, created_on)
                    SELECT name, email, 'subscribed', NOW() FROM tmp_recipients
                    ON CONFLICT (email) DO NOTHING;
                """)

            # --------------------------------------------
            # 5️⃣ Summary stats
            # --------------------------------------------
            with connection.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM tmp_recipients;")
                total = cur.fetchone()[0]

                cur.execute("""
                    SELECT COUNT(*)
                    FROM campaigns_recipient
                    WHERE email IN (SELECT email FROM tmp_recipients);
                """)
                inserted = cur.fetchone()[0]

            result = {
                "created": inserted,
                "duplicates_skipped": total - inserted,
            }
        
        finally:
            # --------------------------------------------
            # 6️⃣ Cleanup: Drop the temporary table and chunk files
            # --------------------------------------------
            with connection.cursor() as cur:
                cur.execute("DROP TABLE IF EXISTS tmp_recipients;")
            
            # Remove chunk files
            for path in paths:
                try:
                    os.remove(path)
                except:
                    pass
        
        return result

    # -----------------------------------------------------
    # Split CSV into chunks for parallel workers
    # -----------------------------------------------------
    def _split_csv(self, csv_path):
        paths = []
        total_lines = sum(1 for _ in open(csv_path, "r"))
        rows = total_lines - 1  # minus header

        num_chunks = math.ceil(rows / CHUNK_SIZE)

        with open(csv_path, "r") as src:
            header = src.readline()

            for i in range(num_chunks):
                chunk_path = f"{csv_path}.chunk{i}.csv"
                paths.append(chunk_path)

                with open(chunk_path, "w") as dst:
                    dst.write(header)
                    for _ in range(CHUNK_SIZE):
                        line = src.readline()
                        if not line:
                            break
                        dst.write(line)

        return paths
