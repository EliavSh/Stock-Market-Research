from threading import Thread


class MyThread(Thread):
    def __init__(self, app):
        Thread.__init__(self)
        self.app = app

    def run(self):
        self.app.run()
