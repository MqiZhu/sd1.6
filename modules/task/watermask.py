from io import BytesIO
import base64

from PIL import Image, ImageDraw, ImageFont


def load_explicit_watermark_image():
    base64_str = "iVBORw0KGgoAAAANSUhEUgAAAGQAAAAsCAYAAACT6R1VAAAAAXNSR0IArs4c6QAAAIRlWElmTU0AKgAAAAgABQESAAMAAAABAAEAAAEaAAUAAAABAAAASgEbAAUAAAABAAAAUgEoAAMAAAABAAIAAIdpAAQAAAABAAAAWgAAAAAAAACWAAAAAQAAAJYAAAABAAOgAQADAAAAAQABAACgAgAEAAAAAQAAAGSgAwAEAAAAAQAAACwAAAAANW67IwAAAAlwSFlzAAAXEgAAFxIBZ5/SUgAAAVlpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADx4OnhtcG1ldGEgeG1sbnM6eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IlhNUCBDb3JlIDYuMC4wIj4KICAgPHJkZjpSREYgeG1sbnM6cmRmPSJodHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4KICAgICAgPHJkZjpEZXNjcmlwdGlvbiByZGY6YWJvdXQ9IiIKICAgICAgICAgICAgeG1sbnM6dGlmZj0iaHR0cDovL25zLmFkb2JlLmNvbS90aWZmLzEuMC8iPgogICAgICAgICA8dGlmZjpPcmllbnRhdGlvbj4xPC90aWZmOk9yaWVudGF0aW9uPgogICAgICA8L3JkZjpEZXNjcmlwdGlvbj4KICAgPC9yZGY6UkRGPgo8L3g6eG1wbWV0YT4KGV7hBwAAD+ZJREFUeAHtnAlsVVUax997bV/7WlrKvkMLsoOyDERcWCrIJktgEGSdAUYRAyqZOKCy6GiGxGAcBYGJoqCCkGAKAgLKJvuiLAGRHYqFytbS0pX2vfn9b3ueD2hpHy0Zzbwv+d4992z33O//befcpnZb8WSni6egWzmuleFoOBwOgdUeoN8kkEcxC06Dr8FXYdWJfGWZX3Pbb0mFKSBi4EqwQBBA7oIrlwD5SEAyFTtgySkdPg8nwiK1GQW3Knx/1FgY+Q6qR4cYWEDkwmayosbSJUBIwMgpiLLAkaX8DGfCvvLl9jdS59vJt3MzGmNgTS6zU5thigG6iwSMnIzsIuhbFU6F5dLUfgcVBojp1IJCTfgmbCY3bYGrfxKQ/OTi5WUEynW4UFBuB8Sg1pgBteEc2NRRDFApJGBAkcwViy/DRtm90/oCogEyrxpwA/iOztQFqHQSMKA4mSYSToJNrLFm9gVEFWGwXJWCUIDujwQMKIopAiMFVp1FRvCmIpZagSJ/F6D7JwHJWxlrHVj7OQFjYSBAVFBFFFwNVkerkWuA7p8EJHO5rnq+jzAWojoF8WBYHf+wFBysV/hDkLGSKqzWayUGABeVivxmr/G7fSMJPDc319a4cWN71apVHRcuXHCfOnXKUiK1tW3b1h4UFGT/6aef3Ckpcs9FU+XKle0ak5WV5dGcJaWwsDBr3JUrV/waV8j8xkqq03Za7cY1yTqawGWaWT300EP20NBQ+9WrVz1GaHqoL9WqVcsuvn79uufYsWMlss569erZz507p7Vmw87atWuH/PLLL7aCeqXqYhcCdyA0ikWSp0mTJrbo6GgjhyI7+jYAoO3kyZOeGzdu+DXOdw6fsryUjlf2wm4zYStuZCFlFj8KhCOBaU4nQg9JTEy8ReDVq1e3JyUlqV0CDOY+hHuKRdODDz7oOHToUMa33377eGxsbMslS5bET5069eoDDzxgR0i2S5cuvZqampr47LPPLtm4cWMWcwYxp/e5xsL0hJo1azqxMHkFPd/bh7KRi28d1V7SBs/J3Dm+c3tb/S/oeQfgZLmsUFg5sTIrsxCK907SeDQ49+OPP27Eoivu27fv/PTp05MoB5sXUB8Ayn3llVcqdO7cuSHCTJo4cWKCb5/CVoAQ7QCSh/V1rVKlypMDBgy4ASCfMj54+fLlrajrVq5cuYshISFLe/bsGex0Oh3GHdntds/Fixfduj948GAWoI5EcZ5wu92ZtGkLIADsHo8nj3s93qorKNuoV6UF0s2bN7NffPHFVz/77LOU4tasie5Cmk8Al4ctQJRdqaJMUl0WJ0Hn9ejRI3Lo0KEz8bfVHn744V0AMqlRo0ayAOuFKDvolzFkyJBOrVu3/uevv/66CkDebNq0aRR9pLV3UIMGDexr167NGTFiRHXcTHsEm/Luu+9+Q9lFvMh65JFHntKghQsXvrpu3bpTFPVuvnNJoOGsLQxA8iIiIiLhurigBObKdDgcQQKDGBTFVfKwgKJsE5jcu/Py8jwA3ohyNpYoyyoLJdazBIiVVWmDIk3Qwks9OYKWG8qcMWNGV4GRnZ19qXz58m0/+uijRmPHjj2Oy3Gh4QZ8aaNVRkvlumx6YV0Lo7p16zqIRZmTJk16CguIPnHixHysUD7ONXny5NrEjC4INq1///49Bg0a1Is5fd/Hw5iKZ8+e/QEFWMkYO0Ck6Tnx8fHTn3nmmUMUy8GZxJ3ZgBNRsWLF8dzriENeRHPpGnTt2rV5FSpUqI9VGkCKXDP9iyPNKxkIB4dclgpGQBRLRwCgxQURLJ/CrK/s2LFjXpcuXabhljpTfwShKaPzko/QfIXnbTcFrMCGu5HSRJBhDQQ497Jly7Zwr41sFjGjH/FBZfn2wVwLJdokxOWwA623nonGy0Mo9czcsmVL90qVKrWXoly+fHk6XXJ5p3QpAECc5r0+xYIkN4eyOa5lRZrTpR+9hIRY6smbN2/u2L17d9b777/fAKtozQutiYuLW8sLvUAm1INnfL5nz55cf7MaxtnQ6qBNmzal7tq1q6/L5WqQk5OTjDVo3dlTpkypGxsbOwLN3kK2dhHXNmTDhg0vvPXWW8c7duzo4vng7rbjnsJxbbmsM+LIkSPKbCzCGpTpXPvwww/b4fYmA/YNhL8fC69K2U7caq6OpNLfcCnTTFTzQpYScw0VINotqqJUpOylWrVqNl40p3fv3l002YEDBzZySSXz2QQgfybraQNAWxCSXEOJSQkAYEgQ0S1bthylgWhwgRxtebiwCaqbNWvW3NGjRz+pMsCkbd68+RoszZcH0DsqBw5mDU7WSTGfMjIyclasWNGpV69es7AIycO+devWFQMHDlxJKv4aCtQcMGZj5BtoK2/cbMHwsrgYQJzSDIFSakAwexsCl0uJQqN645+TXn/99cPcR2AVm7jaEGZ3LnY0W7clJgVzOqefOXNmTHh4eB20Nh00grGCdILzENxgR9LX+JkzZx5GMZQx2rAIARFJ1qX7qL59+1YZOXJkNfqG+Dzf8grM5Wzfvn0/BG3/4IMP/oplr+7Xr98b58+fn0lMHEXG+DlWtRiwK2ru+0RaS74vLIsHNGvWzEG8uIGQOmLq1dmoLQGIq6NGjSqPpv2MFp4mSHYGpDq4kotY0S2xpKg1ICjH999/n7Ft27ZeMTExg3El24lNGfj5OPx56M6dO/ehwctWrVoVzxxOgLCUC4HOLIhnelE3Qo8m2diyaNGiaVFRUQrOIqsv7i+jRo0a/2BMLSzlHNYcyZr7cB3As64TV7ap84IFC/RhSbFHt6VWYk3iQ5rUCuo+dfdWBAAz0N6iRQtZgY0XX8vFTgoqq0lBu9cD2jiymY4AsogsRRpcLBltRghuhKNAPh9hDZLLYg77uHHjTjPJLMDSfE7106TJycl7sdIUWRJ9bcSdKNLUUzQ5AMAI05Is8Sdm5cqV4YASy3q7Ef/apKWlHcRCdjVs2LA/ljWPrO0Y8efQ3r17lY2JrLH5xTL79chdSWDKMswi/Z6d2GHHOnKk/VhBB03AnuK1CRMmuBGQldqSkViuhNS1G81fEYAtwRX3sB9//NGNmwl79NFHN8+fP3/0888/f/Tpp5+24gKC1fDQ7t27h8kySGm977B69epPcDFymepr6oOJR6EApXEiS6gE+xp9+vR5UxWZmZnncVHxAJL85Zdfrnv77bdXHj58uCsnAcMAbBAKJ5erhEDuvixJa3RrUgFSKtImjwkyhw0b1hEfHsELJyoFJVWM1D275Sg0NQffn0asaYJ7ackGT399UaKX0nkUccT53HPPyRqsHbNwVhnysB/IK3BP+TX8Yj1yS+H4fgEi9ygz1mbUVxGsMnFoNy5x6vbt26cQo3oSyHewQR2OJX+Vnp4+h2c58ALDOXGYMWfOnGW8S6kUmHUURlpLnixE501asCr8NkO013b06FGBWg6f25Wr7Z133pk0bdq0cxRNBifBp+3fv39oq1at/t6mTZs47vfCJSa01kPcCUXztXs2xxhFjsdFCQBXt27dwjp16uRBoDpGCcWS0wBPGZuXiEGhjz/++NdUBBEvemAlbhSpz5o1a1qyh5oIuE1oW9KuXTulvU7eTWD7AsttqUhy13w5AkSaquzhnixFu2fcSsbSpUtbof1N0eatLDgBIYSTWnrkHnTQSDmcs6adZFpZgBj30ksvLXzvvffOoW08unhSLMGNWELQGB8L8R0s92gpFUDMUZzxbVSZnf04TgzkyrzKx1wqhxOPKqEsE3mPuiQhF4gh8XPnzp1OWn1Glsb5WdDixYt1zmWsU1OWBen5kn+2Fix/6F0cZb+IbxIam4uPt6wD97GB+zyE5hAYaJqNcypPXFxcKC7gAoFxO64siuxLsSaDlzNCK/FLFghd3z3uWKsBmH3IOp67hBR2Ocf/X8Ffc7+GTEsfSW4ZyDrlJTLnzZt3nTVOxDW9QXxKwBWPf/nllxegZP/CqkIAQ0ctWcSre/Imdyz2twrJUAExUxYiQLQx8BsUfSQiFmSz6FoE9l5kQakcIu5hLhduzM33Aor5hBvQ/HnUb37ssceeICboIHApbAEBMFqLBaCud6MCELXztgQr0E02xjirjoD8yfjx45URmaMhPV9t4ShHsI7mAc/qy9rrcPaWgXK5WHPOF198cQgAjmBlDbp27fo3PW/w4MGV8AY1ANiNIriUuRFvpEz3JDvGGdL7a23CwcqyUikIHePvKZaMpPn0DGInnskLTuCwL239+vUZmLw+DN2i8aSLMsmIMWPG7GQD9xc9gXOl8uT2PxAbxjI2mSqXvvSprTAyZ0cA4IQdCNDy5foIVtDfboRcv379aOoqDx8+PJwU2INQra97nB7kyXIh9VVwtnEaPaNDhw6WpdJP7lDVAjmbsigGwBbL+gSELJMEJRmAnBzlSHYacMv7arwfpPGyXGuXrgAnUPQXdX6hjfuxEQ/saFQWLL9c5EcmabD2K8ePH8/lG8Yx+orCZs+enQ4foRwEQHf9QIUQLG2Sx0CDPewXBIhHFmLaAEdAyNIk7JunT5/OI5BbIKufCLCsK+upoIJ2+bxLIoIORfhehaDsyPdOXiv26Dl4huG43QqRkZFSYlmMZWnWpP7/CAzJXZtOCxBddcZTTQV/SSmpLIJNXwQpokeBvKg5pJk6WMQ3h0ugpJseQHCgaeEl+YRbYD3hbDr/jbv4z3fffZfEs5wJCQlu3JdeLJjyPrRYQMjfB2tesx7j1kh9VRfCZ4DNAHGBbyrLCfaJ1JXES9g5OUhBEavgIWQdDr23eYafV40TmDIIsTduaCHt4JIsSOP+Z6Q0GyWQVUuTQwDYIUsVAa6NoC0hSePCBDb3arqDSNFtHO+or+aKIF4ESbDGiu4YQIWxctyzMlO5YBdWpu8qhXUvSZ2lGHQ8DifAlrM0/q8hFfVgLVB1v1siBbX+skSWYcAwi1Ub51x2XKO7KDBMX/0RBm6vRH3NGF1JjR14BZtcobE633Y/ypKz5K09mTI9S/AGEO1o/wRbwU2NAbqvEjDWcZannIQtHCR8NegmA74AK/KpLkD3VwKSvXydXJXIkrmxBgPAWRq0eVCgMXUUA1TGEpBsJeMzsOKYDMIiA4huVKlgeEI3kLdT/m3gt4wkIDCUkl+CldmJvMp/e/5sXJc6VIaVSQSAQQhlRJKrOR05RFmZ4i3yvR0Q81zlkRpYERYoolsG5lcFfv2QgAFDceMgrKxKMvVaB2XLj+laGF2lUgMEikgDA6BYovDrxwhcbkrxWWAogboDDOruCojadb6kTZCOI6xjCq7mAQFwEMZdyCiwPI1itXaoh+FCLYN6i4oTqkExjN71YJ13GWDk/ww4FANUIAHJTCwQJCMdiZyDL8MiI9P8u9t+1Vgc+U4gYKrAshj9bZXM0DdT4/b/npSpyqsICLl9/XuNEtN/AZq54L8rHx+JAAAAAElFTkSuQmCC"
    return Image.open(BytesIO(base64.b64decode(base64_str)))


