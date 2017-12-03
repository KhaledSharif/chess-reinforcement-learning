from functools import reduce
from keras import metrics
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.optimizers import Adam
from keras.utils import to_categorical
from pandas import read_csv
from pandas import DataFrame
from keras import regularizers
from keras.layers import Conv1D, Dense, MaxPooling1D, Dropout, Flatten, BatchNormalization
from glob import glob
import numpy as np
import random
import string

model = Sequential()
model.add(Dense(64, activation='selu', kernel_initializer="glorot_uniform", input_shape=(64,)))
model.add(BatchNormalization())
model.add(Dropout(0.5))
for j in range(8):
	model.add(Dense(64, activation='selu', kernel_initializer="glorot_uniform"))
	model.add(Dropout(0.5))
model.add(Dense(1, activation='tanh'))
model.compile(optimizer=Adam(), loss="mse")

df = DataFrame()
for file in glob("csv/*pgn*.csv"):
	print("Processing '{}'.".format(file.split("/")[-1]))
	tf = read_csv(file, index_col=None)
	classes = [-1, 0, 1]
	lengths = [len(tf[tf["result"] == c]) for c in classes]
	minimum_length = min(lengths)
	class_tfs = [tf[tf["result"] == c].copy().sample(minimum_length) for c in classes]
	tf = reduce(lambda x, y: x.append(y, ignore_index=True), class_tfs)
	df = df.append(tf, ignore_index=True)
	print("Length is now {}.".format(len(df)))
print("\n")

training_columns = list(set(list(df)) - {"result"})
X, Y = df[training_columns].values, df["result"].values
model.fit(X, Y, epochs=100, validation_split=0.1, )
s = "".join([random.choice(string.ascii_letters) for _ in range(10)])
model.save("models/regular_nn_{}.h5".format(s.lower()))
