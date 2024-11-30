from datetime import timedelta
from unittest import mock
import pytest

from utils.sqlalchemy import mode, operator


@pytest.mark.asyncio
class TestCleanDisk:
    @pytest.mark.parametrize("file_exists", (True, False))
    async def test_clean(
        self,
        file_exists,
        now,
        file,
        clean_disk,
        os_mock,
        get_current_time_mock,
        mocker,
    ):
        mocker.patch("services.clean.os", os_mock)
        mocker.patch("services.clean.get_current_time", get_current_time_mock)

        if not file_exists:
            os_mock.remove.side_effect = FileNotFoundError

        await clean_disk()

        clean_disk.filter_seq_class.assert_has_calls(
            [
                mock.call(
                    mode.or_,
                    clean_disk.created_at_filter.return_value,
                    clean_disk.updated_at_filter.return_value,
                ),
                mock.call(
                    mode.and_,
                    clean_disk.is_removed_from_disk_filter.return_value,
                    clean_disk.filter_seq_class.return_value,  # not perfect :/
                ),
            ]
        )
        clean_disk.is_removed_from_disk_filter.assert_called_once_with(
            False,
            operator.is_,
        )
        clean_disk.created_at_filter.assert_called_once_with(
            now - timedelta(days=clean_disk.max_days),
            operator.le,
        )
        clean_disk.updated_at_filter.assert_called_once_with(
            now - timedelta(days=clean_disk.max_days_unused),
            operator.le,
        )
        clean_disk.repo.get_by_filters.assert_called_once_with(
            filters=clean_disk.filter_seq_class.return_value
        ),
        clean_disk.repo.multi_update.assert_called_once_with(
            [str(file.uuid)] if file_exists else [],
            values={"is_removed_from_disk": True},
        )
        os_mock.remove.assert_called_once_with(file.path)
