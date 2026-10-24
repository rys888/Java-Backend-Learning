#!/usr/bin/env python3
"""生成 Obsidian 八股复习清单；从计划专属勾选记录生成清单。Python 3.9+，无第三方依赖。"""
import argparse
import collections
import datetime as dt
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import uuid
from zoneinfo import ZoneInfo

BASE = Path(__file__).resolve().parent
ORDER = ['Java 基础', '集合', 'Java 并发编程 JUC', 'Java虚拟机 JVM', 'Spring', 'MySQL', 'Redis', '消息队列']


def read_json(path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding='utf-8'))


def write_text(path, text):
    if path.exists() and path.read_text(encoding='utf-8') == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.tmp')
    temp.write_text(text, encoding='utf-8')
    os.replace(temp, path)


def write_json(path, data):
    write_text(path, json.dumps(data, ensure_ascii=False, indent=2) + '\n')


def scan(vault, source, config):
    result, excluded = {}, []
    include = set(config.get('include', []))
    exclude = set(config.get('exclude', []))
    if not source.is_dir():
        raise ValueError('题库目录不存在：' + str(source))
    for path in sorted(source.rglob('*.md')):
        rel = path.relative_to(source).as_posix()
        text = path.read_text(encoding='utf-8').strip()
        # 显式保留优先；同名目录页只有含站内链接时才自动排除。
        reason = None
        if rel in exclude:
            reason = '配置排除'
        elif rel not in include:
            if not text:
                reason = '空白页'
            elif path.parent == source:
                reason = '总目录'
            elif path.stem == path.parent.name and '[[' in text:
                reason = '目录页'
            elif path.stem == path.parent.name and '跳过' in text:
                reason = '占位页'
        if reason:
            excluded.append({'path': rel, 'reason': reason})
            continue
        key = path.relative_to(vault).as_posix()
        result[key] = {'path': key, 'title': path.stem,
                       'section': path.relative_to(source).parts[0],
                       'digest': hashlib.sha256(text.encode()).hexdigest()}
    return result, excluded


def sync_catalog(state, scanned, today):
    catalog = state['catalog']
    by_path = {v['path']: k for k, v in catalog.items()}
    missing = {k for k, v in catalog.items() if v['path'] not in scanned}
    initial = not catalog
    for path, item in scanned.items():
        key = by_path.get(path)
        if key is None:
            # 内容唯一匹配优先，其次唯一同名匹配；不修改原文来添加 ID。
            candidates = [k for k in missing if catalog[k]['digest'] == item['digest']]
            if not candidates:
                candidates = [k for k in missing if catalog[k]['title'] == item['title']]
            if len(candidates) == 1:
                key = candidates[0]
                missing.remove(key)
            else:
                key = uuid.uuid4().hex
                catalog[key] = {'first_seen': today, 'new': not initial}
        catalog[key].update(item, active=True)
    for key in missing:
        catalog[key]['active'] = False


def reviewed(records, paths, start, today):
    return any(start <= date <= today and any(p in values for p in paths)
               for date, values in records.items())


def update_completion(state, scopes, today):
    """只使用本批次的完成事件，计划外热力图记录不参与轮次计算。"""
    catalog = state['catalog']
    for current in state['rounds']:
        for batch in current['batches']:
            events = scopes.get(str(current['number']) + ':' + batch['date'], {})
            seeds = set(batch.get('seed_done', []))
            dates = {}
            for key in batch['ids']:
                event = events.get(key)
                if event is not None:
                    if event['checked'] and batch['date'] <= event['date'] <= today:
                        dates[key] = event['date']
                elif key in seeds:
                    dates[key] = batch.get('finished_on', batch['date'])
            batch['done'] = list(dates)
            if batch_finished(batch, catalog):
                batch['finished_on'] = max(dates.values(), default=today)
            else:
                batch.pop('finished_on', None)
        completed = {k for b in current['batches'] for k in b['done']}
        active = {k for k in current.get('target_ids', catalog) if catalog[k]['active']}
        if active and active <= completed:
            current['completed_on'] = max(b['finished_on'] for b in current['batches'])
            current['topic_count'] = len(active)
        else:
            current.pop('completed_on', None)


def pending_checkbox_edit(path, state, batch):
    """编辑器的勾选尚未被插件接收时，生成器不得覆盖它。"""
    if not path.exists() or 'rendered_done' not in batch:
        return False
    text = path.read_text(encoding='utf-8')
    paths = {state['catalog'][k]['path'][:-3]: k for k in batch['ids']
             if state['catalog'][k]['active']}
    tasks = {paths[target]: check.lower() == 'x' for check, target in re.findall(
        r'^\s*- \[([ xX])\] \[\[([^|\]]+)\|[^\]]+\]\]', text, re.M) if target in paths}
    if len(tasks) != len(paths):
        return False
    checked = {k for k, value in tasks.items() if value}
    return checked != (set(batch['rendered_done']) & set(paths.values())) and checked != (set(batch['done']) & set(paths.values()))


