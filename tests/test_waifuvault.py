import io
import re

import pytest
import waifuvault


# Response Mock Object
class response_mock:
    def __init__(self, ok, text, content=None, code=None):
        self.ok = ok
        self.code = code
        self.text = text
        self.content = content


# Mocked responses
ok_response_numeric_long = response_mock(True,
                                    '{"url":"https://waifuvault.moe/f/something", "token":"test-token", "bucket":"test-bucket", "retentionPeriod":28860366525, "options":{"protected": false, "oneTimeDownload": false, "hideFilename": false}}')
ok_response_numeric = response_mock(True,
                                    '{"url":"https://waifuvault.moe/f/something", "token":"test-token", "bucket":"test-bucket", "retentionPeriod":100, "options":{"protected": false, "oneTimeDownload": false, "hideFilename": false}}')
ok_response_numeric_protected = response_mock(True,
                                    '{"url":"https://waifuvault.moe/f/something", "token":"test-token", "bucket":"test-bucket", "retentionPeriod":100, "options":{"protected": true, "oneTimeDownload": false, "hideFilename": false}}')
ok_response_human = response_mock(True,
                                  '{"url":"https://waifuvault.moe/f/something", "token":"test-token", "bucket":"test-bucket", "retentionPeriod":"10 minutes", "options":{"protected": false, "oneTimeDownload": false, "hideFilename": false}}')
bad_request = response_mock(False,
                            '{"name": "BAD_REQUEST", "message": "Error Test", "status": 400}',code=400)
restrictions_response = response_mock(True,
                                      '[{"type": "MAX_FILE_SIZE","value": 536870912},{"type": "BANNED_MIME_TYPE","value": "application/x-msdownload,application/x-executable"}]')
restrictions_small_response = response_mock(True,
                                      '[{"type": "MAX_FILE_SIZE","value": 100},{"type": "BANNED_MIME_TYPE","value": "application/x-msdownload,application/x-executable"}]')
size_response = response_mock(True,
                              '{"recordCount": 100, "recordSize":100000}')

album_response = response_mock(True,
                               '{"token": "test-album", "bucketToken": "test-bucket", "publicToken": null, \
                               "name": "test-name", "files": [{ \
                                "token": "test-file", "url": "test-file-url", "views": 0, "bucket": "test-bucket",\
                                "album": { \
                                    "token": "test-album", \
                                    "publicToken": null, \
                                    "name": "test-name", \
                                    "bucket": "test-bucket", \
                                    "dateCreated": 0 \
                                }, \
                                "retentionPeriod": 0, \
                                "options": { \
                                    "hideFilename": false, \
                                    "oneTimeDownload": false, \
                                    "protected": false \
                                    } \
                                } \
                                ]}')

# URL Upload Tests
def test_upload_url(mocker):
    # Given
    mock_put = mocker.patch('requests.put', return_value = ok_response_numeric)
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)
    upload_file = waifuvault.FileUpload("https://walker.moe/assets/sunflowers.png", expires="10m")

    # When
    upload_res = waifuvault.upload_file(upload_file)
    mock_put.assert_called_once_with(
        'https://waifuvault.moe/rest',
        params={'expires': '10m'},
        data={'url': 'https://walker.moe/assets/sunflowers.png'},
        headers=None)

    # Then
    assert (upload_res.url == "https://waifuvault.moe/f/something"), "URL does not match"
    assert (upload_res.token == "test-token"), "Token does not match"
    assert (upload_res.options.protected is False), "Protected does not match"
    assert (upload_res.retentionPeriod == 100), "Retention does not match"


