from remote_embed import Embed; embed = Embed('0.0.0.0', 9999, this_coding='gb18030', debugger_coding='utf8')

a = 2

def func(x, y, z):
    print(a, x, y, z)
    embed()
    print(a, x, y, z)

func(1, 2, [3])