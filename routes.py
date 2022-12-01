from fastapi import APIRouter, Body, Request, Response, HTTPException, status, File, UploadFile

from fastapi.encoders import jsonable_encoder
from typing import List

import uuid
from dotenv import dotenv_values
import os
import requests

config = dotenv_values(".env")

router = APIRouter()

DB = "feed"

@router.get("/getFeedForUser/{user_id}/{token}")
def getFeedForUser(token:str, request:Request):
    resp =  requests.post(request.app.auth_service+f"/verify/{token}")
    userID = str(resp.json()["username"]).lower()
    if  resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Unauthorized")
    response =  request.app.database[DB].find({"userID": userID})
    return [i for i in response]

@router.patch("/updateFeedDataForFollowers/{userID}/{token}")
def updateFeedDataForFollowers(token:str, userID:str, postID:str, request: Request):
    resp =  requests.post(request.app.auth_service+f"/verify/{token}")
    userID = str(resp.json()["username"]).lower()
    if  resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    followers = requests.get(request.app.graph_service + f"/getFollowersList/{userID}")

    for follower in followers:
        request.app.database[DB].update_one({"userID": follower},{"$push": { "posts": { "$each": [postID], "$slice": 500, "$position": 0 }}})

