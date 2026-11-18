"""Validate model atlas data and build an offline HTML. Python stdlib only."""
import argparse
from html import escape
import json
from pathlib import Path
import re

SKILL = Path(__file__).resolve().parents[1]


def require(ok, message):
    if not ok:
        raise ValueError(message)


def text(value):
    return isinstance(value, str) and bool(value.strip())


def refs_valid(refs, context):
    require(isinstance(refs, list) and refs, f'{context}: refs must contain source evidence')
    for ref in refs:
        require(text(ref.get('label')) and re.match(r'https?://', ref.get('url', '')),
                f'{context}: each ref needs a label and HTTP(S) URL')


def graph_valid(g, context):
    require(text(g.get('title')) and text(g.get('caption')), f'{context}: title/caption required')
    require(isinstance(g.get('boxes'), list) and g['boxes'], f'{context}: boxes required')
    ids, positions = set(), set()
    for box in g['boxes']:
        require(len(box) in (4, 5), f'{context}: box is [id,col,row,title,optional_kind]')
        ident, col, row, title = box[:4]
        require(text(ident) and ident not in ids and text(title), f'{context}: box IDs must be unique')
        require(type(col) is int and type(row) is int and min(col, row) >= 0,
                f'{context}/{ident}: nonnegative integer col/row required')
        require((col, row) not in positions, f'{context}: two boxes occupy the same position')
        ids.add(ident)
        positions.add((col, row))
    require(set(g.get('details', {})) == ids, f'{context}: details must cover every box exactly')
    for ident, detail in g['details'].items():
        require(all(text(detail.get(k)) for k in ('purpose', 'input', 'output', 'operators')),
                f'{context}/{ident}: purpose/input/output/operators required')
    for edge in g.get('edges', []):
        require(len(edge) in (2, 3) and edge[0] in ids and edge[1] in ids,
                f'{context}: edge references an unknown box')
    g.setdefault('edges', [])
    g.setdefault('blocks', [])
    for block in g['blocks']:
        graph_valid(block, context+'/'+block.get('title', '?'))


def validate(data):
    for key in ('model', 'title', 'subtitle', 'baseline', 'dimension_legend'):
        require(text(data.get(key)), f'{key} is required')
    for key in ('paper_url', 'repo_url'):
        require(not data.get(key) or re.match(r'https?://', data[key]), f'{key} must be HTTP(S)')
    require(data.get('groups') and data.get('nodes') and data.get('modes'), 'groups/nodes/modes required')
    groups = {g['id'] for g in data['groups']}
    require(len(groups) == len(data['groups']), 'duplicate group IDs')
    for group in data['groups']:
        require(text(group.get('label')) and re.fullmatch(r'#[0-9a-fA-F]{6}', group.get('color', '')),
                'group needs label and six-digit hex color')
    modes = {m['id'] for m in data['modes']}
    require(len(modes) == len(data['modes']) and all(text(m.get('label')) for m in data['modes']),
            'modes need unique IDs and labels')
    require(data.get('default_mode', data['modes'][0]['id']) in modes, 'invalid default_mode')
    data.setdefault('edges', [])
    ids = {n['id'] for n in data['nodes']}
    require(len(ids) == len(data['nodes']) and all(re.fullmatch(r'[a-z][a-z0-9-]*', i) for i in ids),
            'node IDs must be unique lowercase slugs')
    sections = ('io', 'config', 'mechanics', 'training', 'innovation', 'sources')
    require(all(text(data.get('sections', {}).get(k)) for k in sections), 'all six section bodies required')
    for mode in data['modes']:
        mode_id = mode['id']
        used_positions = set()
        for index, base in enumerate(data['nodes']):
            require(set(base.get('variants', {})) <= modes, f'{base["id"]}: unknown variant mode')
            n = {**base, **base.get('variants', {}).get(mode_id, {})}
            require(n['id'] == base['id'], 'variant must not change node ID')
            require(n.get('group') in groups and text(n.get('title')) and text(n.get('summary')),
                    f'{n["id"]}: group/title/summary required')
            require(len(n.get('overview', [])) == 2 and all(text(s) for s in n['overview']),
                    f'{n["id"]}: explicit overview input/output required')
            require(n.get('ops') and all(len(op) == 2 and all(text(s) for s in op) for op in n['ops']),
                    f'{n["id"]}: ordered ops required')
            require(isinstance(n.get('notes'), list) and all(text(s) for s in n['notes']),
                    f'{n["id"]}: notes must be a list')
            refs_valid(n.get('refs'), n['id'])
            row = index//3
            default_col = 2-index % 3 if row % 2 else index % 3
            pos = n.get('position', [default_col, row])
            require(len(pos) == 2 and all(type(v) is int and v >= 0 for v in pos), 'invalid overview position')
            require(tuple(pos) not in used_positions, 'overview positions overlap')
            used_positions.add(tuple(pos))
            graph_valid(n.get('diagram', {}), mode_id+'/'+n['id'])
        for edge in mode.get('edges', data.get('edges', [])):
            require(len(edge) in (2, 3) and edge[0] in ids and edge[1] in ids,
                    f'{mode_id}: overview edge has an unknown endpoint')
    # Narrative HTML is authored by the agent. Interactive code is supplied separately.
    for sections_data in [data['sections'], *[m.get('sections', {}) for m in data['modes']]]:
        for body in sections_data.values():
            require(isinstance(body, str) and not re.search(r'<script\b|\bon\w+\s*=|javascript:', body, re.I),
                    'section HTML must not contain executable scripts/handlers; use --extra-js')
            require(not re.search(r'<(?:link|iframe|img|video|audio|object|embed)\b', body, re.I),
                    'section embeds need a reviewed local template extension; no remote runtime assets')
    return data


def build(data, extra_js=''):
    validate(data)
    assets = SKILL/'assets'
    template = (assets/'atlas.template.html').read_text(encoding='utf-8')
    replacements = {
        '/*__CSS__*/': (assets/'atlas.css').read_text(encoding='utf-8'),
        '/*__DIAGRAM_JS__*/': (assets/'diagram-runtime.js').read_text(encoding='utf-8'),
        '/*__EXTRA_JS__*/': extra_js,
        '/*__DATA__*/': 'const DATA = '+json.dumps(data, ensure_ascii=False).replace('<', '\\u003c')+';',
    }
    require(not re.search(r'</script\s*>', extra_js, re.I), 'extra JS must not contain a closing script tag')
    for marker, value in replacements.items():
        require(template.count(marker) == 1, f'template marker missing or duplicated: {marker}')
        template = template.replace(marker, value)
    template = template.replace('<title>模型架构图谱</title>', '<title>'+escape(data['model'])+' · 模型架构交互图谱</title>')
    require(not re.search(r'<(?:script|link)\b[^>]*(?:src|href)=["\']https?://', template, re.I),
            'generated page has an external runtime dependency')
    script = re.search(r'<script>([\s\S]*?)</script>', template).group(1)
    return template, script


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('data', type=Path)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--js-output', type=Path)
    parser.add_argument('--extra-js', type=Path)
    args = parser.parse_args()
    data = json.loads(args.data.read_text(encoding='utf-8-sig'))
    page, script = build(data, args.extra_js.read_text(encoding='utf-8') if args.extra_js else '')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding='utf-8')
    if args.js_output:
        args.js_output.parent.mkdir(parents=True, exist_ok=True)
        args.js_output.write_text(script, encoding='utf-8')
    print(f'Built {len(data["nodes"])} modules / {len(data["modes"])} configurations: {args.output}')


if __name__ == '__main__':
    main()