def test_upload_bucket(mocker):
    # Given
    mock_put = mocker.patch('requests.put', return_value = ok_response_numeric)
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)
    upload_file = waifuvault.FileUpload("https://walker.moe/assets/sunflowers.png", expires="10m", bucket_token="test-bucket")

    # When
    upload_res = waifuvault.upload_file(upload_file)
    mock_put.assert_called_once_with(
        'https://waifuvault.moe/rest/test-bucket',
        params={'expires': '10m'},
        data={'url': 'https://walker.moe/assets/sunflowers.png'},
        headers=None)

    # Then
    assert (upload_res.url == "https://waifuvault.moe/f/something"), "URL does not match"
    assert (upload_res.token == "test-token"), "Token does not match"
    assert (upload_res.bucket == "test-bucket"), "Bucket does not match"
    assert (upload_res.options.protected is False), "Protected does not match"
    assert (upload_res.retentionPeriod == 100), "Retention does not match"


def test_upload_url_error(mocker):
    # Given
    mock_put = mocker.patch('requests.put', return_value = bad_request)
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)

    # When
    upload_file = waifuvault.FileUpload("https://walker.moe/assets/sunflowers.png", expires="10m")

    # Then
    with pytest.raises(Exception, match=re.escape('Error 400 (BAD_REQUEST): Error Test')):
        upload_res = waifuvault.upload_file(upload_file)


def test_upload_file(mocker):
    # Given
    mock_put = mocker.patch('requests.put', return_value = ok_response_numeric)
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)
    upload_file = waifuvault.FileUpload("tests/testfile.png", expires="10m")

    # When
    upload_res = waifuvault.upload_file(upload_file)

    # Then
    mock_put.assert_called_once()
    assert (upload_res.url == "https://waifuvault.moe/f/something"), "URL does not match"
    assert (upload_res.token == "test-token"), "Token does not match"
    assert (upload_res.options.protected is False), "Protected does not match"
    assert (upload_res.retentionPeriod == 100), "Retention does not match"


def test_upload_file_error(mocker):
    # Given
    mock_put = mocker.patch('requests.put', return_value = bad_request)
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)

    # When
    upload_file = waifuvault.FileUpload("tests/testfile.png", expires="10m")

    # Then
    with pytest.raises(Exception, match=re.escape('Error 400 (BAD_REQUEST): Error Test')):
        upload_res = waifuvault.upload_file(upload_file)


def test_upload_buffer(mocker):
    # Given
    mock_put = mocker.patch('requests.put', return_value = ok_response_numeric)
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)
    with open("tests/testfile.png", "rb") as fh:
        buf = io.BytesIO(fh.read())
    upload_file = waifuvault.FileUpload(buf,"testfile_buf.png",expires="10m")

    # When
    upload_res = waifuvault.upload_file(upload_file)

    # Then
    mock_put.assert_called_once()
    assert (upload_res.url == "https://waifuvault.moe/f/something"), "URL does not match"
    assert (upload_res.token == "test-token"), "Token does not match"
    assert (upload_res.options.protected is False), "Protected does not match"
    assert (upload_res.retentionPeriod == 100), "Retention does not match"


def test_upload_buffer_error(mocker):
    # Given
    mock_put = mocker.patch('requests.put', return_value = bad_request)
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)
    with open("tests/testfile.png", "rb") as fh:
        buf = io.BytesIO(fh.read())

    # When
    upload_file = waifuvault.FileUpload(buf, "testfile_buf.png", expires="10m")

    # Then
    with pytest.raises(Exception, match=re.escape('Error 400 (BAD_REQUEST): Error Test')):
        upload_res = waifuvault.upload_file(upload_file)


def test_upload_restriction_error(mocker):
    # Given
    waifuvault.clear_restrictions()
    mock_put = mocker.patch('requests.put', return_value=bad_request)
    mock_get = mocker.patch('requests.get', return_value=restrictions_small_response)

    # When
    upload_file = waifuvault.FileUpload("tests/testfile.png", expires="10m")

    # Then
    with pytest.raises(Exception, match=re.escape('File size 97674 is larger than max allowed 100')):
        upload_res = waifuvault.upload_file(upload_file)