def select_topics(state, count):
    catalog = state['catalog']
    current = state['rounds'][-1]
    assigned = {k for b in current['batches'] for k in b['ids']}
    pools = collections.defaultdict(list)
    for key, item in catalog.items():
        if item['active'] and key not in assigned:
            pools[item['section']].append(key)
    for keys in pools.values():
        keys.sort(key=lambda k: (not catalog[k]['new'], hashlib.sha256(
            (str(current['number']) + k).encode()).hexdigest()))
    chosen = []
    allocated = collections.Counter()
    sections = sorted(pools, key=lambda s: (ORDER.index(s) if s in ORDER else 99, s))
    # 每个非空板块先安排一篇，再按剩余题量分配。
    for section in sections:
        if len(chosen) >= count:
            break
        chosen.append(pools[section].pop(0))
        allocated[section] += 1
    while len(chosen) < count:
        available = [s for s in sections if pools[s]]
        if not available:
            break
        section = max(available, key=lambda s: len(pools[s]) / (allocated[s] + 1))
        chosen.append(pools[section].pop(0))
        allocated[section] += 1
    return chosen


def batch_finished(batch, catalog):
    return all(k in batch['done'] or not catalog[k]['active'] for k in batch['ids'])


def render_batch(state, batch):
    catalog = state['catalog']
    round_ = next(r for r in state['rounds'] if batch in r['batches'])
    active = {k for k, v in catalog.items() if v['active']}
    done = {k for b in round_['batches'] for k in b['done']} & active
    completed_rounds = sum('completed_on' in r for r in state['rounds'])
    shown = [k for k in batch['ids'] if catalog[k]['active']]
    lines = ['# 今日八股复习', '',
             f"{batch['date']} · 第 {round_['number']} 轮 · 已完成 {completed_rounds} 轮 · 本轮 {len(done)}/{len(active)} · 本次 {len(set(batch['done']) & set(shown))}/{len(shown)}", '']
    groups = collections.defaultdict(list)
    for key in shown:
        groups[catalog[key]['section']].append((key, catalog[key]))
    for section in sorted(groups, key=lambda s: (ORDER.index(s) if s in ORDER else 99, s)):
        lines += ['## ' + section, '']
        for key, item in groups[section]:
            # 完整 vault 相对路径避免同名笔记歧义，别名保持简约。
            lines.append('- [' + ('x' if key in batch['done'] else ' ') + '] [[' + item['path'][:-3] + '|' + item['title'] + ']]')
        lines.append('')
    if not shown:
        lines += ['暂无待复习题目。', '']
    return '\n'.join(lines)


def render_progress(state):
    current = state['rounds'][-1]
    catalog = state['catalog']
    active = {k for k, v in catalog.items() if v['active']}
    done = {k for b in current['batches'] for k in b['done']} & active
    lines = ['# 复习进度', '', f"已完成 {sum('completed_on' in r for r in state['rounds'])} 轮 · 当前第 {current['number']} 轮 · {len(done)}/{len(active)} 篇", '',
             '| 板块 | 已复习 / 题数 |', '| --- | --- |']
    sections = sorted({catalog[k]['section'] for k in active}, key=lambda s: (ORDER.index(s) if s in ORDER else 99, s))
    for section in sections:
        keys = {k for k in active if catalog[k]['section'] == section}
        lines.append(f'| {section} | {len(keys & done)} / {len(keys)} |')
    lines += ['', '## 轮次记录', '', '| 轮次 | 开始 | 完成 | 完成时题数 |', '| --- | --- | --- | --- |']
    for round_ in state['rounds']:
        lines.append(f"| {round_['number']} | {round_['started_on']} | {round_.get('completed_on', '进行中')} | {round_.get('topic_count', '—')} |")
    return '\n'.join(lines) + '\n'


