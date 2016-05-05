import subprocess

__author__ = 'kayvan'

popen = subprocess.Popen("git status | head -n 1 | cut -f 3 -d ' '", stdin=subprocess.PIPE, shell=True,
                         stdout=subprocess.PIPE)
print popen.communicate()[0]
# , "|", "head", "-n", "1", "|", "cut", "-f", "3", "-d", "\' \'"