def test_file_info(mocker):
    # Given
    mock_get = mocker.patch('requests.get', return_value = ok_response_human)

    # When
    upload_info = waifuvault.file_info("test-token",True)

    # Then
    mock_get.assert_called_once_with(
        'https://waifuvault.moe/rest/test-token',
        params={'formatted': 'true'})
    assert (upload_info.url == "https://waifuvault.moe/f/something"), "URL does not match"
    assert (upload_info.token == "test-token"), "Token does not match"
    assert (upload_info.options.protected is False), "Protected does not match"
    assert (upload_info.retentionPeriod == "10 minutes"), "Retention does not match"


def test_file_info_long(mocker):
    # Given
    mock_get = mocker.patch('requests.get', return_value = ok_response_numeric_long)

    # When
    upload_info = waifuvault.file_info("test-token",False)

    # Then
    mock_get.assert_called_once_with(
        'https://waifuvault.moe/rest/test-token',
        params={'formatted': 'false'})
    assert (upload_info.url == "https://waifuvault.moe/f/something"), "URL does not match"
    assert (upload_info.token == "test-token"), "Token does not match"
    assert (upload_info.options.protected is False), "Protected does not match"
    assert (upload_info.retentionPeriod == 28860366525), "Retention does not match"


def test_file_info_error(mocker):
    # When
    mock_get = mocker.patch('requests.get', return_value = bad_request)

    # Then
    with pytest.raises(Exception, match=re.escape('Error 400 (BAD_REQUEST): Error Test')):
        upload_info = waifuvault.file_info("bad-token",True)


def test_update_info(mocker):
    # Given
    mock_patch = mocker.patch('requests.patch', return_value = ok_response_numeric_protected)

    # When
    update_info = waifuvault.file_update("test-token","dangerWaifu")

    # Then
    mock_patch.assert_called_once_with(
        'https://waifuvault.moe/rest/test-token',
        data={'password': 'dangerWaifu','hideFilename': 'false'})
    assert (update_info.url == "https://waifuvault.moe/f/something"), "URL does not match"
    assert (update_info.token == "test-token"), "Token does not match"
    assert (update_info.options.protected is True), "Protected does not match"
    assert (update_info.retentionPeriod == 100), "Retention does not match"


def test_update_info_error(mocker):
    # When
    mock_patch = mocker.patch('requests.patch', return_value = bad_request)

    # Then
    with pytest.raises(Exception, match=re.escape('Error 400 (BAD_REQUEST): Error Test')):
        update_info = waifuvault.file_update("test-token","dangerWaifu")


def test_delete(mocker):
    # Given
    mock_del = mocker.patch('requests.delete',
        return_value=response_mock(True,
            'true'))

    # When
    del_file = waifuvault.delete_file("test-token")

    # Then
    mock_del.assert_called_once_with('https://waifuvault.moe/rest/test-token')
    assert (del_file is True), "Delete did not return true"


def test_delete_error(mocker):
    # When
    mock_del = mocker.patch('requests.delete', return_value = bad_request)

    # Then
    with pytest.raises(Exception, match=re.escape('Error 400 (BAD_REQUEST): Error Test')):
        del_file = waifuvault.delete_file("test-token")


def test_download(mocker):
    # Given
    mock_get = mocker.patch('requests.get',return_value = response_mock(True,'', bytes("someval","utf8")))

    # When
    file_down = waifuvault.get_file(waifuvault.FileResponse(url="https://waifuvault.moe/f/something"), "dangerWaifu")

    # Then
    mock_get.assert_called_once_with('https://waifuvault.moe/f/something', headers={'x-password': 'dangerWaifu'})
    assert (isinstance(file_down, io.BytesIO)), "Download did not return a buffer"


def test_download_error(mocker):
    # When
    mock_get = mocker.patch('requests.get', return_value=bad_request)

    # Then
    with pytest.raises(Exception, match=re.escape('Error 400 (BAD_REQUEST): Error Test')):
        file_down = waifuvault.get_file(waifuvault.FileResponse(url="https://waifuvault.moe/f/something"), "dangerWaifu")


