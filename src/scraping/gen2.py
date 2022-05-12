import csv

from scraping import makeEncounterCSV
from utils import getDataPath, openLink, parseName


def main():
    dataPath = getDataPath()
    fname = dataPath + 'encounters-gsc.csv'
    fname_none = dataPath + 'none-gen2.csv'

    with open(fname, 'w', newline='', encoding='utf-8') as csvFile, open(fname_none, 'w', newline='', encoding='utf-8') as csvFile_none:
        writer = csv.writer(csvFile)
        writer.writerow(['Location', 'Pokemon', 'G', 'S',
                        'C', 'Method', 'Levels', 'Morning Rate', 'Day Rate', 'Night Rate'])
        writer_none = csv.writer(csvFile_none)
        writer_none.writerow(['Version Group Code', 'Location'])

        # Navigate to link
        bs = openLink(
            'https://bulbapedia.bulbagarden.net/wiki/List_of_locations_by_index_number_(Generation_II)', 0, 10)

        # Section where desired table is
        findSection = bs.find('span', id=f'List')

        # Desired table (nested within an outer table)
        findTable = findSection.findNext('table').find('table')
        makeEncounterCSV(findTable, {'GSC': writer, 'None': writer_none}, 'II')


if __name__ == '__main__':
    main()
