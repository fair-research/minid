from minid import MinidClient
client = MinidClient()
client.login()
minid = client.register_file(
    'foo.txt',
    test=True,
    title='My Foo File',
    locations=['http://example.com/foo.txt']
)
