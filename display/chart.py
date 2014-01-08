# View

class chart:

    def __init__(self, datasets, settings=None, chart_type=None):
        import matplotlib.pyplot as plt
        import atexit
        
        self.__plt = plt
        self.__old_ax = None
        atexit.register(lambda destruct: self.__plt.close(), self)

        self.datasets = datasets
        self.type = chart_type
        self.type = "scatter"

        from viz.display.chart_config import _chart_settings
        default_settings = _chart_settings
        default_settings["lines"] = []

        if settings != None:
            default_settings.update(settings)
            self.settings = default_settings
        else:
            self.settings = default_settings

        self.settings["lines"] = []

    def __str__(self):
        representation = ""

        for d in self.datasets:
            representation += str(d)
            representation += "\n"

        return representation

    # def plot(self, bundle):
    #     pass
    #     # This should be a list of:
    #     #   Titles
    #     #   Labels
    #     #   Styles
    #     #   Twinxing can be figured here.

    def _merge(self, new_settings, old_settings):
        if new_settings != None:
            for category in new_settings:
                for setting in new_settings[category]:
                    old_settings[category][setting] = new_settings[category][setting]

        return old_settings

    def plot(self, bundle=None, twinx=False, show=True, **kwargs):
        """ Plot a single x,y dataset. """
        #print len(self.datasets)
        import viz.display.chart_config as cc
        
        if kwargs != None:
            for d_set in self.datasets:
                d_set.process(kwargs)

        if not twinx:
            ### Need to make this listified.
            bundle = self._merge(bundle, cc._bundle)

            d_set = self.datasets[0]

            fig, ax = self.setup_plot(first=True)

            if bundle["y"]["do_spline"]:
                bundle["y"]["spline"] = self._get_spline(d_set)

            self._plot_xy(bundle, data=d_set, show=False)

            self._setup_axes(d_set, bundle, last=True)
            
            if self.settings["type"] == "time":
                fig.autofmt_xdate()

            if show:
                self.__plt.show()

        elif twinx:
            ##print "Bundles\n", bundle
            first = True
            for d_set,bundle in zip(self.datasets, bundle):
                bundle = self._merge(bundle, cc._bundle)

                if kwargs != None:
                    d_set.process(kwargs)

                fig, ax = self.setup_plot(first)

                if bundle["y"]["do_spline"]:
                    bundle["y"]["spline"] = self._get_spline(d_set)

                self._plot_xy(bundle, data=d_set, show=False)

                bundle["y"]["twinx"] = not first
                self._setup_axes(d_set, bundle, last=not first)
                
                if self.settings["type"] == "time":
                    fig.autofmt_xdate()

                if not first and show:
                    self.__plt.show()
                
                first = False

    def _plot_xy(self, bundle=None, data=None, show=False):
        """ Plot a list of x-values against a list of y-values. """
        import numpy as np

        ax = self.__plt.gca()

        x_params = bundle["x"]
        y_params = bundle["y"]

        if data == None:
            d_set = self.datasets[0]
            x = d_set.X.values
            y = d_set.Y.values

        else:
            x = data.X.values
            y = data.Y.values
        
        # Legend marks.
        marks = {}
        if bundle != None:
            if y_params["do_spline"]:
                spline = y_params["spline"]
                ax.plot(spline[0], spline[1], y_params["spline_mode"], lw=y_params["spline_width"])
            
            if y_params["do_fill"]:
                if self.settings["scale"] == "log":
                    fill_min = 1.01
                else:
                    fill_min = min(ax.get_yticks())
                if y_params["do_spline"]:
                    spline = y_params["spline"]
                    ax.fill_between(spline[0], spline[1], fill_min, color=y_params["fill_color"], linewidth=1, hatch=y_params["fill_hatch"], alpha=y_params["fill_alpha"])
                else:
                    ax.fill_between(x, y, fill_min, color=y_params["fill_color"], hatch=y_params["fill_hatch"], linewidth=1, alpha=y_params["fill_alpha"])

        if x.size == 1:
            x = list(range(len(y)))

        point = ax.plot(x, y, y_params["mode"], ms=y_params["mark_size"], label=self.settings["legend"]["point"])
        marks["point"] = point

        if self.settings["regression"] != None:
            x, y, m = self.settings["regression"]
            regression, = ax.plot(x, y, 'b--', label=self.settings["legend"]["regression"])
            marks["regression"] = regression
            x_mid, y_mid = x[x.size//20], y[y.size//20]
            ax.annotate('$f(x) \\sim x^{-\\alpha}$; $\\alpha='+str(round(m,3))+'$',
                xy=(x_mid, y_mid),
                xytext=(x_mid-(ax.get_xlim()[1]-ax.get_xlim()[0])/4, y_mid-(ax.get_xlim()[1]-ax.get_ylim()[0])/6),
                arrowprops=dict(facecolor='black', shrink=0.05), fontsize=15
            )

        if self.settings["legend"] != None:
            ax.legend(numpoints=1, bbox_to_anchor=[1, 0.9])
            # legend = self.settings["legend"]; print legend

            # labels = []
            # if "point" in legend:
            #     labels.append(legend["point"])
            # if "regression" in legend:
            #     labels.append(legend["regression"])

            # if len(labels) != 0 and "point" in marks and "regression" in marks:
            #     ax.legend((point, regression), labels, numpoints=1)
            # elif len(labels) != 0 and "point" in marks:
            #     ax.legend(point, labels, numpoints=1)

        if show:
            print "Not Happening - plotxy"
            self.__plt.show()

    def __setup_x_axis(self, x, bundle):    

        import numpy as np

        # if self.__old_ax == None:
        ax = self.__plt.gca()
        # else:
        #     ax = self.__old_ax

        # X stuff.
        x_min = min(x)
        x_max = max(x)
        
        plot_type = self.settings["type"]
        offset = self.settings["offset"]

        major_ticks = None
        minor_ticks = None
        
        # Handle plot_type.
        if plot_type == "scatter":
            # Number of decimal places after dividing max(y) by 10.
            delta = round((x_max-x_min) / 10)
            diff_exponent = len(str(delta)) - 3
            delta = round(x_min / 10)
            min_exponent = len(str(delta)) - 1
            delta = round(x_max / 10)
            max_exponent = len(str(delta)) - 2

            diff = (x_max - x_min) / 10.

            _x_min = round(x_min, -min_exponent)
            _x_max = round(x_max, -max_exponent)*2
            _diff = round(diff, -diff_exponent)
            tick_diff = round(_diff/(x_max-_x_max))
            major_ticks = np.arange(_x_min, _x_max+_diff*tick_diff, _diff)

            major_ticks = ax.get_xticks()

            x_min = min(major_ticks)
            x_max = max(major_ticks)

        elif plot_type == "time":
            # Round 'min' and 'max' to nearest ten.
            x_tick_min = round(x_min, -1) - 10
            x_tick_max = round(x_max, -1) + 20
            if self.__old_ax != None:
                ax = self.__old_ax
                curr_x_ticks = ax.get_xticks()
                
                new_x_less = x_tick_min < min(curr_x_ticks)
                new_x_more = x_tick_max > max(curr_x_ticks)

                if new_x_less or new_x_more:
                    #print "\n\n\n\nIs this ever happening?", curr_x_ticks
                    major_ticks = [decade for decade in np.arange(x_tick_min, x_tick_max, 10)]
                    minor_ticks = [half for half in np.arange(x_tick_min, x_tick_max - 5, 5)]
                
                    x_min = min(major_ticks); #print x_min
                    x_max = max(major_ticks); #print x_max

            else:
                major_ticks = [decade for decade in np.arange(x_tick_min, x_tick_max, 10)]
                minor_ticks = [half for half in np.arange(x_tick_min, x_tick_max - 5, 5)]
            
                x_min = min(major_ticks)
                x_max = max(major_ticks)

        else:
            #print("Invalid 'plot_type'")
            return
        
        if major_ticks != None:
            ax.set_xticks(major_ticks)
        
        if minor_ticks != None:
            ax.set_xticks([minor_ticks[i] for i in range(len(minor_ticks)) if i%2==1], minor=True)

        difference = x_max - x_min

        lim_min = x_min - difference * offset
        lim_max = x_max + difference * offset
        ax.set_xlim((lim_min, lim_max))

        ax.spines['bottom'].set_bounds(x_min, x_max)
        ax.xaxis.set_ticks_position('bottom')
        ax.xaxis.set_tick_params(width=4, length=5, color=bundle["mode"][0])
        ax.xaxis.set_tick_params(which="minor", length=4, color=bundle["mode"][0])
    
    def __set_ylim(self, y_min, y_max):
        ax = self.__plt.gca()

        offset = self.settings["offset"]
        difference = y_max - y_min
        
        lim_min = y_min - difference * offset

        lim_max = y_max + difference * offset
        
        ax.set_ylim((lim_min, lim_max))

    def _set_ylim(self, y_min, y_max, bundle=None):

        if bundle != None and bundle["do_spline"]:
            spline = bundle["spline"]
            if (max(spline[1]) > y_max):
                #print "This Can't be!"
                y_max = max(spline[1])

        # If we're 'twinxing' and aligning two datasets...
        if self.__old_ax != None and self.settings["align_y_axes"]:
            lim_min, lim_max = self.__old_ax.get_ylim()[0], self.__old_ax.get_ylim()[1]

            #print "We do come here, right?"
            ax = self.__plt.gca()

            ax.set_ylim((lim_min, lim_max))
            return
        
        self.__set_ylim(y_min, y_max)

    def __setup_y_axis(self, y, bundle):
    
        import numpy as np

        ax = self.__plt.gca()

        # Chart stuff.
        offset = self.settings["offset"]
        y_scale = self.settings["scale"]
        
        # Y stuff.
        y_min = min(y)
        y_max = max(y)
        twinx = bundle["twinx"]

        major_ticks = None
        minor_ticks = None
        
        ax.set_yscale(y_scale)
    
        # Handle y_scale.
        if y_scale == "log":
            #y_min = 0
            
            # Number of decimal places after dividing max(y) by 10.
            exponent = len(str(round(y_max / 10)))
            #major_ticks = [10**i for i in range(0, exponent)]
            major_ticks = ax.get_yticks()
            y_min = min(major_ticks)
            y_max = max(major_ticks)          
            
        elif y_scale == "linear":
            if (max(y) - min(y)) > 10:
                # Number of decimal places after dividing max(y) by 10.
                delta = round(y_min / 10)
                min_exp = len(str(delta))
                delta = round(y_max / 10)
                max_exp = len(str(delta))-2

                tick_min = round(y_min, -min_exp)
                tick_max = round(y_max, -max_exp)
                tick = (tick_max - tick_min) / 10

                if (y_max > tick_max-tick):
                    while tick_max < y_max+tick:
                        tick_max += tick
                if (y_min < tick_min):
                    while tick_min > y_min:
                        tick_min -= tick

                major_ticks = np.arange(tick_min, tick_max, tick)

                y_min = min(major_ticks)
                y_max = max(major_ticks)
            else:
                # Number of decimal places after dividing max(y) by 10.
                min_exp = len(str(y_min))
                max_exp = len(str(y_max))-2

                tick_min = round(0)
                tick_max = round(y_max)
                tick = (tick_max - tick_min) / 10

                if (y_max > tick_max-tick):
                    while tick_max < y_max+tick:
                        tick_max += tick
                if (y_min < tick_min):
                    while tick_min > y_min:
                        tick_min -= tick

                major_ticks = np.arange(tick_min, tick_max, tick)

                y_min = min(major_ticks)
                y_max = max(major_ticks)
            
        else:
            #print("Invalid 'y_scale'")
            return
        
        if twinx:
            if y_scale != "log":
                self._set_ylim(y_min, y_max, bundle)

            self.settings["lines"].append({"type": "y-axis-r", "axis": ax, "start": min(ax.get_xlim()), "min": min(major_ticks), "max": max(major_ticks), "limits": ax.get_ylim(), "color": bundle["mode"][0], "width": 4, "style": "-", "alpha": 1. })

        elif not twinx:
            if y_scale != "log":
                self._set_ylim(y_min, y_max, bundle)

            ax.yaxis.set_ticks_position('left')
            self.settings["lines"].append({"type": "y-axis-l", "axis": ax, "start": min(ax.get_xlim()), "min": min(major_ticks), "max": max(major_ticks), "limits": ax.get_ylim(), "color": bundle["mode"][0], "width": 4, "style": "-", "alpha": 1. })

        self.settings["lines"].append({"type": "h-guide", "axis": ax, "start":max(y), "color": bundle["mode"][0], "width": 1, "alpha": .4, "style": "--" })

        if y_scale != "log":
            minor_ticks = [(major_ticks[1] - major_ticks[0]) * i / 2 for i in range(1, len(major_ticks)*2-1)]
            
            if major_ticks != None:
                ax.set_yticks(major_ticks)#, map(lambda y: "%.1f" % y, major_ticks*(10**(-7))))
            if minor_ticks != None:
                ax.set_yticks([minor_ticks[i] for i in range(len(minor_ticks)) if i%2==0], minor=True)

        ax.yaxis.set_tick_params(which="major", width=4, length=5, color=bundle["mode"][0])
        ax.yaxis.set_tick_params(which="minor", width=1, length=4, color=bundle["mode"][0])
        
    def __draw_lines(self, bundle):

        ax = self.__plt.gca()

        x_limits = ax.get_xlim()
        y_limits = ax.get_ylim()
        offset = self.settings["offset"]
        x_min = min(ax.get_xticks())
        x_max = max(ax.get_xticks())
        y_min = min(ax.get_yticks())
        y_max = max(ax.get_yticks())
        
        axis_length = x_limits[1] - x_limits[0]
        lim_min_ratio = (x_min - x_limits[0]) / axis_length
        lim_max_ratio = (x_limits[1] - x_max) / axis_length
        ax.axhline(min(y_limits), lim_min_ratio, 1-lim_max_ratio, lw=4, color="k")

        lines = self.settings["lines"]; ###print "LINES", lines
        for line in lines:
            if line["type"] == "y-axis-l":
                ax = line["axis"]
                y_limits = line["limits"]

                axis_length = y_limits[1] - y_limits[0]

                lim_min_ratio = abs(line["min"] - y_limits[0]) / axis_length; ###print "LIMINIMRATIO:", lim_min_ratio
                lim_max_ratio = abs(y_limits[1] - line["max"]) / axis_length; ###print "LIMAXINRAITO:", lim_max_ratio

                ax.axvline(min(ax.get_xlim()), lim_min_ratio, 1-lim_max_ratio, lw=line["width"], color=line["color"], alpha=line["alpha"])

            elif line["type"] == "y-axis-r":
                ax = line["axis"]
                y_limits = line["limits"]

                axis_length = y_limits[1] - y_limits[0]

                lim_min_ratio = abs(line["min"] - y_limits[0]) / axis_length; ###print "LIMINIMRATIO:", lim_min_ratio
                lim_max_ratio = abs(y_limits[1] - line["max"]) / axis_length; ###print "LIMAXINRAITO:", lim_max_ratio
                ax.axvline(max(ax.get_xlim()), lim_min_ratio, 1-lim_max_ratio, lw=line["width"], color=line["color"], alpha=line["alpha"])

            elif line["type"] == "h-guide":
                a = line["axis"]
                axis_length = x_limits[1] - x_limits[0]
                lim_min_ratio = (min(ax.get_xticks()) - x_limits[0]) / axis_length
                lim_max_ratio = (x_limits[1] - min(ax.get_xticks())) / axis_length
                a.axhline(line["start"], lim_min_ratio, lim_max_ratio, lw=4, color=line["color"], ls=line["style"], alpha=line["alpha"])
                print "My kinda guide!"

        del self.settings["lines"]

    def _setup_axes(self, data, bundle=None, first=True, last=False):
        
        ax = self.__plt.gca()

        ax.set_xlabel(bundle["x"]["label"])
        ax.set_ylabel(bundle["y"]["label"])

        self.__setup_x_axis(data.X, bundle["x"])
        self.__setup_y_axis(data.Y, bundle["y"])

        if last:
            self.__draw_lines(bundle)

        # Hide spines.
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        ax.spines['bottom'].set_visible(False)

    def setup_plot(self, first=True):
        """ Configures the axis with the 'parameters'. """
        if not first:
            if self.settings["ax"] == None:
                fig = self.__plt.gcf()
                ax = fig.gca()
                
            else:
                fig = self.__plt.gcf()
                ax = self.settings["ax"]
                #fig.sca(ax)

            self.__old_ax = ax
            ax = ax.twinx()
            self.__plt.sca(ax)

        elif first:
            if self.settings["ax"] == None:
                fig, ax = self.__plt.subplots()
            else:
                fig = self.__plt.gcf()
                ax = self.settings["ax"]
                fig.sca(ax)
                ##print "\n\nAXIS", ax
            
            ax.grid(True, "major", alpha=.5)
            ax.grid(True, "minor", alpha=.2)
            
            suptitle = self.settings["suptitle"]
            title = self.settings["title"]
            if title != None:
                self.__plt.title(title)

            if suptitle != None:
                self.__plt.suptitle(suptitle)
        
        return fig, ax

    def _get_spline(self, data):
        from scipy.interpolate import interp1d, splrep
        import numpy as np

        x = data.X.values
        y = data.Y.values

        ###print "LEN X", len(x), "LEN Y", len(y)
        
        cubic = interp1d(x, y, kind='cubic')

        x_new = np.arange(x[0], x[-1]+.25, .25)
        y_new = cubic(x_new)#; ###print "YNEW!!!", y_new

        # Filter negative values.
        indices = [i for i in range(len(y_new)) if y_new[i] > 0]
        y_new = [y_new[i] for i in indices]
        x_new = [x_new[i] for i in indices]

        return x_new, y_new