import json
from pathlib import Path

root = Path(__file__).resolve().parent
notebooks = [root / 'analysis' / 'notebooks' / 'test_analyse_uni.ipynb', root / 'analysis' / 'notebooks' / 'test_analyse.ipynb']
changed_any = False

for nb_path in notebooks:
    nb = json.loads(nb_path.read_text(encoding='utf-8'))
    changed = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        src = cell.get('source', [])
        text = ''.join(src)
        if 'dataset_freelance_groupe.csv' not in text:
            continue

        if nb_path.name == 'test_analyse.ipynb':
            old_block = [
                'try:\n',
                '    script_dir = os.path.dirname(os.path.abspath(__file__))\n',
                'except NameError:\n',
                '    script_dir = os.getcwd()\n',
                'csv_path = os.path.join(script_dir, "..", "..", "dataset", "dataset_freelance_groupe.csv")\n',
                'csv_path = os.path.normpath(csv_path)\n',
            ]
            if all(line in src for line in old_block):
                new_block = [
                    'cwd = os.getcwd()\n',
                    'csv_path = os.path.join(cwd, "..", "..", "dataset", "dataset_freelance_groupe.csv")\n',
                    'if not os.path.exists(csv_path):\n',
                    '    csv_path = os.path.join(cwd, "..", "dataset", "dataset_freelance_groupe.csv")\n',
                    'csv_path = os.path.normpath(csv_path)\n',
                ]
                start = None
                for i in range(len(src) - len(old_block) + 1):
                    if src[i:i+len(old_block)] == old_block:
                        start = i
                        break
                if start is not None:
                    src[start:start+len(old_block)] = new_block
                    cell['source'] = src
                    changed = True
            elif 'script_dir = os.path.dirname(os.path.abspath(__file__))\n' in text:
                # fallback: replace the specific lines if they appear in a reflowed block
                new_src = []
                skip = False
                for line in src:
                    if line == 'try:\n' and 'script_dir = os.path.dirname(os.path.abspath(__file__))\n' in ''.join(src):
                        skip = True
                        continue
                    if skip and line.startswith('except NameError:'):
                        continue
                    if skip and line.startswith('    script_dir = os.getcwd()'):
                        continue
                    if skip and line.startswith('csv_path = os.path.join(script_dir'):
                        new_src.extend(new_block)
                        skip = False
                        continue
                    if skip and line.startswith('csv_path = os.path.normpath(csv_path)'):
                        continue
                    if skip and line.startswith('try:'):
                        continue
                    if not skip:
                        new_src.append(line)
                cell['source'] = new_src
                changed = True

    if changed:
        nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding='utf-8')
        print(f'Updated {nb_path.name}')
        changed_any = True

if not changed_any:
    print('No notebook references needed patching.')
