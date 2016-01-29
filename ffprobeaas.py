from flask import Flask, request, jsonify, Response
from subprocess import Popen, PIPE
from urlparse import urlparse
from urllib import urlencode
from httplib import HTTPConnection, HTTPSConnection

FFPROBE_PATH = "/opt/ffmpeg/ffprobe"
app = Flask(__name__)

def get_url_info(url):
    url = urlparse(url)
    if url.scheme not in ["http", "https"] or not bool(url.netloc):
        return "{\"error\": \"Uh uh uh ;)\"}"
    if "?" in url.geturl():
        return "{\"error\": \"Direct file URLS only please :)\"}"
    conn = HTTPConnection(url.netloc) if url.scheme == "http" else HTTPSConnection(url.netloc) if url.scheme == "https" else None
    if not conn:
        return "{\"error\": \"wat\"}"
    conn.request("HEAD", url.path)
    res = conn.getresponse()
    if str(res.status)[0] != "2" or res.getheader("Content-Length") == "0":
        return "{\"error\": \"Go away ;)\"}"
    FFPROBE = [FFPROBE_PATH, "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", url.geturl().replace(" ", "%20")]
    p = Popen(FFPROBE, stdout=PIPE, stderr=PIPE)
    out = p.communicate()
    if out[1]:
        return out[1]
    else:
        return out[0]

@app.route("/")
def help():
    return jsonify({"help": "/get?url=http://i.imgur.com/3jBS8Pi.gif"})

@app.route("/get")
def probe():
    if request.args.get("url"):
        resp = Response(get_url_info(request.args.get("url")))
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Content-Type"] = "application/json"
        return resp
    else:
        return jsonify({"error": "Gonna need something here."})

if __name__ == "__main__":
    app.run(port=47641)
