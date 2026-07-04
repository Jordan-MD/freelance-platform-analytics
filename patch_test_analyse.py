import json
from pathlib import Path
p = Path('analysis/notebooks/test_analyse.ipynb')
nb = json.loads(p.read_text(encoding='utf-8'))
changed = False
for cell in nb['cells']:
    if cell.get('cell_type') != 'code':
        continue
    src = cell['source']
    for i, line in enumerate(src):
        if line == 'csv_path = os.path.join(cwd, "..", "..", "dataset", "dataset_freelance_groupe.csv")\n':
            src[i] = 'csv_path = os.path.join(cwd, "dataset", "dataset_freelance_groupe.csv")\n'
            src[i+1:i+1] = [
                'if not os.path.exists(csv_path):\n',
                '    csv_path = os.path.join(cwd, "..", "..", "dataset", "dataset_freelance_groupe.csv")\n'
            ]
            changed = True
            break
if changed:
    p.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding='utf-8')
    print('updated')
else:
    print('no change')
