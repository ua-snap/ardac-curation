"""Helper functions for running the sample pipeline"""

def jprint(msg):
    """J-print, for jupyter printing!
    Just a simple wrapper around print() to print to both
    the jupyter notebook as well as the terminal that called it
    
    This relies on hard-coded reference to global t_out varriable
    containing the results of `t_out = open("/dev/stdout", "w")`
    """
    print(msg, file=t_out, flush=True) # prints to terminal
    return


def generate_nested_dict(dim_combos):
    """Dynamically generate a nested dict based on the different
    dimension name combinations
    Args:
        dim_combos (list): List of lists of decoded coordinate
            values (i.e. season, model, scenario names/values)
    Returns:
        Nested dict with empty dicts at deepest levels
    #
    """

    def default_to_regular(d):
        """Convert a defaultdict to a regular dict
        Thanks https://stackoverflow.com/a/26496899/11417211
        """
        if isinstance(d, defaultdict):
            d = {k: default_to_regular(v) for k, v in d.items()}
        return d

    nested_dict = lambda: defaultdict(nested_dict)
    di = nested_dict()
    for map_list in dim_combos:
        get_from_dict(di, map_list[:-1])[map_list[-1]] = {}

    return default_to_regular(di)


def get_from_dict(data_dict, map_list):
    """Use a list to access a nested dict
    Thanks https://stackoverflow.com/a/14692747/11417211
    """
    return reduce(operator.getitem, map_list, data_dict)