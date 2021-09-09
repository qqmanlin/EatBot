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

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)


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
                                '3. 找食譜：可以透過搜尋功能以及簡易分類功能瀏覽您想尋找的食譜。\n\n'\
                                '4. 每日驚喜：隨機菜譜、美食新聞、折價券。'.format(name)

                        message.append(TextSendMessage(text_))
                        # line_bot_api.reply_message(event.reply_token, message)
                    if '身體資訊' in mtext: # 找生鮮
                        text_ = '請選擇食譜'
                        message.append(TextSendMessage(text_))

                    if '吃' in mtext: # 找食譜
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

                    if '選項看看看' in mtext:
                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    title='找食譜',
                                    text='想找的類型是',
                                    actions=[
                                        MessageTemplateAction(
                                            label='早餐',
                                            text='早餐'
                                        ),
                                        MessageTemplateAction(
                                            label='午餐',
                                            text='午餐'
                                        ),
                                        MessageTemplateAction(
                                            label='晚餐',
                                            text='晚餐'
                                        ),
                                        MessageTemplateAction(
                                            label='甜點',
                                            text='甜點'
                                        )])))
                    if ('早餐' or '午餐' or '晚餐') in mtext:
                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    title='找食譜',
                                    text='想找的風格是',
                                    actions=[
                                        MessageTemplateAction(
                                            label='煎',
                                            text='煎'
                                        ),
                                        MessageTemplateAction(
                                            label='煮',
                                            text='煮'
                                        ),
                                        MessageTemplateAction(
                                            label='炒',
                                            text='炒'
                                        ),
                                        MessageTemplateAction(
                                            label='炸',
                                            text='炸'
                                        )])))
                    if '甜點' in mtext:
                        message.append(
                            TemplateSendMessage(
                                alt_text='Buttons template',
                                template=ButtonsTemplate(
                                    title='找食譜',
                                    text='想找的風格是',
                                    actions=[
                                        MessageTemplateAction(
                                            label='麵包',
                                            text='麵包'
                                        ),
                                        MessageTemplateAction(
                                            label='糕點',
                                            text='糕點'
                                        ),
                                        MessageTemplateAction(
                                            label='點心',
                                            text='點心'
                                        ),
                                        MessageTemplateAction(
                                            label='其他',
                                            text='其他'
                                        )])))


                    if '關鍵字搜尋' in mtext:
                        text_ = '請輸入關鍵字'
                        message.append(TextSendMessage(text_))

                    if '營養素' in mtext: #找私廚
                        text_ = '請輸入所在地址'
                        message.append(TextSendMessage(text_))

                    line_bot_api.reply_message(event.reply_token, message)

        return HttpResponse()
    else:
        return HttpResponseBadRequest()