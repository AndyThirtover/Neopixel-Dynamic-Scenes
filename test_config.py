import yaml

cfile = open('configs.yaml','w')
cdata = {'guff':'test', 'guff2':4761}
cfile.write(yaml.dump(cdata))
cfile.close()


with open('configs.yaml','r') as rfile:
    cfg = yaml.load(rfile)

for section in cfg:
    print(section)

if cfg.has_key('guff'):
    print("Guff Found")