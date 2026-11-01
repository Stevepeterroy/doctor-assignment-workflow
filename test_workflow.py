import tempfile, unittest, uuid
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from workflow import Scheduler, parse_route


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db = Path(self.tmp.name) / "db"
        self.s = Scheduler(self.db)
        self.s.import_roster(Path(__file__).with_name("doctors.example.csv"))

    def test_unknown_requires_review(self):
        for value in [None, "unknown", "general because patient...", ""]:
            self.assertIsNone(parse_route(value))
        self.assertEqual(
            self.s.assign("unknown", str(uuid.uuid4()))["status"], "REVIEW_REQUIRED"
        )

    def test_idempotent_and_persistent(self):
        request = str(uuid.uuid4())
        first = self.s.assign("general", request)
        self.assertEqual(Scheduler(self.db).assign("general", request), first)
        with self.assertRaises(ValueError):
            self.s.assign("emergency", request)
        self.assertEqual(
            self.s.assign("general", str(uuid.uuid4()))["status"], "REVIEW_REQUIRED"
        )

    def test_concurrent_assignment_no_double_booking(self):
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(
                pool.map(
                    lambda _: Scheduler(self.db).assign("general", str(uuid.uuid4())),
                    range(2),
                )
            )
        self.assertEqual(sum(r["status"] == "ASSIGNED" for r in results), 1)

    def test_reimport_does_not_reset(self):
        self.s.assign("general", str(uuid.uuid4()))
        self.s.import_roster(Path(__file__).with_name("doctors.example.csv"))
        self.assertEqual(
            self.s.assign("general", str(uuid.uuid4()))["status"], "REVIEW_REQUIRED"
        )
