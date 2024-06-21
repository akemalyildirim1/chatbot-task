"""Tests module."""


def mock_async_func_generator(return_value):
    async def mock_func(*args, **kwargs):
        return return_value

    return mock_func
