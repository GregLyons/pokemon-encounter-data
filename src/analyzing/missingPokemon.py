import csv

from utils import (getAnalysisDataPath, getDataPath, getEncounterDataPath,
                   getNumberOfGens)


def missingPokemon(fnames, pokemonInGen):
    handledPokemon = set()
    for fname in fnames:
        with open(fname, 'r', encoding='utf-8') as encounterCSV:
            reader = csv.DictReader(encounterCSV)

            for row in reader:
                pokemonName = row["Pokemon"]
                handledPokemon.add(pokemonName)

    return pokemonInGen - handledPokemon


def main():
    with open(getAnalysisDataPath() + 'missing-pokemon.csv', 'w', newline='', encoding='utf-8') as missingCSV:
        writer = csv.writer(missingCSV)
        writer.writerow(['Gen', 'Pokemon'])

        # Iterate over gens and find Pokemon missing from encounter data
        # TODO: Other gens later
        for gen in range(1, 5):
            pokemonInGen = set()

            # Populate set of Pokemon in gen
            with open(getDataPath() + 'pokemon-gen.csv', 'r', encoding='utf-8') as genCSV:
                reader = csv.DictReader(genCSV)

                for row in reader:
                    pokemonName, pokemonGen = row["Pokemon Name"], int(
                        row["Gen"])
                    if pokemonGen <= gen:
                        pokemonInGen.add(pokemonName)

            # Find missing Pokemon
            # Gen 1
            if gen == 1:
                fnames = [
                    getEncounterDataPath() + 'encounters-rby.csv',
                ]
            # Gen 2
            elif gen == 2:
                fnames = [
                    getEncounterDataPath() + 'encounters-gsc.csv',
                ]
            # Gen 3
            elif gen == 3:
                fnames = [
                    getEncounterDataPath() + 'encounters-rse.csv',
                    getEncounterDataPath() + 'encounters-frlg.csv',
                ]
            # Gen 4
            elif gen == 4:
                fnames = [
                    getEncounterDataPath() + 'encounters-dppt.csv',
                    getEncounterDataPath() + 'encounters-hgss.csv',
                ]
            # TODO: later gens
            else:
                fnames = []
            missing = missingPokemon(fnames, pokemonInGen)

            # Write missing Pokemon to CSV
            for pokemonName in missing:
                writer.writerow([gen, pokemonName])


if __name__ == '__main__':
    main()
