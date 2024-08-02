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
textpackmatch = { 926737806: 'Otr', 
                 1254546530: 'Eerie Country', 
                 1703604612: 'jiggasGreenFire', 
                 2337452747: 'Diederiks_tile_Palooza', 
                 2384329562: 'tkTiles_01', 
                 2463499011: 'Grapeseed', 
                 2536865912: 'Blackwood', 
                 2554699200: 'FantaStreetTiles_01', 
                 2595249356: 'Fort Knox linked to Eerie Country', 
                 2599752664: 'DylansTiles', 
                 2734679675: 'GreensTiles', 
                 2740919036: 'SkizotsTiles', 
                 2774834715: 'EN_Newburbs', 
                 2784607980: 'EN_Flags', 
                 2804428637: 'BigZombieMonkeys_tile_pack', 
                 2837923608: 'Perts Party Tiles', 
                 2844685624: "Tryhonesty's Tiles", 
                 2844829195: 'Oujinjin Tiles', 
                 2852704777: 'Simon-MDs-Tiles', 
                 2879745353: 'Melos Tiles for Miles', 
                 2898065560: 'AzaMountainTiles', 
                 2901328637: 'FearsFunkyTiles', 
                 2923495608: 'dylanstiles_bundle', 
                 2925574774: 'Cookie_Tiles', 
                 2977982429: 'DylansTiles_Elysium', 
                 2991554892: 'TileToItemComverter', 
                 3003792372: 'Ryu Tiles'}

falsepositive=['2392987599',#Over the River 2nd route
               '2595785944',#Aquatsar Yacht club
               '2603239477',#ModManager:Server
               '2725216703',#NorthWest Blockade
               '2782415851',#Irvington Road
               '2789257975',#BedfordFalls
               '2803291537',#FortKnoxLinkedtoEerieCountry
               '3085088928',#Leavenburg
               '3085090251',#Leavenburg-Riversdebridge
               '522891356'] #coryerdon
#note: these are false positives because they contain no \texturepack\ folder, no effect on map

def addRequiredModpacks(steamid):
    if steamid in falsepositive:
        return "" #dont add anything to depend_textures
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
                maps.append((name, mods[name],mod_id))   #add mod_id to support auto-depend_textures
            elif 'texture' in mods[name]:
                textures.append((name, mods[name],mod_id))

    with open('map_data.yaml', 'w') as f:
        #################
        dependsavepath=".\\scripts\\dependsave\\"
        if len(os.listdir(dependsavepath)) == 2:
            refreshDepends=1 #force refresh if no mod_id.txt files present
        else:
            with open(dependsavepath+"refreshDepends.txt","r") as refresh:
                if refresh.readline().strip() == "1":
                    refreshDepends=1
                else:
                    refreshDepends=0
            refresh.close()
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
            ################
            startTime = time.time()
            pathtosave=dependsavepath+str(mod_id)+".txt"
            if os.path.exists(pathtosave):
                with open(pathtosave,"r") as depview:
                    neededSteamIDs = [line.rstrip() for line in depview]
                    for steamID in neededSteamIDs:
                        nextitem= addRequiredModpacks(steamID)
                        f.write(nextitem)
                depview.close()
            else:
                if refreshDepends==1:
                    lstOfRecMods=get_mod_dep.get_info(mod_id)
                    if len(lstOfRecMods) > 0:
                        with open(pathtosave,"w") as depsave:
                            for neededSteamID in lstOfRecMods:
                                depsave.write(str(neededSteamID)+"\n")
                                nextitem= addRequiredModpacks(neededSteamID)
                                f.write(nextitem)
                        depsave.close()
            with open(dependsavepath+"refreshDepends.txt","w") as refresh:
                refresh.write("0") #set refreshDepends = 0 after getting all {steamid}.txt files}
            refresh.close()        #(opening with "w" overwrites file)
            total+=(time.time()-startTime)
            ################
            if 'texture' in m:
                f.write(TEXTURE_TEMPLATE.format(m['texture']))
            f.write('\n\n')
        print("depend_textures took",total,"seconds")
