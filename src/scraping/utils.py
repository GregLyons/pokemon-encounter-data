import re
import urllib.request

from bs4 import BeautifulSoup


# Path to data folder
def getEncounterDataPath():
    return 'src\\data\\encounter-data\\'

# Current number of generations of Pokemon


def numberOfGens():
    return 8

# Returns BeautifulSoup object given link


def openLink(url, retryCount, retryMax):
    try:
        req = urllib.request.Request(
            url, headers={'User-Agent': "Magic Browser"})
        html = urllib.request.urlopen(req)
        bs = BeautifulSoup(html.read(), 'html.parser')
        return bs
    except urllib.error.HTTPError:
        if retryCount < retryMax:
            openLink(url, retryCount + 1, retryMax)
    else:
        return None

# converts roman numeral for gen to arabic numeral


def genSymbolToNumber(roman):
    roman = roman.rstrip('\n')
    if roman.upper() == 'I':
        return 1
    elif roman.upper() == 'II':
        return 2
    elif roman.upper() == 'III':
        return 3
    elif roman.upper() == 'IV':
        return 4
    elif roman.upper() == 'V':
        return 5
    elif roman.upper() == 'VI':
        return 6
    elif roman.upper() == 'VII':
        return 7
    elif roman.upper() == 'VIII':
        return 8
    elif roman.upper() == 'IX':
        return 9
    else:
        raise ValueError('Not a valid gen.')

# converts dex number to gen


def dexNumberToGen(dexNumber):
    dexNumber = int(dexNumber)
    if dexNumber <= 151:
        return 1
    elif dexNumber <= 251:
        return 2
    elif dexNumber <= 386:
        return 3
    elif dexNumber <= 493:
        return 4
    elif dexNumber <= 649:
        return 5
    elif dexNumber <= 721:
        return 6
    elif dexNumber <= 809:
        return 7
    else:
        return 8

#


def versionGroupDictionary():
    versionDict = {
        "RB": ["Red/Blue", 1],
        "Y": ["Yellow", 1],
        "Stad": ["Stadium", 1],
        "GS": ["Gold/Silver", 2],
        "C": ["Crystal", 2],
        "Stad2": ["Stadium 2", 2],
        "RS": ["Ruby/Sapphire", 3],
        "E": ["Emerald", 3],
        "Colo": ["Colosseum", 3],
        "XD": ["XD: Gale of Darkness", 3],
        "FRLG": ["Fire Red/Leaf Green", 3],
        "DP": ["Diamond/Pearl", 4],
        "Pt": ["Platinum", 4],
        "HGSS": ["Heart Gold/Soul Silver", 4],
        "PBR": ["Pokemon Battle Revolution", 4],
        "BW": ["Black/White", 5],
        "B2W2": ["Black 2/White 2", 5],
        "XY": ["X/Y", 6],
        "ORAS": ["Omega Ruby/Alpha Sapphire", 6],
        "SM": ["Sun/Moon", 7],
        "USUM": ["Ultra Sun/Ultra Moon", 7],
        "PE": ["Let's Go Pikachu/Let's Go Eeevee", 7],
        "SwSh": ["Sword/Shield", 8],
        "BDSP": ["Brilliant Diamond/Shining Pearl", 8]
    }

    return versionDict

# given gen, returns list of version group codes for that gen


def getVersionGroupsInGen(gen):
    if gen in range(numberOfGens() + 1):
        versionGroupProtoDict = versionGroupDictionary()

        return [versionGroup for versionGroup in versionGroupProtoDict.keys() if versionGroupProtoDict[versionGroup][-1] == gen]
    else:
        raise ValueError("Not a valid Gen!")

# parse names in different forms from Bulbapedia to a common, snake_case form


