import os
from django.test.runner import DiscoverRunner


class MyTestRunner(DiscoverRunner):
    def teardown_test_environment(self, **kwargs):
        super(MyTestRunner, self).teardown_test_environment(**kwargs)
        os.remove('.env.test')
