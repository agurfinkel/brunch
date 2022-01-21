# Configuration files

Place configuration files in yaml format under name `conf.yaml`.
For example,

```yaml
fixedpoint:
  engine: spacer
z3: 
  st: ''
  v: 1
```

Rename to unique easy-to-remember name using 

```bash
$ ./brunch/yama -v conf.yaml -o .
```