def parseName(text):
    text = text.strip('\n')
    # extract species and form data (latter in parentheses, if present)
    if '(' in text:
        speciesAndForm = [part.strip().strip(')') for part in text.split('(')]
        speciesName = speciesAndForm[0]
        form = speciesAndForm[1].replace('(', '').replace(')', '')

        # remove 'Form' and 'Forme'
        form = re.sub(r'[Ff]orme*', '', form)

        # various cases to handle
        if speciesName in ['Wormadam', 'Burmy']:
            form = form.replace('Cloak', '')
        elif speciesName in ['Darmanitan', 'Morpeko']:
            form = form.replace('Mode', '')
            # switch order 'Galarian Standard' to 'Standard Galarian for Darmanitan; does nothing for Morpeko'
            form = re.sub(r'Galarian (Standard|Zen)', r'\1 Galarian', form)
        elif speciesName == 'Oricorio':
            form = form.replace('Style', '')
        elif speciesName == 'Urshifu':
            #  preserve 'Rapid Strike' to match with Smogon API
            form = form.replace('Single Strike Style', '')
            form = form.replace('Rapid Strike Style', 'Rapid Strike')
        elif speciesName in ['Zacian', 'Zamazenta']:
            # Bulbapedia adds 'Hero of Many Battles', but Smogon does not
            form = form.replace('Hero of Many Battles', '')
            # Zacian and Zamazenta, remove noun in 'Crowned [noun]'
            form = form.replace('Sword', '')
            form = form.replace('Shield', '')
        elif speciesName in ['Pumpkaboo', 'Gourgeist']:
            form = form.replace('Size', '')
        elif speciesName in ['Indeedee', 'Meowstic']:
            form = form.replace('Female', 'f').replace('Male', 'm')
        elif speciesName == 'Calyrex':
            form = form.replace('Rider', '')

        # sometimes on Bulbapedia the form has the species name again
        form = form.replace(speciesName, '')

        # change regional names
        form = form.replace('Alolan', 'Alola')
        form = form.replace('Galarian', 'Galar')
    else:
        speciesName = text
        form = ''

    if 'Nidoran' in speciesName:
        # sometimes Nidoran will have the gender symbol (Bulbapedia)
        speciesName = speciesName.replace(
            '???', ' Female').replace('Female', 'f')
        speciesName = speciesName.replace('???', ' Male').replace('Male', 'm')

    if 'Necrozma' in speciesName:
        if 'awn' in form and 'ings' not in form:
            form = 'Dawn Wings'
        elif 'usk' in form and 'usk' not in form:
            form = 'Dusk Mane'

    # combine species and form name after parsing
    text = (speciesName + ' ' + form).strip().replace('  ', ' ')

    # hyphens to undescores
    text = text.replace('-', '_')

    # remove commas, apostophes, periods, colons, percent signs
    text = re.sub(r'[,\'\.:\%]', '', text)

    # separate lowercase followed by uppercase, e.g. 'ExtremeSpeed' to 'Extreme Speed'--for Bulbapedia typos
    text = re.sub(r'([a-z])([A-Z])', r'\1 \2', text)

    # force rename
    text = text.replace('Dusk Mane', 'Dusk')
    text = text.replace('Dawn Wings', 'Dawn')
    text = text.replace('Noice Face', 'Noice')
    text = text.replace('Ice Face', 'Ice')
    if 'Minior' in text:
        text = text.replace('Core', '')
    if 'Hoopa' in text:
        text = text.replace('Confined', '')
    text = text.replace('West Sea', 'West')
    text = text.replace('East Sea', 'East')

    # replace spaces with underscores, convert to lowercase, and strip any underscores on the ends (e.g. from Ash-Greninja')
    return text.replace(' ', '_').lower().strip('_').replace('??', 'e')


def legendsArceusList():
    return [
        'wyrdeer',
        'kleavor',
        'ursaluna',
        'basculegion',
        'basculegion_male',
        'basculegion_female',
        'sneasler',
        'overqwil',
        'enamorus',
        'enamorus_incarnate',
        'enamorus_therian',
        'growlithe_hisuian',
        'arcanine_hisuian',
        'voltorb_hisuian',
        'electrode_hisuian',
        'typhlosion_hisuian',
        'qwilfish_hisuian',
        'sneasel_hisuian',
        'dialga_origin',
        'palkia_origin',
        'samurott_hisuian',
        'lilligant_hisuian',
        'zorua_hisuian',
        'zoroark_hisuian',
        'braviary_hisuian',
        'sliggoo_hisuian',
        'goodra_hisuian',
        'avalugg_hisuian',
        'decidueye_hisuian',
        'basculin_white_striped',
    ]


