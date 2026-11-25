import os;
import yaml;
import subprocess;

shipData = {}
lastCommit = None
diff = list()
renderCache = {}

groupReplace = {"Security":"TSFMC", "Sr":"Caelestinus", "Ussp":"USSP", "BlackMarket":"PDV", "Syndicate":"Black Market"}
accessReplace = {"Tsfmc":"TSFMC", "MieyoSecurity":"Mieyo Security"}
engineReplace = {"AME":"IRE"}

class NameGenerator(yaml.YAMLObject):
    yaml_tag = u'!type:NanotrasenNameGenerator'

class GridModEntityReplace(yaml.YAMLObject):
    yaml_tag = u'!type:GridModEntityReplace'

def parseFiles():
    for root, dirs, files in os.walk('Resources\Prototypes\_Mono\Shipyard'):
        if (root == 'Resources\Prototypes\_Mono\Shipyard' or root == 'Resources\Prototypes\_Mono\Shipyard\Base'):
            continue
        for file in files:
            path = os.path.join(root, file)
            with open(path, "r", errors='ignore') as f:
                data = (yaml.full_load(f))[0]
                shipData[data['id']] = data

def buildTSV():
    out = "Name\tDescription\tPrice\tPurchasable\tCategory\tGroup\tClass\tEngine\tRequired Access\n"
    for data in shipData.values():
        price = data['price']
        if price:
            price = format(price, ",")
        else:
            price = ''
        imageLink = f'[[File:ShipRender-{id}.png|center|x200px]]'
        out = out + ("%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" % (imageLink, data.get('name', ''), data.get('description', ''), price, ('No' if data.get('purchasable') == False else 'Yes'), data.get('category', ''), data.get('group', ''), data.get('class', ''), data.get('engine', ''), data.get('access', 'None')))
    with open('out.tsv', "w") as f:
        f.write(out)

def buildWikiTable():
    out = '{| class="wikitable sortable"\n!Image\n!Name\n!Description\n!Price\n!Purchasable\n!Category\n!Group\n!Class(es)\n!Engine(s)\n!Required Access(es)'
    for id, data in shipData.items():
        price = data['price']
        if price:
            price = format(price, ",")
        else:
            price = ''
        imageLink = f'[[File:ShipRender-{id}.png|center|x200px]]'

        group = data.get('group', '')
        group = groupReplace.get(group, group)

        access = data.get('access', '')
        access = accessReplace.get(access, access)

        engines = data.get('engine', [])
        for i in range(len(engines)):
            engines[i] = engineReplace.get(engines[i], engines[i])

        out = out + "\n|-\n|" + "\n|".join([imageLink, data.get('name', ''), data.get('description', ''), price, ('No' if data.get('purchasable') == False else 'Yes'), data.get('category', ''), group, ", ".join(data.get('class', '')), ", ".join(engines), access])
    out = out + "\n|}"
    with open("wikitable.txt", "w") as f:
        f.write(out)

def listPaths():
    out = "dotnet run --project Content.MapRenderer "
    paths = list()
    for data in shipData.values():
        if data['shuttlePath'] in diff:
            paths.append(data['shuttlePath'])
    out = out + " ".join(paths)
    print(out)

def render():
    cmd = ["dotnet", "run", "--no-build", "--project", "Content.MapRenderer"]
    for data in shipData.values():
        if data['shuttlePath'] in diff:
            path:str = data['shuttlePath']
            cmd.append(path)
            shortPath = path[path.rindex('/')+1:path.index('.yml')]
            renderCache[data['id']] = f"Resources\MapImages\{shortPath}\{shortPath}-0.png"
    subprocess.run(cmd)

def getDiff():
    global diff
    cmd = ["git", "diff", "HEAD~", "HEAD", "--name-only"]
    diff = subprocess.run(cmd, stdout=subprocess.PIPE).stdout
    diff = diff.splitlines()
    diff = list(map(lambda n: "/"+str(os.path.relpath(str(n, encoding='utf-8'), 'Resources')).replace('\\', '/'), diff))

def run() -> dict:
    getDiff()
    parseFiles()
    # buildWikiTable()
    render()
    return renderCache
