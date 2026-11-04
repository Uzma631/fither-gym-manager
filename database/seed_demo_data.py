"""
database/seed_demo_data.py — Populate fither_gym with fictional demo data.

SAFETY RULES:
  1. This script NEVER deletes existing data by default.
  2. It checks whether demo data already exists before inserting.
  3. To reset demo data, pass --reset on the command line.
     Reset only removes rows flagged with a demo marker in the notes field.
  4. Real business data (rows without the demo marker) is never touched.

Run:
    python database/seed_demo_data.py            # safe insert (skip if exists)
    python database/seed_demo_data.py --reset    # delete demo rows, then re-insert

All names and phone numbers are clearly fictional.
"""

import sys, os, argparse
from datetime import date, timedelta
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import db_connection
from utils.date_utils import calculate_end_date

# ── Demo data marker ──────────────────────────────────────────────────────────
DEMO_MARKER = "[DEMO DATA]"   # Added to notes field of every demo row

# ── Fictional members ─────────────────────────────────────────────────────────
DEMO_MEMBERS = [
    # (full_name, phone, joining_date, gender, notes)
    ("Ayesha Tariq",     "03001111001", date(2024, 1, 15), "Female", f"{DEMO_MARKER} Demo member"),
    ("Fatima Malik",     "03002222002", date(2024, 2, 10), "Female", f"{DEMO_MARKER} Demo member"),
    ("Sana Iqbal",       "03003333003", date(2024, 3, 5),  "Female", f"{DEMO_MARKER} Demo member"),
    ("Zara Khan",        "03004444004", date(2024, 3, 20), "Female", f"{DEMO_MARKER} Demo member"),
    ("Nadia Hussain",    "03005555005", date(2024, 4, 1),  "Female", f"{DEMO_MARKER} Demo member"),
    ("Hira Butt",        "03006666006", date(2024, 4, 18), "Female", f"{DEMO_MARKER} Demo member"),
    ("Mehwish Alam",     "03007777007", date(2024, 5, 3),  "Female", f"{DEMO_MARKER} Demo member"),
    ("Rukhsar Rafiq",    "03008888008", date(2024, 5, 22), "Female", f"{DEMO_MARKER} Demo member — student"),
    ("Amina Sheikh",     "03009999009", date(2024, 6, 10), "Female", f"{DEMO_MARKER} Demo member"),
    ("Bushra Niazi",     "03011111010", date(2024, 6, 28), "Female", f"{DEMO_MARKER} Demo member"),
    ("Lubna Raza",       "03022222011", date(2024, 7, 5),  "Female", f"{DEMO_MARKER} Demo member"),
    ("Shazia Nawaz",     "03033333012", date(2024, 7, 19), "Female", f"{DEMO_MARKER} Demo member"),
    ("Kiran Baig",       "03044444013", date(2024, 8, 8),  "Female", f"{DEMO_MARKER} Demo member — student"),
    ("Rabia Siddiqui",   "03055555014", date(2024, 8, 25), "Female", f"{DEMO_MARKER} Demo member"),
    ("Uzma Farooq",      "03066666015", date(2024, 9, 12), "Female", f"{DEMO_MARKER} Demo member"),
    ("Tasneem Akhtar",   "03077777016", date(2024, 10, 1), "Female", f"{DEMO_MARKER} Demo member — never subscribed"),
    ("Noor Fatima",      "03088888017", date(2024, 10, 15),"Female", f"{DEMO_MARKER} Demo member — never subscribed"),
]

# ── Subscription scenarios ────────────────────────────────────────────────────
# Each entry: (member_index_0based, plan_id, start_date, agreed_fee, payments_list)
# payments_list: list of (amount, payment_date, method)
TODAY = date.today()

