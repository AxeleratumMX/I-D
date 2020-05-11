import json
import os
import sys

data_file = sys.argv[1]
output_file = sys.argv[2]

SENTIMENTS = {
    'Positive': 'Positive', 
    'Neutral': 'None', 
    'Negative': 'Negative'
}

DEFAULT_SENTIMENT = 'Neutral'

ASPECTS = [
    'general',
    'servicio',
    'ambiente',
    'precio',
    'comida',
    'ubicación'
]


GENERAL_TAG = 'ejemplos'
ID_TAG = 'id'
ORIGINAL_TAG = 'review_original'
CORRECTED_TAG = 'review_corregido'
STARS_TAG = 'estrellas'
CONTEXT_TAG = 'contexto'
ESTABLISHMENT_TAG = 'establecimiento'
OPINIONS_TAG = 'opiniones'

ASPECT_TAG = 'aspecto'
TARGET_TAG = 'target_entity'
SENTIMENT_TAG = 'sentimiento'
POLARITY_TAG = 'polaridad'

COLUMNS = [
    'id',
    'sentence1',
    'sentence2',
    'label'
]


print('Leyendo el archivo \"', data_file, '\"')
file_exists = os.path.isfile(data_file)


if file_exists:
    line_count = 0
    
    ofile = open(output_file, 'w', encoding='utf-8')
    ofile.write('\t'.join(COLUMNS))
    ofile.write('\n')
    

    with open(data_file, 'r', encoding='utf-8') as json_file:
        datastore = json.load(json_file)

    lines = []
    # Get each example
    for example in datastore:#[GENERAL_TAG]:
        print('Processing example ', example[ID_TAG])
        # Get each opinion per example
        combinations = {}
        targets = set()

        for opinion in example[OPINIONS_TAG]:
            combination_key = '{}-{}'.format(opinion[ASPECT_TAG], opinion[TARGET_TAG])
            if combination_key not in combinations:
                combinations[combination_key] = set()

            combinations[combination_key].add(opinion[POLARITY_TAG])
            targets.add(opinion[TARGET_TAG])

        for aspect in ASPECTS:
            for target in targets:
                combination_key = '{}-{}'.format(aspect, target)
                labels = [0] * len(SENTIMENTS)
                sentiment_found = False
                lines = []
                for sentiment_idx, sentiment_key in enumerate(SENTIMENTS):
                    if combination_key in combinations:
                        if sentiment_key in combinations[combination_key]:
                            sentiment_found = True
                            labels[sentiment_idx] = 1

                if not sentiment_found:
                    labels[list(SENTIMENTS.keys()).index(DEFAULT_SENTIMENT)] = 1
                

                for label_idx, label in enumerate(labels):
                    if label == 1:
                        line = [
                            example[ID_TAG], 
                            example[CONTEXT_TAG] + '. ' + ' '.join(example[ORIGINAL_TAG].split()),
                            '{} - {} - {}'.format( example[CONTEXT_TAG], aspect, target ),
                            SENTIMENTS[list(SENTIMENTS.keys())[label_idx]]
                            #' '.join(map(str, labels))
                        ]

                        lines.append(line)

                        line = [
                            example[ID_TAG], 
                            example[CONTEXT_TAG] + '. ' + ' '.join(example[CORRECTED_TAG].split()),
                            '{} - {} - {}'.format( example[CONTEXT_TAG], aspect, target ),
                            SENTIMENTS[list(SENTIMENTS.keys())[label_idx]]
                            #' '.join(map(str, labels))
                        ]
                        
                        lines.append(line)

                if len(lines) > 0:
                    for line in lines:               
                        ofile.write('%s\t%s\t%s\t%s\n' % (str(line[0]), line[1], line[2], line[3]))
                        line_count += 1

        print('Final del ejemplo en linea ', line_count)

    ofile.close()
    print('Archivo guardado en \"', output_file, '\"')
else:
    print('No existe el archivo \"', data_file, '\"')