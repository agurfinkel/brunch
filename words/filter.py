import sys
import json
import importlib.resources
from . import get_nouns

nouns = get_nouns()
new_nouns = list()

filtered_resource = importlib.resources.files(__package__) / "filtered_nouns.json"

exact = False

bws = list()

if sys.argv[1] == '--exact':
    exact = True
    bws = sys.argv[2:]
else:
    bws = sys.argv[1:]

for n in nouns:
    bad = False
    for bw in bws:
        if (exact and bw == n) or (not exact and bw in n):
            bad = True
            break
  
    if not bad:
        new_nouns.append(n)


with open(filtered_resource, 'w') as f:
    json.dump(new_nouns, f)

print('Eliminated: ')
print(set(nouns)-set(new_nouns))