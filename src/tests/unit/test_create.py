import io
from pathlib import Path
from unittest import mock
import uuid
from fastapi import UploadFile
import pytest

from schemas.files import CreateFileSchema, UploadedFile
from utils.exceptions import Custom400Exception


@pytest.mark.asyncio
class TestCreateFile:
    async def test_invalid_size(
        self,
        extract_metadata_mock,
        create_file,
        aiofiles_mock,
        aiostream_mock,
        session,
        mocker,
    ):
        mocker.patch("services.create.aiofiles", aiofiles_mock)
        extract_metadata_mock.return_value.size = create_file.max_bytes + 1

        upload_file = UploadFile(
            file=io.BytesIO(),
            size=1024,
            filename="filename",
            headers=None,
        )

        with pytest.raises(Custom400Exception):
            await create_file(upload_file, session=session)

        extract_metadata_mock.assert_called_once_with(upload_file)
        aiofiles_mock.open.assert_not_called()
        aiostream_mock.write.assert_not_called()
        create_file.repo.create.assert_not_called()

    async def test_create(
        self,
        extract_metadata_mock,
        create_file,
        aiofiles_mock,
        aiostream_mock,
        session,
        mocker,
    ):
        uuid_mock = mock.Mock()
        uuid_mock.uuid4.return_value = uuid.uuid4()

        mocker.patch("services.create.aiofiles", aiofiles_mock)
        mocker.patch("services.create.random_string", return_value="random")
        mocker.patch("services.create.uuid", uuid_mock)

        expected_path = str(
            Path(
                create_file.base_path,
                f"random.{extract_metadata_mock.return_value.ext}",
            )
        )

        upload_file = UploadFile(
            file=io.BytesIO(),
            size=1024,
            filename="filename",
            headers=None,
        )
        result = await create_file(upload_file, session=session)

        assert isinstance(result, UploadedFile)
        assert result.uuid == create_file.repo.create.return_value.uuid
        assert result.path == create_file.repo.create.return_value.path
        assert result.size == create_file.repo.create.return_value.size
        assert result.format == create_file.repo.create.return_value.format
        assert result.name == create_file.repo.create.return_value.name
        assert result.ext == create_file.repo.create.return_value.ext
        assert result.created_at == create_file.repo.create.return_value.created_at
        assert result.available_for_download is True
        extract_metadata_mock.assert_called_once_with(upload_file)
        aiofiles_mock.open.assert_called_once_with(
            expected_path,
            "wb",
        )
        upload_file.file.seek(0)
        aiostream_mock.write.assert_called_once_with(await upload_file.read())
        create_file.repo.create.assert_called_once_with(
            entry=CreateFileSchema(
                uuid=uuid_mock.uuid4.return_value,
                path=expected_path,
                size=extract_metadata_mock.return_value.size,
                format=extract_metadata_mock.return_value.format,
                name=extract_metadata_mock.return_value.name,
                ext=extract_metadata_mock.return_value.ext,
            ),
            session=session,
        )
