from template import Itemplate
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from io import BytesIO
import asyncio
import aiohttp

class TempDefault(Itemplate):
    def __init__(self):
        self.__rank_color = {
            'unranked': np.array([0,0,0], dtype=np.uint8),
            'newbie': np.array([0x80,0x80,0x80], dtype=np.uint8),
            'pupil': np.array([0,0x80,0], dtype=np.uint8),
            'specialist': np.array([0x03,0xa8,0x93], dtype=np.uint8),
            'expert': np.array([0,0,0xff], dtype=np.uint8),
            'candidate master': np.array([0xaa,0,0xaa], dtype=np.uint8),
            'master': np.array([0xff,0x8c,0], dtype=np.uint8),
            'international master': np.array([0xff,0x66,0], dtype=np.uint8),
            'grandmaster': np.array([0xff,0,0], dtype=np.uint8),
            'international grandmaster': np.array([0xcc,0,0], dtype=np.uint8),
            'legendary grandmaster': np.array([0x80,0,0], dtype=np.uint8),
        }
        self.font_rating = 'fonts/NovaMono.ttf'
        self.font_rank = 'fonts/DosisMed.ttf'
        self.font_name = 'fonts/DosisSemi.ttf'
    async def generate_async(self, name: str, rank: str, rating: int, link_avatar: str):
        async def gene_bytes_avatar():
            async with aiohttp.ClientSession() as session:
                async with session.get(link_avatar) as req_avatar:
                    return await req_avatar.read()

        task_avatar = asyncio.create_task(gene_bytes_avatar())
        img = Image.new('RGB',(518,320),(255,255,255))
        arr_mask = np.ones((160,160),dtype=bool)
        for x in range(160):
            for y in range(160):
                if x/(y-79.5)>-0.5 and x/(y-79.5)<0.5:
                    arr_mask[x,y] = False
        for x in range(160):
            for y in range(160):
                if (x-159)/(y-79.5)>-0.5 and (x-159)/(y-79.5)<0.5:
                    arr_mask[x,y] = False

        arr_rank = np.zeros((160,160,3),dtype=np.uint8)
        for y in range(160):
            for x in range(160):
                dx, dy = x-79, y-79
                da, db = dx - dy/1.732051, dy*2/1.732051
                dist = (np.abs(da) + np.abs(db) + np.abs(da+db))/2
                bt = dist/79*0.4
                arr_rank[x,y] = self.__rank_color[rank]*(1-bt) + np.array([0xff,0xff,0xff])*bt
        img_rank = Image.fromarray(arr_rank)
        str_rating = str(rating) if rating>=0 else '----'
        ttf_rating = ImageFont.truetype(self.font_rating,40)
        tw, th = ttf_rating.getsize(str_rating)
        draw_rating = ImageDraw.Draw(img_rank)
        draw_rating.text(((160-tw)//2,(160-th)//2),str_rating,'white',ttf_rating)

        img.paste(img_rank,(99,139),Image.fromarray(arr_mask))
        
        size_name = 48
        for i in range(48,0,-1):
            ttf_tmp = ImageFont.truetype(self.font_name,i)
            tw, th = ttf_tmp.getsize(name)
            if tw <= 285:
                size_name = i
                break

        ttf_name = ImageFont.truetype(self.font_name,size_name)
        tw, th = ttf_name.getsize(name)
        draw_name = ImageDraw.Draw(img)
        draw_name.text((220, 56 + (48-size_name)//2), name,(0x45,0x45,0x45),ttf_name)

        ttf_rank = ImageFont.truetype(self.font_rank,28)
        tw, th = ttf_rank.getsize(rank)
        draw_name.text((220, 116 - (48-size_name)//2), rank,(0x45,0x45,0x45),ttf_rank)

        bytes_avatar = await task_avatar
        io_avatar = BytesIO(bytes_avatar)
        avatar = Image.open(io_avatar).resize((160,160),Image.ANTIALIAS)
        img.paste(avatar,(20,20),Image.fromarray(arr_mask))

        return img
    
    def generate(self, name: str, rank: str, rating: int, link_avatar: str) -> Image:
        return asyncio.run(self.generate_async(name, rank, rating, link_avatar))

    def fail(self, msg: str):
        img = Image.new('RGB',(518,320),(255,255,255))
        ttf = ImageFont.truetype(self.font_name,48)
        tw, th = ttf.getsize(msg)
        draw = ImageDraw.Draw(img)
        draw.text(((518 - tw) // 2, (320 - th) // 2), msg,(0x80,0x80,0x80),ttf)
        return img

