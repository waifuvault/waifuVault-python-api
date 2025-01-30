# waifuvault-python-api

![tests](https://github.com/waifuvault/waifuVault-python-api/actions/workflows/deploy.yml/badge.svg)
[![GitHub issues](https://img.shields.io/github/issues/waifuvault/waifuVault-python-api.png)](https://github.com/waifuvault/waifuVault-python-api/issues)
[![last-commit](https://img.shields.io/github/last-commit/waifuvault/waifuVault-python-api)](https://github.com/waifuvault/waifuVault-python-api/commits/master)

This contains the official API bindings for uploading, deleting and obtaining files
with [waifuvault.moe](https://waifuvault.moe/). Contains a full up to date API for interacting with the service

## Installation

```sh
pip install waifuvault
```

## Usage

This API contains 19 interactions:

1. [Upload File](#upload-file)
2. [Get file Info](#get-file-info)
3. [Update file Info](#update-file-info)
4. [Delete File](#delete-file)
5. [Get File](#get-file)
6. [Create Bucket](#create-bucket)
7. [Delete Bucket](#delete-bucket)
8. [Get Bucket](#get-bucket)
9. [Create Album](#create-album)
10. [Delete Album](#delete-album)
11. [Get Album](#get-album)
12. [Associate File](#associate-file)
13. [Disassociate File](#disassociate-file)
14. [Share Album](#share-album)
15. [Revoke Album](#revoke-album)
16. [Download Album](#download-album)
17. [Get Restrictions](#get-restrictions)
18. [Clear Restrictions](#clear-restrictions)
19. [Get File Stats](#get-file-stats)

The package is namespaced to `waifuvault`, so to import it, simply:

```python
import waifuvault
```

### Upload File<a id="upload-file"></a>

To Upload a file, use the `upload_file` function. This function takes the following options as an object:

| Option            | Type               | Description                                                     | Required       | Extra info                       |
|-------------------|--------------------|-----------------------------------------------------------------|----------------|----------------------------------|
| `target`          | `string or buffer` | The target to upload can be a buffer, URL or filename           | true           | URL or file path                 |
| `target_name`     | `string`           | The filename of the target if it is a buffer                    | true if buffer | Filename with extension          |
| `bucket_token`    | `string`           | Token for a bucket to upload the file into                      | false          | Create bucket gives token        |
| `expires`         | `string`           | A string containing a number and a unit (1d = 1day)             | false          | Valid units are `m`, `h` and `d` |
| `hideFilename`    | `boolean`          | If true, then the uploaded filename won't appear in the URL     | false          | Defaults to `false`              |
| `password`        | `string`           | If set, then the uploaded file will be encrypted                | false          |                                  |
| `oneTimeDownload` | `boolean`          | if supplied, the file will be deleted as soon as it is accessed | false          |                                  |

> **NOTE:** Server restrictions are checked by the SDK client side *before* upload, and will throw a ValueError exception if they are violated

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

### Update File Info<a id="update-file-info"></a>

If you have a token from your upload, then you can update the information for the file.  You can change the password or remove it, 
you can set custom expiry time or remove it, and finally you can choose whether the filename is hidden.

Use the `file_update` function. This function takes the following options as parameters:

| Option              | Type     | Description                                             | Required | Extra info                                  |
|---------------------|----------|---------------------------------------------------------|----------|---------------------------------------------|
| `token`             | `string` | The token of the upload                                 | true     |                                             |
| `password`          | `string` | The current password of the file                        | false    | Set to empty string to remove password      |
| `previous_password` | `string` | The previous password of the file, if changing password | false    |                                             |
| `custom_expiry`     | `string` | Custom expiry in the same form as upload command        | false    | Set to empty string to remove custom expiry |
| `hide_filename`     | `bool`   | Sets whether the filename is visible in the URL or not  | false    |                                             |

```python
import waifuvault
update_info = waifuvault.file_update(your_token,custom_expiry="2d")
print(upload_info.retentionPeriod)
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

### Create Bucket<a id="create-bucket"></a>

Buckets are virtual collections that are linked to your IP and a token. When you create a bucket, you will receive a bucket token that you can use in Get Bucket to get all the files in that bucket

> **NOTE:** Only one bucket is allowed per client IP address, if you call it more than once, it will return the same bucket token

To create a bucket, use the `create_bucket` function. This function does not take any arguments.

```python
import waifuvault
bucket = waifuvault.create_bucket()
print(bucket.token)
```

### Delete Bucket<a id="delete-bucket"></a>

Deleting a bucket will delete the bucket and all the files it contains.

> **IMPORTANT:**  All contained files will be **DELETED** along with the Bucket!

To delete a bucket, you must call the `delete_bucket` function with the following options as parameters:

| Option      | Type      | Description                       | Required | Extra info        |
|-------------|-----------|-----------------------------------|----------|-------------------|
| `token`     | `string`  | The token of the bucket to delete | true     |                   |

> **NOTE:** `deleteBucket` will only ever either return `true` or throw an exception if the token is invalid

```python
import waifuvault
resp = waifuvault.delete_bucket("some-bucket-token")
print(resp)
```

### Get Bucket<a id="get-bucket"></a>

To get the list of files contained in a bucket, you use the `get_bucket` functions and supply the token.
This function takes the following options as parameters:

| Option      | Type      | Description             | Required | Extra info        |
|-------------|-----------|-------------------------|----------|-------------------|
| `token`     | `string`  | The token of the bucket | true     |                   |

This will respond with the bucket and all the files the bucket contains.

```python
import waifuvault
bucket = waifuvault.get_bucket("some-bucket-token")
print(bucket.token)
print(bucket.files)  # Array of file objects
```

### Create Album<a id="create-album"></a>
Albums are shareable collections of files that exist within a bucket.

To create an album, you use the `create_album` function and supply a bucket token and name.

The function takes the following parameters:

| Option         | Type      | Description                         | Required | Extra info        |
|----------------|-----------|-------------------------------------|----------|-------------------|
| `bucket_token` | `string`  | The token of the bucket             | true     |                   |
| `name`         | `string`  | The name of the album to be created | true     |                   |

This will respond with an album object containing the name and token of the album.

```python
import waifuvault
album = waifuvault.create_album("some-bucket-token", "album-name")
print(album.token)
print(album.name)
print(album.files)  # Array of file objects
```

### Delete Album<a id="delete-album"></a>
To delete an album, you use the `delete_album` function and supply the album token and a boolean indication of whether
or not the files contained in the album should be deleted or not.  If you chose false, the files will be returned to the
bucket.

The function takes the following parameters:

| Option         | Type     | Description                         | Required | Extra info        |
|----------------|----------|-------------------------------------|----------|-------------------|
| `album_token`  | `string` | The private token of the album      | true     |                   |
| `delete_files` | `bool`   | Whether the files should be deleted | true     |                   |

> **NOTE:** If `delete_files` is set to True, the files will be permanently deleted 

This will respond with a boolean indicating success.

```python
import waifuvault
resp = waifuvault.delete_album("some-album-token", False)
print(resp)
```

### Get Album<a id="get-album"></a>
To get the contents of an album, you use the `get_album` function and supply the album token.  The token can be either the private token
or the public token.

The function takes the following parameters:

| Option   | Type     | Description            | Required | Extra info                     |
|----------|----------|------------------------|----------|--------------------------------|
| `token`  | `string` | The token of the album | true     | Can be private or public token |

This will respond with the album object containing the album information and files contained within the album.

```python
import waifuvault
album = waifuvault.get_album("some-album-token")
print(album.token)
print(album.bucket_token)
print(album.public_token)
print(album.name)
print(album.files)  # Array of file objects
```

### Associate File<a id="associate-file"></a>
To add files to an album, you use the `associate_file` function and supply the private album token and 
a list of file tokens.

The function takes the following parameters:

| Option  | Type           | Description                         | Required | Extra info |
|---------|----------------|-------------------------------------|----------|------------|
| `token` | `string`       | The private token of the album      | true     |            |
| `files` | `list[string]` | List of file tokens to add to album | true     |            |

This will respond with the new album object containing the added files.

```python
import waifuvault
album = waifuvault.associate_file("some-album-token", ["file-token-1","file-token-2"])
print(album.token)
print(album.name)
print(album.files)  # Array of file objects
```

### Disassociate File<a id="disassociate-file"></a>
To remove files from an album, you use the `disassociate_file` function and supply the private album token and
a list of file tokens.

The function takes the following parameters:

| Option  | Type           | Description                         | Required | Extra info |
|---------|----------------|-------------------------------------|----------|------------|
| `token` | `string`       | The private token of the album      | true     |            |
| `files` | `list[string]` | List of file tokens to add to album | true     |            |

This will respond with the new album object with the files removed.

```python
import waifuvault
album = waifuvault.disassociate_file("some-album-token", ["file-token-1","file-token-2"])
print(album.token)
print(album.name)
print(album.files)  # Array of file objects
```

### Share Album<a id="share-album"></a>
To share an album, so it contents can be accessed from a public URL, you use the `share_album` function and
supply the private token.

The function takes the following parameters:

| Option  | Type           | Description                         | Required | Extra info |
|---------|----------------|-------------------------------------|----------|------------|
| `token` | `string`       | The private token of the album      | true     |            |

This will respond with the public URL with which the album can be found.

```python
import waifuvault
url = waifuvault.share_album("some-album-token")
print(url)
```

> **NOTE:** The public album token can now be found in the `get_album` results

### Revoke Album<a id="revoke-album"></a>
To revoke the sharing of an album, so it will no longer be accessible publicly, you use the `revoke_album` function
and supply the private token.

The function takes the following parameters:

| Option  | Type           | Description                         | Required | Extra info |
|---------|----------------|-------------------------------------|----------|------------|
| `token` | `string`       | The private token of the album      | true     |            |

This will respond with a boolean True if the album was revoked.

```python
import waifuvault
resp = waifuvault.revoke_album("some-album-token")
print(resp)
```

> **NOTE:** Once revoked, the URL for sharing is destroyed.  If the album is later shared again, the URL issued will be different.

### Download Album<a id="download-album"></a>
To download the contents of an album as a zip file, you use the `download_album` function and
supply a private or public token for the album.

The zip file will be returned as a buffer.

The function takes the following parameters:

| Option  | Type           | Description                              | Required | Extra info |
|---------|----------------|------------------------------------------|----------|------------|
| `token` | `string`       | The private or public token of the album | true     |            |


```python
import waifuvault
album_zip = waifuvault.download_album("some-album-token")
print(album_zip.__sizeof__())
```

### Get Restrictions<a id="get-restrictions"></a>

To get the list of restrictions applied to the server, you use the `get_restrictions` functions.

This will respond with an array of name, value entries describing the restrictions applied to the server.

> **NOTE:** Restrictions are cached for 10 minutes

```python
import waifuvault
restrictions = waifuvault.get_restrictions()

print(restrictions.Restrictions)  # Array of restriction objects
```

### Clear Restrictions<a id="clear-restrictions"></a>

To clear the cached restrictions in the SDK, you use the `clear_restrictions` function.

This will remove the cached restrictions and a fresh copy will be downloaded at the next upload.

```python
import waifuvault
waifuvault.clear_restrictions()
```

### Get File Stats<a id="get-file-stats"></a>

To get general file stats for the server, you use the `get_file_stats` function.

This takes no parameters and returns the number of files and the size of files on the server.

```python
import waifuvault
stats = waifuvault.get_file_stats()

print(stats.record_count)
print(stats.record_size)
```