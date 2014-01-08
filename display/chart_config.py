_chart_settings =    {
                        # Global Settings - specific to all X,Y variables' depiction.
                        "ax": None,
                        "type": "scatter",
                        "suptitle": None,
                        "title": None,
                        "offset": 0.04,
                        "lines": [],
                        "twinx": False,
                        "align_y_axes": False,
                        "scale": "linear",
                        "regression": None,
                        "legend": None
                    }

_bundle =  {
                "x":     {
                    # Global Settings - specific to all X variables' depiction.
                    "max": 0, "min": 0,
                    "label": "X",

                    # Local Settings - specific to individual X variable depiction.
                    "mode": "ko"
                },
                "y":     {
                    # Global Settings - specific to all Y variables' depiction.
                    "max": 0, "min": 0,
                    "label": "Y", "twinx": False,

                    # Local Settings - specific to individual Y variable depiction.
                    "do_fill": True, "fill_color": "green", "fill_alpha": 1, "fill_hatch": "///", "fill_min": 0,
                    "mode": "go", "mark_size": 6, "mark_alpha": 1.,
                    "do_spline": True, "spline": None, "spline_mode": "k--", "spline_width": 2.0
                }
            }