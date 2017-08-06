import requests
import os


def copy_file(source, dest, buffer_size=1024 * 1024):
    while True:
        copy_buffer = source.read(buffer_size)
        if not copy_buffer:
            break
        dest.write(copy_buffer)

class Request():

    HOST = "127.0.0.1"
    PORT = "8080"

    @staticmethod
    def upload(url, data, filepath):

        if not os.path.exists(filepath):
            raise Exception('File not found exception!')

        try:
            with open(filepath, 'wb') as f:
                requests.post(url, files=f, data=f)
        except Exception as e:
            raise e

    @staticmethod
    def download(url, dest):
        r = requests.get(url, stream=True)
        print(r.status_code)
        if r.status_code == requests.codes.ok:
            copy_file(r.raw, dest)
        else:
            raise Exception('Url cannot found!' + str(r.status_code))

    pass

if __name__ == "__main__":
    url = 'http://www.java2s.com/Code/JarDownload/apache-commons/apache-commons-lang.jar.zip'
    # Request.download(url, open('test.zip', 'wb+'))
    data = {'data' : open('test.zip', 'wb+')}
    r = requests.post(url, data=data, stream=True)
    print(r.content)
