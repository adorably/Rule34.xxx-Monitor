
class Data_Storage:
    def __init__(self) -> None:
        self.tag_id = ''
        self.tag_posts = 0
        self.pre_posts = 0
        self.pid = 0
        self.spinner_array = ['/', '-', '\\', '|']
        self.collected_posts = {
            'posts': [

            ]
        }
        self.temp_posts = {
            'posts': [

            ]
        }
        self.config = {
            'discord': {
                'webhook_url': '',
                'webhook_username': 'Rule34'
            },
            'app': {
                'refresh_time': 30
            }
        }

data = Data_Storage()