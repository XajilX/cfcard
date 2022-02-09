from flask import Flask, make_response, request
from PIL import Image
from template import TemplateGetter
from io import BytesIO
import requests as rqs
import json

app = Flask(__name__)

@app.route('/')
def index():
    name = request.args['user']
    theme = request.args.get('theme','')
    res = json.loads(
        rqs.get(f'https://codeforces.com/api/user.info?handles={name}').text
        )
    img = Image.new('L',(0,0))
    if 'status' in res and res['status'] == 'OK':
        info = res['result'][0]
        res_img = rqs.get(info['titlePhoto'])
        rank, rating = info.get('rank','unranked'), info.get('rating',-1)
        io_avatar = BytesIO(res_img.content)
        img_avatar = Image.open(io_avatar)
        img = TemplateGetter().getTemplate(theme).generate(name,rank,rating,img_avatar)
    else:
        img = TemplateGetter().getTemplate(theme).fail()
    
    io_img = BytesIO()
    img.save(io_img,'png')
    io_img.seek(0)
    ret = make_response(io_img.read())
    ret.headers['Content-Type'] = 'image/png'
    return ret

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
