import compileall
import sys
ok = compileall.compile_dir('app', force=True)
print('compiled=', ok)
sys.exit(0 if ok else 2)
