# GeoIntel Bug Report

> All issues listed below have been fixed.

## 🔴 Critical / High

### 1. ✅ MIME type always defaults to JPEG — `image_processor.py`, `geointel.py`

`process_image()` returned only the base64 string with no MIME type information. `geointel.py` called `generate_content()` without a `mime_type` argument, so all images (PNG, WebP, GIF) were sent to Gemini as `image/jpeg`. This could cause the API to misinterpret image data.

**Fix:** `process_image()`, `download_image()`, and `load_local_image()` now return `Tuple[str, str]` / `Tuple[bytes, str]` with the detected MIME type. `geointel.py` passes the MIME type through to `generate_content()`.

### 2. ✅ No content-type validation for URL downloads — `image_processor.py:35-51`

`download_image()` did not check the `Content-Type` header from the HTTP response. Non-image content (HTML, JSON, etc.) would be silently base64-encoded and sent to the API.

**Fix:** Added content-type validation that raises `InvalidImageError` if the response is not `image/*`.

### 3. ✅ API key could leak in error messages — `api_client.py:173-176`

On HTTP errors, `response.text` was logged and included in the raised `APIError`. The raw response body could contain sensitive information or request context. Additionally, `requests.exceptions.RequestException` can include the full URL (containing the API key) in its message.

**Fix:** Error handler now extracts the structured error message from the JSON response body instead of dumping raw `response.text`.

---

## 🟡 Medium

### 4. ✅ No image size limit — `image_processor.py`

Neither `download_image()` nor `load_local_image()` checked the size of image data. A multi-GB file would exhaust memory or produce a request far too large for the API.

**Fix:** Added `MAX_IMAGE_SIZE_BYTES` (20 MB) to `config.py`. Size is checked via `os.path.getsize()` for local files and `len(response.content)` for downloads, before base64 encoding.

### 5. ✅ API timeout too short — `config.py:6`

`API_TIMEOUT = 30` seconds for Gemini 2.5 Flash vision requests with large images could cause frequent timeouts.

**Fix:** Increased to 60 seconds.

### 6. ✅ HTTP error message lost context — `image_processor.py:48-49`

The error handler for failed image downloads (`"HTTP error when downloading image: {e}"`) did not include the URL or status code, making debugging difficult.

**Fix:** Error message now includes the HTTP status code and the URL that failed.

### 7. ✅ `requirements.txt` missing version constraints — `requirements.txt`

`flask` and `flask-cors` had no version pins in `requirements.txt`, while `setup.py` pinned them to `>=2.3.0` and `>=4.0.0` respectively. Users installing via `pip install -r requirements.txt` could get incompatible versions.

**Fix:** Added matching version constraints: `flask>=2.3.0`, `flask-cors>=4.0.0`.
