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
        for opinion in example[OPINIONS_TAG]:
            for aspect in ASPECTS:

                # Generates pseudo-sentences for all sentiments 
                sentiment_lines = []
                set_none = 0
                for sentiment_key in SENTIMENTS:
                    sentiment_val = SENTIMENTS[sentiment_key]
                    # Generates sentence per each sentence
                    tag = 1 if opinion[POLARITY_TAG] == sentiment_key and opinion[ASPECT_TAG] == aspect else 0
                    set_none += tag
                    # Original sentence
                    line = [
                        example[ID_TAG], 
                        example[CONTEXT_TAG] + '. ' + ' '.join(example[ORIGINAL_TAG].split()),
                        '%s - %s - %s - %s' % (sentiment_val, example[CONTEXT_TAG], opinion[TARGET_TAG], aspect),
                        tag,
                        sentiment_key
                    ]
                    sentiment_lines.append(line)
                    # Corrected sentence
                    line = [
                        example[ID_TAG], 
                        example[CONTEXT_TAG] + '. ' + ' '.join(example[CORRECTED_TAG].split()),
                        '%s - %s - %s - %s' % (sentiment_val, example[CONTEXT_TAG], opinion[TARGET_TAG], aspect),
                        tag,
                        sentiment_key
                    ]
                    sentiment_lines.append(line)

                # If there arent any tag default sentiment will be set to 1
                if set_none == 0:
                    for line in sentiment_lines:
                        if line[-1] == DEFAULT_SENTIMENT:
                            line[-2] = 1
                            
                # Append lines to dataset
                for line in sentiment_lines:
                    ofile.write('%s\t%s\t%s\t%s\n' % (str(line[0]), line[1], line[2], line[3]))
                    line_count += 1

        print('Final del ejemplo en linea ', line_count)

    ofile.close()
    print('Archivo guardado en \"', output_file, '\"')
else:
    print('No existe el archivo \"', data_file, '\"')