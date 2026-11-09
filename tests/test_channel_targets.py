import unittest
from unittest.mock import Mock

from services.channel_service import get_channel_info, get_channel_video_ids
from utils.url import parse_channel_target


class ChannelTargetTests(unittest.TestCase):
    def test_parses_ids_handles_and_urls(self):
        self.assertEqual(parse_channel_target("UCabc_123"), ("id", "UCabc_123"))
        self.assertEqual(parse_channel_target("@Canal"), ("forHandle", "Canal"))
        self.assertEqual(
            parse_channel_target("https://www.youtube.com/@Vis%C3%A3oBostil/featured"),
            ("forHandle", "VisãoBostil"),
        )
        self.assertEqual(
            parse_channel_target("https://youtube.com/channel/UCabc-123"),
            ("id", "UCabc-123"),
        )
        self.assertEqual(
            parse_channel_target("https://youtube.com/user/canalantigo"),
            ("forUsername", "canalantigo"),
        )
        self.assertEqual(
            parse_channel_target("https://youtube.com/c/CanalPersonalizado"),
            ("forHandle", "CanalPersonalizado"),
        )
        self.assertEqual(
            parse_channel_target("https://youtube.com/lulaoficial"),
            ("forHandle", "lulaoficial"),
        )

    def test_handle_lookup_returns_canonical_channel_id(self):
        request = Mock()
        request.execute.return_value = {
            "items": [
                {
                    "id": "UCcanonical",
                    "snippet": {"title": "Canal"},
                    "statistics": {},
                    "contentDetails": {"relatedPlaylists": {"uploads": "UUcanonical"}},
                }
            ]
        }
        channels = Mock()
        channels.list.return_value = request
        youtube = Mock()
        youtube.channels.return_value = channels

        info = get_channel_info(youtube, "https://youtube.com/@Canal")

        channels.list.assert_called_once_with(
            part="snippet,statistics,contentDetails", forHandle="Canal"
        )
        self.assertEqual(info["channel_id"], "UCcanonical")

    def test_quota_rotation_retries_same_playlist_page(self):
        first_page_request = Mock()
        first_page_request.execute.return_value = {
            "items": [{"contentDetails": {"videoId": "video-new"}}],
            "nextPageToken": "PAGE_2",
        }
        quota_request = Mock()
        quota_request.execute.side_effect = Exception("quotaExceeded")
        resumed_request = Mock()
        resumed_request.execute.return_value = {
            "items": [{"contentDetails": {"videoId": "video-old"}}],
        }

        first_playlist = Mock()
        first_playlist.list.side_effect = [first_page_request, quota_request]
        first_client = Mock()
        first_client.playlistItems.return_value = first_playlist

        second_playlist = Mock()
        second_playlist.list.return_value = resumed_request
        second_client = Mock()
        second_client.playlistItems.return_value = second_playlist

        client_pool = Mock()
        client_pool.get_client.side_effect = [first_client, first_client, second_client]
        client_pool.rotate_key.return_value = True

        video_ids = get_channel_video_ids(
            first_client,
            "UCchannel",
            "UUuploads",
            client_pool=client_pool,
        )

        self.assertEqual(video_ids, ["video-new", "video-old"])
        client_pool.rotate_key.assert_called_once_with()
        second_playlist.list.assert_called_once_with(
            part="contentDetails",
            playlistId="UUuploads",
            maxResults=50,
            pageToken="PAGE_2",
        )


if __name__ == "__main__":
    unittest.main()
