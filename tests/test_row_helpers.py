import unittest

from handlers.utils import (
    get_reaction_from_row,
    get_auto_react_from_row,
    parse_reaction_command,
    parse_bos_command,
    parse_subscription_duration,
    get_subscription_duration_seconds,
)
from handlers.admin import parse_admin_command
from handlers.admin import parse_admin_command


class RowHelperTests(unittest.TestCase):
    def test_group_row_uses_reaction_and_auto_react_columns(self):
        row = (1, "Test Group", "🔥", 1, 42, "2024-01-01")
        self.assertEqual(get_reaction_from_row(row), "🔥")
        self.assertTrue(get_auto_react_from_row(row))

    def test_missing_row_falls_back_to_defaults(self):
        self.assertEqual(get_reaction_from_row(None), "random")
        self.assertFalse(get_auto_react_from_row(None))

    def test_reaction_command_parses_simple_and_premium_modes(self):
        self.assertEqual(parse_reaction_command("/reaksiya 👍"), ("react", "👍"))
        self.assertEqual(parse_reaction_command("/reaksiya premium"), ("premium", None))
        self.assertEqual(parse_reaction_command("/reaksiya"), ("selector", None))

    def test_bos_command_parses_count_and_emoji(self):
        self.assertEqual(parse_bos_command("/bos 👍"), (1, "👍"))
        self.assertEqual(parse_bos_command("/bos5 ⭐"), (5, "⭐"))
        self.assertEqual(parse_bos_command("/bos"), (1, None))

    def test_subscription_duration_parses_supported_values(self):
        self.assertEqual(parse_subscription_duration("1 oy"), (1, "month"))
        self.assertEqual(parse_subscription_duration("1 hafta"), (1, "week"))
        self.assertEqual(parse_subscription_duration("48 soat"), (48, "hour"))
        self.assertEqual(parse_subscription_duration("24 soat"), (24, "hour"))
        self.assertEqual(parse_subscription_duration("bir umr"), (1, "forever"))

    def test_admin_command_parses_numeric_counts(self):
        self.assertEqual(parse_admin_command("/admin"), (True, None))
        self.assertEqual(parse_admin_command("/admin11"), (True, 11))
        self.assertEqual(parse_admin_command("/admin100"), (True, 100))
        self.assertEqual(parse_admin_command("/start"), (False, None))


if __name__ == "__main__":
    unittest.main()
