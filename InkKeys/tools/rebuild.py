"""Re-export the delivered editable PSD with pinned PSD2Live, without GPU inference."""
from pathlib import Path
import subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
app=ROOT/'workspace/tools/PSD2Live/app'
assert list(app.glob('*.jar')), 'Run tools/setup_tools.py first; it verifies the pinned upstream archive.'
assert (ROOT/'source/InkKeys.psd').is_file(), 'Final editable PSD is missing'
subprocess.run(['java','-Dfile.encoding=UTF-8','--class-path',str(app/'*'),str(ROOT/'tools/BuildInkKeys.java'),str(ROOT/'source/InkKeys.psd'),str(ROOT/'workspace/export')],check=True,cwd=ROOT)
subprocess.run([sys.executable,str(ROOT/'tools/package_model.py')],check=True,cwd=ROOT)
subprocess.run([sys.executable,str(ROOT/'tools/check_assets.py'),'model'],check=True,cwd=ROOT)
subprocess.run([sys.executable,str(ROOT/'tools/test_input_positions.py')],check=True,cwd=ROOT)
print('Re-export complete. Run tools/test_native.py on Windows before replacing an installed model.')
