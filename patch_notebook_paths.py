import json
from pathlib import Path

root = Path(__file__).resolve().parent
notebooks = [
    root / 'analysis' / 'notebooks' / 'test_analyse_uni.ipynb',
    root / 'analysis' / 'notebooks' / 'test_analyse.ipynb',
]

for nb_path in notebooks:
    nb = json.loads(nb_path.read_text(encoding='utf-8'))
    updated = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') != 'code':
            continue
        src = cell['source']
        for i, line in enumerate(src):
            if line == 'csv_path = os.path.join(os.getcwd(), "dataset", "dataset_freelance_groupe.csv")\n':
                src[i] = 'csv_path = os.path.join(os.getcwd(), "..", "..", "dataset", "dataset_freelance_groupe.csv")\n'
                updated = True
            if line == 'csv_path = os.path.join(cwd, "dataset", "dataset_freelance_groupe.csv")\n':
                src[i] = 'csv_path = os.path.join(cwd, "..", "..", "dataset", "dataset_freelance_groupe.csv")\n'
                updated = True
    if updated:
        nb_path.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding='utf-8')
        print(f'patchedd {nb_path.name}')