def test_create_bucket(mocker):
    # Given
    mock_create = mocker.patch('requests.get',
                            return_value=response_mock(True,
                                                       '{"token": "test-bucket", "files":[], "albums":[]}'))

    # When
    bucket = waifuvault.create_bucket()

    # Then
    mock_create.assert_called_once_with('https://waifuvault.moe/rest/bucket/create')
    assert (bucket.token == "test-bucket"), "Create Bucket did not return bucket"


def test_get_bucket(mocker):
    # Given
    mock_get = mocker.patch('requests.post',
                               return_value=response_mock(True,
                                                          '{"token": "test-bucket", "files":[{"token":"some-file-token", "url":"some-file-url", "bucket":"test-bucket", "retentionPeriod":10, "options":{"hideFilename":false, "oneTimeDownload": false, "protected":false}}], "albums":[]}'))

    # When
    bucket = waifuvault.get_bucket("test-bucket")

    # Then
    mock_get.assert_called_once_with('https://waifuvault.moe/rest/bucket/get', json={'bucket_token': 'test-bucket'})
    assert (bucket.token == "test-bucket"), "Get Bucket did not return bucket"
    assert (isinstance(bucket.files[0], waifuvault.FileResponse)), "Get Bucket did not return a file response instance"
    assert (bucket.files[0].bucket == "test-bucket"), "Get Bucket file response not in bucket"


def test_delete_bucket(mocker):
    # Given
    mock_del = mocker.patch('requests.delete',
                            return_value=response_mock(True,
                                                       'true'))

    # When
    del_bucket = waifuvault.delete_bucket("test-bucket")

    # Then
    mock_del.assert_called_once_with('https://waifuvault.moe/rest/bucket/test-bucket')
    assert (del_bucket is True), "Delete Bucket did not return true"


def test_create_album(mocker):
    # Given
    mock_get = mocker.patch('requests.post',
                            return_value=response_mock(True,
                                                       '{"token": "test-album", "bucketToken":"test-bucket", "publicToken":null, "name":"test-name", "files":[]}'))

    # When
    album = waifuvault.create_album("test-bucket", "test-name")

    # Then
    mock_get.assert_called_once_with('https://waifuvault.moe/rest/album/test-bucket', json={'name': 'test-name'})
    assert (isinstance(album, waifuvault.AlbumResponse)), "Create Album did not return album response instance"
    assert (album.token == "test-album"), "Create Album did not return album token"
    assert (album.bucket_token == "test-bucket"), "Create Album did not return bucket token"
    assert (album.name == "test-name"), "Create Album did not return album name"


def test_delete_album(mocker):
    # Given
    mock_del = mocker.patch('requests.delete',
                            return_value=response_mock(True,
                                                       '{"success":true, "description":"yes"}'))

    # When
    del_album = waifuvault.delete_album("test-album", True)

    # Then
    mock_del.assert_called_once_with('https://waifuvault.moe/rest/album/test-album?deleteFiles=true')
    assert (del_album is True), "Delete Album did not return true"


def test_get_album(mocker):
    # Given
    mock_get = mocker.patch('requests.get',
                            return_value=response_mock(True,
                                                       '{"token":"test-token", "bucketToken": "test-bucket", "publicToken": null, "name":"test-name", "files":[]}'))

    # When
    album = waifuvault.get_album("test-album")

    # Then
    mock_get.assert_called_once_with('https://waifuvault.moe/rest/album/test-album')
    assert (isinstance(album, waifuvault.AlbumResponse)), "Get Album did not return an album response instance"
    assert (album.token == 'test-token'), "Get Album returned wrong album token"
    assert (album.bucket_token == 'test-bucket'), "Get Album returned wrong bucket token"
    assert (album.public_token is None), "Get Album returned wrong public token"
    assert (album.name == 'test-name'), "Get Album returned wrong name"


def test_share_album(mocker):
    # Given
    mock_share = mocker.patch('requests.get',
                            return_value=response_mock(True,
                                                       '{"success":true, "description":"test-url"}'))

    # When
    share_album = waifuvault.share_album("test-album")

    # Then
    mock_share.assert_called_once_with('https://waifuvault.moe/rest/album/share/test-album')
    assert (share_album == 'test-url'), "Share Album did not return correct URL"


