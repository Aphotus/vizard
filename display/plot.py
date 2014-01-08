#import matplotlib.pyplot as plt
#import matplotlib.cm as cm

import os, sys, atexit
os.chdir(os.path.dirname(sys.argv[0]))

from mpl_toolkits.basemap import Basemap
import numpy as np

import math

# Global Variables
_fig = None
_ax = None

class Plot:
    """ Class representing a two-dimensional plot. """
    def __init__(self, data, title="Title", t="scatter", m=","):
        self.data = data
        self.title = title
        self.t = t
        self.m = m

    def show(self, ylab=None):
        """ Displays a window with the figures. """
        data = self.data
        fits = Plot.regression(self)

        fig, ax = plt.subplots()
        plt.title(self.title)

        if self.t == "scatter":
            for i in range(len(data)):
                if i == 0:
                    a = ax
                    mode = ('b'+self.m, 'b--')
                elif i == 1:
                    a = ax.twinx()
                    mode = ('g'+self.m, 'g--')

                a.plot(data[i]["x"], data[i]["y"], mode[0])
                a.plot(fits[i]["x"], fits[i]["y"], mode[1])

                a.set_xlabel('Years')
                a.set_ylabel(data[i]["y_lab"])

                for tl in a.get_yticklabels():
                    tl.set_color(mode[0][0])

            fig.autofmt_xdate()

        elif self.t == "time_series":
            from array import array
            import math

            for i in range(len(data)):
                if i == 0:
                    a = ax
                    mode = 'b'+self.m
                elif i == 1:
                    a = ax.twinx()
                    mode = 'r'+self.m

                dat = data[i]

                _min = min(dat["y"])
                _max = max(dat["y"]) - _min

                dat["y"] = [(y-_min)/_max for y in dat["y"]]

                dates = dat["x"]
                values = dat["y"]

                a.plot(dates, [math.asin(v)/math.pi for v in values], mode)

                a.set_xlabel('Years')
                a.set_ylabel(dat["y_lab"])

                for tl in a.get_yticklabels():
                    tl.set_color(mode[0])

            fig.autofmt_xdate()

        elif self.t == "time_series_comp":
            from array import array
            import math
            import numpy as np

            for i in range(len(data)):
                dat = data[i]

                _min = min(dat["y"])
                _max = max(dat["y"]) - _min

                dat["y"] = [(y-_min)/_max for y in dat["y"]]

                data[i]["y"] = dat["y"]

            first = data[0]["y"]
            second = data[1]["y"]

            dates = list(set(data[0]["x"]) & set(data[1]["x"]))

            points = []

            for d in dates:
                points.append(first[data[0]["x"].index(d)] - second[data[1]["x"].index(d)])

            composition = {"x": dates, "y": points}
            self.data = (self.data[0], self.data[1], composition)

            fits = Plot.regression(self)

            ax.plot(dates, points, "m"+self.m)
            ax.plot(fits[2]["x"], fits[2]["y"], "m--")

            ax.set_xlabel('Years')

            if ylab == None:
                ax.set_ylabel(data[0]["y_lab"])
            elif ylab != None:
                ax.set_ylabel(ylab)

            for tl in ax.get_yticklabels():
                tl.set_color('m')

            fig.autofmt_xdate()

        plt.show()

    def regression(self):
        import numpy as np

        fits = []

        for d in self.data:
            x = np.array(range(len(d["y"])))
            y = np.array([_y for _y in d["y"] if _y < 3])

            x_avg = x.mean()
            y_avg = y.mean()

            xy_avg = np.mean(x * y)

            sigma = np.mean(x**2) - (x_avg ** 2)

            m = (xy_avg - (x_avg * y_avg)) / sigma
            b = y_avg - (m * x_avg)

            x_vals = [x for x in d["x"]]
            y_vals = [m*(x_vals.index(x)) + b for x in x_vals]

            fits.append({"x": x_vals, "y": y_vals})

        return fits

    def netcdfPlot(self, key, mode="f", suppress=False, cm_=None):
        try:
            data = self.data[key][:][0]
        except:
            print("Wrong key name.")
            return

        variables = self.data
        lons = variables['lon'][:][0]
        lats = variables['lat'][:][0]

        LON_0 = -40.
        LAT_0 = 72.
        LAT_TS = 72.

        x = variables['x1'][:]
        y = variables['y1'][:]

        w = max(x) - min(x)
        h = max(y) - min(y)

        m = Basemap(width=w-50000, height=h-50000, resolution='l', projection='stere', lat_ts=LAT_TS, lat_0=LAT_0, lon_0=LON_0)

        # # Draw parallels.
        parallels = np.arange(0.,90,10.)
        m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,zorder=-1)

        # # Draw meridians.
        meridians = np.arange(180.,360.,10.)
        m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10,zorder=-1)

        m.drawcoastlines(zorder=3,alpha=0.7)
        m.fillcontinents(color='#FFFFFF',alpha=0.6)

        x, y = m(lons,lats)

        self._register_cms()

        # Contour data over the map.
        if mode == "f":
            if cm_ != "hot":
                cs = m.contourf(x,y,data,30,zorder=2,alpha=.75,cmap=self.cms[0])
            else:
                cs = m.contourf(x,y,data,15,zorder=2,alpha=.75,cmap=cm.RdYlBu_r)

            # add colorbar.
            cbar = m.colorbar(cs,location='right',pad="5%")
            cbar.set_label(self.clab)
        elif mode == "l":
            if cm_ != "hot":
                cs = m.contour(x,y,data,15,linewidths=np.arange(2, .5, -.1),zorder=2,cmap=self.cms[0])
            else:
                cs = m.contour(x,y,data,15,zorder=2,cmap=cm.PuOr_r)

        if not suppress:
            plt.title(self.title)
            plt.show()

    def gradientPlot(self, keys):
        variables = self.data

        g_surftemp = np.gradient(variables[keys[0]][:][0])
        g_airtemp2m = np.gradient(variables[keys[1]][:][0])

        g = np.array(g_surftemp) - np.array(g_airtemp2m)

        lons = variables['lon'][:][0]
        lats = variables['lat'][:][0]

        LON_0 = -40.
        LAT_0 = 72.
        LAT_TS = 72.

        x = variables['x1'][:]
        y = variables['y1'][:]

        w = max(x) - min(x)
        h = max(y) - min(y)

        m = Basemap(width=w-50000, height=h-50000, resolution='l', projection='stere', lat_ts=LAT_TS, lat_0=LAT_0, lon_0=LON_0)

        # # Draw parallels.
        parallels = np.arange(0.,90,10.)
        m.drawparallels(parallels,labels=[1,0,0,0],fontsize=10,zorder=-1)

        # # Draw meridians.
        meridians = np.arange(180.,360.,10.)
        m.drawmeridians(meridians,labels=[0,0,0,1],fontsize=10,zorder=-1)

        m.drawcoastlines(zorder=3,alpha=0.7)
        m.fillcontinents(color='#FFFFFF',alpha=0.6)

        x, y = m(lons,lats)

        self._register_cms()

        # Contour data over the map.
        cs = m.contourf(x,y,g[0],15,zorder=2,alpha=.75,cmap=cm.Accent)

        # add colorbar.
        cbar = m.colorbar(cs,location='right',pad="5%")
        cbar.set_label(self.clab)

        plt.title(self.title)
        plt.show()

    def close(self):
        plt.close()

    def _register_cms(self):
        import matplotlib.colors as col
        # define individual colors as hex values
        cpool = [ '#ffffff', '#dddddd', '#bbbbbb', '#999999', '#666699', '#333366', '#111150',
                  '#000033', '#000000', '#2edfea', '#ea2ec4', '#ea2e40', '#cdcdcd',
                  '#577a4d', '#2e46c0', '#f59422', '#219774', '#8086d9' ]

        cpool_cm = col.ListedColormap(cpool[0:9], 'indexed')
        #cm.register_cmap(name='indexed', cmap=cpool_cm)

        cdict = {'red': ((0.0, 1.0, 1.0),   # First color index. (purple)
                         (0.2, 0.0, 0.0),   # Second color index. (blue)
                         (0.8, 0.0, 0.0),   # Third color index. (green)
                         (0.9, 0.0, 0.0),   # Fourth color index. (orange)
                         (1.0, 0.0, 0.0)),  # Fifth color index. (red)
             'green': ((0.0, 1.0, 1.0),
                       (0.2, 0.0, 0.0),
                       (0.8, 0.0, 0.0),
                       (0.9, 0.0, 0.0),
                       (1.0, 0.0, 0.0)),
             'blue': ((0.0, 1.0, 1.0),
                      (0.2, 0.8, 0.8),
                      (0.8, 0.6, 0.6),
                      (0.9, 0.4, 0.4), 
                      (1.0, 0.2, 0.2))}

        rain_map = col.LinearSegmentedColormap('rain',cdict,N=5,gamma=0.75)
        #cm.register_cmap(name='rain', cmap=rain_map)

        self.cms = [cpool_cm, rain_map]
        
