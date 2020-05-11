import xlrd
import xlwt
import numpy as np
import sklearn
from sklearn.model_selection import StratifiedShuffleSplit
import sys

def uniques_exists(y):
	uniques = []

	for y_ in y:
		if '-'.join(y_) not in uniques:
			uniques.append('-'.join(y_))
		else:
			return False

	return True


def get_stratified_shuffle_split(x, y, proportion):
	
	if uniques_exists(y):
		print('There are uniques classes, then they can\'t be stratified')
		return None
	
	
	sss = StratifiedShuffleSplit(n_splits=1, train_size=proportion, test_size=(1 - proportion))

	indices = list(sss.split(x, y))


	first_set = x[indices[0][0]]
	first_classes_set = y[indices[0][0]]

	second_set = x[indices[0][1]]
	second_classes_set = y[indices[0][1]]

	return indices[0][0], indices[0][1]

def is_int(s):
    try: 
        int(s)
        return True
    except ValueError:
        return False

def read_xlsx(filename, class_columns, columns_order):
	workbook = xlrd.open_workbook(filename)
	sheet = workbook.sheet_by_index(0)

	reviews = {}
	x = []
	y = []

	row_dict = {}

	for row_idx in range(0, sheet.nrows): 
		if row_idx > 0:
			row_dict['id'] = int(sheet.cell(row_idx, 0).value)
			row_dict['original'] = sheet.cell(row_idx, 1).value
			row_dict['corrected'] = sheet.cell(row_idx, 2).value
			row_dict['stars'] = sheet.cell(row_idx, 3).value if not is_int(sheet.cell(row_idx, 3).value) else int(sheet.cell(row_idx, 3).value)
			row_dict['context'] = sheet.cell(row_idx, 4).value
			row_dict['establishment'] = sheet.cell(row_idx, 5).value
			row_dict['aspect'] = sheet.cell(row_idx, 6).value
			row_dict['target'] = sheet.cell(row_idx, 7).value
			row_dict['sentiment'] = sheet.cell(row_idx, 8).value
			row_dict['polarity'] = sheet.cell(row_idx, 9).value

			if row_dict['id'] not in reviews:
				reviews[row_dict['id']] = [row_dict['original'], row_dict['corrected'], row_dict['stars'], row_dict['context'], row_dict['establishment']]

			row_dict['original'] = reviews[row_dict['id']][0]
			row_dict['corrected'] = reviews[row_dict['id']][1]
			row_dict['stars'] = reviews[row_dict['id']][2]
			row_dict['context'] = reviews[row_dict['id']][3]
			row_dict['establishment'] = reviews[row_dict['id']][4]

			x_ = []
			y_ = []

			for column in columns_order:
				if column in class_columns:
					y_.append(row_dict[column])
				else:
					x_.append(row_dict[column])
					

			x.append( tuple(x_) )
			y.append( tuple(y_) )

	x = np.asarray(x)
	y = np.asarray(y)

	return x, y


def write_xlsx(filename, indices, x, y, class_columns, columns):
	wb = xlwt.Workbook()
	sheet = wb.add_sheet('Data')

	for idx, column in enumerate(columns):
		sheet.write(0, idx, column)

	for row_idxx, search_idx in enumerate(indices):
		row_idx = row_idxx + 1

		y_search = 0
		x_search = 0

		for col_idx, column in enumerate(columns):
			if column in class_columns:
				sheet.write(row_idx, col_idx, y[search_idx][y_search])
				y_search += 1
			else:
				sheet.write(row_idx, col_idx, x[search_idx][x_search])
				x_search += 1

	wb.save(filename)

	
def valid_indices(used_indices, added_indices):
	for idx in added_indices:
		if idx in used_indices:
			return False

	return True








filename = sys.argv[1]
dev_partition = float(sys.argv[2])
dev_filename = sys.argv[3]
train_partition = float(sys.argv[4])
train_filename = sys.argv[5]
test_partition = float(sys.argv[6])
test_filename = sys.argv[7]

class_columns = [x.strip() for x in sys.argv[8].split(',')]
columns = ['id', 'original', 'corrected', 'stars', 'context', 'establishment', 'aspect', 'target', 'sentiment', 'polarity']




if dev_partition + train_partition + test_partition != 1:
	print('The sum of partitions must be 1')
	exit(-1)




print('Proportions:    Train: {}    Test: {}    Dev: {}'.format(train_partition, test_partition, dev_partition))

x, y = read_xlsx(filename, class_columns, columns)

total_examples = len(x)

train_indices, other_indices = get_stratified_shuffle_split(x, y, train_partition)

print('Examples:    Train: {}, {}    Other: {}, {}'.format(total_examples * train_partition, len(train_indices), total_examples * (1 - train_partition), len(other_indices)))

indices_map = { idx: indice for idx, indice in enumerate(other_indices) }

other_x = x[other_indices]
other_y = y[other_indices]

total_examples = len(other_x)

dev_partition = dev_partition / ( 1 - train_partition ) 

print('Adjusted dev: {}'.format(dev_partition))

dev_indices, test_indices = get_stratified_shuffle_split(other_x, other_y, dev_partition)

print('Examples:    Dev: {}, {}    Test: {}, {}'.format(total_examples * dev_partition, len(dev_indices), total_examples * (1 - dev_partition), len(test_indices)))

dev_indices = np.array( [ indices_map[indice] for indice in dev_indices ] )
test_indices = np.array( [ indices_map[indice] for indice in test_indices ] )


write_xlsx(dev_filename, dev_indices, x, y, class_columns, columns)

used_indices = dev_indices

if not valid_indices(used_indices, train_indices):
	print('Some indices in train_indices exists in dev_indices')
	exit(-2)


write_xlsx(train_filename, train_indices, x, y, class_columns, columns)

used_indices = np.concatenate([used_indices, train_indices])


if not valid_indices(used_indices, test_indices):
	print('Some indices in test_indices exists in dev_indices or train_indices')
	exit(-3)

write_xlsx(test_filename, test_indices, x, y, class_columns, columns)

print('Done!')




