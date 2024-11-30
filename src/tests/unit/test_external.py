import pytest


class S3Error(Exception):
    pass


class FileError(Exception):
    pass


class UploadError(Exception):
    pass


@pytest.mark.asyncio
class TestSaveFileToS3:
    @pytest.mark.parametrize(
        "s3_error,file_error,upload_error,expected_error",
        (
            (False, False, False, None),
            (True, False, False, S3Error),
            (False, True, False, FileError),
            (False, False, True, UploadError),
        ),
    )
    async def test_failure(
        self,
        s3_error,
        file_error,
        upload_error,
        expected_error,
        file,
        boto3_mock,
        s3_mock,
        save_file_to_s3,
        aiofiles_mock,
        aiostream_mock,
        mocker,
    ):
        mocker.patch("services.external.aiofiles", aiofiles_mock)
        if s3_error:
            boto3_mock.client.side_effect = S3Error
        if file_error:
            aiofiles_mock.open.side_effect = FileError
        if upload_error:
            s3_mock.upload_fileobj.side_effect = UploadError

        result = await save_file_to_s3("uuid")

        assert result == (expected_error is None)
        save_file_to_s3.repo.get_by_id.assert_called_once_with("uuid")
        if expected_error is None:
            save_file_to_s3.repo.update.assert_called_once_with(
                file,
                values={"is_saved_to_s3": True},
            )
        else:
            save_file_to_s3.repo.update.assert_not_called()
        boto3_mock.client.assert_called_once_with(
            "s3",
            endpoint_url=save_file_to_s3.endpoint_url,
        )
        if s3_error:
            aiofiles_mock.open.assert_not_called()
            s3_mock.upload_fileobj.assert_not_called()
            return
        aiofiles_mock.open.assert_called_once_with(file.path, "rb")
        if file_error:
            s3_mock.upload_fileobj.assert_not_called()
            return
        s3_mock.upload_fileobj.assert_called_once_with(
            aiostream_mock,
            save_file_to_s3.bucket,
            file.path.strip("/"),
        )
