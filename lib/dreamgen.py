import random

def nightmgen():
    verbs=["sense","open","see","hear","catch","realize","notice","spot","perceive","turn to","arrive at"]
    nverb=random.choice(verbs)
    adjs=["horrible","bloody","colourful","gruesome","withered","loud","obscene","ethereal","silent","shadowy"]
    nadj=random.choice(adjs)
    nouns=["scream","figure","finger","insects","eyesocket","machine","scene","room","painting","sky","building"]
    nnoun=random.choice(nouns)
    places=["under the ground","in a forest","all around","in the back of your mind","above you","in front of your face","next to you","in the distance","in a corner","under you"]
    nplace=random.choice(places)
    # You VERB a ADJECTIVE NOUN PLACE.
    nightmaretext="You {0} some {1} {2} {3}.".format(nverb,nadj,nnoun,nplace)
    return nightmaretext