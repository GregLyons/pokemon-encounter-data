import csv

from utils import getDataPath, openLink


def makeEncounterCSV(fname):
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
            visitLocationLink(locationLink)
            visitedHrefs.add(locationLink['href'])

    with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile)

    return


def visitLocationLink(locationLink):
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
    print(locationName)
    findTableSection = encounterSection.find_next('span', id=f'Generation_I')

    # If no table for desired gen, leave
    if findTableSection == None:
        return False

    findTable = findTableSection.find_next('table')
    rows = findTable.find('tbody').findChildren('tr', recursive=False)
    print(rows)
    for row in rows:
        cells = row.findChildren(['td', 'th'], recursive=False)

        print(len(cells))

    return True


def main():
    dataPath = getDataPath()
    makeEncounterCSV(dataPath + 'encounters.csv')


if __name__ == '__main__':
    main()
