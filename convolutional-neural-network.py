from functools import reduce

from keras import metrics
from keras.callbacks import ReduceLROnPlateau
from keras.models import Sequential
from keras.optimizers import Adam
from keras.utils import to_categorical
from pandas import read_csv
from pandas import DataFrame
from keras.layers import Conv2D, Dense, MaxPooling2D, Dropout, Flatten
from glob import glob


model = Sequential()
model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(8,8,1)))
for i in range(2):
	model.add(Conv2D(32, kernel_size=(3, 3), activation='relu'))
	model.add(Dropout(0.25))
model.add(MaxPooling2D(pool_size=(2, 2)))
model.add(Dropout(0.25))
model.add(Flatten())
for j in range(4):
	model.add(Dense(64, activation='relu'))
	model.add(Dropout(0.5))
model.add(Dense(3, activation='sigmoid'))
model.compile(optimizer=Adam(), loss="categorical_crossentropy", metrics=[metrics.mae, metrics.categorical_accuracy])


df = DataFrame()
for file in glob("csv/*.csv"):
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
X = X.reshape((X.shape[0], 8, 8, 1,))
Y = to_categorical(Y + 1, num_classes=3)

reduce_lr = ReduceLROnPlateau(monitor='loss', factor=0.2, patience=5, min_lr=1e-6)

model.fit(X, Y, epochs=100, validation_split=0.25, callbacks=[reduce_lr],)