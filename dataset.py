# Model

class dataset:

    def __init__(self, X=None, Y=None, sources=None):
        import copy
        import pandas as pd

        if type(X) != pd.Series:
            X = pd.Series(range(Y.size))
        # else:
        #     X = copy.deepcopy(X)
        
        self.X = X
        self.Y = Y
        #self.Y = copy.deepcopy(Y)[:100]
        self.sources = sources

    def __str__(self):
        representation = "X:\n\t" + str(self.X) + "\n"
        representation += "Y:\n\t" + str(self.Y)

        return representation

    def find_source(self, variable):
        for source in self.sources:
            if variable in source:
                return source

    def process(self, data_transforms):
        ##print "SETTINGS", data_transforms
        if "aggregate" in data_transforms:
            if data_transforms["aggregate"]:
                ##print "AGGREGATING"
                sources = {}

                x_sourced = hasattr(self.X, "name")
                y_sourced = hasattr(self.Y, "name")
                both_sourced = x_sourced and y_sourced

                if x_sourced:
                    sources["x"] = self.find_source(self.X.name)

                if y_sourced:
                    sources["y"] = self.find_source(self.Y.name)

                if both_sourced:
                    self.aggregate(sources)

        import pandas as pd
        for transform,do_it in data_transforms.items():
            if transform == "normal":
                if do_it:
                    self.Y = self.Y.astype(float)
                    #self.Y = (self.Y - self.Y.min()) / (self.Y.max() - self.Y.min())
                    from viz.analysis.data_ops import normalize
                    ###print self.Y
                    self.Y = pd.Series(normalize(self.Y))
                    ###print "\n\n\n", self.Y
            elif transform == "exclude":
                if do_it:
                    from viz.analysis.data_ops import exclude
                    self.Y = pd.Series(exclude(self.Y.values))

    def aggregate(self, sources):
        """ Aggregates Y-values based on X-values. """
        ##print "HERIEO"
        import pandas as pd
        data = sources["y"][self.Y.name][sources["y"][self.Y.name] > 0]

        X = sorted(set(self.X.values))

        #print "Aggregating"
        if type(sources["x"]) == pd.DataFrame:
            Y = [sum(data[sources["x"][self.X.name] == x_]) for x_ in X]
            self.X = pd.Series(X, name=self.X.name)
            self.Y = pd.Series(Y, name=self.Y.name)

        #print "Aggregated"
         
        ###print self.Y
        # Perform aggregation.
        # This involves using the correct source for a particular variable.
        # How to check for this?
        # See which one it is in.