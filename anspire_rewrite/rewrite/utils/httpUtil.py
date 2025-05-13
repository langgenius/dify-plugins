import httpx, json

timeout = httpx.Timeout(600.0, connect=600, read=600, write=600)

def do_request(request_obj):
    """
    请求
    :param request_obj:
    :return:
    """
    _method, _url, _headers, _params, _post_data = request_obj
    with httpx.Client(timeout=timeout) as client:
        _response = client.request(
            _method, _url, headers=_headers, params=_params, data=json.dumps(_post_data)
        )

        return _response.status_code, _response.json()