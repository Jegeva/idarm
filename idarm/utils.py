# copyright : jean-georges valle 2020
class utils:
    def __init__(self):
        pass
     
    def eprint(*args, **kwargs):
        print(*args, file=sys.stderr, **kwargs)

    def get_segsz_mask(sz):
        i=0
        while(sz):
            sz>>=1;
            i+=1
        # python and ~ sometimes...
        return ((0xffffffff>>i)<<i)
