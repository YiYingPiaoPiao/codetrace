
class BlockTrace:
    def __init__(self) -> None:
        pass

    def __enter__(self) -> object:
        print("Starting")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        print("Exit")
        return False


if __name__ == '__main__':

    with BlockTrace():
        print("H")
        pass
    pass