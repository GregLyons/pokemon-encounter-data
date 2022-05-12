import csv
from urllib.error import URLError

from utils import getEncounterDataPath, openLink, parseName


def makeEncounterCSV(findTable, writers, genSymbol):
    # Keep track of links already visited
    visitedHrefs = set()

    # Select rows of table
    rows = findTable.find_all('tr')
    for row in rows:
        cells = row.find_all('td')

        # Ignore rows with less than 4 cells; don't contain useful information
        # Ignore rows with no links
        if len(cells) < 3 or row.find('a') == None:
            continue

        # Cell with desired data
        locationCell = cells[2]

        # Visit each link
        for locationLink in locationCell.find_all('a'):
            # If link has been visited, move on
            if locationLink['href'] in visitedHrefs:
                continue

            # Otherwise, add encounter data
            hasEncounterData, reason = visitLocationLink(
                locationLink, writers, genSymbol)
            visitedHrefs.add(locationLink['href'])

            # Track locations with no encounter data
            if not hasEncounterData:
                locationIndex = int(cells[0].get_text())

                # Gen 1, RBY only
                if genSymbol == 'I':
                    writers['None'].writerow(
                        ['RBY', locationLink.get_text(), reason])
                # Gen 2, GSC only
                elif genSymbol == 'II':
                    writers['None'].writerow(
                        ['GSC', locationLink.get_text(), reason])
                # Gen 3
                elif genSymbol == 'III':
                    # FRLG
                    if locationIndex >= 87 and locationIndex <= 196:
                        writers['None'].writerow(
                            ['FRLG', locationLink.get_text(), reason])
                    # RSE
                    else:
                        writers['None'].writerow(
                            ['RSE', locationLink.get_text(), reason])
                # Gen 4
                elif genSymbol == 'IV':
                    # FRLG
                    if (locationIndex >= 126 and locationIndex <= 234) or locationIndex in [2013, 2014]:
                        writers['None'].writerow(
                            ['HGSS', locationLink.get_text(), reason])
                    # RSE
                    else:
                        writers['None'].writerow(
                            ['DPPt', locationLink.get_text(), reason])

    return


def visitLocationLink(locationLink, writers, genSymbol):
    #
    # Parse locationLink to determine if it has encounter data; if so, find section where encounter data is given
    # region

    locationName = locationLink.get_text()
    # Go to link
    try:
        locationPage = openLink(
            'https://bulbapedia.bulbagarden.net' + locationLink['href'], 0, 10)
    # E.g. non-Bulbapedia link
    except URLError:
        return False, "Did not lead to valid Bulbapedia link"

    print(locationName)

    encounterSection, headerLevel = findEncounterSection(locationPage)

    #
    # Hard-code certain exceptions
    # region

    hardCodedException = False
    if genSymbol == 'IV' and locationName == 'Contest Hall':
        hardCodedException = True

    #
    # endregion
    #

    # If still no encounter section found, leave
    if not encounterSection or hardCodedException:
        return False, "No encounter section found"

    tables, reason = findTables(encounterSection, genSymbol, headerLevel)

    # No tables found
    if len(tables) == 0:
        return False, f"No tables found: {reason}"

    # Tables found; iterate over them
    for table, tableHeader in tables:
        scrapeDataFromTable(locationName, table,
                            tableHeader, writers, genSymbol)

    return True, None


def findEncounterSection(locationPage):
    # Find section of page with encounter data
    # Many pages have sections entitled "Pokémon" representing different things, but encounter data will be in sections with <h2> headings entitled "Pokémon", whereas the other sections may have "Pokémon" in a different heading level (e.g. <h5>).
    h2s = locationPage.find_all('h2')
    encounterSection = None
    for h2 in h2s:
        # Encounter section not found, move on
        if h2.get_text() != 'Pokémon':
            continue
        # Encounter section (most likely) found
        else:
            encounterSection = locationPage.find('span', id=f'Pok.C3.A9mon')

    # Assume encounter section starts with an h2
    headerLevel = 2

    # If no encounter section found, it may be an h3 if the page is split into a games section and an anime section
    if not encounterSection:
        # Check if there's a games section
        gamesSection = locationPage.find('span', id=f'In_the_games')

        # If not, leave
        if not gamesSection:
            return False, None

        # Otherwise, look in games section
        encounterSection = gamesSection.find_next('span', id=f'Pok.C3.A9mon')

        # Encounter section starts with an h3
        headerLevel = 3

    return encounterSection, headerLevel


