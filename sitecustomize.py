import sys
if any('pytest' in arg for arg in sys.argv):
    import test_compat_runtime
