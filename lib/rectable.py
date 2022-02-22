rectable = [["stuff","pear","apple","opportunity","octopus","leander","coca-cola","dreamy","ninedread","polite"],
             ["motorcycle","sodium","memory","pink","octopus","contemporary","tent","location","skeleton","lobby"],
             ["national","forest","fountain","ananas","ignorance","sorrow","living","financial","burial","damage"],
             ["perfume","wash","hell","calamity","recall","petunia","serpent","furniture","mesopotamia","fahrenheit"],
             ["stimulation","concern","eggwhite","apocalypse","quake","wanderer","noseless","dullahan","farewell","stonehenge"],
             ["urine","mouse","pepper","laundry","potter","blacksmith","blonde","foamy","skyless","miniature"],
             ["poltergeist","sandwich","humanity","island","cigarthief","unrealistic","expectations","unhealthy","roguelike","pillars"],
             ["rolex","wearable","icecube","bongwater","fiery","mammoth","folktale","buckethead","veterans","bearhug"],
             ["lowlife","palate","mouthwash","sugarcane","barrack","hardship","friendship","treadmill","officers","listable"],
             ["valkyrie","shrinemaid","killswitch","mannequin","titanic","bulldog","catdog","fairies","substance","dust"]]

def encode(recovery):
    if not recovery:
        return None
    phrase = [rectable[int(recovery[0])][int(recovery[1])],rectable[int(recovery[2])][int(recovery[3])],rectable[int(recovery[4])][int(recovery[5])],
            rectable[int(recovery[5])][int(recovery[4])],rectable[int(recovery[3])][int(recovery[2])],rectable[int(recovery[1])][int(recovery[0])]]
    return phrase

def decode(phrase):
    if not phrase:
        return None
    recover=""
    for x in phrase:
        for y in range(len(rectable)):
            if x in rectable[y]:
                recover=recover+str(y)     
                recover=recover+str(rectable[y].index(x))
    recover=recover[:-6]
    return recover