DEMO_SUBSCRIPTIONS = [
    # Active — fully paid
    (0,  1, TODAY - timedelta(days=20),  Decimal("2500.00"),
     [(Decimal("2500.00"), TODAY - timedelta(days=20), "Cash")]),

    # Active — partially paid
    (1,  2, TODAY - timedelta(days=45),  Decimal("6500.00"),
     [(Decimal("3000.00"), TODAY - timedelta(days=45), "Cash"),
      (Decimal("2000.00"), TODAY - timedelta(days=15), "Bank Transfer")]),

    # Active — no payment yet
    (2,  1, TODAY - timedelta(days=5),   Decimal("2500.00"), []),

    # Expiring within 7 days — fully paid
    (3,  1, TODAY - timedelta(days=25),  Decimal("2500.00"),
     [(Decimal("2500.00"), TODAY - timedelta(days=25), "Cash")]),

    # Expiring within 7 days — partially paid
    (4,  1, TODAY - timedelta(days=26),  Decimal("2500.00"),
     [(Decimal("1500.00"), TODAY - timedelta(days=26), "Cash")]),

    # Active — 6-month plan, fully paid
    (5,  3, TODAY - timedelta(days=60),  Decimal("11000.00"),
     [(Decimal("6000.00"), TODAY - timedelta(days=60), "Bank Transfer"),
      (Decimal("5000.00"), TODAY - timedelta(days=30), "Cash")]),

    # Active — student plan
    (6,  4, TODAY - timedelta(days=10),  Decimal("1800.00"),
     [(Decimal("1800.00"), TODAY - timedelta(days=10), "Cash")]),

    # Expired — last month (fully paid)
    (7,  1, TODAY - timedelta(days=60),  Decimal("1800.00"),
     [(Decimal("1800.00"), TODAY - timedelta(days=60), "Cash")]),

    # Expired — last month (partially paid)
    (8,  2, TODAY - timedelta(days=120), Decimal("6500.00"),
     [(Decimal("3000.00"), TODAY - timedelta(days=120), "Cash")]),

    # Expired — old 6-month (fully paid)
    (9,  3, TODAY - timedelta(days=200), Decimal("11000.00"),
     [(Decimal("5500.00"), TODAY - timedelta(days=200), "Bank Transfer"),
      (Decimal("5500.00"), TODAY - timedelta(days=170), "Cash")]),

    # Member with two subscriptions (renewed) — member index 10
    (10, 1, TODAY - timedelta(days=90),  Decimal("2500.00"),   # old — expired
     [(Decimal("2500.00"), TODAY - timedelta(days=90), "Cash")]),
    (10, 2, TODAY - timedelta(days=10),  Decimal("6500.00"),   # new — active
     [(Decimal("3500.00"), TODAY - timedelta(days=10), "Bank Transfer")]),

    # Active with 3-month plan, partially paid
    (11, 2, TODAY - timedelta(days=30),  Decimal("6500.00"),
     [(Decimal("3000.00"), TODAY - timedelta(days=30), "Cash"),
      (Decimal("1000.00"), TODAY - timedelta(days=5),  "Cash")]),

    # Student plan — active
    (12, 4, TODAY - timedelta(days=15),  Decimal("1800.00"),
     [(Decimal("900.00"),  TODAY - timedelta(days=15), "Cash")]),

    # Active — 6-month, fully paid
    (13, 3, TODAY - timedelta(days=15),  Decimal("11000.00"),
     [(Decimal("11000.00"), TODAY - timedelta(days=15), "Bank Transfer")]),

    # Active — monthly
    (14, 1, TODAY - timedelta(days=3),   Decimal("2500.00"),   # expiring in ~27 days
     [(Decimal("2500.00"), TODAY - timedelta(days=3), "Cash")]),

    # Members 15 and 16 are "never subscribed" — no subscriptions
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_plan_duration(cursor, plan_id: int) -> int:
    cursor.execute("SELECT duration_months FROM membership_plans WHERE plan_id = %s", (plan_id,))
    row = cursor.fetchone()
    return row[0] if row else 1


def demo_data_exists(conn) -> bool:
    """Check whether any demo members already exist."""
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM members WHERE notes LIKE %s", (f"%{DEMO_MARKER}%",))
    count = cursor.fetchone()[0]
    cursor.close()
    return count > 0


def delete_demo_data(conn):
    """Delete all rows flagged with the demo marker. Never touches non-demo rows."""
    cursor = conn.cursor()
    # Collect demo member IDs
    cursor.execute("SELECT member_id FROM members WHERE notes LIKE %s", (f"%{DEMO_MARKER}%",))
    member_ids = [r[0] for r in cursor.fetchall()]

    if member_ids:
        placeholders = ", ".join(["%s"] * len(member_ids))
        # Delete payments → subscriptions → members (foreign key order)
        cursor.execute(
            f"DELETE py FROM payments py "
            f"JOIN subscriptions s ON py.subscription_id = s.subscription_id "
            f"WHERE s.member_id IN ({placeholders})",
            member_ids,
        )
        cursor.execute(
            f"DELETE FROM subscriptions WHERE member_id IN ({placeholders})", member_ids
        )
        cursor.execute(
            f"DELETE FROM members WHERE member_id IN ({placeholders})", member_ids
        )
    conn.commit()
    cursor.close()
    print(f"  ✓ Deleted demo data for {len(member_ids)} member(s).")


# ── Main seeding function ─────────────────────────────────────────────────────

def seed(reset: bool = False):
    print(f"\n{'=' * 55}")
    print(f"  FitHer Gym Manager — Demo Data Seeder")
    print(f"{'=' * 55}")

    with db_connection() as conn:
        exists = demo_data_exists(conn)

        if exists and not reset:
            print("\n  Demo data already exists. Use --reset to replace it.")
            print("  Skipping insert. Real data is unaffected.")
            return

        if reset and exists:
            print("\n  --reset flag detected. Removing existing demo data...")
            delete_demo_data(conn)

        print("\n  Inserting demo members...")
        cursor = conn.cursor()
        inserted_member_ids = []

        for (full_name, phone, joining_date, gender, notes) in DEMO_MEMBERS:
            cursor.execute(
                "INSERT INTO members (full_name, phone, joining_date, gender, notes) "
                "VALUES (%s, %s, %s, %s, %s)",
                (full_name, phone, joining_date, gender, notes),
            )
            inserted_member_ids.append(cursor.lastrowid)
            print(f"    + Member: {full_name}")

        conn.commit()

        print("\n  Inserting demo subscriptions and payments...")
        for sub_def in DEMO_SUBSCRIPTIONS:
            member_idx, plan_id, start_date, agreed_fee, payments = sub_def
            member_id = inserted_member_ids[member_idx]

            duration = get_plan_duration(cursor, plan_id)
            end_date  = calculate_end_date(start_date, duration)

            # Determine status from dates
            today_d = date.today()
            if start_date <= today_d <= end_date:
                status = "active"
            else:
                status = "expired"

            cursor.execute(
                "INSERT INTO subscriptions (member_id, plan_id, start_date, end_date, agreed_fee, status) "
                "VALUES (%s, %s, %s, %s, %s, %s)",
                (member_id, plan_id, start_date, end_date, str(agreed_fee), status),
            )
            sub_id = cursor.lastrowid
            member_name = DEMO_MEMBERS[member_idx][0]
            print(f"    + Subscription for {member_name}: plan {plan_id}, {start_date} -> {end_date} [{status}]")

            for (amount, pay_date, method) in payments:
                cursor.execute(
                    "INSERT INTO payments (subscription_id, amount, payment_date, payment_method, notes) "
                    "VALUES (%s, %s, %s, %s, %s)",
                    (sub_id, str(amount), pay_date, method, DEMO_MARKER),
                )
            if payments:
                print(f"      | {len(payments)} payment(s) recorded")

        conn.commit()
        cursor.close()

    print(f"\n  ✅ Demo data seeded successfully.")
    print(f"  Members inserted:      {len(DEMO_MEMBERS)}")
    print(f"  Subscriptions defined: {len(DEMO_SUBSCRIPTIONS)}")
    print(f"  (2 members have no subscriptions — for 'never subscribed' scenario)")
    print(f"\n  Run the app with:  streamlit run app.py\n")


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed FitHer Gym Manager with demo data.")
    parser.add_argument("--reset", action="store_true",
                        help="Delete existing demo data before re-inserting. Real data is NOT affected.")
    args = parser.parse_args()
    seed(reset=args.reset)
