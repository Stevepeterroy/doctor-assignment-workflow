"""Fictional scheduling demonstration. No clinical triage or live LLM calls."""

import argparse, csv, json, sqlite3, uuid
from contextlib import closing
from pathlib import Path

WARDS = {"general", "emergency", "mental_health"}


def parse_route(output):
    # Fail closed: free-form explanations and unknown labels require human review.
    if not isinstance(output, str) or output.strip().lower() not in WARDS:
        return None
    return output.strip().lower()


class Scheduler:
    def __init__(self, path):
        self.path = str(path)
        with closing(self.connect()) as db, db:
            db.executescript(
                "CREATE TABLE IF NOT EXISTS doctors(name TEXT PRIMARY KEY,ward TEXT NOT NULL,available INTEGER NOT NULL);CREATE TABLE IF NOT EXISTS assignments(request_id TEXT PRIMARY KEY,doctor TEXT NOT NULL,ward TEXT NOT NULL);"
            )

    def connect(self):
        return sqlite3.connect(self.path, timeout=10)

    def import_roster(self, path):
        with open(path, newline="") as f:
            rows = list(csv.DictReader(f))
        for r in rows:
            if (
                not r.get("doctor_name", "").strip()
                or r.get("ward") not in WARDS
                or r.get("status") not in {"active", "inactive"}
            ):
                raise ValueError("Invalid fictional roster")
        with closing(self.connect()) as db, db:
            for r in rows:
                # Re-import must never reset already assigned availability.
                db.execute(
                    "INSERT OR IGNORE INTO doctors VALUES(?,?,?)",
                    (r["doctor_name"].strip(), r["ward"], int(r["status"] == "active")),
                )

    def assign(self, route, request_id):
        ward = parse_route(route)
        if ward is None:
            return {
                "status": "REVIEW_REQUIRED",
                "reason": "Unknown or unavailable classification; human review required",
            }
        try:
            uuid.UUID(request_id)
        except (ValueError, TypeError, AttributeError):
            raise ValueError("request_id must be a UUID")
        with closing(self.connect()) as db, db:
            db.execute("BEGIN IMMEDIATE")
            prior = db.execute(
                "SELECT doctor,ward FROM assignments WHERE request_id=?", (request_id,)
            ).fetchone()
            if prior:
                if prior[1] != ward:
                    raise ValueError("Request ID belongs to a different route")
                return {"status": "ASSIGNED", "doctor": prior[0], "ward": ward}
            doctor = db.execute(
                "SELECT name FROM doctors WHERE ward=? AND available=1 ORDER BY name LIMIT 1",
                (ward,),
            ).fetchone()
            if not doctor:
                return {
                    "status": "REVIEW_REQUIRED",
                    "reason": "No available fictional doctor",
                }
            db.execute("UPDATE doctors SET available=0 WHERE name=?", (doctor[0],))
            db.execute(
                "INSERT INTO assignments VALUES(?,?,?)", (request_id, doctor[0], ward)
            )
            return {"status": "ASSIGNED", "doctor": doctor[0], "ward": ward}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", default="demo.sqlite3")
    parser.add_argument("--roster")
    parser.add_argument("--route")
    parser.add_argument("--request-id", default=str(uuid.uuid4()))
    args = parser.parse_args()
    scheduler = Scheduler(args.db)
    if args.roster:
        scheduler.import_roster(args.roster)
    if args.route:
        print(json.dumps(scheduler.assign(args.route, args.request_id)))
