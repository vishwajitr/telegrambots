scp -r crawlernew/ offersapp6:/home/ubuntu/socialshare
nohup python3 telegrambot2.py &

Similar Bots who pick offers a different sources
bot1-t2t.py
bot2-t2t.py
bot3-t2t.py

Telegram to Intagram
telegramToInsta_profile

Telegram to Facebook
bot4-t2fb.py


https://facebookautoposter.netlify.app/
https://developers.facebook.com/tools/explorer?method=POST&path=105896528030351%2Ffeed&version=v17.0&title=abc&message=lmn

https://developers.facebook.com/docs/graph-api/reference/v2.12/post

token extender
https://developers.facebook.com/tools/debug/accesstoken/


pipreqs
pip install -r requirements.txt
nohup python3 allbots.py &

ps aux | grep allbots.py
kill <processid>


26 Jan
allbots 1.2
changes
1. keeps history of post and repetition avoids
2. own url shortner
3. test parameter inttoduce to test immediately


ps aux | grep url_shortner.py
nohup python3 url_shortner.py &