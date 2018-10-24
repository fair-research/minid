from globus_sdk import native_auth

from minid_client.config import save_tokens, load_tokens


def login():
    try:
        return load_tokens()
    except Exception as e:
        print(str(e))

    tokens = native_auth()
    save_tokens(tokens)

    return tokens