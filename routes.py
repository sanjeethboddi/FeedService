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
def getFeedForUser(token:str, request:Request, response:Response, user_id:str):
    resp =  requests.post(request.app.auth_service+f"/verify/{token}")
    
    if  resp.status_code != 200 or str(resp.json()["username"]).lower() != user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    response =  request.app.database[DB].find({"_id": user_id})
    return response[0]["posts"]

@router.patch("/updateFeedDataForFollowers/{userID}/{postID}/{token}")
def updateFeedDataForFollowers(token:str, userID:str, postID:str, request: Request, response: Response):
    print("Updating feed for followers")
    resp =  requests.post(request.app.auth_service+f"/verify/{token}")
    userID = str(resp.json()["username"]).lower()
    if  resp.status_code != 200:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
    graph_response = requests.get(request.app.graph_service + f"/getFollowersList/{userID}")
    followers = graph_response.json()

    for follower in followers:
        print("Updating feed for follower: ", str(follower))
        request.app.database[DB].update_one({"_id": follower},{"$push": { "posts": { "$each": [postID], "$slice": 500, "$position": 0 }}}, upsert=True)
    # add post to user's feed
    request.app.database[DB].update_one({"_id": userID},{"$push": { "posts": { "$each": [postID], "$slice": 500, "$position": 0 }}}, upsert=True)

    

