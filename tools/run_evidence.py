"""Run a real test phase and retain console output, JUnit, JSON and HTML coverage."""
import json
import subprocess
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[1]
phase = sys.argv[1]
target = sys.argv[2] if len(sys.argv) > 2 else 'tests/'
folder = root / 'docs/evidence' / phase
folder.mkdir(parents=True, exist_ok=True)
command = [sys.executable, '-m', 'pytest', target, '-v', '--tb=short',
           '--junitxml=' + str(folder / 'results.xml'), '--cov=registration',
           '--cov-branch', '--cov-report=term-missing',
           '--cov-report=json:' + str(folder / 'coverage.json'),
           '--cov-report=html:' + str(folder / 'html')]
result = subprocess.run(command, cwd=root, capture_output=True, text=True)
(folder / 'pytest.txt').write_text(result.stdout + result.stderr)
(folder / 'run.json').write_text(json.dumps({
    'command': command, 'exit_code': result.returncode,
    'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip(),
    'source_sha256': __import__('hashlib').sha256((root/'registration.py').read_bytes()).hexdigest(),
    'versions': subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True).splitlines()
}, indent=2)+'\n')
print(result.stdout + result.stderr)
sys.exit(result.returncode)