explicit_watermark_image = load_explicit_watermark_image()


def explicit_watermark(original_image, user_id):
    watermark_width, watermark_height = explicit_watermark_image.size  
    x = original_image.width - watermark_width - 10  
    y = original_image.height - watermark_height - 30  
    original_image.paste(explicit_watermark_image, (x, y), explicit_watermark_image)  

    user_id_text = str(user_id)  
    user_id_font = ImageFont.load_default()
    draw = ImageDraw.Draw(original_image)  
    draw.text((original_image.width - 125, original_image.height - 20), user_id_text, font=user_id_font, fill=(255, 255, 255, 128))  

    return original_image


def implicit_watermark():
    import time
    print("watermask_key: 880651331&576&960&640")
    print(f"wm: 该图是{15506399140}在{time.strftime('%H:%M %d/%m/%Y', time.localtime())}使用荆跃科技算法生成。")

def batch_watermark(original_images, user_id):
    images = []
    for original_image in original_images:
        image = explicit_watermark(original_image, user_id)
        print("add explicit_watermark on 7106837595711078400")
        implicit_watermark()
        print("add implicit_watermark on 7106837595711078400")
        images.append(image)
    
    return images



#def explicit_watermark(original_image, user_id):
#    """显式水印"""
#
#    watermark_width, watermark_height = explicit_watermark_image.size
#    x = original_image.width - watermark_width - 10
#    y = original_image.height - watermark_height - 30
#    original_image.paste(explicit_watermark_image, (x, y), explicit_watermark_image)
#
#    user_id_text = str(user_id)
#    user_id_font = ImageFont.load_default()
#    draw = ImageDraw.Draw(original_image)
#    draw.text((original_image.width - 125, original_image.height - 20), user_id_text, font=user_id_font, fill=(255, 255, 255, 128))
#
#    return original_image
#
#
#def implicit_watermark(image, phone):
#    """隐式水印"""
#
#    with BytesIO() as buf:
#        image.save(buf, "PNG")
#        img_array = np.frombuffer(buf.getvalue(), np.uint8)
#        img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)
#        
#        password_wm = 880651331
#        wm = f"该图是{phone}在{time.strftime('%H:%M %d/%m/%Y', time.localtime())}使用荆跃科技算法生成。"
#        wmc = WaterMark(password_img=1, password_wm=password_wm)
#        wmc.read_img(img=img)
#        wmc.read_wm(wm, mode='str')
#        embed_img = wmc.bwm_core.embed()
#        succ, img_array = cv2.imencode(".png", embed_img)
#        len_wm = len(wmc.wm_bit)
#        watermask_key=f"{password_wm}&{len_wm}&{image.height}&{image.width}"
#        print(f"watermask_key: {watermask_key}")
#        print(f"wm: {wm}")
#
#    return Image.open(BytesIO(img_array)), watermask_key
#
#
#def batch_watermark(original_images, user_id, phone):
#    images = []
#    watermask_keys = []
#    for original_image in original_images:
#        image = explicit_watermark(original_image, user_id)
#        print(f"add explicit_watermark on {user_id}")
#        image, watermask_key = implicit_watermark(image, phone)
#        print(f"add implicit_watermark on {user_id}")
#        images.append(image)
#        watermask_keys.append(watermask_key)
#
#    return images, watermask_keys











