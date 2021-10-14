import time
import json
import random

from django.shortcuts import render

# Create your views here.
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import *

from .cook import Cook_search
from .cook import Cook_keyword

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

print('開始')
food_type = ['history']
food_style = ['history']
recipe = ['history'] #, '日式料理的晚餐 醋飯壽司']
item_count = {'無調味壽司片': 0, '海苔片': 0, '蘆筍': 0, '紅蘿蔔': 0, '壽司醋': 0, '午餐肉': 0, '鮪魚沙拉': 0, '蝦沙拉': 0}
item_price = {'無調味壽司片': 30, '海苔片': 25, '蘆筍': 40, '紅蘿蔔': 35, '壽司醋': 70, '午餐肉': 20, '鮪魚沙拉': 20, '蝦沙拉': 20}
pay_total = ['history']


def flex_receipt_item(item,count, price):
    content = {
        "type": "box",
        "layout": "horizontal",
        "contents": [
            {
                "type": "text",
                "text": item,
                "size": "sm",
                "color": "#555555",
                "flex": 0
            },
            {
                "type": "text",
                "text": "$" + str(count * price),
                "size": "sm",
                "color": "#111111",
                "align": "end"
            }
        ]
    }
    return content

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)  # 傳入的事件
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:

            if isinstance(event, MessageEvent):  # 如果有訊息事件
                print("message", event.message)
                message = []
                if event.message.type == 'text':
                    mtext = event.message.text
                    uid = event.source.user_id
                    profile = line_bot_api.get_profile(uid)
                    name = profile.display_name

                    if 'hi' in mtext.lower() or '嗨' in mtext or 'hello' in mtext.lower():
                        text_ = '{} 您好，感謝您成為「今天吃甚麼」的好友😍😍 \n\n' \
                                '趕快點選主選單！看看有什麼好吃的吧！💪💪💪\n\n' \
                                '我們總共有 4 大功能：\n\n' \
                                '1. 找生鮮：確定要烹飪的料理後，勾選需要的食材，再輸入地址以匹配外送員。\n\n' \
                                '2. 找私廚：輸入所在地址後，匹配附近廚師，並且和廚師協商需求。\n\n' \
                                '3. 找食譜：可以透過搜尋功能以及簡易分類功能瀏覽您想尋找的食譜。\n\n' \
                                '4. 每日驚喜：隨機菜譜、美食新聞、折價券。'.format(name)

                        message.append(TextSendMessage(text_))
                        # line_bot_api.reply_message(event.reply_token, message)

                    # FAKE 1 TO 1
                    elif '龍哥你好' in mtext:
                        time.sleep(2)
                        text_ = '今天想吃什麼呢？'
                        message.append(TextSendMessage(text_))

                    elif '我今天想吃' in mtext:
                        time.sleep(5)
                        text_ = '沒問題！那材料的部分我會準備好。'
                        message.append(TextSendMessage(text_))
                    elif '6 點方便' in mtext:
                        time.sleep(2)
                        text_ = '好的，那我們 6 點見'
                        message.append(TextSendMessage(text_))

                    elif mtext.lower() == 'exit':
                        text_ = '預約完成！\n龍哥資訊\n電話：0930-223-876\n預約時間：{} 18:00'.format(time.strftime("%m/%d", time.localtime()))
                        message.append(TextSendMessage(text_))

                    # ==== Function ====

                    # ====== 找生鮮 ======
                    elif '選擇食譜：' in mtext:
                        recipe_list = mtext.split('：')
                        recipe.append(recipe_list[-1])

                    elif mtext == '找生鮮':
                        for i in item_count.keys():
                            item_count[i] = 0
                        if len(recipe) == 1:
                            text_ = '請先選擇食譜'
                            message.append(TextSendMessage(text_))
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Buttons template',
                                    template=ButtonsTemplate(
                                        thumbnail_image_url='https://i.imgur.com/ZFSzfbz.jpg',
                                        title='找食譜',
                                        text='請選擇要用甚麼方式查找食譜',
                                        actions=[
                                            MessageTemplateAction(
                                                label='選項看看看',
                                                text='選項看看看'
                                            ),
                                            MessageTemplateAction(
                                                label='關鍵字搜尋',
                                                text='關鍵字搜尋'
                                            )])))
                        else:
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Confirm template',
                                    template=ConfirmTemplate(
                                        title='確認菜單',
                                        text='您選擇的菜單為：{}，是否要以此食譜進行食材購買？'.format(recipe[-1]),
                                        actions=[
                                            MessageTemplateAction(
                                                label='Y',
                                                text='以「{}」進行購買'.format(recipe[-1]),
                                            ),
                                            MessageTemplateAction(
                                                label='N',
                                                text='重新選擇食譜'
                                            )])))

                    elif mtext == '重新選擇食譜':
                        recipe.pop()
                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    thumbnail_image_url='https://i.imgur.com/ZFSzfbz.jpg',
                                    title='找食譜',
                                    text='請選擇要用甚麼方式查找食譜',
                                    actions=[
                                        MessageTemplateAction(
                                            label='選項看看看',
                                            text='選項看看看'
                                        ),
                                        MessageTemplateAction(
                                            label='關鍵字搜尋',
                                            text='關鍵字搜尋'
                                        )])))

                    elif '日式料理的晚餐 醋飯壽司' in mtext:
                        message.append(
                            TemplateSendMessage(
                                alt_text='Carousel template',
                                template=CarouselTemplate(
                                    columns=[
                                        CarouselColumn(
                                            title='無調味壽司片',
                                            text= 'Price : 30 元 / 4 片',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-無調味壽司片'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-無調味壽司片'
                                                )]),
                                        CarouselColumn(
                                            title='海苔片',
                                            text='Price : 25 元 / 1 包',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-海苔片'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-海苔片'
                                                )]),
                                        CarouselColumn(
                                            title='蘆筍',
                                            text='Price : 40 元 / 1 袋',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-蘆筍'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-蘆筍'
                                                )]),
                                        CarouselColumn(
                                            title='紅蘿蔔',
                                            text='Price : 35 元 / 1 根',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-紅蘿蔔'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-紅蘿蔔'
                                                )]),
                                        CarouselColumn(
                                            title='壽司醋',
                                            text='Price : 70 元 / 1 瓶',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-壽司醋'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-壽司醋'
                                                )]),
                                        CarouselColumn(
                                            title='午餐肉',
                                            text='Price : 20 元 / 1 罐',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-午餐肉'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-午餐肉'
                                                )]),
                                        CarouselColumn(
                                            title='鮪魚沙拉',
                                            text='Price : 20 元 / 1 罐',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-鮪魚沙拉'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-鮪魚沙拉'
                                                )]),
                                        CarouselColumn(
                                            title='蝦沙拉',
                                            text='Price : 20 元 / 1 罐',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='加入購物車',
                                                    text='加入購物車-蝦沙拉'
                                                ),
                                                MessageTemplateAction(
                                                    label='從購物車中移除',
                                                    text='從購物車中移除-蝦沙拉'
                                                )]),
                                    ]
                                )
                            )
                        )
                    elif '加入購物車' in mtext:
                        item_list = mtext.split('-')
                        item = item_list[-1]
                        if item in item_count:
                            item_count[item] += 1
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Confirm template',
                                    template=ConfirmTemplate(
                                        title='確認',
                                        text='購物車中有 {} {} 份'.format(item, item_count[item]),
                                        actions=[
                                            MessageTemplateAction(
                                                label='繼續選購',
                                                text='以「{}」進行購買'.format(recipe[-1]),
                                            ),
                                            MessageTemplateAction(
                                                label='結帳',
                                                text='結帳'
                                            )])))

                    elif '從購物車中移除' in mtext:
                        item_list = mtext.split('-')
                        item = item_list[-1]
                        if item in item_count:
                            if item_count[item] > 0:
                                item_count[item] -= 1
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Confirm template',
                                    template=ConfirmTemplate(
                                        title='確認',
                                        text='購物車中有 {} {} 份'.format(item, item_count[item]),
                                        actions=[
                                            MessageTemplateAction(
                                                label='繼續選購',
                                                text='以「{}」進行購買'.format(recipe[-1]),
                                            ),
                                            MessageTemplateAction(
                                                label='結帳',
                                                text='結帳'
                                            )])))

                    elif mtext == '結帳':
                        total_count = 0
                        total_money = 0
                        final_item_count = {}
                        for i in item_count.keys():
                            if item_count[i] != 0:
                                final_item_count[i] = item_count[i]
                                total_count += item_count[i]
                                total_money += item_count[i] * item_price[i]
                        pay_total.append(total_money)
                        # print('金額',pay_total)
                        flex_total_item = []
                        for i in final_item_count.keys():
                            flex_total_item.append(flex_receipt_item(i, item_count[i], item_price[i]))

                        message.append(
                            FlexSendMessage(
                                alt_text='結帳',
                                contents={
                                    "type": "bubble",
                                    "body": {
                                        "type": "box",
                                        "layout": "vertical",
                                        "contents": [
                                            {
                                                "type": "text",
                                                "text": "RECEIPT",
                                                "weight": "bold",
                                                "color": "#1DB446",
                                                "size": "sm"
                                            },
                                            {
                                                "type": "text",
                                                "text": "購物清單",
                                                "weight": "bold",
                                                "size": "xxl",
                                                "margin": "md"
                                            },
                                            {
                                                "type": "separator",
                                                "margin": "xxl"
                                            },
                                            {
                                                "type": "box",
                                                "layout": "vertical",
                                                "margin": "xxl",
                                                "spacing": "sm",
                                                "contents": [
                                                    flex_receipt_item('無調味壽司片', item_count['無調味壽司片'], item_price['無調味壽司片']),
                                                    flex_receipt_item('海苔片', item_count['海苔片'],item_price['海苔片']),
                                                    flex_receipt_item('蘆筍', item_count['蘆筍'], item_price['蘆筍']),
                                                    flex_receipt_item('紅蘿蔔', item_count['紅蘿蔔'], item_price['紅蘿蔔']),
                                                    flex_receipt_item('壽司醋', item_count['壽司醋'], item_price['壽司醋']),
                                                    flex_receipt_item('午餐肉', item_count['午餐肉'], item_price['午餐肉']),
                                                    flex_receipt_item('鮪魚沙拉', item_count['鮪魚沙拉'], item_price['鮪魚沙拉']),
                                                    flex_receipt_item('蝦沙拉', item_count['蝦沙拉'], item_price['蝦沙拉']),
                                                    {
                                                        "type": "separator",
                                                        "margin": "xxl"
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "horizontal",
                                                        "margin": "xxl",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "ITEMS",
                                                                "size": "sm",
                                                                "color": "#555555"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": str(total_count),
                                                                "size": "sm",
                                                                "color": "#111111",
                                                                "align": "end"
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "type": "box",
                                                        "layout": "horizontal",
                                                        "contents": [
                                                            {
                                                                "type": "text",
                                                                "text": "TOTAL",
                                                                "size": "sm",
                                                                "color": "#555555"
                                                            },
                                                            {
                                                                "type": "text",
                                                                "text": "$"+str(total_money),
                                                                "size": "sm",
                                                                "color": "#111111",
                                                                "align": "end"
                                                            }
                                                        ]
                                                    },
                                                    {
                                                        "type": "separator",
                                                        "margin": "xs"
                                                    },
                                                    {
                                                        "type": "button",
                                                        "action": {
                                                            "type": "message",
                                                            "label": "LinePay 結帳",
                                                            "text": "LinePay"
                                                        },
                                                        "style": "primary",
                                                        "height": "sm",
                                                        "margin": "md"
                                                    },
                                                    {
                                                        "type": "button",
                                                        "action": {
                                                            "type": "message",
                                                            "label": "現金結帳",
                                                            "text": "現金結帳"
                                                        },
                                                        "style": "secondary",
                                                        "height": "sm",
                                                        "offsetEnd": "none",
                                                        "offsetBottom": "none",
                                                        "margin": "sm"
                                                    }
                                                ]
                                            }
                                        ]
                                    },
                                    "styles": {
                                        "footer": {
                                            "separator": True
                                        }
                                    }
                                }
                            )
                        )

                    if mtext == '現金結帳' or mtext == 'LinePay':
                        text_ = '請輸入送達地址'
                        message.append(TextSendMessage(text_))


                    # ====== 找食譜 ======
                    elif mtext == '找食譜':
                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    thumbnail_image_url='https://i.imgur.com/ZFSzfbz.jpg',
                                    title='找食譜',
                                    text='請選擇要用甚麼方式查找食譜',
                                    actions=[
                                        MessageTemplateAction(
                                            label='選項看看看',
                                            text='選項看看看'
                                        ),
                                        MessageTemplateAction(
                                            label='關鍵字搜尋',
                                            text='關鍵字搜尋'
                                        )])))

                    elif mtext == '選項看看看':
                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    thumbnail_image_url='https://i.imgur.com/ZFSzfbz.jpg',
                                    title='找食譜',
                                    text='想找的類型是',
                                    actions=[
                                        MessageTemplateAction(
                                            label='早餐',
                                            text='早餐',
                                        ),
                                        MessageTemplateAction(
                                            label='午餐',
                                            text='午餐',
                                        ),
                                        MessageTemplateAction(
                                            label='晚餐',
                                            text='晚餐',
                                        ),
                                        MessageTemplateAction(
                                            label='甜點',
                                            text='甜點',
                                        )])))
                    elif (mtext == '早餐') or (mtext == '午餐') or (mtext == '晚餐'):
                        food_type.append(mtext)

                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    thumbnail_image_url='https://i.imgur.com/ZFSzfbz.jpg',
                                    title='找食譜',
                                    text='想找的風格是',
                                    actions=[
                                        MessageTemplateAction(
                                            label='日式',
                                            text='日式',
                                        ),
                                        MessageTemplateAction(
                                            label='韓式',
                                            text='韓式'
                                        ),
                                        MessageTemplateAction(
                                            label='台式',
                                            text='台式'
                                        ),
                                        MessageTemplateAction(
                                            label='其他',
                                            text='其他'
                                        )])))
                    elif mtext == '甜點':
                        food_type.append(mtext)
                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    thumbnail_image_url='https://i.imgur.com/ZFSzfbz.jpg',
                                    title='找食譜',
                                    text='想找的風格是',
                                    actions=[
                                        MessageTemplateAction(
                                            label='麵包',
                                            text='麵包'
                                        ),
                                        MessageTemplateAction(
                                            label='蛋糕',
                                            text='蛋糕'
                                        ),
                                        MessageTemplateAction(
                                            label='點心',
                                            text='點心'
                                        ),
                                        MessageTemplateAction(
                                            label='其他',
                                            text='其他'
                                        )])))

                    elif (mtext == '日式') or (mtext == '韓式') or (mtext == '台式') \
                            or (mtext == '麵包') or (mtext == '蛋糕') or (mtext == '點心') or (mtext == '其他'):

                        food_style.append(mtext)
                        cook = Cook_search(food_type[-1], food_style[-1])
                        content = cook.scrape()
                        print('這裡', content)

                        try:
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Carousel template',
                                    template=CarouselTemplate(
                                        columns=[
                                            CarouselColumn(
                                                thumbnail_image_url=content[0][4],
                                                title=content[0][0],
                                                text=str(content[0][1]) + str(content[0][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[0][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[0][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[0][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[1][4],
                                                title=content[1][0],
                                                text=str(content[1][1]) + str(content[1][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[1][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[1][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[1][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[2][4],
                                                title=content[2][0],
                                                text=str(content[2][1]) + str(content[2][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[2][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[2][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[2][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[3][4],
                                                title=content[3][0],
                                                text=str(content[3][1]) + str(content[3][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[3][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[3][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[3][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[4][4],
                                                title=content[4][0],
                                                text=str(content[4][1]) + str(content[4][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[4][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[4][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[4][0]
                                                    )]),
                                        ])))
                        except:
                            text_ = '此功能維護中，請稍後再試。'
                            message.append(TextSendMessage(text_))



                    elif mtext == '關鍵字搜尋':
                        text_ = '請輸入關鍵字\n格式：搜尋:菜餚'
                        message.append(TextSendMessage(text_))

                    elif len(mtext.split(":")) == 2:
                        keyword = (mtext.split(":"))[-1]

                        cook = Cook_keyword(keyword)
                        content = cook.scrape()
                        print('這裡', content)

                        try:
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Carousel template',
                                    template=CarouselTemplate(
                                        columns=[
                                            CarouselColumn(
                                                thumbnail_image_url=content[0][4],
                                                title=content[0][0],
                                                text=str(content[0][1]) + str(content[0][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[0][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[0][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[0][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[1][4],
                                                title=content[1][0],
                                                text=str(content[1][1]) + str(content[1][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[1][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[1][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[1][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[2][4],
                                                title=content[2][0],
                                                text=str(content[2][1]) + str(content[2][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[2][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[2][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[2][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[3][4],
                                                title=content[3][0],
                                                text=str(content[3][1]) + str(content[3][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[3][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[3][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[3][0]
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url=content[4][4],
                                                title=content[4][0],
                                                text=str(content[4][1]) + str(content[4][2]),
                                                actions=[
                                                    MessageTemplateAction(
                                                        label='詳細資料',
                                                        text=content[4][2]
                                                    ),
                                                    URITemplateAction(
                                                        label='前往食譜',
                                                        uri=content[4][3]
                                                    ),
                                                    MessageTemplateAction(
                                                        label='選擇食譜',
                                                        text='選擇食譜：' + content[4][0]
                                                    )]),
                                        ])))
                        except:
                            text_ = '此功能維護中，請稍後再試。'
                            message.append(TextSendMessage(text_))

                    elif mtext == '找私廚':
                        if pay_total == 1:
                            pass
                        else:
                            pay_total.pop()
                        text_ = '請輸入所在地址'
                        message.append(TextSendMessage(text_))

                    elif mtext == '每日驚喜':
                        i = random.randint(1, 3)

                        if i == 1:  # 抽獎
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Buttons template',
                                    template=ButtonsTemplate(
                                        thumbnail_image_url='https://i.imgur.com/Wcd9eFN.jpg',
                                        title='恭喜獲得抽獎機會！',
                                        text='請立刻按下下方按鈕進行抽獎',
                                        actions=[
                                            MessageTemplateAction(
                                                label='我要抽獎！',
                                                text='我要抽獎！'
                                            )])))

                        elif i == 2:  # 隨機推薦菜餚
                            message.append(
                                TemplateSendMessage(
                                    alt_text='目錄 template',
                                    template=ImageCarouselTemplate(
                                        columns=[
                                            ImageCarouselColumn(
                                                image_url='https://i.imgur.com/I3LiSug.png',
                                                action=URITemplateAction(
                                                    label='芒果乳酪卡拉芬',
                                                    uri='https://icook.tw/recipes/381153'
                                                )
                                            ),
                                            ImageCarouselColumn(
                                                image_url='https://i.imgur.com/WZ51Bc4.png',
                                                action=URITemplateAction(
                                                    label='鹽酥雞',
                                                    uri='https://icook.tw/recipes/389938'
                                                )
                                            ),
                                            ImageCarouselColumn(
                                                image_url='https://i.imgur.com/rBunxT7.png',
                                                action=URITemplateAction(
                                                    label='紅燒蕃茄豬肉麵',
                                                    uri='https://icook.tw/recipes/390175'
                                            ))])))
                        elif i == 3:  # 新聞
                            message.append(
                                TemplateSendMessage(
                                    alt_text='Carousel template',
                                    template=CarouselTemplate(
                                        columns=[
                                            CarouselColumn(
                                                thumbnail_image_url='https://i.imgur.com/91xWgGl.png',
                                                title='一圖秒懂北市中秋烤肉限制',
                                                text='是在規範群聚行為，並非規範烤肉本身，強調「重點是大家要保持社交安全距離，不鼓勵在任何場域戶外或你的陽台來做烤肉。」',
                                                actions=[
                                                    URITemplateAction(
                                                        label='查看新聞',
                                                        uri='https://reurl.cc/WXXgE5'
                                                    )]),

                                            CarouselColumn(
                                                thumbnail_image_url='https://i.imgur.com/RkHnv1K.jpg',
                                                title='中秋「烤肉」懶人包！',
                                                text='中秋想要自己烤，除了烤肉工具，更重要的是「肉品」。趨勢：小包裝、多樣化、口味創新',
                                                actions=[
                                                    URITemplateAction(
                                                        label='查看新聞',
                                                        uri='https://udn.com/news/story/11474/4882807'
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url='https://i.imgur.com/QqNlO6J.png',
                                                title='21種烤肉食材熱量排行大公開',
                                                text='中秋想要健康烤肉不僅要注意食材，配料、沾醬及飲料也不能輕忽。營養師整理出「21種烤肉食材熱量排行」',
                                                actions=[
                                                    URITemplateAction(
                                                        label='查看新聞',
                                                        uri='https://health.ltn.com.tw/article/breakingnews/3672365'
                                                    )]),
                                            CarouselColumn(
                                                thumbnail_image_url='https://i.imgur.com/UnjqRps.jpg',
                                                title='來台南絕對不可錯過的超人氣排隊美食',
                                                text='講到全台最好吃的縣市，老饕心中的TOP 1絕對是號稱美食之都的台南！來到台南不怕吃不夠，而是怕自己的胃不夠裝！',
                                                actions=[
                                                    URITemplateAction(
                                                        label='查看新聞',
                                                        uri='https://www.chinatimes.com/realtimenews/20210918001391-260405?chdtv'
                                                    )]),
                                        ])))





                    elif mtext == '龍哥_詳細資料':
                        text_ = '龍哥\n經歷：\n\t福華大飯店前主廚\n\t10 年的專業主廚經驗\n' \
                                '拿手菜品：\n\t糖醋排骨\n\t舒芙蕾\n\t歐姆蛋'
                        message.append(TextSendMessage(text_))

                    elif mtext == 'Sophia_詳細資料':
                        text_ = 'Sophia\n經歷：\n\t法國藍帶廚藝學校畢業\n\t8 年的專業主廚經驗\n' \
                                '拿手菜品：\n\t歐式馬鈴薯牛肉派\n\t威靈頓牛排'
                        message.append(TextSendMessage(text_))

                    elif mtext == '亂煮阿祥_詳細資料':
                        text_ = '亂煮阿祥\n經歷：\n\t高雄餐旅大學中餐廚藝系畢業\n\t中餐烹飪類金手獎\n' \
                                '拿手菜品：\n\t佛跳牆\n\t蒜蓉茄子'
                        message.append(TextSendMessage(text_))




                    line_bot_api.reply_message(event.reply_token, message)

                if event.message.type == 'location':
                    if len(pay_total) != 1:
                        time.sleep(2)
                        text_ = '訂單已成立，李先生正在外送的路上'
                        message.append(TextSendMessage(text_))

                    else:
                        message.append(
                            TemplateSendMessage(
                                alt_text='Carousel template',
                                template=CarouselTemplate(
                                    columns=[
                                        CarouselColumn(
                                            thumbnail_image_url='https://i.imgur.com/83EPj9S.png',
                                            title='龍哥',
                                            text='拿手菜品：\n\t糖醋排骨\n\t舒芙蕾\n\t歐姆蛋',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='詳細資料',
                                                    text='龍哥_詳細資料'
                                                ),
                                                MessageTemplateAction(
                                                    label='一對一溝通',
                                                    text='與龍哥連線'
                                                ),
                                                MessageTemplateAction(
                                                    label='call',
                                                    text='0930223876'
                                                )]),

                                        CarouselColumn(
                                            thumbnail_image_url='https://i.imgur.com/u5TwXpJ.png',
                                            title='Sophia',
                                            text='拿手菜品：\n\t歐式馬鈴薯牛肉派\n\t威靈頓牛排',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='詳細資料',
                                                    text='Sophia_詳細資料'
                                                ),
                                                MessageTemplateAction(
                                                    label='一對一溝通',
                                                    text='與 Sophia 連線'
                                                ),
                                                MessageTemplateAction(
                                                    label='call',
                                                    text='091234678'
                                                )]),
                                        CarouselColumn(
                                            thumbnail_image_url='https://i.imgur.com/wNJOiDw.jpg',
                                            title='亂煮阿祥',
                                            text='拿手菜品：\n\t佛跳牆\n\t蒜蓉茄子',
                                            actions=[
                                                MessageTemplateAction(
                                                    label='詳細資料',
                                                    text='亂煮阿祥_詳細資料'
                                                ),
                                                MessageTemplateAction(
                                                    label='一對一溝通',
                                                    text='與亂煮阿祥連線'
                                                ),
                                                MessageTemplateAction(
                                                    label='call',
                                                    text='094316287'
                                                )]),
                                    ])))

                    line_bot_api.reply_message(event.reply_token, message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()
