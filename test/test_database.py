import unittest
from ytracker.database import Criteria


class TestCriteria(unittest.TestCase):

    def setUp(self) -> None:
        self.criteria = Criteria()

    def test_init(self):
        self.assertIsInstance(self.criteria, Criteria)
        self.assertEqual('', self.criteria._where)
        self.assertEqual('', self.criteria._order_by)

    def test_where_returns_self(self):
        criteria_object = self.criteria.where('')
        self.assertIsInstance(criteria_object, Criteria)

    def test_order_by_returns_self(self):
        criteria_object = self.criteria.order_by('')
        self.assertIsInstance(criteria_object, Criteria)

    def test_dunder_str_where(self):
        self.criteria.where("id = 'id1'")
        self.assertEqual("WHERE id = 'id1'", str(self.criteria))

    def test_dunder_str_where_multiple(self):
        self.criteria.where("id = 'id1'").where("deleted = 'True'")
        self.assertEqual("WHERE id = 'id1' AND deleted = 'True'", str(self.criteria))

    def test_dunder_str_where_multiple_and_logical_operator(self):
        self.criteria.where("id = 'id1'", 'OR').where("deleted = 'True'")
        self.assertEqual("WHERE id = 'id1' OR deleted = 'True'", str(self.criteria))

    def test_dunder_str_order_by(self):
        self.criteria.order_by('created_at')
        self.assertEqual('ORDER BY created_at', str(self.criteria))

    def test_dunder_str_order_by_multiple(self):
        self.criteria.order_by('created_at').order_by('deleted')
        self.assertEqual('ORDER BY created_at, deleted', str(self.criteria))

    def test_dunder_str_order_by_multiple_and_descending(self):
        self.criteria.order_by('created_at', 'DESC')
        self.assertEqual('ORDER BY created_at DESC', str(self.criteria))

    def test_dunder_str_order_by_multiple_descending(self):
        self.criteria.order_by('created_at', 'DESC').order_by('updated_at', 'DESC')
        self.assertEqual('ORDER BY created_at DESC, updated_at DESC', str(self.criteria))

    def test_dunder_order_by_descending_lower_case(self):
        self.criteria.order_by('created_at', 'desc')
        self.assertEqual('ORDER BY created_at DESC', str(self.criteria))

    def test_dunder_str_where_and_order_by_multiple_and_descending(self):
        (self.criteria
         .where("id = 'id1'", 'AND')
         .where("deleted = 'False'")
         .order_by('created_at', 'desc')
         .order_by('updated_at', 'desc'))
        self.assertEqual(
            "WHERE id = 'id1' AND deleted = 'False' ORDER BY created_at DESC, updated_at DESC",
            str(self.criteria)
        )


if __name__ == '__main__':
    unittest.main()