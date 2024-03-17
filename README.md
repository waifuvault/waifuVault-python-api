# waifuvault-python-api

This contains the official API bindings for uploading, deleting and obtaining files
with [waifuvault.moe](https://waifuvault.moe/). Contains a full up to date API for interacting with the service

## Installation

```sh
pip install waifuvault
```

## Usage

This API contains 4 interactions:

1. [Upload File](#upload-file)
2. [Get file Info](#get-file-info)
3. [Delete File](#delete-file)
4. [Get File](#get-file)

The package is namespaced to `waifuvault`, so to import it, simply:

```python
import waifuvault
```

### Upload File<a id="upload-file"></a>

To Upload a file, use the `upload_file` function. This function takes the following options as an object:

| Option         | Type               | Description                                                 | Required       | Extra info                       |
|----------------|--------------------|-------------------------------------------------------------|----------------|----------------------------------|
| `target`       | `string or buffer` | The target to upload can be a buffer, URL or filename       | true           | URL or file path                 |
| `target_name`  | `string`           | The filename of the target if it is a buffer                | true if buffer | Filename with extension          |
| `expires`      | `string`           | A string containing a number and a unit (1d = 1day)         | false          | Valid units are `m`, `h` and `d` |
| `hideFilename` | `boolean`          | If true, then the uploaded filename won't appear in the URL | false          | Defaults to `false`              |
| `password`     | `string`           | If set, then the uploaded file will be encrypted            | false          |                                  |

Using a URL:

```python
import waifuvault
upload_file = waifuvault.FileUpload("https://waifuvault.moe/assets/custom/images/08.png")
upload_res = waifuvault.upload_file(upload_file)
print(f"{upload_res.url}")
```

Using a file path:

```python
import waifuvault
upload_file = waifuvault.FileUpload("./files/aCoolFile.png")
upload_res = waifuvault.upload_file(upload_file)
print(f"{upload_res.url}")
```

Using a buffer:

```python
import waifuvault
import io

with open("./files/aCoolFile.png", "rb") as fh:
    buf = io.BytesIO(fh.read())

upload_file = waifuvault.FileUpload(buf, "aCoolFile.png")
upload_res = waifuvault.upload_file(upload_file)
print(f"{upload_res.url}")
```

### Get File Info<a id="get-file-info"></a>

If you have a token from your upload. Then you can get file info. This results in the following info:

* token
* url
* protected
* retentionPeriod

Use the `file_info` function. This function takes the following options as parameters:

| Option      | Type      | Description                                                        | Required | Extra info        |
|-------------|-----------|--------------------------------------------------------------------|----------|-------------------|
| `token`     | `string`  | The token of the upload                                            | true     |                   |
| `formatted` | `boolean` | If you want the `retentionPeriod` to be human-readable or an epoch | false    | defaults to false |

```python
import waifuvault
upload_info = waifuvault.file_info(your_token,False)
print(upload_info.retentionPeriod)
print(upload_info.url)
```

Human-readable timestamp:

```python
import waifuvault
upload_info = waifuvault.file_info(your_token,True)
print(upload_info.retentionPeriod)
print(upload_info.url)
```

### Delete File<a id="delete-file"></a>

To delete a file, you must supply your token to the `delete_file` function.

This function takes the following options as parameters:

| Option  | Type     | Description                              | Required | Extra info |
|---------|----------|------------------------------------------|----------|------------|
| `token` | `string` | The token of the file you wish to delete | true     |            |

> **NOTE:** `delete_file` will only ever either return `true` or throw an exception if the token is invalid

```python
import waifuvault
del_file = waifuvault.delete_file(your_token)
print(del_file)
```

### Get File<a id="get-file"></a>

This lib also supports obtaining a file from the API as a Buffer by supplying either the token or the unique identifier
of the file (epoch/filename).

Use the `get_file` function. This function takes the following options an object:

| Option     | Type     | Description                                | Required                           | Extra info                                      |
|------------|----------|--------------------------------------------|------------------------------------|-------------------------------------------------|
| `token`    | `string` | The token of the file you want to download | true only if `filename` is not set | if `filename` is set, then this can not be used |
| `url`      | `string` | The URL of the file                        | true only if `token` is not set    | if `token` is set, then this can not be used    |
| `password` | `string` | The password for the file                  | true if file is encrypted          | Passed as a parameter on the function call      |

> **Important!** The Unique identifier filename is the epoch/filename only if the file uploaded did not have a hidden
> filename, if it did, then it's just the epoch.
> For example: `1710111505084/08.png` is the Unique identifier for a standard upload of a file called `08.png`, if this
> was uploaded with hidden filename, then it would be `1710111505084.png`

Obtain an encrypted file

```python
import waifuvault
upload_enc_res = FileResponse(your_token,None,False,None)
file_enc_down = waifuvault.get_file(upload_enc_res,"your_password")
print(file_enc_down.__sizeof__())
```

Obtain a file from URL

```python
import waifuvault
upload_enc_res = FileResponse(None,your_url,False,None)
file_enc_down = waifuvault.get_file(upload_enc_res,"your_password")
print(file_enc_down.__sizeof__())
```

