import os
import yaml
import get_mod_dep
import time

DEFAULT_MAP = '''
    default:
        map_root: pz_root
        map_path: |- # map path from map root
            media\\maps\\Muldraugh, KY
        encoding: utf8
        texture_root: pz_root
        texture_path: |- # texture path from textrue root
            media\\texturepacks
        texture_files:
            - Erosion.pack
            - ApCom.pack
            - RadioIcons.pack
            - ApComUI.pack
            - JumboTrees2x.pack
            - Tiles2x.floor.pack
            - Tiles2x.pack
'''

TEXTURE_TEMPLATE = '''
        texture_root: mod_root
        texture_path: |-
            {}
        texture_file_patterns: ['.*[.]pack']'''

MAP_TEMPLATE = '''
        map_root: mod_root
        map_path: |-
            {}
        encoding: utf8
        depend_texutres:
            - default'''

######
textpackmatch = {
    2898065560: 'AzaMountainTiles', 
    2804428637: 'BigZombieMonkeys_tile_pack', 
    2925574774: 'Cookie_Tiles',
    2337452747: 'Diederiks_tile_Palooza',
    2599752664: 'DylansTiles',
    2923495608: 'dylanstiles_bundle',
    2977982429: 'DylansTiles_Elysium',
    2774834715: 'EN_Newburbs',
    2784607980: 'EN_Flags',
    2554699200: 'FantaStreetTiles_01',
    2901328637: 'FearsFunkyTiles',
    2734679675: 'GreensTiles',
    2879745353: 'Melos Tiles for Miles',
    2844829195: 'Oujinjin Tiles',
    3003792372: 'Ryu Tiles',
    2837923608: 'Perts Party Tiles',
    2740919036: 'SkizotsTiles',
    2852704777: 'Simon-MDs-Tiles',
    2384329562: 'tkTiles_01',
    2844685624: "Tryhonesty's Tiles",
    1703604612: 'jiggasGreenFire',
    2463499011: 'Grapeseed',
    2536865912: 'Blackwood',
    2991554892: 'TileToItemComverter',
    1254546530: 'Eerie Country',
    2595249356: 'Fort Knox linked to Eerie Country',
    926737806: 'Otr',

    }

def addRequiredModpacks(steamid):
                   #Otr 2nd rte,    Aquatsar,   MM:Server, NW Blockade, Irvingtn Rd, BdfrdFlls,KnoxLtoEerie,Leavenburg -riversdebridge,   coryerdon,
    falsepositive=["2603239477","2392987599","2725216703","2789257975","2803291537","522891356","2595785944","3085090251","3085088928","2782415851"]
    if steamid in falsepositive:
        return ""
    if int(steamid) in textpackmatch:
        formatted="\n            - "+textpackmatch.get(int(steamid))
    else:
        return "\n            - error: steamid "+str(steamid)
    return formatted
########

def has_texture(tpath):
    if not os.path.isdir(tpath):
        return False
    for f in os.listdir(tpath):
        if f.endswith('.pack'):
            return True
    return False

def is_map(mpath):
    if not os.path.isdir(mpath):
        return False
    for f in os.listdir(mpath):
        if f.endswith('.lotheader'):
            return True
    return False

def get_mod_conf(mod_root, mod_id):
    conf = {}
    mod_path = os.path.join(mod_root, mod_id, 'mods')
    for name in os.listdir(mod_path):
        mod = {}
        tpath = os.path.join(mod_id, 'mods', name, 'media', 'texturepacks')
        if has_texture(os.path.join(mod_root, tpath)):
            mod['texture'] = tpath
        map_root = os.path.join(mod_path, name, 'media', 'maps')
        if os.path.isdir(map_root):
            for map_name in os.listdir(map_root):
                mpath = os.path.join(mod_id, 'mods', name, 'media', 'maps', map_name)
                if is_map(os.path.join(mod_root, mpath)):
                    if 'map' in mod:
                        print('multiple maps in single mod:')
                        print(mpath)
                    else:
                        mod['map'] = mpath
        conf[name] = mod
    return conf

if __name__ == '__main__':
    total=0
    with open('conf.yaml', 'r') as f:
        conf = yaml.safe_load(f.read())
    mod_root = conf['mod_root']
    textures = []
    maps = []
    for mod_id in os.listdir(mod_root):
        if not os.path.isdir(os.path.join(mod_root, mod_id)):
            continue
        mods = get_mod_conf(mod_root, mod_id)
        for name in mods:
            if 'map' in mods[name]:
                maps.append((name, mods[name],mod_id))
            elif 'texture' in mods[name]:
                textures.append((name, mods[name],mod_id))
    
    with open('map_data.yaml', 'w') as f:
        #################
        dependsavepath=".\\scripts\\dependsave\\"
        with open(dependsavepath+"refreshDepends.txt","r") as refresh:
            if refresh.readline().strip() == "1":
                saveTime=1
            else:
                saveTime=0
        ##################
        f.write('textures:\n')
        for name, t, mod_id in textures:
            f.write('    {}:'.format(name))
            f.write(TEXTURE_TEMPLATE.format(t['texture']))
            f.write('\n\n')
        f.write('maps:' + DEFAULT_MAP)
        for name, m,mod_id in maps:
            f.write('    {}:'.format(name))
            f.write(MAP_TEMPLATE.format(m['map']))
            ########
            startTime = time.time()
            pathtosave=dependsavepath+str(mod_id)+".txt"
            if os.path.exists(pathtosave):
                with open(pathtosave,"r") as depview:
                    neededSteamIDs = [line.rstrip() for line in depview]
                    for steamID in neededSteamIDs:
                        nextitem= addRequiredModpacks(steamID)
            else:
                if saveTime==1:
                    lstOfRecMods=get_mod_dep.get_info(mod_id)
                    if len(lstOfRecMods) > 0:
                        with open(pathtosave,"w") as depsave:
                            for neededSteamID in lstOfRecMods:
                                depsave.write(str(neededSteamID)+"\n")
                                nextitem= addRequiredModpacks(neededSteamID)
                                f.write(nextitem)
            total+=(time.time()-startTime)
            ########
            if 'texture' in m:
                f.write(TEXTURE_TEMPLATE.format(m['texture']))
            f.write('\n\n')
        print("depend_textures took",total,"seconds")