def test_revoke_album(mocker):
    # Given
    mock_revoke = mocker.patch('requests.get',
                            return_value=response_mock(True,
                                                       '{"success":true, "description":"test-url"}'))

    # When
    revoke_album = waifuvault.revoke_album("test-album")

    # Then
    mock_revoke.assert_called_once_with('https://waifuvault.moe/rest/album/revoke/test-album')
    assert (revoke_album is True), "Revoke Album did not return true"


def test_associate_file(mocker):
    # Given
    mock_associate = mocker.patch('requests.post', return_value=album_response)

    # When
    album = waifuvault.associate_file("test-album", ["file1","file2"])

    # Then
    mock_associate.assert_called_once_with('https://waifuvault.moe/rest/album/test-album/associate', json={'fileTokens': ['file1','file2']})
    assert (isinstance(album, waifuvault.AlbumResponse)), "Associate File did not return album response instance"
    assert (album.token == "test-album"), "Associate File did not return album token"
    assert (album.bucket_token == "test-bucket"), "Associate File did not return bucket token"
    assert (album.name == "test-name"), "Associate File did not return album name"
    assert (album.files[0].token == "test-file"), "Associate File did not return file token"


def test_disassociate_file(mocker):
    # Given
    mock_disassociate = mocker.patch('requests.post', return_value=album_response)

    # When
    album = waifuvault.disassociate_file("test-album", ["file1","file2"])

    # Then
    mock_disassociate.assert_called_once_with('https://waifuvault.moe/rest/album/test-album/disassociate', json={'fileTokens': ['file1','file2']})
    assert (isinstance(album, waifuvault.AlbumResponse)), "Disassociate File did not return album response instance"
    assert (album.token == "test-album"), "Disassociate File did not return album token"
    assert (album.bucket_token == "test-bucket"), "Disassociate File did not return bucket token"
    assert (album.name == "test-name"), "Disassociate File did not return album name"


def test_download_album(mocker):
    # Given
    mock_download_album = mocker.patch('requests.post',return_value = response_mock(True,'', bytes("someval","utf8")))

    # When
    album_down = waifuvault.download_album("test-album")

    # Then
    mock_download_album.assert_called_once_with('https://waifuvault.moe/rest/album/download/test-album', json=[])
    assert (isinstance(album_down, io.BytesIO)), "Download album did not return a buffer"


def test_get_restrictions(mocker):
    # Given
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)

    # When
    restrictions = waifuvault.get_restrictions()

    # Then
    mock_get.assert_called_once_with('https://waifuvault.moe/rest/resources/restrictions')
    assert (isinstance(restrictions, waifuvault.RestrictionResponse)), "Get Restrictions did not return a retriction response instance"
    assert (len(restrictions.Restrictions) == 2), "Get Restrictions wrong number of restrictions"


def test_get_file_stats(mocker):
    # Given
    mock_get = mocker.patch('requests.get', return_value=size_response)

    # When
    file_stats = waifuvault.get_file_stats()

    # Then
    mock_get.assert_called_once_with('https://waifuvault.moe/rest/resources/stats/files')
    assert (isinstance(file_stats, waifuvault.FilesInfo)), "Get File Stats did not return a FilesInfo response instance"
    assert (file_stats.record_count == 100), "Get File Stats wrong number of records"
    assert (file_stats.record_size== 100000), "Get File Stats wrong size of records"


def test_url_args():
    # Given
    file_down = waifuvault.FileUpload("https://waifuvault.moe/test", expires="1d", password="testpassword", hidefilename=True, oneTimeDownload=True)

    # When
    args = file_down.build_parameters()

    # Then
    assert (args.get("expires") == "1d"), "expires not in arguments"
    assert (args.get("hide_filename") == "true"), "hide_filename not in arguments"
    assert (args.get("one_time_download") == "true"), "one_time_download not in arguments"
