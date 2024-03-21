import io
import time

import waifuvault


# URL Upload Tests
def test_upload_url():
    upload_file = waifuvault.FileUpload("https://twistedsisterscleaning.walker.moe/assets/sunflowers.png", expires="10m")
    upload_res = waifuvault.upload_file(upload_file)
    assert (upload_res.url.startswith('http')), "not a URL returned"
    assert ('-' in upload_res.token), "not a token returned"
    time.sleep(1)

    upload_info = waifuvault.file_info(upload_res.token,True)
    assert ('seconds' in upload_info.retentionPeriod), "not a human readable timestamp returned"
    time.sleep(1)

    update_info = waifuvault.file_update(upload_res.token,"dangerWaifu")
    assert update_info.protected, "encryption returned false"
    time.sleep(1)

    file_down = waifuvault.get_file(upload_res,"dangerWaifu")
    assert (isinstance(file_down, io.BytesIO)), "not a buffer returned"
    assert (file_down.__sizeof__() > 0), "zero size buffer returned"
    time.sleep(1)

    del_file = waifuvault.delete_file(upload_res.token)
    assert del_file, "delete returned false"
    time.sleep(1)


# File Upload Tests
def test_upload_file():
    upload_file = waifuvault.FileUpload("tests/testfile.png", expires="10m")
    upload_res = waifuvault.upload_file(upload_file)
    assert (upload_res.url.startswith('http')), "not a URL returned"
    assert ('-' in upload_res.token), "not a token returned"
    time.sleep(1)

    upload_info = waifuvault.file_info(upload_res.token,True)
    assert ('seconds' in upload_info.retentionPeriod), "not a human readable timestamp returned"
    time.sleep(1)

    update_info = waifuvault.file_update(upload_res.token,"dangerWaifu")
    assert update_info.protected, "encryption returned false"
    time.sleep(1)

    file_down = waifuvault.get_file(upload_res, "dangerWaifu")
    assert (isinstance(file_down, io.BytesIO)), "not a buffer returned"
    assert (file_down.__sizeof__() > 0), "zero size buffer"
    time.sleep(1)

    del_file = waifuvault.delete_file(upload_res.token)
    assert del_file, "delete file returned false"
    time.sleep(1)


# Buffer Upload Tests
def test_upload_buffer():
    with open("tests/testfile.png", "rb") as fh:
        buf = io.BytesIO(fh.read())
    upload_file = waifuvault.FileUpload(buf,"testfile_buf.png",expires="10m")
    upload_res = waifuvault.upload_file(upload_file)
    assert (upload_res.url.startswith('http')), "not a URL returned"
    assert ('-' in upload_res.token), "not a token returned"
    time.sleep(1)

    upload_info = waifuvault.file_info(upload_res.token,True)
    assert ('seconds' in upload_info.retentionPeriod), "not a human readable timestamp returned"
    time.sleep(1)

    update_info = waifuvault.file_update(upload_res.token,"dangerWaifu")
    assert update_info.protected, "encryption returned false"
    time.sleep(1)

    file_down = waifuvault.get_file(upload_res, "dangerWaifu")
    assert (isinstance(file_down, io.BytesIO)), "not a buffer returned"
    assert (file_down.__sizeof__() > 0), "zero size buffer"
    time.sleep(1)

    del_file = waifuvault.delete_file(upload_res.token)
    assert del_file
    time.sleep(1)
