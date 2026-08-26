import random
import unittest

from generate_dataset import CRED_SCOPE
from generate_stress_test import make_example


def policy_label(steps):
    reads = []
    approvals = set()
    for step in steps:
        if step["action"] == "read_credential":
            reads.append(step["resource"])
        elif step["action"] == "temporary_approval":
            approvals.add(step["resource"])
        elif step["action"] == "connect_host":
            host = step["resource"]
            for credential in reads:
                if host not in CRED_SCOPE[credential] and f"{credential}@{host}" not in approvals:
                    return 1
    return 0


class StressGeneratorTest(unittest.TestCase):
    def test_labels_follow_authorization_history(self):
        rng = random.Random(8128)
        for label in [0, 1]:
            for _ in range(200):
                row = make_example(rng, label)
                self.assertEqual(policy_label(row["steps"]), label)
                self.assertGreaterEqual(len(row["steps"]), 14)
                self.assertLessEqual(len(row["steps"]), 32)


if __name__ == "__main__":
    unittest.main()
