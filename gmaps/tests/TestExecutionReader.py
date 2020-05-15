import json
import unittest

from gmaps.executions.reader import ExecutionDbReader


class TestExecutionReader(unittest.TestCase):
    _output_config = {
        "host": "localhost",
        "database": "gmaps",
        "db_user": "postgres",
        "db_pass": "1234"
    }

    def test_execution_info_retrievement(self):
        reader = ExecutionDbReader(self._output_config)
        reader.auto_boot()
        executions = reader.read()
        reader.finish()
        assert all(
            ["postal_code" in execution and "base_url" in execution and "types" in execution and "country" in execution
             for execution in executions])
        print(json.dumps(executions))
