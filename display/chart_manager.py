# Controller

class chart_manager:
    def __init__(self, datasets):
        """ Contains a list of 'charts' and plots them based on rules. """
        self.datasets = datasets
        self.charts = []

        import chart_config as cc
        self.settings = [dict(cc._chart_settings) for _ in range(len(datasets))]

    def __str__(self):
        representation = ""

        for d_set in self.datasets:
            representation += str(d_set)
            representation += "\n"

        return representation

    def subplot(self, nrow=1, ncol=1, bundles=None, settings=None, twinx=False, **kwargs):

        # Here, a single 'fig' will be created with multiple 'axes'
        # The number of axes will be equal to 'nrow * ncol'
        # There will be many 'charts' for one figure.

        import matplotlib.pyplot as plt
        import copy
        fig, axes = plt.subplots(nrow, ncol)
        
        sets = []
        if len(axes.shape) == 1:
            for ax,setting in zip(axes,self.settings):
                setting["ax"] = ax
                sets.append(dict(setting))

        elif len(axes.shape) == 2:
            count = 0
            for i in range(nrow):
                for j in range(ncol):
                    ax = axes[i,j]
                    setting = self.settings[count]
                    setting["ax"] = ax
                    sets.append(dict(setting))
                    print "Blah!"
                    count += 1
        
        self.plot(bundles, sets, twinx, show=False, **kwargs)

    def plot(self, bundles=None, settings=None, twinx=False, show=True, **kwargs):
        #print "SETTINGS", settings
        from chart import chart

        self.process(**kwargs)

        #print self.settings

        if bundles != None:
            diff = len(self.datasets) - len(bundles)
            if diff > 0:
                bundles += [dict(bundles[-1]) for _ in range(diff)]
        else:
            import chart_config as cc
            bundles = [dict(cc._bundle) for _ in range(len(self.datasets))]

        # if settings != None:
        #     for default,new in zip(self.settings, settings):
        #         default.update(new)

        #print self.settings
        _twinx = len(self.datasets) % 2 == 0

        #print len(self.datasets), len(bundles), settings

        # if len(self.charts) == 0:
            ##print "Calculate charts"

        if _twinx and twinx:
            for i in range(0, len(self.datasets), 2):
                d_one = self.datasets[i]
                d_two = self.datasets[i+1]
                b_one = bundles[i]
                b_two = bundles[i+1]
                c = chart([d_one, d_two], self.settings.pop(0))
                #print "Twinxing!"
                c.plot([b_one, b_two], twinx=twinx, show=show, **kwargs)
                self.charts.append(c)

        else:
            for d_set,bundle,settings in zip(self.datasets, bundles, self.settings):
                c = chart([d_set], settings)
                c.plot(bundle, twinx=False, show=show, **kwargs)
                self.charts.append(c)

        # else:
        #     #print "Don't recalculate old charts."
        #     for c in self.charts:
        #         c.plot(bundle=None, **kwargs)

    def process(self, **kwargs):
        for setting,value in kwargs.items():
            if setting == "normal":
                for s in self.settings:
                    s["align_y_axes"] = value
                    #print value

    def set_regressions(self, regressions):
        diff = len(regressions) - len(self.settings)
        if diff > 0:
            import copy
            last_setting = self.settings[-1]
            last_copy = copy.deepcopy(last_setting)
            self.settings = self.settings + [copy.deepcopy(last_setting) for _ in range(diff)]
        for setting,regression in zip(self.settings,regressions):
            if setting != None:
                setting["regression"] = regression

    def set_legends(self, legends):
        diff = len(legends) - len(self.settings)
        if diff > 0:
            import copy
            last_setting = self.settings[-1]
            last_copy = copy.deepcopy(last_setting)
            self.settings = self.settings + [copy.deepcopy(last_setting) for _ in range(diff)]
        for setting,legend in zip(self.settings,legends):
            if setting != None:
                setting["legend"] = legend

    def set_titles(self, titles):
        diff = len(titles) - len(self.settings)
        if diff > 0:
            import copy
            last_setting = self.settings[-1]
            last_copy = copy.deepcopy(last_setting)
            self.settings = self.settings + [copy.deepcopy(last_setting) for _ in range(diff)]
        for setting,title in zip(self.settings,titles):
            if title != None:
                setting["title"] = title

    # Doesn't look good.
    def set_suptitles(self, suptitles):

        diff = len(suptitles) - len(self.settings)
        if diff > 0:
            import copy
            self.settings = self.settings + (list(copy.deepcopy(self.settings[-1][:])) * diff)

        for setting,suptitle in zip(self.settings, suptitles):
            setting["suptitle"] = suptitle