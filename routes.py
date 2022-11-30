from fastapi import APIRouter, Body, Request, Response, HTTPException, status, File, UploadFile

from fastapi.encoders import jsonable_encoder
from typing import List

import uuid
from dotenv import dotenv_values
import os
import requests

config = dotenv_values(".env")


router = APIRouter()

DB = "posts"
IMAGE_FOLDER = config["IMAGE_DIR"]
# GRAPH_SERVICE_URL = config["GRAPH_SERVICE_URL"]

@router.get("/getFeedForUser")
def getFeedForUser(request:Request):
    # dummy user ID
    userID = "sanjeethboddi"
    response =  request.app.database[DB].find({"userID": userID})
    return [i for i in response]

@router.patch("/updateFeedDataForFollowers/")
def updateFeedDataForFollowers(postID:str, request: Request):
    # dummy user ID
    userID = "sanjeethboddi"
    followers = requests.get(GRAPH_SERVICE_URL + f"/getFollowersList/{userID}")

    for follower in followers:
        request.app.database[DB].update_one({"userID": follower},{"$push": { "posts": { "$each": [postID], "$slice": 500, "$position": 0 }}})

