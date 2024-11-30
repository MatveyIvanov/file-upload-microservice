import io
from fastapi import UploadFile
import pytest

from schemas.files import FileMetadata


class TestExtractMetadata:
    @pytest.mark.parametrize(
        "upload_file,expected_result",
        (
            (
                UploadFile(
                    io.BytesIO(),
                    size=1024,
                    filename="filename.ext",
                    headers=None,
                ),
                FileMetadata(
                    size=1024,
                    format="unknown",
                    name="filename.ext",
                    ext="ext",
                ),
            ),
            (
                UploadFile(
                    io.BytesIO(),
                    size=1024,
                    filename="filename.png",
                    headers={"content-type": "image/png"},
                ),
                FileMetadata(
                    size=1024,
                    format="image/png",
                    name="filename.png",
                    ext="png",
                ),
            ),
        ),
    )
    def test_extract(self, upload_file, expected_result, extract_metadata):
        assert extract_metadata(upload_file) == expected_result
