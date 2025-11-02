
import functools

def trace(param: int = 0):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            print(func.__name__)
            print("This is a wrapper!")
            result = func(*args, **kwargs)
            return result

        return wrapper
    return decorator

@trace()
def my_func(a: int = 0, b: int = 0):
    return a + b

if __name__ == '__main__':
    count = my_func(1, 2)
    print(count)