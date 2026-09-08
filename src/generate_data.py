"""
generate_data.py
-----------------
Creates a synthetic but realistic dataset for a small family clinic:
- patients.csv
- appointments.csv
- billing.csv
- feedback.csv

Run this once to populate /data before starting the SQLite database.
"""

import csv
import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

NUM_PATIENTS = 250
NUM_APPOINTMENTS = 900
START_DATE = datetime(2025, 1, 1)
END_DATE = datetime(2025, 12, 31)

FIRST_NAMES = ["Ravi", "Priya", "Arjun", "Sneha", "Karthik", "Divya", "Manoj", "Anitha",
               "Suresh", "Lakshmi", "Vikram", "Meena", "Naveen", "Kavya", "Ramesh", "Pooja"]
LAST_NAMES = ["Reddy", "Kumar", "Rao", "Naidu", "Sharma", "Iyer", "Gupta", "Chowdary", "Varma", "Prasad"]

DEPARTMENTS = ["General Medicine", "Pediatrics", "Gynecology", "Orthopedics", "Dermatology", "ENT"]
APPT_STATUS_WEIGHTS = [("Completed", 0.70), ("No-show", 0.12), ("Cancelled", 0.10), ("Rescheduled", 0.08)]
PAYMENT_METHODS = ["Cash", "UPI", "Card", "Insurance"]
PAYMENT_STATUS_WEIGHTS = [("Paid", 0.78), ("Pending", 0.15), ("Overdue", 0.07)]

FEEDBACK_POSITIVE = [
    "Doctor was very attentive and explained everything clearly.",
    "Short waiting time, very efficient staff.",
    "Clean facility and friendly front desk.",
    "Great follow-up call after my visit.",
]
FEEDBACK_NEUTRAL = [
    "Visit was fine, nothing special.",
    "Average experience, doctor was a bit rushed.",
]
FEEDBACK_NEGATIVE = [
    "Waited over an hour past my appointment time.",
    "Billing took too long and was confusing.",
    "Front desk was unresponsive to my calls.",
    "Had to reschedule twice due to poor communication.",
]


def weighted_choice(weighted_list):
    options, weights = zip(*weighted_list)
    return random.choices(options, weights=weights, k=1)[0]


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days),
                              hours=random.randint(8, 18),
                              minutes=random.choice([0, 15, 30, 45]))


def generate_patients():
    patients = []
    for pid in range(1, NUM_PATIENTS + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        age = random.randint(1, 85)
        gender = random.choice(["M", "F"])
        registered_on = random_date(START_DATE, END_DATE).date()
        patients.append([pid, name, age, gender, registered_on])
    return patients


def generate_appointments(patients):
    appointments = []
    for aid in range(1, NUM_APPOINTMENTS + 1):
        patient = random.choice(patients)
        pid = patient[0]
        dept = random.choice(DEPARTMENTS)
        appt_date = random_date(START_DATE, END_DATE)
        status = weighted_choice(APPT_STATUS_WEIGHTS)
        fee = random.choice([300, 400, 500, 600, 800, 1000])
        appointments.append([aid, pid, dept, appt_date, status, fee])
    return appointments


def generate_billing(appointments):
    billing = []
    bid = 1
    for appt in appointments:
        aid, pid, dept, appt_date, status, fee = appt
        if status != "Completed":
            continue  # no bill for no-shows/cancellations
        payment_status = weighted_choice(PAYMENT_STATUS_WEIGHTS)
        payment_method = random.choice(PAYMENT_METHODS)
        billed_amount = fee + random.choice([0, 0, 0, 100, 200])  # occasional add-on charges
        paid_amount = billed_amount if payment_status == "Paid" else (
            round(billed_amount * random.uniform(0.3, 0.8)) if payment_status == "Pending" else 0
        )
        billing.append([bid, aid, pid, billed_amount, paid_amount, payment_status, payment_method])
        bid += 1
    return billing


def generate_feedback(appointments):
    feedback = []
    fid = 1
    for appt in appointments:
        aid, pid, dept, appt_date, status, fee = appt
        if status != "Completed":
            continue
        if random.random() > 0.4:  # not every completed visit gets feedback
            continue
        rating = random.choices([5, 4, 3, 2, 1], weights=[0.35, 0.30, 0.15, 0.12, 0.08])[0]
        if rating >= 4:
            comment = random.choice(FEEDBACK_POSITIVE)
        elif rating == 3:
            comment = random.choice(FEEDBACK_NEUTRAL)
        else:
            comment = random.choice(FEEDBACK_NEGATIVE)
        feedback.append([fid, aid, pid, rating, comment, appt_date.date()])
        fid += 1
    return feedback


def write_csv(path, header, rows):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


def main():
    patients = generate_patients()
    appointments = generate_appointments(patients)
    billing = generate_billing(appointments)
    feedback = generate_feedback(appointments)

    write_csv(DATA_DIR / "patients.csv",
              ["patient_id", "name", "age", "gender", "registered_on"], patients)
    write_csv(DATA_DIR / "appointments.csv",
              ["appointment_id", "patient_id", "department", "appointment_date", "status", "fee"],
              appointments)
    write_csv(DATA_DIR / "billing.csv",
              ["bill_id", "appointment_id", "patient_id", "billed_amount", "paid_amount",
               "payment_status", "payment_method"], billing)
    write_csv(DATA_DIR / "feedback.csv",
              ["feedback_id", "appointment_id", "patient_id", "rating", "comment", "feedback_date"],
              feedback)

    print(f"Generated {len(patients)} patients, {len(appointments)} appointments, "
          f"{len(billing)} bills, {len(feedback)} feedback entries in {DATA_DIR}")


if __name__ == "__main__":
    main()