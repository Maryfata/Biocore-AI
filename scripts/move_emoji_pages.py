from pathlib import Path
import shutil

root = Path('app/pages')
backup = Path('app/pages_legacy')
backup.mkdir(parents=True, exist_ok=True)
patterns = ['📊', '🔗', '🎓', '👥', '🤖', '📋', '💨', '🧠', '🦾', '📚', '🏫']
moved = []
for f in root.iterdir():
    if any(p in f.name for p in patterns) and f.is_file():
        destination = backup / f.name
        shutil.move(str(f), str(destination))
        moved.append(f.name)

print('moved', moved)
