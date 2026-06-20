import importlib
m = importlib.import_module('app.utils')
print('MODULE:', m)
print('HAS safe_import_plotly:', hasattr(m, 'safe_import_plotly'))
print('FILE:', getattr(m, '__file__', None))
print('SAFE funcs:', [n for n in dir(m) if n.startswith('safe')])
print('DONE')
