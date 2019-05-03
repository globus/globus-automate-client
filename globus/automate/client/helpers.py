import json
# Pattern (and code) taken from:
# https://gist.github.com/mivade/384c2c41c3a29c637cb6c603d4197f9f


def argument(*name_or_flags, **kwargs):
    """Convenience function to properly format arguments to pass to the
    subcommand decorator.
    """
    args = list()
    for arg in name_or_flags:
        args.append(arg)
    return args, kwargs
    # return ([*name_or_flags], kwargs) # <-- tuple, set, and list unpacking requires Python 3.5 or greater


def subcommand(args, parent, **kwargs):
    def decorator(func):
        parser = parent.add_parser(
            func.__name__.replace('_', '-'),
            description=func.__doc__,
            **kwargs)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
        return func

    return decorator


_internal_arg_names = ['func', 'subcommand', 'identifier']


def clear_internal_args(args):
    for arg_name in _internal_arg_names:
        try:
            args.pop(arg_name)
        except KeyError:
            pass  # Its ok if the key is not in the list to be cleared
    return args


def json_parse_args(in_dict, key_names):
    for key_name in key_names:
        val = in_dict.pop(key_name, None)
        if val is not None:
            try:
                val = json.loads(val)
            except ValueError:
                raise ValueError(
                    'value for {}: {} is not encoded in JSON'.format(
                        key_name, val))
            in_dict[key_name] = val
    return in_dict
