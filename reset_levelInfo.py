import pickle, os

info = {"tutorial": True,
        "Easy": [True] + [False for f in os.listdir("levels/Easy")[1:]],
        "Medium": [False for f in os.listdir("levels/Medium")],
        "Advanced": [False for f in os.listdir("levels/Advanced")],
        "Hard": [False for f in os.listdir("levels/Hard")],
        "Expert": [False for f in os.listdir("levels/Expert")]}


with open("levelInfo.pkl", "wb") as file:
    pickle.dump(info, file, pickle.HIGHEST_PROTOCOL)
