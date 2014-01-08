
def read(path, delimiter=",", subset=None):
    """ Read data from path. """
    import os
    import pandas as pd

    file_name, file_extension = os.path.splitext(path)

    if file_extension == ".csv":
        data = pd.read_csv(path, delimiter=delimiter)

    elif file_extension == ".txt":
        data = pd.read_table(path, delimiter=delimiter)

    if subset == None:
        df = data.dropna(how='any')
    else:
        df = data.dropna(how='any', subset=subset)

    return df, os.path.basename(file_name)