from remote_embed import Embed; embed = Embed(popup='nc.exe')

a = 2

def func(x, y, z):
    print(a, x, y, z)
    embed()
    print(a, x, y, z)

func(1, 2, [3])