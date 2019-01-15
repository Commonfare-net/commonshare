import pandas

df = pandas.read_csv('results-survey474757.csv')
print df.dtypes
print df['NestedCircles'].describe()