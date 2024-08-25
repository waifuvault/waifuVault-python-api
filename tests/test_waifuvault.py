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
                                                       '{"token": "test-bucket", "files":[]}'))

    # When
    bucket = waifuvault.create_bucket()

    # Then
    mock_create.assert_called_once_with('https://waifuvault.moe/rest/bucket/create')
    assert (bucket.token == "test-bucket"), "Create Bucket did not return bucket"


def test_get_bucket(mocker):
    # Given
    mock_get = mocker.patch('requests.post',
                               return_value=response_mock(True,
                                                          '{"token": "test-bucket", "files":[{"token":"some-file-token", "url":"some-file-url", "bucket":"test-bucket", "retentionPeriod":10, "options":{"hideFilename":false, "oneTimeDownload": false, "protected":false}}]}'))

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


def test_get_restrictions(mocker):
    # Given
    mock_get = mocker.patch('requests.get', return_value=restrictions_response)

    # When
    restrictions = waifuvault.get_restrictions()

    # Then
    mock_get.assert_called_once_with('https://waifuvault.moe/rest/resources/restrictions')
    assert (isinstance(restrictions, waifuvault.RestrictionResponse)), "Get Restrictions did not return a retriction response instance"
    assert (len(restrictions.Restrictions) == 2), "Get Restrictions wrong number of restrictions"


def test_url_args():
    # Given
    file_down = waifuvault.FileUpload("https://waifuvault.moe/test", expires="1d", password="testpassword", hidefilename=True, oneTimeDownload=True)

    # When
    args = file_down.build_parameters()

    # Then
    assert (args.get("expires") == "1d"), "expires not in arguments"
    assert (args.get("hide_filename") == "true"), "hide_filename not in arguments"
    assert (args.get("one_time_download") == "true"), "one_time_download not in arguments"