def run(base=BASE, today=None):
    base = base.resolve()
    config = read_json(base / '配置.json')
    count = config['daily_count']
    if not isinstance(count, int) or not 15 <= count <= 25:
        raise ValueError('daily_count 必须是 15 到 25 的整数')
    today = today or dt.datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    dt.date.fromisoformat(today)
    vault = (base / config['vault']).resolve()
    source = vault / config['source']
    marker_path = vault / config['review_records']
    # 读失败时停止，绝不将不可读记录当成“未完成”覆盖进度。
    marker = read_json(marker_path)
    if not isinstance(marker, dict) or not isinstance(marker.get('records'), dict):
        raise ValueError('找不到或无法识别热力图复习记录：' + str(marker_path))
    records = marker['records']
    if any(not isinstance(v, list) or any(not isinstance(p, str) for p in v) for v in records.values()):
        raise ValueError('热力图记录格式无效')
    checks = read_json(base / '.复习勾选.json', {'version': 1, 'batches': {}})
    if checks.get('version') != 1 or not isinstance(checks.get('batches'), dict):
        raise ValueError('复习勾选状态格式无效')
    scopes = checks['batches']
    for events in scopes.values():
        if not isinstance(events, dict):
            raise ValueError('复习勾选事件格式无效')
        for event in events.values():
            if (not isinstance(event, dict) or not isinstance(event.get('checked'), bool)
                    or not isinstance(event.get('date'), str)):
                raise ValueError('复习勾选事件格式无效')
            dt.date.fromisoformat(event['date'])
    scanned, excluded = scan(vault, source, config)
    if not scanned:
        raise ValueError('有效题库为空，保留现有进度与清单')
    state_path = base / '复习状态.json'
    state = read_json(state_path, {'version': 1, 'catalog': {}, 'rounds': [
        {'number': 1, 'started_on': today, 'batches': []}]})
    if state['version'] != 1:
        raise ValueError('不支持的复习状态版本')
    if today < state.get('last_date', today):
        raise ValueError('日期早于上次更新，停止以保护历史进度')
    # 迁移时仅保留已经记入计划的完成状态，之后不再从全局打卡推断。
    if state.get('completion_version') != 2:
        for round_ in state['rounds']:
            for batch in round_['batches']:
                batch['seed_done'] = list(batch.get('done', []))
        state['completion_version'] = 2
    update_completion(state, scopes, today)
    # 每个自然日换题；未完成的批次继续保留在每日记录中。
    current = state['rounds'][-1]
    if current.get('completed_on', today) < today:
        current['target_ids'] = [k for k, v in state['catalog'].items() if v['active']]
        state['rounds'].append({'number': current['number'] + 1, 'started_on': today, 'batches': []})
        for item in state['catalog'].values():
            item['new'] = False
    sync_catalog(state, scanned, today)
    update_completion(state, scopes, today)
    current = state['rounds'][-1]
    if 'completed_on' in current:
        current['topic_count'] = sum(v['active'] for v in state['catalog'].values())
    batch = current['batches'][-1] if current['batches'] else None
    entry_batch = batch
    fixed = base / '今日八股复习.md'
    entry_pending = bool(batch and pending_checkbox_edit(fixed, state, batch))
    if entry_pending and batch['date'] < today:
        write_text(base / '每日记录' / (batch['date'] + '.md'), fixed.read_text(encoding='utf-8'))
    if batch is None or batch['date'] < today:
        ids = select_topics(state, count)
        if not ids:
            # 全部题目已安排，即进入下一轮；旧轮次是否完成仍由实际勾选决定。
            current['target_ids'] = [k for k, v in state['catalog'].items() if v['active']]
            state['rounds'].append({'number': current['number'] + 1, 'started_on': today, 'batches': []})
            for item in state['catalog'].values():
                item['new'] = False
            current = state['rounds'][-1]
            ids = select_topics(state, count)
        if ids:
            if batch:
                batch['end_date'] = (dt.date.fromisoformat(today) - dt.timedelta(days=1)).isoformat()
            batch = {'date': today, 'ids': ids, 'done': [], 'seed_done': []}
            current['batches'].append(batch)
            update_completion(state, scopes, today)
    state['last_date'] = today
    # 每日记录独立保留；未消费的复选框操作不覆盖。
    for round_ in state['rounds']:
        for archived in round_['batches']:
            archive_path = base / '每日记录' / (archived['date'] + '.md')
            if not (entry_pending and archived is entry_batch) and not pending_checkbox_edit(archive_path, state, archived):
                write_text(archive_path, render_batch(state, archived))
                archived['rendered_done'] = list(archived['done'])
    if batch:
        fixed = base / '今日八股复习.md'
        # 换日允许覆盖入口；旧日勾选保留在对应的每日记录。
        if not (entry_pending and batch is entry_batch):
            write_text(fixed, render_batch(state, batch))
    write_text(base / '复习进度.md', render_progress(state))
    write_json(base / '题库索引.json', {'topics': [v for v in state['catalog'].values() if v['active']], 'excluded': excluded})
    write_json(state_path, state)
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', type=Path, default=BASE, help='复习目录（用于隔离验证）')
    args = parser.parse_args()
    base = args.base.resolve()
    with (base / '.update.lock').open('w') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            return
        run(base)


if __name__ == '__main__':
    main()
