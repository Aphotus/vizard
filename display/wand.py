
class wand:

    import numpy as np
    import math
    from scipy.interpolate import interp1d

    # Local Plot Settings. - One bivariate settings unit.
    __bundle = None

    def __init__(self, parameters):
        self.__bundle = {   "plot": {
                            "title": parameters["plot"]["title"],
                            "axis": None
                            },
                            "x":    {
                                "mode": parameters["X"]["mode"]
                            },
                            "y":    {
                                "label": parameters["Y"]["label"],
                                "mode": parameters["Y"]["mode"],
                                "point_size": parameters["Y"]["point_size"],
                                "point_alpha": parameters["Y"]["point_alpha"],
                                "do_fill": parameters["Y"]["do_fill"],
                                "fill_color": parameters["Y"]["fill_color"],
                                "fill_alpha": parameters["Y"]["fill_alpha"],
                                "fill_hatch": parameters["Y"]["fill_hatch"],
                                "do_spline": parameters["Y"]["do_spline"],
                                "spline": parameters["Y"]["splines"],
                                "spline_mode": parameters["Y"]["spline_mode"],
                                "spline_width": parameters["Y"]["spline_width"]
                            }
                        }

    def _merge(self, new_settings, old_settings):
        for category in new_settings:
            for setting in new_settings[category]:
                old_settings[category][setting] = new_settings[category][setting]

        return old_settings

    def get_bundle(self, x, y, _bundle=None):
        bundle = self.__bundle

        if _bundle != None:
             _bundle = self._merge(_bundle, bundle)
        
        if bundle["y"]["do_spline"]:
            x_new, y_new = self._get_spline(x, y)
            bundle["y"]["spline"] = [x_new, y_new]
            self.parameters["Y"]["splines"].append(bundle["y"]["spline"])

        bundle["x"]["min"] = min(x)
        bundle["x"]["max"] = max(x)

        bundle["y"]["min"] = min(y)
        bundle["y"]["max"] = max(y)

        return bundle

