import typing as t


def merge_lists(*args) -> t.Optional[t.List]:
    """
    Merge/concatenate a set of lists passed in the args. If any value in the args list is
    None, it is ignored. If all values in the args list are None (or the args list is
    empty) None is returned.

    If an arg encountered in the list is a dict rather than a list, all subsequent values
    in the args list will be treated as keys into the dict and the value for those keys
    in the dict will be treated as lists to be concatenated as with the other lists
    passed in the args prior to the dict.
    """

    ret_list: t.Optional[t.List] = None
    dict_val: t.Optional[t.Dict] = None
    for arg in args:
        list_for_arg: t.Optional[t.List] = None
        if isinstance(arg, dict):
            dict_val = arg
        elif dict_val is not None and arg in dict_val:
            list_for_arg = dict_val[arg]
            if not isinstance(list_for_arg, list):
                list_for_arg = None
        elif isinstance(arg, list):
            list_for_arg = arg
        if list_for_arg is not None:
            if ret_list is None:
                ret_list = list_for_arg
            else:
                ret_list += list_for_arg
    return ret_list
