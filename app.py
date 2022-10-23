from flask import Flask, make_response, request
from PIL import Image
from template import TemplateGetter
from io import BytesIO
import requests as rqs
import json
import re

app = Flask(__name__)

@app.route('/')
def index():
    
    rqs.adapters.DEFAULT_RETRIES = 5
    name = request.args['user']
    theme = request.args.get('theme','')
    img = Image.new('L',(0,0))
    try:
        res = json.loads(
            rqs.get(f'https://codeforces.com/api/user.info?handles={name}').text
            )
        if 'status' in res and res['status'] == 'OK':
            info = res['result'][0]
            rank, rating = info.get('rank','unranked'), info.get('rating',-1)
            link_avatar = info['titlePhoto']

            if re.search("^(http:|https:)", link_avatar) is None:
                link_avatar = 'https:' + link_avatar

            print(link_avatar)
            img = TemplateGetter().getTemplate(theme).generate(name,rank,rating,link_avatar)
        else:
            img = TemplateGetter().getTemplate(theme).fail('User Not Found')
    except Exception as e:
        print(e)
        img = TemplateGetter().getTemplate(theme).fail('Source Error')
    
    io_img = BytesIO()
    img.save(io_img,'png')
    io_img.seek(0)
    ret = make_response(io_img.read())
    ret.headers['Content-Type'] = 'image/png'
    
    return ret

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
