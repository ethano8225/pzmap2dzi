import os
import yaml
import get_mod_dep

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

########
realdependencies={}
fakedependencies=[]
# note: these are false positives because they contain no \texturepack\ folder, no textures, etc 
#(no effect on map)

def addRequiredModpacks(steamid):
    if steamid in fakedependencies:
        return ""
    if int(steamid) in realdependencies:
        formatted="\n            - "+realdependencies.get(int(steamid))
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
        map_root = os.path.join(mod_path, name, 'media', 'maps')
        fullpath=os.path.join(mod_root, tpath)
        
        #############################
        if has_texture(fullpath) and os.path.isdir(map_root) and int(mod_id) in realdependencies:
            for map_name in os.listdir(map_root):                               #if int(mod_id) in real, that means 
                mpath = os.path.join(mod_id, 'mods', name, 'media', 'maps', map_name)#the map's textures may also be required for other
                if is_map(os.path.join(mod_root, mpath)):                            #maps to load, otherwise other maps don't need it
                    if 'map' in mod:
                        print('multiple maps in single mod:')
                        print(mpath)
                    else:
                        mod['map+texture'] = mpath+":"+tpath
        ##############################
        
        else:
            if has_texture(fullpath):
                mod['texture'] = tpath
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
    
    #############
    dependsavepath=".\\scripts\\dependsave\\"
    if len(os.listdir(dependsavepath)) == 3:
        refreshDepends=1 #force refresh if only default files present
    else:
        with open(dependsavepath+"refreshDepends.txt","r") as refresh:
            if refresh.readline().strip() == "1":
                refreshDepends=1
            else:
                refreshDepends=0
        refresh.close()
    with open('.\\scripts\\dependsave\\realDependencies.txt', 'r') as neededDeps:
        neededModIDsandMFoldername =[line.rstrip() for line in neededDeps]
        for i in range(len(neededModIDsandMFoldername)):
            x=neededModIDsandMFoldername[i].split("\t")

            modID,mapname=x[0],x[1]
            realdependencies[int(modID)]=mapname
    with open('.\\scripts\\dependsave\\fakeDependencies.txt', 'r') as fakeDeps:
        fakeIDs =[line.rstrip() for line in fakeDeps]
        for steamID in fakeIDs:
            fakedependencies.append(steamID)
    #############        Immediately deal with fake, real, and refreshdepends as to ensure depend_textures is correct
    
    with open('conf.yaml', 'r') as f:
        conf = yaml.safe_load(f.read())
    mod_root = conf['mod_root']
    textures = []
    maps = []
    mapandtexture=[]
    for mod_id in os.listdir(mod_root):
        if not os.path.isdir(os.path.join(mod_root, mod_id)):
            continue
        mods = get_mod_conf(mod_root, mod_id)
        for name in mods:
            
            #############
            if 'map+texture' in mods[name]: #adds a new variation, if mod is map and texture,
                mapandtexture.append((name, mods[name],mod_id))
            #############
            
            elif 'map' in mods[name]:
                maps.append((name, mods[name],mod_id))   #add mod_id to support auto-depend_textures
            elif 'texture' in mods[name]:
                textures.append((name, mods[name],mod_id))
    with open('map_data.yaml', 'w') as f:
        f.write('textures:\n')

        for name, t, mod_id in textures:
            f.write('    {}:'.format(name))
            f.write(TEXTURE_TEMPLATE.format(t['texture']))
            f.write('\n\n')
        print(mapandtexture)
        for name, t, mod_id in mapandtexture:
            f.write('    {}:'.format(name))
            save=t['map+texture']
            both=save.split(":")
            mp,text=both[0],both[1]
            f.write(TEXTURE_TEMPLATE.format(text))
            f.write('\n\n')
            
        f.write('maps:' + DEFAULT_MAP)
        f.write('\n')
        for name, m, mod_id in mapandtexture:
            print(name)
            f.write('    {}:'.format(name))
            save=m['map+texture']
            both=save.split(":")
            mp,text=both[0],both[1]
            print(mp, "MP")
            f.write(MAP_TEMPLATE.format(mp))
            pathtosave=dependsavepath+str(mod_id)+".txt"
            if os.path.exists(pathtosave) and refreshDepends==0:
                with open(pathtosave,"r") as depview:
                    neededSteamIDs = [line.rstrip() for line in depview]
                    for steamID in neededSteamIDs:
                            nextitem= addRequiredModpacks(steamID)
                            f.write(nextitem)
                    f.write("\n            - "+name)
                    depview.close()
            else:
                lstOfRecMods=get_mod_dep.get_info(mod_id)
                if len(lstOfRecMods)>0:
                    with open(pathtosave,"w") as depsave:
                        for neededSteamID in lstOfRecMods:
                            depsave.write(str(neededSteamID)+"\n")
                            nextitem= addRequiredModpacks(neededSteamID)
                            f.write(nextitem)
                        f.write("\n            - "+name)
                    depsave.close()
                else:
                    f.write("\n            - "+name) #if no mods req'd but it still needs to call itself
            f.write('\n\n')                          #for example, Eerie Country


        for name, m,mod_id in maps:
            f.write('    {}:'.format(name))
            f.write(MAP_TEMPLATE.format(m['map']))
            
            ################
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
                    if len(lstOfRecMods)>0:
                        with open(pathtosave,"w") as depsave:
                            for neededSteamID in lstOfRecMods:
                                depsave.write(str(neededSteamID)+"\n")
                                nextitem= addRequiredModpacks(neededSteamID)
                                f.write(nextitem)
                        depsave.close()
            with open(dependsavepath+"refreshDepends.txt","w") as refresh:
                refresh.write("0") #set refreshDepends = 0 after getting all {steamid}.txt files}
            refresh.close()        #(opening with "w" overwrites file)
            ################
            
            if 'texture' in m:
                f.write(TEXTURE_TEMPLATE.format(m['texture']))
            f.write('\n\n')
