import requests
import re

URL_TEMPLATE = 'https://steamcommunity.com/sharedfiles/filedetails/?id={mod_id}'
TITLE_PATTERN = re.compile('<div class="workshopItemTitle">([^<>]*)</div>')
DEP_PATTERN = re.compile('<a href="([^"]*)"[^>]*>\\s*<div class="requiredItem">\\s*(.*?)\\s*</div>\\s*</a>', re.MULTILINE)

def get_info(mod_id):
    url = URL_TEMPLATE.format(mod_id=mod_id)
    rsp = requests.get(url)
    match = TITLE_PATTERN.search(rsp.text)
    depend = []
    for match in DEP_PATTERN.finditer(rsp.text):
        if match:
            dep_id = match.group(1).split('=')[-1]
            depend.append(dep_id)
    return depend