if __name__ == '__main__':
    # Testing Move name parser
    print('Testing move name parser...')
    moveTests = [
        ['Karate Chop', 'karate_chop'],
        ['Razor Wind', 'razor_wind'],
        ['Roar of Time', 'roar_of_time'],
        ['All-Out Pummeling', 'all_out_pummeling'],
        ['U-turn', 'u_turn'],
        ['Multi-Attack', 'multi_attack'],
        ['10,000,000 Volt Thunderbolt', '10000000_volt_thunderbolt'],
        ['Light That Burns the Sky', 'light_that_burns_the_sky'],
        ['G-Max Wildfire', 'g_max_wildfire'],
        ['G-Max Stun Shock', 'g_max_stun_shock'],
        ['Will-O-Wisp', 'will_o_wisp'],
        ['ExtremeSpeed', 'extreme_speed'],
        ['Extreme Speed', 'extreme_speed'],
        ['RKS System', 'rks_system'],
        ['Soul-Heart', 'soul_heart']
    ]

    for test in moveTests:
        if (parseName(test[0]) != test[1]):
            print(parseName(test[0]), 'is not', test[1])
    print('Finished testing move name parser.')

    # Testing Pokemon name parser
    print('Testing Pokemon name parser...')
    pokemonTests = [
        ['Dragapult', 'dragapult'],
        ['Kommo-o', 'kommo_o'],
        ['Tapu Lele', 'tapu_lele'],
        ['Charizard (Mega Charizard X)', 'charizard_mega_x'],
        ['Blastoise (Mega Blastoise)', 'blastoise_mega'],
        ['Raticate (Alolan Raticate)', 'raticate_alola'],
        ['Pikachu (Partner Pikachu)', 'pikachu_partner'],
        ['Meowth (Galarian Meowth)', 'meowth_galar'],
        ['Farfetch\'d', 'farfetchd'],
        ['Farfetch\'d (Galarian Farfetch\'d)', 'farfetchd_galar'],
        ['Groudon (Primal Groudon)', 'groudon_primal'],
        ['Deoxys (Normal Forme)', 'deoxys_normal'],
        ['Wormadam (Plant Cloak)', 'wormadam_plant'],
        ['Rotom (Heat Rotom)', 'rotom_heat'],
        ['Giratina (Altered Forme)', 'giratina_altered'],
        ['Darmanitan (Standard Mode)', 'darmanitan_standard'],
        ['Darmanitan (Galarian Zen Mode)', 'darmanitan_zen_galar'],
        ['Kyurem (Black Kyurem)', 'kyurem_black'],
        ['Greninja (Ash-Greninja)', 'greninja_ash'],
        ['Gourgeist (Small Size)', 'gourgeist_small'],
        ['Zygarde (50% Forme)', 'zygarde_50'],
        ['Zygarde-10%', 'zygarde_10'],
        ['Hoopa (Hoopa Confined)', 'hoopa'],
        ['Wishiwashi (School Form)', 'wishiwashi_school'],
        ['Minior (Meteor Form)', 'minior_meteor'],
        ['Minior (Core)', 'minior_core'],
        ['Necrozma (Dusk Mane Necrozma)', 'necrozma_dusk'],
        ['Toxtricity (Low Key Form)', 'toxtricity_low_key'],
        ['Eternatus (Eternamax Eternatus)', 'eternatus_eternamax'],
        ['Urshifu (Single Strike Style)', 'urshifu'],
        ['Urshifu (Rapid Strike Style)', 'urshifu_rapid_strike'],
        ['Indeedee (Male)', 'indeedee_m'],
        ['Indeedee (Female)', 'indeedee_f'],
        ['Mr. Mime', 'mr_mime'],
        ['Type: Null', 'type_null'],
        ['Zacian (Hero of Many Battles)', 'zacian'],
        ['Zacian (Crowned Sword)', 'zacian_crowned'],
        ['Diancie (Mega Diancie)', 'diancie_mega'],
        ['Calyrex (Ice Rider Calyrex)', 'calyrex_ice'],
        ['Nidoran???', 'nidoran_f'],
        ['Nidoran???', 'nidoran_m'],
        ['Deerling (Summer)', 'deerling_summer']
    ]

    for test in pokemonTests:
        if (parseName(test[0], 'pokemon') != test[1]):
            print(parseName(test[0], 'pokemon'), 'is not', test[1])
    print('Finished testing Pokemon name parser.')
