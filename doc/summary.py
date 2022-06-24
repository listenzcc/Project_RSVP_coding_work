# coding: utf-8

mdname = 'workflow'

titles = []

with open('%s.md' % mdname, 'r') as f:
    for j, x in enumerate(f.readlines()):
        if x.startswith('#'):
            print(x)
            titles.append(x)
            # titles.append('%d\n' % j)

with open('%s_catalog.md' % mdname, 'w') as f:
    f.writelines(titles)