def findTables(encounterSection, genSymbol, headerLevel):
    tables = []

    # Otherwise, find desired gen
    findGenSection = encounterSection.find_next(
        'span', id=f'Generation_{genSymbol}')

    # E.g. Sea Route 20, 'Generation I' used as ID for preceding section that's not encounter-related
    if not findGenSection:
        findGenSection = encounterSection.find_next(
            'span', id=f'Generation_{genSymbol}_2')

    # E.g. New Bark Town
    if not findGenSection:
        findGenSection = encounterSection.find_next(
            'span', id=f'Generation_{genSymbol}_3')

    # # If no table for desired gen, leave
    # if findGenSection == None:
    #     return [], 'No tables found for desired gen.'

    # Once we've found the section with the encounter data, there may be multiple tables (e.g. a table for each floor of Mt. Moon in Gen I). In this case, we iterate over the tables from the starting point (an 'h2' or an 'h3') until we reach the next section (another 'h2' or 'h3', which will be a sibling of the starting point).
    if not findGenSection:
        # If location exists in other gens and has encounter data, then that means there's no encounter data for this gen
        for genSymbol in ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII']:
            if encounterSection.find_next('span', id=f'Generation_{genSymbol}'):
                return [], 'Has Pokemon in other Gen'
            # E.g. Scorched Slab
            elif encounterSection.find_next('span', id=f'Generation_{genSymbol}_2'):
                return [], 'Has Pokemon in other Gen'

        # Otherwise, there is encounter data for this gen only, which is why there's no section for this particular gen
        tableHeader = 'N/A'
        for sibling in encounterSection.parent.next_siblings:
            # Stop when next header tag of same level is reached
            if sibling.name == encounterSection.parent.name:
                break
            elif sibling.name == 'table':
                tables.append([sibling, tableHeader])
            if sibling.name in ['h2', 'h3', 'h4', 'h5']:
                tableHeader = ' '.join(sibling.stripped_strings)
    else:
        tableHeader = 'N/A'
        for sibling in findGenSection.parent.next_siblings:
            # Stop when next header tag of same level is reached
            if sibling.name == findGenSection.parent.name:
                break
            elif sibling.name == 'table':
                tables.append([sibling, tableHeader])
            # The heading preceding the table
            if sibling.name in ['h2', 'h3', 'h4', 'h5']:
                # E.g. Kanto Safari Zone in Generation 3
                siblingHeaderLevel = int(sibling.name[1])
                if siblingHeaderLevel <= headerLevel:
                    break

                tableHeader = ' '.join(sibling.stripped_strings)

    return tables, None


def scrapeDataFromTable(locationName, table, tableHeader, writers, genSymbol):

    # Parse header row to get number of games being considered
    headerRow = table.find('tr')
    colSpan = 6
    for th in headerRow.findChildren(['th'], recursive=False):
        if 'Games' in th.get_text():
            try:
                colSpan = int(th['colspan'])
            # Block-based encounter Safari Zone
            except KeyError:
                print('NO COL SPAN')
                return

    rows = table.find('tbody').findChildren('tr', recursive=False)[1:]
    for row in rows:

        cells = row.findChildren(['td', 'th'], recursive=False)

        # Ignore rows which are headers for sections/don't have enough cells
        if len(cells) < 4:
            continue

        try:
            numberGames = int(colSpan / int(cells[1]['colspan']))
        except KeyError:
            print('NO COL SPAN')
            return

        # Ignore rows which are headers for sections/don't have enough cells
        if len(cells) < 4 + numberGames:
            continue

        csvRow = [locationName, tableHeader]

        pokemonName = parseName(cells[0].get_text(
        ).strip('\n'))
        csvRow.append(pokemonName)

        # Get presence of data in games
        games = cells[1:1+numberGames]
        versionGroupCode = ''
        for game in games:
            # White background indicates not present in game
            if game['style'] in ['background:#FFF;', 'background:#FFFFFF;']:
                csvRow.append(False)
            else:
                csvRow.append(True)
            versionGroupCode += ''.join(game.stripped_strings)

        # Indicates encounter rate same at all times of day
        if len(cells) == 4 + numberGames:
            method = ' '.join(list(cells[-3].stripped_strings))
            csvRow.append(method)
            levels = ' '.join(list(cells[-2].stripped_strings))
            csvRow.append(levels)

            rate = ' '.join(list(cells[-1].stripped_strings))

            # Rate applies at all times
            if genSymbol in ['II', 'IV']:
                csvRow += [rate, rate, rate]
            # Not Gen 2, so no times of day dependence
            else:
                csvRow.append(rate)

            # Navel Rock, Gen 3
            if versionGroupCode == 'FRLGE':
                writers['FRLG'].writerow(
                    [locationName, 'N/A', pokemonName, True, True, method, levels, rate])
                writers['RSE'].writerow(
                    [locationName, 'N/A', pokemonName, False, False, True, method, levels, rate])

            # General case
            else:
                # E.g. Mining Museum page
                if genSymbol == 'IV' and versionGroupCode == 'BDSP':
                    continue

                writers[versionGroupCode].writerow(csvRow)
        # Encounter rates depend on time of day
        else:
            method = ' '.join(list(cells[-5].stripped_strings))
            csvRow.append(method)
            levels = ' '.join(list(cells[-4].stripped_strings))
            csvRow.append(levels)

            morningRate = ' '.join(list(cells[-3].stripped_strings))
            csvRow.append(morningRate)
            dayRate = ' '.join(list(cells[-2].stripped_strings))
            csvRow.append(dayRate)
            nightRate = ' '.join(list(cells[-1].stripped_strings))
            csvRow.append(nightRate)

            writers[versionGroupCode].writerow(csvRow)

    return


def main():
    dataPath = getEncounterDataPath()
    makeEncounterCSV(dataPath + 'encounters.csv')


if __name__ == '__main__':
    main()
