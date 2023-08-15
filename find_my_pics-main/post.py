class Post:
    def __init__(self, img, username, date):
        self.img = img
        self.username = username
        self.date = date

    def get_all_posts():
        sample = []
        sample.append(Post('', 'boyuqin', 'Mon, 29 Mar 2023 14:30:00 GMT'))
        sample.append(Post('https://images.unsplash.com/photo-1679939099455-6fb0ec91e794?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1674&q=80', 'boyuqin', 'Sun, 28 Mar 2023 12:30:00 GMT'))
        sample.append(Post('https://images.unsplash.com/photo-1680011415159-c0bfef591a0f?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80', 'boyuqin', 'Mon, 29 Mar 2023 00:24:00 GMT'))
        sample.append(Post('https://images.unsplash.com/photo-1680079640329-238b05dee3bf?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2600&q=80', 'boyuqin', 'Mon, 29 Mar 2023 04:34:00 GMT'))
        sample.append(Post('https://images.unsplash.com/photo-1680007966627-d49ae18dbbae?ixlib=rb-4.0.3&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=2070&q=80', 'boyuqin', 'Mon, 29 Mar 2023 04:12:00 GMT'))
        return sample