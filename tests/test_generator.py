import random
import unittest

import generate_dataset as generator


def violations(steps):
    found = []
    for first, step in enumerate(steps):
        if step["action"] != "read_credential":
            continue
        credential = step["resource"]
        for second in range(first + 1, min(len(steps), first + generator.WINDOW + 1)):
            candidate = steps[second]
            if (
                candidate["action"] == "connect_host"
                and candidate["resource"] not in generator.CRED_SCOPE[credential]
            ):
                found.append((first, second, credential, candidate["resource"]))
    return found


class GeneratorInvariantTest(unittest.TestCase):
    def setUp(self):
        random.seed(20260825)

    def test_unsafe_examples_contain_generated_violation(self):
        for _ in range(500):
            self.assertTrue(violations(generator.make_unsafe_trajectory()))

    def test_benign_examples_do_not_contain_generated_violation(self):
        for _ in range(500):
            self.assertFalse(violations(generator.make_benign_trajectory()))

    def test_lengths_and_resources_are_in_declared_ranges(self):
        for factory in [generator.make_unsafe_trajectory, generator.make_benign_trajectory]:
            for _ in range(200):
                steps = factory()
                self.assertGreaterEqual(len(steps), generator.MIN_LEN)
                self.assertLessEqual(len(steps), generator.MAX_LEN)
                for step in steps:
                    self.assertIn(step["action"], generator.FILLER_ACTIONS + [
                        "read_credential", "connect_host"
                    ])


if __name__ == "__main__":
    unittest.main()
