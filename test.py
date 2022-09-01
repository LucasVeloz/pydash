import unittest
from r2a.r2ahash import R2AHash


class R2AHashTest(unittest.TestCase):
  def __init__(self, methodName: str = ...):
    super().__init__(methodName)
    self.r2aHash = R2AHash(1)

  def test_start(self):
    self.assertEqual(self.r2aHash.current_quality.get('current'), 'H')
    self.assertEqual(self.r2aHash.current_quality.get('old'), 'H')
    self.assertEqual(self.r2aHash.timer.get('average'), 0)
    self.assertEqual(self.r2aHash.timer.get('start'), 0)
    self.assertEqual(self.r2aHash.timer.get('end'), 0)

  def test_quality_by_time(self):
    self.assertEqual(self.r2aHash.get_quality_by_time(0.01), 'H')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.1), 'HM')
    self.assertEqual(self.r2aHash.get_quality_by_time(1), 'HL')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.09), 'HM')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.9), 'HM')
    self.assertEqual(self.r2aHash.get_quality_by_time(9), 'HL')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.009), 'H')

    self.r2aHash.current_quality['old'] = 'M'

    self.assertEqual(self.r2aHash.get_quality_by_time(0.01), 'MH')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.1), 'M')
    self.assertEqual(self.r2aHash.get_quality_by_time(1), 'ML')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.09), 'M')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.9), 'M')
    self.assertEqual(self.r2aHash.get_quality_by_time(9), 'ML')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.009), 'MH')

    self.r2aHash.current_quality['old'] = 'L'

    self.assertEqual(self.r2aHash.get_quality_by_time(0.01), 'LH')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.1), 'LM')
    self.assertEqual(self.r2aHash.get_quality_by_time(1), 'L')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.09), 'LM')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.9), 'LM')
    self.assertEqual(self.r2aHash.get_quality_by_time(9), 'L')
    self.assertEqual(self.r2aHash.get_quality_by_time(0.009), 'LH')

  def test_update_quality(self):
    self.r2aHash.update_quality()


if __name__ == '__main__':
    unittest.main()