"""在临时 vault 验证真实状态流转，不读取或写入正式标记。"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('review', Path(__file__).with_name('更新复习.py'))
review = importlib.util.module_from_spec(spec)
spec.loader.exec_module(review)


class ReviewTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.vault = Path(self.temp.name)
        self.base = self.vault / 'java' / '八股复习'
        self.base.mkdir(parents=True)
        self.marker = self.vault / 'markers.json'
        self.records = {}
        self.save_records()
        self.config = {'daily_count': 20, 'vault': '../..', 'source': 'java/八股笔记',
                       'review_records': 'markers.json', 'include': [], 'exclude': []}
        review.write_json(self.base / '配置.json', self.config)
        for i in range(47):
            self.add('板块' + str(i % 8), '题' + str(i))
        self.add('板块0', '板块0', '[[题0]]')
        self.add('板块0', '空白', '')

    def tearDown(self):
        self.temp.cleanup()

    def add(self, section, title, text=None):
        path = self.vault / 'java/八股笔记' / section / (title + '.md')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text if text is not None else '知识内容：' + title)
        return path

    def save_records(self):
        review.write_json(self.marker, {'records': self.records})

    def run_day(self, day):
        return review.run(self.base, '2026-10-' + str(day))

    def mark(self, day, paths):
        # 模拟插件：通用热力图之外，仅对当前清单生成批次专属事件。
        self.records['2026-10-' + str(day)] = paths
        self.save_records()
        state = review.read_json(self.base / '复习状态.json')
        current = state['rounds'][-1]
        batch = current['batches'][-1]
        scope_path = self.base / '.复习勾选.json'
        scope = review.read_json(scope_path, {'version': 1, 'batches': {}})
        events = {}
        whole = 'java/八股复习/今日八股复习.md' in paths
        for key in batch['ids']:
            events[key] = {'checked': whole or state['catalog'][key]['path'] in paths,
                           'date': '2026-10-' + str(day)}
        scope['batches'][str(current['number']) + ':' + batch['date']] = events
        review.write_json(scope_path, scope)

    def test_daily_refresh_toggle_and_new_topics(self):
        state = self.run_day(23)
        batch = state['rounds'][-1]['batches'][-1]
        ids = batch['ids']
        self.assertEqual(len(ids), 20)
        self.assertEqual(len({state['catalog'][k]['section'] for k in ids}), 8)
        self.assertEqual(sum(v['active'] for v in state['catalog'].values()), 47)
        content = (self.base / '今日八股复习.md').read_bytes()
        self.run_day(23)
        self.assertEqual(content, (self.base / '今日八股复习.md').read_bytes())
        self.mark(23, [state['catalog'][ids[0]]['path']])
        state = self.run_day(23)
        self.assertEqual(state['rounds'][-1]['batches'][-1]['done'], ids[:1])
        self.mark(23, [])
        self.assertFalse(self.run_day(23)['rounds'][-1]['batches'][-1]['done'])
        self.add('板块0', '新补题')
        next_state = self.run_day(24)
        self.assertFalse(set(next_state['rounds'][-1]['batches'][-1]['ids']) & set(ids))
        self.assertTrue(any(next_state['catalog'][k]['title'] == '新补题' for k in next_state['rounds'][-1]['batches'][-1]['ids']))
        self.mark(24, ['java/八股复习/今日八股复习.md'])
        self.run_day(24)
        state = self.run_day(25)
        next_ids = state['rounds'][-1]['batches'][-1]['ids']
        self.assertFalse(set(ids) & set(next_ids))
        self.assertEqual(len(state['rounds'][-1]['batches']), 3)
        # 前一天固定入口的标记不会把新清单整份标成完成。
        self.assertFalse(state['rounds'][-1]['batches'][-1]['done'])
        # 各个双链都能指向真实文件。
        for item in state['catalog'].values():
            if item['active']:
                self.assertTrue((self.vault / item['path']).is_file())

    def test_round_history_and_next_round(self):
        seen = set()
        for day, expected in [(23, 20), (24, 20), (25, 7)]:
            state = self.run_day(day)
            batch = state['rounds'][-1]['batches'][-1]
            self.assertEqual(len(batch['ids']), expected)
            self.assertFalse(seen & set(batch['ids']))
            seen.update(batch['ids'])
            self.mark(day, [state['catalog'][k]['path'] for k in batch['ids']])
            state = self.run_day(day)
        self.assertEqual(len(seen), 47)
        self.assertEqual(state['rounds'][-1]['completed_on'], '2026-10-25')
        self.assertEqual(len(self.run_day(25)['rounds']), 1)
        self.add('板块0', '轮后新题')
        state = self.run_day(26)
        self.assertEqual(len(state['rounds']), 2)
        self.assertEqual(state['rounds'][0]['topic_count'], 47)
        self.assertEqual(state['rounds'][1]['number'], 2)
        self.assertEqual(len(state['rounds'][1]['batches'][0]['ids']), 20)
        self.assertFalse(state['rounds'][1]['batches'][0]['done'])

    def test_extra_review_does_not_complete_future_batch_or_round(self):
        state = self.run_day(23)
        batch = state['rounds'][-1]['batches'][-1]
        unassigned = [k for k, v in state['catalog'].items() if k not in batch['ids']]
        extra_paths = [state['catalog'][k]['path'] for k in unassigned]
        self.records['2026-10-23'] = extra_paths
        self.save_records()
        state = self.run_day(23)
        self.assertFalse(state['rounds'][-1]['batches'][-1]['done'])
        self.mark(23, ['java/八股复习/今日八股复习.md'])
        state = self.run_day(23)
        self.records['2026-10-24'] = extra_paths
        self.save_records()
        state = self.run_day(24)
        next_batch = state['rounds'][-1]['batches'][-1]
        self.assertTrue(set(next_batch['ids']) <= set(unassigned))
        self.assertFalse(next_batch['done'])
        self.assertNotIn('completed_on', state['rounds'][-1])
        self.assertEqual(sum(len(b['done']) for b in state['rounds'][-1]['batches']), 20)

    def test_daily_new_batch_without_completing_yesterday(self):
        first = self.run_day(23)
        ids = first['rounds'][0]['batches'][0]['ids']
        second = self.run_day(24)
        next_batch = second['rounds'][0]['batches'][-1]
        self.assertEqual(len(next_batch['ids']), 20)
        self.assertEqual(next_batch['date'], '2026-10-24')
        self.assertFalse(set(ids) & set(next_batch['ids']))
        self.assertTrue((self.base / '每日记录/2026-10-23.md').exists())
        self.assertTrue((self.base / '每日记录/2026-10-24.md').exists())
        self.assertFalse(second['rounds'][0]['batches'][0]['done'])

    def test_pending_checkbox_edit_not_overwritten(self):
        self.run_day(23)
        page = self.base / '今日八股复习.md'
        text = page.read_text().replace('- [ ]', '- [x]', 1)
        page.write_text(text)
        self.run_day(23)
        self.assertEqual(page.read_text(), text)

    def test_rename_edit_delete_and_bad_input(self):
        state = self.run_day(23)
        batch = state['rounds'][-1]['batches'][-1]
        key = batch['ids'][0]
        item = state['catalog'][key]
        old = self.vault / item['path']
        new = old.with_name('改名后.md')
        old.rename(new)
        state = self.run_day(23)
        self.assertTrue(state['catalog'][key]['active'])
        self.assertTrue(state['catalog'][key]['path'].endswith('改名后.md'))
        new.write_text('补充内容')
        self.assertIn(key, self.run_day(23)['rounds'][-1]['batches'][-1]['ids'])
        new.unlink()
        self.assertFalse(self.run_day(23)['catalog'][key]['active'])
        state_before = (self.base / '复习状态.json').read_bytes()
        self.marker.write_text('{ invalid')
        with self.assertRaises(json.JSONDecodeError):
            self.run_day(24)
        self.assertEqual((self.base / '复习状态.json').read_bytes(), state_before)


if __name__ == '__main__':
    unittest.main(verbosity=2)
