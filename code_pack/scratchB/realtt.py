import json
# red: read clearly from image (Mon-Fri)
RED=[]
for h in range(7,12): RED+= [h*60+m for m in range(0,60,10)]
RED+= [12*60+m for m in range(0,60,5)]
RED+= [13*60+m for m in range(5,60,10)]
RED+= [14*60+m for m in (5,10,15,20,25,30,40,50)]
for h in (15,16,17): RED+= [h*60+m for m in range(0,60,10)]
RED+= [18*60+m for m in (0,10,20,30)]
# yellow: low-res image; 07-12, 15-18 clear; 13:xx and 14:xx uncertain
def yellow(s13=0,s14=0,y14=None):
    Y=[]
    for h in range(7,12): Y+= [h*60+m for m in range(5,60,10)]
    Y+= [12*60+m for m in range(5,60,5)]
    Y+= [13*60+m+s13 for m in range(0,60,10)]
    base14=(0,10,15,20,25,30,35,45,55) if y14 is None else y14
    Y+= [14*60+m+s14 for m in base14]
    for h in (15,16,17): Y+= [h*60+m for m in range(5,60,10)]
    Y+= [18*60+m for m in (5,15,25,35)]
    return Y
if __name__=='__main__':
    Y=yellow()
    print('red',len(RED),'yellow',len(Y),'total',len(RED)+len(Y))
    import collections
    def byh(L):
        c=collections.Counter(t//60 for t in L);return [c[h] for h in range(7,19)]
    print('red by hour 7..18',byh(RED));print('yel by hour',byh(Y))
    print('12:00-13:59: red',sum(1 for t in RED if 720<=t<840),'yel',sum(1 for t in Y if 720<=t<840))
    json.dump({'red':RED,'yellow':Y},open('tt/real_tt.json','w'))
