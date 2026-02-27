# GeoIntel Bug Report

> All issues listed below have been fixed.

## 🔴 Critical / High

### 1. ✅ Python 3.9 compatibility broken — `config.py:18`

The `str | None` union syntax requires Python 3.10+. The rest of the codebase uses `Optional[str]` from `typing`, and `setup.py` declares broad Python 3 compatibility.

**Fix:** Changed to `Optional[str]` for consistency and backward compatibility.

### 2. ✅ API key exposed in error messages — `api_client.py:81,90`

The error handler on line 90 dumped `response.text` alongside the URL context, which could inadvertently leak the API key in logs or terminal output.

**Fix:** Error handler now extracts the error message from the JSON response body instead of dumping raw response text.

### 3. ✅ Hardcoded browser-fingerprint headers — `api_client.py:62-76`

Request headers included `sec-ch-ua`, `sec-ch-ua-platform`, `sec-gpc`, and a fake `Referer`, clearly copy-pasted from browser DevTools. These were unnecessary for server-side API calls.

**Fix:** Removed all browser-fingerprint headers, keeping only `Content-Type: application/json`.

### 4. ✅ No response structure validation — `response_parser.py:52-67`

After `json.loads`, the parsed result was returned as-is with no validation that `locations` was a list or had required fields. Malformed responses would crash downstream code.

**Fix:** Added `_normalize_location()` helper that ensures all required fields exist with safe defaults. Added validation that `locations` is a list. All locations are normalized before being returned.

---

## 🟡 Medium

### 5. ✅ Missing file encoding on Windows — `cli.py:38`

No `encoding='utf-8'` was specified when writing the output file. On Windows the default encoding is the system locale (e.g., `cp1252`), which would crash on non-Latin characters.

**Fix:** Added `encoding='utf-8'` to the `open()` call.

### 6. ✅ API timeout too short — `api_client.py:84`

`timeout=20` seconds for a Gemini 2.5 Flash vision request with image analysis was too aggressive.

**Fix:** Increased timeout to 60 seconds.

### 7. ✅ Version constraint missing in `setup.py` — `setup.py:8`

`requirements.txt` specifies `requests>=2.31.0`, but `setup.py` only listed `'requests'` with no version constraint.

**Fix:** Changed `install_requires` to `['requests>=2.31.0']` to match `requirements.txt`.

### 8. ✅ HTTP error message loses context — `image_utils.py:44-45`

The error handler for image downloads stripped the URL and status code, making debugging impossible.

**Fix:** Error message now includes the HTTP status code and the URL that failed.

---

## 🟢 Low

### 9. ✅ Inconsistent type annotation style — `config.py`

`config.py` used `str | None` (PEP 604), while every other module used `Optional[str]`.

**Fix:** Resolved as part of fix #1 — now uses `Optional[str]` consistently.

### 10. ✅ No image size limit — `image_utils.py`

`encode_image_to_base64` read entire files into memory with no size check. A multi-GB file would exhaust memory.

**Fix:** Added a 20 MB size limit (`MAX_IMAGE_SIZE_BYTES` in `config.py`), enforced for both local files (via `os.path.getsize`) and downloaded URLs (via `len(response.content)`) before base64 encoding.

### 11. ✅ `setup.py` formatting — `setup.py:10-14`

The `entry_points` block had inconsistent indentation.

**Fix:** Reformatted `setup.py` with consistent indentation throughout.
