import csv

from scraping import makeEncounterCSV
from utils import getDataPath, openLink, parseName


def main():
    dataPath = getDataPath()
    fname = dataPath + 'encounters-gsc.csv'

    with open(fname, 'w', newline='', encoding='utf-8') as csvFile:
        writer = csv.writer(csvFile)
        writer.writerow(['Location', 'Pokemon', 'G', 'S',
                        'C', 'Method', 'Levels', 'Morning Rate', 'Day Rate', 'Night Rate'])

        # Navigate to link
        bs = openLink(
            'https://bulbapedia.bulbagarden.net/wiki/List_of_locations_by_index_number_(Generation_II)', 0, 10)

        # Section where desired table is
        findSection = bs.find('span', id=f'List')

        # Desired table (nested within an outer table)
        findTable = findSection.findNext('table').find('table')
        makeEncounterCSV(findTable, {'GSC': writer}, 'II')


if __name__ == '__main__':
    main()
