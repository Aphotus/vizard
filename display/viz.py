# -*- coding: utf-8 -*-
"""
Created on Thu Oct 24 22:18:03 2013

@author: Evin
"""

class viz:
    """ Automatically detects type of data sources and plots them. """

    def __init__(self, files, subsets=None):
        """ Initializes the viz object. """
        import vizard.util.file_io as fio

        # Need to keep track of:
        #~  File names of the data sources [data_source.ext, ...]
        #~  Names of the variables contained in each data source { variable.data_source: data_source.ext }
        #       Always display 'variable' name unless two variables with the same name.
        #       In that case, 'variable.data_source'
        #       Any variable can always be uniquely referenced by 'variable.data_source'.

        self.files = {}
        self.sources = {}
        self.variables = {}
        # Is the 'path' variable a list? If so, add all variables.
        # If not, add variables from one file.
        if type(files) == list:
            for i,file_ in enumerate(files):
                if type(file_) == tuple:
                    f, delim = file_
                else:
                    f = file_
                    delim = ','

                if subsets != None:
                    subset = subsets[i]

                else:
                    subset = None
                    
                variables, file_name = fio.read(f, delimiter=delim, subset=subset)
                self.files[file_name] = variables

                for v in variables:
                    if v in self.variables:
                        v_new = file_name + "_" + v

                        self.sources[v_new] = variables
                        self.variables[v_new] = variables[v]
                    else:
                        self.sources[v] = variables
                        self.variables[v] = variables[v]

        else:
            if type(files) == tuple:
                    f, delim = files
            else:
                f = files
                delim = ','

            variables, file_name = fio.read(f, delimiter=delim, subset=subsets)
            self.files[file_name] = variables

            for v in variables:
                self.sources[v] = variables
                self.variables[v] = variables[v]

    def __getitem__(self, key=None):
        from vizard.display.chart import chart
        from vizard.display.chart_manager import chart_manager
        from vizard.dataset import dataset

        if key == None:
            print("Nothing to return.")
            return None

        elif type(key) == str:
            # X is Y
            
            #~ This is kind of a hack...
            import pandas as pd
            d_vars = self.variables[key]
            source = self.sources[key]

            return chart_manager([dataset(Y=d_vars, sources=[source])])

        elif type(key) == tuple:
            if len(key) == 2:
                x = key[0]
                y = key[1]

                both_strings = type(x) == str and type(y) == str
                both_tuples = type(x) == tuple and type(y) == tuple

                if both_strings:
                    # Just plot a single 'chart' from a single 'dataset'
                    i_vars = self.variables[x]
                    d_vars = self.variables[y]

                    sources = [self.sources[key] for key in (i_vars.name, d_vars.name)]

                    cm = chart_manager([dataset(i_vars, d_vars, sources=sources)])

                    # Use a single 'chart' to plot a vanilla bivariate dataset.
                    return cm

                #~ Twinx
                elif both_tuples:
                    # Now get the variables.
                    i_vars = self._get_data(x)
                    d_vars = self._get_data(y)

                    diff = len(d_vars) - len(i_vars)
                    if diff > 0:
                        i_vars += [i_vars[-1]] * diff

                    datasets = []
                    for x_, y_ in zip(i_vars, d_vars):
                        sources = [self.sources[key] for key in (x_.name, y_.name)]
                        datasets.append(dataset(x_, y_, sources))
               
                    cm = chart_manager(datasets)

                    # Use the 'chart manager' to plot multiple datasets.
                    return cm
                else:
                    # Now get the variables.
                    i_vars = self._get_data([x])
                    d_vars = self._get_data(y)

                    datasets = []
                    #sources = [self.sources[key] for key in (x,y)]

                    ##print i_vars
                    diff = len(d_vars) - len(i_vars)
                    if diff > 0:
                        i_vars += [i_vars[-1]] * diff
                    for x_, y_ in zip(i_vars, d_vars):
                        #print x_
                        #print y_

                        sources = [self.sources[key] for key in (x_.name, y_.name)]
                        datasets.append(dataset(x_, y_, sources))
               
                    cm = chart_manager(datasets)

                    # Use the 'chart manager' to plot multiple datasets.
                    return cm

        return None      

    def _get_data(self, names):
        data = []
        for name in names:
                try:
                    data.append(self.variables[name])
                except KeyError as e:
                    print "The independent variable 'x' does not exist."
                    print "Wrong name was:", name

        return data

if __name__ == "__main__":
    from chart import chart

    print "Hi"