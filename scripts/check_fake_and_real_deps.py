import os
import yaml
import get_mod_dep
# This is meant to check for "fake dependencies". some maps say they need something
#to work but don't need their texture files, if their media/texturepacks file doesn't exist, ignore them

extraDebugPrint=True               # change to False if u dont want a lot of print()'s
if __name__ == '__main__':
    with open('conf.yaml', 'r') as f:
        conf = yaml.safe_load(f.read())
    mod_root = conf['mod_root']
    f.close()

    allrequiredmods = []
    realdependencies=[]

    fakedependencies=[]
    notdownloaded_fakedep=[]
    noTextures=[]
    if extraDebugPrint:print("Opening fakeDependencies.txt")
    with open(".\\scripts\\dependsave\\realDependencies.txt","w") as realFile:
        with open(".\\scripts\\dependsave\\fakeDependencies.txt","w") as fakeFile:
            for mod_steamid in os.listdir(mod_root): #C:~\Steam\steamapps\workshop\content\108600\
                RequiredMods=get_mod_dep.get_info(mod_steamid)
                if len(RequiredMods)==0:
                    if extraDebugPrint:print("No required mods for steamID:",mod_steamid)
                    continue #skips mods with 0 required mods
                else:
                    for modSteamID in RequiredMods:
                        if modSteamID not in allrequiredmods: 
                            allrequiredmods.append(modSteamID)
                        else: #skip as the mod has been checked if it's fake or not
                            continue 
                        
                        mod_path = os.path.join(mod_root, modSteamID, 'mods') #C:~\Steam\steamapps\workshop\content\108600\{modSteamID}\mods
                        if os.path.isdir(mod_path)==False:
                            if extraDebugPrint:print("Not downloaded, fake dependency, steamID:",modSteamID,'\n')
                            notdownloaded_fakedep.append(modSteamID)   # If mod DNE in mods, it must be fakemod
                            fakedependencies.append(modSteamID)
                            fakeFile.write(modSteamID+"\n")       #(assuming user accounted for needed mods)
                            continue
                        i=0
                        #Only dealing with existing mods
                        mod_pathDirLen=len(os.listdir(mod_path))
                        breakoutTime=0
                        for name in os.listdir(mod_path):
                            i+=1

                            if extraDebugPrint:print("Now checking modname:",name,"steamID:",modSteamID, "for textures")
                            texturepath = os.path.join(mod_path, name, 'media', 'texturepacks')
                            if os.path.isdir(texturepath):
                                dirsave=os.listdir(texturepath)
                                if len(dirsave)==0 and mod_pathDirLen==i: #dirsave=list of stuff in ~\workshop\content\108600, modpathdirlen prevents
                                        if breakoutTime==0:               #this from auto-skipping other folders in ~\workshop\content\108600\steamModID\
                                            noTextures.append(modSteamID) #(i.e. steamModID\1 contains no texurepack but steamModID\2 has one)
                                            fakedependencies.append(modSteamID)
                                            fakeFile.write(modSteamID+"\n")
                                            if extraDebugPrint:print("modname:",name,"steamID:",modSteamID, "has no textures")
                                        else:
                                            if extraDebugPrint:print("modname:",name,"steamID:",modSteamID, "has no textures, but still a real dependency")
                                        continue
                                else:
                                    if extraDebugPrint:print(modSteamID,"possible real dependency")
                                    for filename in dirsave:
                                        if filename.endswith('.pack'):
                                            if modSteamID not in realdependencies: # don't add dupes
                                                realdependencies.append(modSteamID+":"+name)
                                                realFile.write(modSteamID+"\t"+name+"\n")
                                                if extraDebugPrint:print("Real dependency, checking any other folders in",modSteamID,"\n")
                                            breakoutTime=1
                                            break
                                        print("None of the files in ~/"+modSteamID+'/mods/'+name+'/media/texturepacks are correct (.pack)')
                            else:
                                if extraDebugPrint:print("No texturepacks folder in ~/"+modSteamID+'/mods/'+name+'/media/\nChecking if there are any other folders in',modSteamID+'/mods/')
                                if mod_pathDirLen==i:
                                    if breakoutTime==0:
                                        fakedependencies.append(modSteamID) # downloaded, has no texturepacks folder, fake dep.
                                        fakeFile.write(modSteamID+"\n")
                                        if extraDebugPrint:print("No other folders found, fake dependency.\n")
                                    else:
                                        if extraDebugPrint:print("No other folders found, but still real dependency\n")
            print('\n\nFAKE DEPENDENCIES\n',fakedependencies, "\n",sep="")
            print("\nREAL DEPENDENCIES\n",realdependencies,sep="")
            fakeFile.close()

            if extraDebugPrint==1:
                print("\nExtra info: these are off-cases (still included in fake dependencies)\nNOT DOWNLOADED",notdownloaded_fakedep)
                print("NO TEXTURES",noTextures)
                print("Were all the required mods accounted for?") 
                if len(allrequiredmods)==len(fakedependencies)+len(realdependencies):
                #if this is not true, the length of allrequired does not match fake+real dependencies, aka, some required_mods were missed somehow
                #could be an issue if somehow length matches without all modid's in fakedependencies being different from realdependencies 
                    print("Yes")
                else:
                    print("No")
