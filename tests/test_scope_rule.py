import unittest

from stateful_rule_baseline import predict


class StatefulRuleTest(unittest.TestCase):
    def setUp(self):
        self.scope = {"cred_1": {"host_1"}}

    def test_flags_out_of_scope_connection_within_window(self):
        steps = [
            {"action": "read_credential", "resource": "cred_1"},
            {"action": "connect_host", "resource": "host_2"},
        ]
        self.assertEqual(predict(steps, self.scope), 1)

    def test_allows_in_scope_connection(self):
        steps = [
            {"action": "read_credential", "resource": "cred_1"},
            {"action": "connect_host", "resource": "host_1"},
        ]
        self.assertEqual(predict(steps, self.scope), 0)

    def test_forgets_credential_after_window(self):
        steps = [{"action": "read_credential", "resource": "cred_1"}]
        steps += [{"action": "read_file", "resource": "file_1"}] * 6
        steps += [{"action": "connect_host", "resource": "host_2"}]
        self.assertEqual(predict(steps, self.scope), 0)


if __name__ == "__main__":
    unittest.main()
