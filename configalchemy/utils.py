import traceback


def display_property_attribute_error_exceptions(function):
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except AttributeError:
            traceback.print_exc()
            raise

    return wrapper
