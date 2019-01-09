import tensorflow as tf

PATH = "/home/newcomer/Desktop/tensorfun/"
SAVE_PATH = "/home/newcomer/Desktop/tensorfun/" 

feature_names = [
    'SepalLength',
    'SepalWidth',
    'PetalLength',
    'PetalWidth']

def m_input_fn(FILE):
	def get_line(line):
		line = tf.decode_csv(line, [[0.], [0.], [0.], [0.], [0]])
		return dict(zip(feature_names, line[:-1])), line[-1]

	data = tf.data.TextLineDataset(PATH + FILE)
	data = data.skip(1)
	data = data.map(get_line)
	data = data.batch(4)
	data = data.repeat(8)

	iterator = data.make_one_shot_iterator()
	features, labels = iterator.get_next()

	return features, labels


feature_columns = [ tf.feature_column.numeric_column(i) for i in feature_names ]


classifier = tf.estimator.DNNClassifier(feature_columns=feature_columns,
	hidden_units = [10,10],
	n_classes = 3,
	model_dir = SAVE_PATH)

classifier.train(input_fn=lambda: m_input_fn("iris_training.csv"))


results = classifier.evaluate(input_fn= lambda: m_input_fn("iris_test.csv"))

for r in results:
	print r , results[r]


prediction_input = [[5.9, 3.0, 4.2, 1.5],  # -> 1, Iris Versicolor
                    [6.9, 3.1, 5.4, 2.1],  # -> 2, Iris Virginica
                    [5.1, 3.3, 1.7, 0.5]]  # -> 0, Iris Sentosa


# In memory predictions read
def mem_input_fn():
	def to_tensor_representation(line):
		line = tf.split(line, 4)
		return dict(zip(feature_columns, line))

	# Add data to memory
	data = tf.data.Dataset.from_tensor_slices(prediction_input)
	data = data.map(to_tensor_representation)
	iterator = data.make_one_shot_iterator()
	features = iterator.get_next()

	return features, None # Because because we want to predict

results = classifier.predict(input_fn = lambda: mem_input_fn())

for r in results:
	print r 
	idx = r["classes"][0]
	print idx, r["probabilities"][int(idx)]
