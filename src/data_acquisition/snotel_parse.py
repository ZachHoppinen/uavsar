import pandas as pd
data_dir = '?'
df = pd.read_csv(join(data_dir, 'banner_2021.csv'), skiprows = 3)
df.loc[:, 'swe'] = df['WTEQ.I-1 (in) ']*0.0254
df.loc[:, 'precip'] = df['PREC.I-1 (in) ']*0.0254
df.loc[:, 'sd'] = df['SNWD.I-1 (in) ']*0.0254
# df.loc[:, 'temp'] = df['TOBS.I-1 (degC) ']
df.loc[:, 'datetime'] = df.Date +'T'+ df.Time
df.datetime = pd.to_datetime(df.datetime)
df = df.set_index('datetime')
df = df.drop(['Date','Time', 'Site Id', 'Unnamed: 7', 'WTEQ.I-1 (in) ', 'PREC.I-1 (in) ', 'SNWD.I-1 (in) ', 'TOBS.I-1 (degC) '], axis =1)

df.to_csv(join(data_dir, 'banner_snotel.csv'))