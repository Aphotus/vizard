def apply(x, y, settings):
    for setting, value in settings.items():
        if setting == "dropna":
            if value:
                x = x.dropna(how='any')
                y = y.dropna(how='any')
        elif setting == "normalize":
            if value:
                y = normalize(y)
        elif setting == "aggregate":
            if value:
                result = []
                for x_ in x:
                    y = [sum(y[1 == 1])]

    return x, y

def normalize(data):
        max_value = float(max(data))
        min_value = float(min(data))
        
        for i in range(len(data)):
            data[i] = (data[i] - min_value) / (max_value - min_value)
            
        return data

def exclude(data, n=2):
    import numpy as np

    # Outlier removal.
    mean = np.mean(data)
    std = np.std(data)
    _max = mean + n * std
    _min = mean - n * std
    
    indices = list(set([i for i in range(len(data)) if data[i] <= _min and data[i] >= _max]))
    for i in range(len(data)):        
        if i in indices:
            data[i] = 0

    return data
        
def preprocess(data, correlate=None, n=2, norm=False):
    import numpy as np

    # Normalization.
    if norm:
        data = normalize(data)
    
    # Outlier removal.
    mean = np.mean(data)
    std = np.std(data)
    _max = mean + n * std
    _min = mean - n * std
    
    indices = list(set([i for i in range(len(data)) if data[i] <= _min and data[i] >= _max]))
    for i in range(len(data)):        
        if i in indices:
            data[i] = 0
        
    return np.array(data)