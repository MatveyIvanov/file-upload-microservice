import uuid
from datetime import datetime
from unittest import mock

import pytest

from config.di import get_di_test_container
from models.file import File
from schemas.files import FileMetadata
from services.clean import CleanDisk
from services.create import CreateFile
from services.external import SaveFileToS3
from services.extract import ExtractMetadata

__container = get_di_test_container()


@pytest.fixture(scope="session")
def container():
    return __container


@pytest.fixture
def session():
    return mock.Mock()


@pytest.fixture
def now():
    return datetime(2024, 1, 1)


@pytest.fixture
def file(now):
    return File(
        uuid=uuid.uuid4(),
        path="path",
        size=1024,
        format="format",
        name="name",
        ext="ext",
        is_saved_to_s3=True,
        is_removed_from_disk=False,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def repo_mock_factory():
    def factory(instance):
        rows = [[instance]]
        repo = mock.AsyncMock()
        repo.all.return_value = rows
        repo.get_by_id.return_value = instance
        repo.get_by_ids.return_value = rows
        repo.get_by_field.return_value = instance
        repo.get_by_filters.return_value = rows
        repo.exists_by_field.return_value = True
        repo.create.return_value = instance
        repo.update.return_value = None
        repo.multi_update.return_value = None
        repo.delete.return_value = None
        repo.delete_by_field.return_value = None
        return repo

    return factory


@pytest.fixture
def filter_mock_factory():
    def factory(model_class):
        filter = mock.Mock()
        filter.return_value = filter
        return filter

    return factory


@pytest.fixture
def filter_seq_mock():
    filter_seq = mock.Mock()
    filter_seq.return_value = filter_seq
    filter_seq.compile.return_value = []
    return filter_seq


@pytest.fixture
def aiostream_mock():
    aiostream = mock.AsyncMock()
    return mock.AsyncMock(return_value=aiostream)


@pytest.fixture
def aiofiles_mock(aiostream_mock):
    class mockedasynccontextmanager:
        async def __aenter__(self, *args, **kwargs):
            return aiostream_mock

        async def __aexit__(self, *args, **kwargs):
            return

    aiofiles = mock.Mock()
    aiofiles.open.return_value = mockedasynccontextmanager()
    return aiofiles


@pytest.fixture()
def os_mock():
    os = mock.AsyncMock()
    return os


@pytest.fixture
def get_current_time_mock(now):
    get_current_time = mock.Mock(return_value=now)
    return get_current_time


@pytest.fixture
def extract_metadata_mock(file):
    return mock.Mock(
        return_value=FileMetadata(
            size=file.size,
            format=file.format,
            name=file.name,
            ext=file.ext,
        )
    )


@pytest.fixture
def s3_mock():
    s3 = mock.AsyncMock()
    return mock.AsyncMock(return_value=s3)


@pytest.fixture
def boto3_mock(s3_mock):
    class mockedasynccontextmanager:
        async def __aenter__(self, *args, **kwargs):
            return s3_mock

        async def __aexit__(self, *args, **kwargs):
            return

    boto3 = mock.Mock()
    boto3.client.return_value = mockedasynccontextmanager()
    return boto3


@pytest.fixture
def clean_disk(
    repo_mock_factory,
    filter_mock_factory,
    filter_seq_mock,
    file,
    container,
):
    with container.clean_disk.override(
        CleanDisk(
            max_days=10,
            max_days_unused=10,
            repo=repo_mock_factory(file),
            created_at_filter=filter_mock_factory(File),
            updated_at_filter=filter_mock_factory(File),
            is_removed_from_disk_filter=filter_mock_factory(File),
            filter_seq_class=filter_seq_mock,
        )
    ):
        return container.clean_disk()


@pytest.fixture
def create_file(
    file,
    repo_mock_factory,
    extract_metadata_mock,
    container,
):
    with container.create_file.override(
        CreateFile(
            base_path="/path",
            max_bytes=2048,
            repo=repo_mock_factory(file),
            extract_metadata=extract_metadata_mock,
        )
    ):
        return container.create_file()


@pytest.fixture
def save_file_to_s3(
    file,
    repo_mock_factory,
    boto3_mock,
    container,
):
    with container.save_file_to_s3.override(
        SaveFileToS3(
            repo=repo_mock_factory(file),
            boto3=boto3_mock,
            endpoint_url="s3://example.com",
            bucket="bucker",
        )
    ):
        return container.save_file_to_s3()


@pytest.fixture
def extract_metadata(container):
    with container.extract_metadata.override(ExtractMetadata()):
        return container.extract_metadata()
