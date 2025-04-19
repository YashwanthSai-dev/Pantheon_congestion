def check_call(*args, **kwargs):
    print("[Dummy subprocess_wrappers] check_call called with:", args, kwargs)
    return 0

def check_output(*args, **kwargs):
    print("[Dummy subprocess_wrappers] check_output called with:", args, kwargs)
    return b"dummy_output"

def call(*args, **kwargs):
    print("[Dummy subprocess_wrappers] call called with:", args, kwargs)
    return 0
