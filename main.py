import milestones.linux
import inspect

run_configuration = {
    "LINUX": {
    }
}

test_count = 1
test_config_key = ""


def run_test(test):
    global test_count

    status = test()

    if status == 0:
        status = "SUCCESS"
    else:
        status = "FAILED"

    print("{}/{} - {} - {}".format(test_count, run_configuration[test_config_key]["TOTAL_TESTS"], test.__name__, status))
    test_count += 1


def _line_order(value):
    return value[2]


def run_linux_tests():
    global test_config_key
    test_config_key = "LINUX"

    name_func_tuples = inspect.getmembers(milestones.linux, inspect.isfunction)


    sorted_functions = []
    for name, func in name_func_tuples:
        if name.startswith("test_"):
            _, start_line = inspect.getsourcelines(func)
            sorted_functions.append((name, func, start_line))

    run_configuration[test_config_key]["TOTAL_TESTS"] = len(sorted_functions)
    sorted_functions.sort(key=_line_order)

    for name, func, _ in sorted_functions:
        run_test(func)


if __name__ == '__main__':
    run_linux_tests()
