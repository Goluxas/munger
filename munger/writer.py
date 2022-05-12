import csv
from typing import Callable, Iterable

from .munger import Processor


class Writer:
    def __init__(
        self,
        filename: str,
        condition: Callable,
        include_errors: bool,
        use_fieldnames: Iterable = None,
    ):
        self._open_file(filename)
        self.condition = condition
        self.include_errors = include_errors
        self.fieldnames = use_fieldnames

    def __exit__(self, exception_type, exception_value, exception_traceback):
        self.file.close()

    def __del__(self):
        self.file.close()

    def _open_file(self, filename: str):
        self.file = open(filename, "w")
        # will initialize fieldnames before first write
        self.writer = csv.DictWriter(self.file, fieldnames=[])
        self._fields_initialized = False

    def write(self, processor: Processor) -> bool:
        """Writes the document to file, according to initialized parameters

        Returns:
            bool - True if the doc was written
        """
        if not self._fields_initialized:
            headers = self.fieldnames or list(processor.document.keys())
            if self.include_errors:
                headers.append("ValidationErrors")
            self.writer.fieldnames = headers
            self.writer.writeheader()

            self._fields_initialized = True

        output = processor.document.copy()
        if self.include_errors:
            output["ValidationErrors"] = str(processor.errors)

        if (
            self.condition is not None
            and self.condition(processor)
            or self.condition is None
        ):
            self.writer.writerow(output)
            return True

        return False
