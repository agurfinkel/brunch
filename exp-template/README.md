```
python3.9 -m venv .venv
vim ./.venv/lib/python3.9/site-packages/brunch.pth
source ./.venv/bin/activate
pip install -r /ag/brunch/requirements.txt
python -m spacer.name_z3 /ag/bat-exp/bin/z3 -o bin
vim conf/opts.yaml
python -m spacer.yama conf/opts.yaml  -o ./conf
find /ag/bat-exp/data/ldv-bat -name '*.smt2' | head > ldv-bat.idx
python -m spacer.mktool bin/z3_deep_space-hit-c34b1d0 conf/z3-spurned.yaml
python -m spacer.mkpar run/hit-spurned.sh idx/ldv-bat.idx
time ./run/run-hit-spurned.sh
python -m spacer.log_scrab -o out/hit.spurned.ldv-bat.mymble.cervix.18_01_2022-t20-24-58/stats.csv out/hit.spurned.ldv-bat.mymble.cervix.18_01_2022-t20-24-58
```
