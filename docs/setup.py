import os

from hesiod import __version__

conf_file = "docs/source/conf.py"
with open(conf_file) as f:
    lines = f.readlines()

release_prefix = "release = "
with open("docs/source/conf.py", "wt") as f:
    for line in lines:
        if not release_prefix in line:
            f.write(line)
    f.write(f'{release_prefix}"{__version__}"\n')

os.system("poetry export -f requirements.txt -o docs/requirements.txt --without-hashes")
