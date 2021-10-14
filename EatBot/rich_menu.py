import requests
import json


# token -> Messaging API > Channel access token (long-lived) （需要點 issue）
token = 'odxu5LlWs+3Y2zWjVGboTsvjRZ6i9raKjs5YQXrYZRnSNtOqaLuZrB9EyBLQtZ2VV0gghTGCYob/LvwFFItjDX3srvljVFECebNFWcZNlbhcACZTRZAR4ATO3tsAy0PtMQ8cSH2lHsEXHH0YPcxQmQdB04t89/1O/w1cDnyilFU='

# headers -> "Authorization" : "Bearer token"
headers = {"Authorization":"Bearer odxu5LlWs+3Y2zWjVGboTsvjRZ6i9raKjs5YQXrYZRnSNtOqaLuZrB9EyBLQtZ2VV0gghTGCYob/LvwFFItjDX3srvljVFECebNFWcZNlbhcACZTRZAR4ATO3tsAy0PtMQ8cSH2lHsEXHH0YPcxQmQdB04t89/1O/w1cDnyilFU=" , "Content-Type":"application/json"}

# Step 1 執行以下內容至 ======== 區

# body = {
#     "size": {"width": 2500, "height": 1686},
#     "selected": "false",
#     "name": "Menu",
#     "chatBarText": "更多資訊",
#     "areas":[
#         {
#           "bounds": {"x": 61, "y": 51, "width": 1148, "height": 747},
#           "action": {"type": "message", "text": "找生鮮"}
#         },
#         {
#           "bounds": {"x": 1281, "y": 51, "width": 1148, "height": 747},
#           "action": {"type": "message", "text": "找私廚"}
#         },
#         {
#           "bounds": {"x": 61, "y": 868, "width": 1148, "height": 747},
#           "action": {"type": "message", "text": "找食譜"}
#         },
#         {
#           "bounds": {"x": 1281, "y": 868, "width": 1148, "height": 747},
#           "action": {"type": "message", "text": "每日驚喜"}
#         }
#     ]
#   }
#
# req = requests.request('POST', 'https://api.line.me/v2/bot/richmenu',
#                        headers=headers,data=json.dumps(body).encode('utf-8'))
#
# print(req.text) # 複製 request id
# {"richMenuId":"richmenu-2d0096c50bc07759277fc29aa3147068"}

# Step 1 執行至以上內容
# ===================

# Step 2 執行以下內容 comment Step 1

from linebot import (
    LineBotApi, WebhookHandler
)
# # =======================================================
line_bot_api = LineBotApi(token)
rich_menu_id = 'richmenu-2d0096c50bc07759277fc29aa3147068'
# # =======================================================
path = 'menu.png'

with open(path, 'rb') as f:
    line_bot_api.set_rich_menu_image(rich_menu_id, "image/png", f)
# # =======================================================
req = requests.request('POST', 'https://api.line.me/v2/bot/user/all/richmenu/'+rich_menu_id,
                       headers=headers)
print(req.text)


#
# rich_menu_list = line_bot_api.get_rich_menu_list()
#
#
# # # =======================================================
# # line_bot_api.delete_rich_menu(rich_menu_id)