def getSpline(x, y):
    from scipy.interpolate import interp1d

    cubic = interp1d(x, y, kind='cubic')

    xnew = np.arange(x[0], x[-1], .25)
    
    ynew = cubic(xnew)
    
    indices = [i for i in range(len(ynew)) if ynew[i] > 0]
    ynew = [ynew[i] for i in indices]
    xnew = [xnew[i] for i in indices]
    
    return xnew, ynew
    
def _setup(ax, x, y, params):
    _min = -.02
    ticks = ax.get_yticks()
    scale = params["scale"]
    suppress = params["suppress"]
    normal = params["normalize"]
    
    min_lim = .95
    max_lim = 1.05
    
    min_line = .02
    max_line = .95
    
    min_scalex = .995
    max_scalex = 1 + 1 - min_scalex
    
    min_scaley = .995
    
    min_decade = round(x[0] * min_scalex, -1)
    max_decade = round(x[-1] * max_scalex, -1)
    
    if scale == "log":
        _min = 1
        
        # Number of decimal places of the result of dividng by 10.
        exponent = len(str(round(max(y) / 10)))
        ticks = [10**i for i in range(1, exponent)]
        print(exponent)
    
    if suppress:
        if len(x) > len(ax.get_xticks()):
            #ax.xaxis.reset_ticks()
            
            # X-Axis stuff.
            ax.set_xticks([decade for decade in np.arange(min_decade, max_decade+1, 10)])
            ax.set_xticks([half for half in np.arange(min_decade, max_decade+1, 5)], minor=True)
            ax.set_xlim((min(ax.get_xticks())*min_scalex, max(ax.get_xticks())*max_scalex))
            ax.spines['bottom'].set_bounds(min_decade, max_decade)
            ax.xaxis.set_ticks_position('bottom')
            
            if "ratio" in params:
                ax.axhline(_min, params["ratio"]/2, max_line, ls="-", lw=4, color="k")
            else:
                ax.axhline(_min, .02, .98, lw=4, color="k")
                
            ax.xaxis.set_tick_params(width=6)
            
            # Y-Axis stuff.
        
        # Get the 'opposite' y-axis.
        a = ax.twinx()
        
        # Set tick positions to the right.
        a.spines['right'].set_bounds(1, max(ticks))
        a.spines['right'].set_visible(True)
        
        # Y-Axis stuff.
        #ax.set_yscale(scale)
        min_limy = _min * min_lim
        max_limy = ax.get_ylim()[1]
        a.set_ylim((min_limy, max_limy))
        a.set_yticks(ticks)
        
        if "ratio" in params:
            ax.axhline(max(ticks), params["ratio"]/2, max_line, ls="--", color="k", alpha=.2, lw=3)
        
        max_line = (max(ticks) / max_limy)
        a.axvline(max_decade*max_scalex, min_line, max_line, lw=4, color=params["mode"][0])
        a.yaxis.set_tick_params(width=6, color=params["mode"][0])
        
        ax = a
        
    else:
        # Set tick positions to the left.
        if normal:
            ax.spines['left'].set_bounds(0, max(ticks))
        else:
            ax.spines['left'].set_bounds(_min, max(ticks))
        
        ax.yaxis.set_ticks_position('left')
        
        # Hide spines.
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.spines['left'].set_visible(False)
        
        # X-Axis stuff.
        ax.set_xticks([decade for decade in np.arange(min_decade, max_decade+1, 10)])
        ax.set_xticks([half for half in np.arange(min_decade, max_decade+1, 6)], minor=True)
        
        min_limx = min(ax.get_xticks()) * min_scalex
        max_limx = max(ax.get_xticks()) * max_scalex
        ax.set_xlim((min_limx, max_limx))
        
        ax.spines['bottom'].set_bounds(min_decade, max_decade)
        ax.xaxis.set_ticks_position('bottom')
        #ax.axhline(_min, .02, .98, lw=4, color="k")
        ax.xaxis.set_tick_params(width=6)
        
        # Y-Axis stuff.
        ax.set_yscale(scale)
        
        min_limy = _min * min_lim
        max_limy = max([max(ticks), max(params["ynew"])]) * max_lim
        
        ax.set_ylim((min_limy, max_limy))
        ax.set_yticks(ticks)
        
        if max(ticks) < max(params["ynew"]):
            params["ratio"] = 1 - (max(ax.get_xticks()) - min(ax.get_xticks())) / (max_limx - min_limx); print(params["ratio"])         
            
            max_line = 1 - math.asin(max(params["ynew"]) - max(ticks))
        
        ax.axvline(min_decade*min_scalex, min_line, max_line, lw=4, color=params["mode"][0])
        ax.yaxis.set_tick_params(width=6, color=params["mode"][0])
    
    if normal:
        _min = 0
    
    return _min, ax

def plot(x, y, title=None, xlab="X", ylab="Y", params=None):
    import matplotlib.pyplot as plt
    
    global _fig, _ax

    #print("Length: ", len(x), len(y))
    
    if params == None:
        return
            
    xnew, ynew = getSpline(x, y)
    params["ynew"] = ynew

    if params["suppress"]:
        fig = _fig
        ax = _ax
    else:
        fig, ax = plt.subplots()
        _fig = fig
        _ax = ax
    
    _min, ax = _setup(ax, x, y, params)
    
    ax.plot(xnew, ynew, params["spline_mode"], linewidth=params["spline_width"])
    ax.fill_between(xnew, ynew, _min, color=params["fill_color"], hatch=params["hatch"], alpha=params["alpha"])
    ax.plot(x, y, params["mode"], ms=params["mark_size"])
    
    fig.autofmt_xdate()

    if title != None:
        plt.title(title)
    
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
        
    ax.grid(True, alpha=.5)
    plt.show()

