import csv

from utils import getDataPath, openLink, parseName


def makeEncounterCSV(fname):

    with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Location', 'Pokemon', 'R', 'B',
                        'Y', 'Method', 'Levels', 'Rate'])

        # Navigate to link
        bs = openLink(
            'https://bulbapedia.bulbagarden.net/wiki/List_of_locations_by_index_number_(Generation_I)', 0, 10)

        # Section where desired table is
        findSection = bs.find('span', id=f'List_of_locations_by_index_number')

        # Desired table (nested within an outer table)
        findTable = findSection.findNext('table').find('table')

        # Keep track of links already visited
        visitedHrefs = set()

        # Select rows of table
        rows = findTable.find_all('tr')
        for row in rows:
            cells = row.find_all('td')

            # Ignore rows with less than 4 cells; don't contain useful information
            # Ignore rows with no links
            if len(cells) != 4 or row.find('a') == None:
                continue

            # Cell with desired data
            locationCell = cells[2]

            # Visit each link
            for locationLink in locationCell.find_all('a'):
                # If link has been visited, move on
                if locationLink['href'] in visitedHrefs:
                    continue
                # Otherwise, add encounter data
                visitLocationLink(locationLink, writer)
                visitedHrefs.add(locationLink['href'])

    return


def visitLocationLink(locationLink, writer):
    #
    # Parse locationLink to determine if it has encounter data; if so, find section where encounter data is given
    # region

    locationName = locationLink.get_text()
    locationPage = openLink(
        'https://bulbapedia.bulbagarden.net' + locationLink['href'], 0, 10)

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

    # If no encounter section found, leave
    if encounterSection == None:
        return False

    # Otherwise, find desired gen
    findTableSection = encounterSection.find_next('span', id=f'Generation_I')

    # If no table for desired gen, leave
    if findTableSection == None:
        return False

    #
    # endregion
    #

    #
    # Add table data to .csv
    # region
    findTable = findTableSection.find_next('table')

    # Parse header row to get number of games being considered
    headerRow = findTable.find('tr')
    numberGames = 1
    for th in headerRow.findChildren(['th'], recursive=False):
        if 'Games' in th.get_text():
            numberGames = int(int(th['colspan']) / 2)

    rows = findTable.find('tbody').findChildren('tr', recursive=False)[1:]
    for row in rows:

        cells = row.findChildren(['td', 'th'], recursive=False)

        # Ignore rows which are headers for sections/don't have enough cells
        if (len(cells) < 4 + numberGames):
            continue

        csvRow = [locationName]

        pokemonName = parseName(cells[0].get_text(
        ).strip('\n'))
        csvRow.append(pokemonName)

        # Get presence of data in games
        games = cells[1:1+numberGames]
        for game in games:
            # White background indicates not present in game
            if game['style'] in ['background:#FFF;', 'background:#FFFFFF;']:
                csvRow.append(False)
            else:
                csvRow.append(True)

        location = ' '.join(list(cells[-3].stripped_strings))
        csvRow.append(location)
        levels = ' '.join(list(cells[-2].stripped_strings))
        csvRow.append(levels)
        rate = ' '.join(list(cells[-1].stripped_strings))
        csvRow.append(rate)

        writer.writerow(csvRow)
    #
    # endregion
    #

    return True


def main():
    dataPath = getDataPath()
    makeEncounterCSV(dataPath + 'encounters.csv')


if __name__ == '__main__':
    main()
