#!/usr/bin/env python
if __name__ == '__main__':
    import pytest
    import sys
    package_name = 'kwplot'
    mod_dpath = package_name
    test_dpath = 'tests'
    pytest_args = [
        '--cov-config', '.coveragerc',
        '--cov-report', 'html',
        '--cov-report', 'term',
        '--xdoctest',
        '--cov=' + package_name,
        mod_dpath, test_dpath
    ]
    pytest_args = pytest_args + sys.argv[1:]
    sys.exit(pytest.main(pytest_args))
