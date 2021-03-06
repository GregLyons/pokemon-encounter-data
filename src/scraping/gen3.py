import csv

from scraping import makeEncounterCSV
from utils import getEncounterDataPath, openLink


def main():
    dataPath = getEncounterDataPath()
    fname_rse = dataPath + 'encounters-rse.csv'
    fname_frlg = dataPath + 'encounters-frlg.csv'
    fname_none = dataPath + 'none-gen3.csv'

    with open(fname_rse, 'w', newline='', encoding='utf-8') as csvFile_rse, open(fname_frlg, 'w', newline='', encoding='utf-8') as csvFile_frlg, open(fname_none, 'w', newline='', encoding='utf-8') as csvFile_none:
        writer_rse = csv.writer(csvFile_rse)
        writer_rse.writerow(['Location', 'Sub-location', 'Pokemon', 'R', 'S',
                             'E', 'Method', 'Levels', 'Rate'])
        writer_frlg = csv.writer(csvFile_frlg)
        writer_frlg.writerow(
            ['Location', 'Sub-location', 'Pokemon', 'FR', 'LG', 'Method', 'Levels', 'Rate'])
        writer_none = csv.writer(csvFile_none)
        writer_none.writerow(['Version Group Code', 'Location', 'Reason'])

        # Navigate to link
        bs = openLink(
            'https://bulbapedia.bulbagarden.net/wiki/List_of_locations_by_index_number_(Generation_III)', 0, 10)

        # Section where desired table is
        findSection = bs.find('span', id=f'List')

        # Desired table (nested within an outer table)
        findTable = findSection.findNext('table')
        makeEncounterCSV(
            findTable, {'RSE': writer_rse, 'FRLG': writer_frlg, 'None': writer_none}, 'III')


if __name__ == '__main__':
    main()
