#CATAN with efficient random generator
from numpy import shape as np_shape
from numpy import zeros as np_zeros
from numpy import ones as np_ones
from numpy import isin as np_isin
from numpy import array as np_array
from numpy import arange as np_arange
from cv2 import imwrite as cv2_imwrite 
from cv2 import imshow as cv2_imshow
from cv2 import putText as cv2_putText
from cv2 import circle as cv2_circle
from cv2 import VideoWriter as cv2_VideoWriter
from cv2 import line as cv2_line
from cv2 import FONT_HERSHEY_SIMPLEX as cv2_FONT_HERSHEY_SIMPLEX
from cv2 import waitKey as cv2_waitKey
from cv2 import destroyAllWindows as cv2_destroyAllWindows
from random import sample as sample
from random import randint as randint
from math import sin as sin
from math import cos as cos
from math import sqrt as sqrt
from math import pi as pi
from time import time
from os import path as os_path 
from os import makedirs as os_makedirs 

def polygon(image,c,side,edges,rotate,fill,color=[50,50,50]):
    """
    Recursive Algorithm
    Input: (image,center of polygon, length of each side, number of edges, color of edges,
            rotation of object as a factor of alpha, fill or empty inside, color of filling)
            
    Output: image including the filled polygon
    """
    def poly_skin(image,c,side,edges,color,rotate):
        """
        Input: (image,center of polygon, length of each side, number of edges, color of edges,
            rotation of object as a factor of alpha)
           
        Output: image including the polygon
        """
        alpha = 2.0*pi/edges
        beta = alpha*float(rotate)
        r = side/(2.0*sin(alpha/2.0))
        nodes = np_zeros((edges,2))
        for i in xrange(edges):
            nodes[i,:]=np_array([int(c[0]+r*sin(i*alpha+alpha/2.0+beta)+0.5),int(c[1]+r*cos(i*alpha+alpha/2.0+beta)+0.5)])
        nodes = nodes.astype('uint32')
        #for i in xrange(edges):
        #    cv2_circle(image,(nodes[i,0],nodes[i,1]),1,color1,1)
        for i in xrange(edges):
            cv2_line(image,(nodes[edges-i-1,0],nodes[edges-i-1,1]),(nodes[edges-i-2,0],nodes[edges-i-2,1]),color,2)
        return image,side
    if side < fill or fill < 0:
        image,small_side = poly_skin(image,c,side,edges,color,rotate)
        return image,small_side
    else:
        image,small_side = poly_skin(image,c,side,edges,color,rotate)
        return polygon(image,c,side-2,edges,rotate,fill,color)
    
def centers(c,side,edges,catan):
    """
    Input: (center,length of the inner side, number of edges, type of CATAN)
    Output: numpy array of "many" points
    """
    alpha = 2.0*pi/edges

    if catan == "CATAN_ext":
        i_y = int(1*small_side/(3*sqrt(3)-1.0)+0.5)*1.3
        i_x = int(i_y*cos(alpha)+0.5)*2.3
        #i_y = int(1*small_side/(3*sqrt(3)-1.0)+0.5)*1.4
        #i_x = int(i_y*cos(alpha)+0.5)*2.4
        many,j,j_x = 30,7,3
    else: 
        i_y = int(1.5*small_side/(3*sqrt(3)-1.0)+0.5)*1.05
        i_x = int(i_y*cos(alpha)+0.5)*2.3
        many,j,j_x = 19,5,2
    
    centers = np_zeros((many,2))
    raw_centers = np_zeros((many,3))
    k=0
    for j_y in np_arange(j)-j_x:
        if j==5:
            j+=1
        for j_j in np_arange(j-abs(j_y)-1):
            g = j-abs(j_y)-1
            f = 0.5*(g%2==0)
            j_k = j_j-g/2+f
            #print j-abs(j_y)-1,(j_j,j_y),j_k
            centers[k,:] = [int(c[0]+i_x*j_k+0.5),int(c[1]+i_y*j_y+0.5)]
            raw_centers[k,:] = [j-abs(j_y)-1,j_j,j_y]
            k+=1    
    #print centers
    return centers,raw_centers
    
def color_number(points,catan,r_c):
    """
    Input: (center points of polygon tiles in pixels, CATAN version, center points of polygon tiles in reletive pose)
    Output: A numpy matrix including random colors, random positions and random assigned numbers at the center of tiles
            "Red numbers are not adjacet"
    """
    def random_info(info2,deny,points_new,k,red):
        i=0
        final_points=np_ones((np_shape(info2)[0],5))*(-1)
        num = []
        while i < red:
            if i == 0:
                num.append(int(points_new[0,-1]))
            else: 
                while True:
                    r = randint(0,np_shape(info2)[0]-1)
                    s=0
                    for j in xrange(i):
                        s += sum(np_isin(deny[num[j]+1],r+1))*1
                    if sum(np_isin(num,r)*1)>0 or s!=0:
                        continue
                    else:
                        p = int(points_new[np_isin(points_new[:,-1],r),-1][0])
                        break
                num.append(p)             
            i+=1
        pn_68 = points_new[np_isin(points_new[:,-1],num),:]

        final_points[0:len(num),0] = pn_68[:,0]
        final_points[0:len(num),1] = pn_68[:,1]
        final_points[0:len(num),2] = info2[k:k+len(num),0]
        final_points[0:len(num),3] = info2[k:k+len(num),1]
        final_points[0:len(num),4] = pn_68[:,-1]
        f = list(np_isin(final_points[:,3],[6,8])==False)
        pn = points_new[np_isin(points_new[:,-1],num)==False]
        final_points[len(num):,0:2] = pn[:,0:2]
        final_points[len(num):,4] = pn[:,-1]
        final_points[len(num):,2:4] = info2[np_isin(info2[:,1],[6,8])==False,:]
        return final_points
        
        
    color=[150235235,30110240,190160080,20110180,50250240,80255080]
    if catan == 'CATAN':
        color_num=[1,3,3,4,4,4]
        number_num = [1,1,2,2,2,2,2,2,2,2,1]
        k=1#number of desert(s)
        red = 4 #number of red numbers
        deny = {1:[1,2,4,5],2:[1,2,3,5,6],3:[2,3,6,7],4:[1,4,5,8,9],5:[1,2,4,5,6,9,10],6:[2,3,5,6,7,10,11],
           7:[3,6,7,11,12],8:[4,8,9,13],9:[4,5,8,9,10,13,14],10:[5,6,9,10,11,14,15],11:[6,7,10,11,12,15,16],
           12:[7,11,12,16],13:[8,9,13,14,17],14:[9,10,13,14,15,17,18],15:[10,11,14,15,16,18,19],
           16:[11,12,15,16,19],17:[13,14,17,18],18:[14,15,17,18,19],19:[15,16,18,19]}
    else:
        
        deny = {1:[1,2,4,5],2:[1,2,3,5,6],3:[2,3,6,7],4:[1,4,5,8,9],5:[1,2,4,5,6,9,10],6:[2,3,5,6,7,10,11],
           7:[3,6,7,11,12],8:[4,8,9,13,14],9:[4,5,8,9,10,14,15],10:[5,6,9,10,11,15,16],11:[6,7,10,11,12,16,17],
           12:[7,11,12,17,18],13:[8,13,14,19],14:[8,9,13,14,15,19,20],15:[9,10,14,15,16,20,21],
           16:[10,11,15,16,17,21,22],17:[11,12,16,17,18,22,23],18:[12,17,18,23],19:[13,14,19,20,24],
               20:[14,15,19,20,21,24,25],21:[15,16,20,21,22,25,26],22:[16,17,21,22,23,26,27],
               23:[17,18,22,23,27],24:[19,20,24,25,28],25:[20,21,24,25,26,28,29],26:[21,22,25,26,27,29,30],
               27:[22,23,26,27,30],28:[24,25,28,29],29:[25,26,28,29,30],30:[26,27,29,30]}
        color_num=[2,5,5,6,6,6]
        number_num = [2,2,3,3,3,3,3,3,3,3,2]
        red = 6 #number of red numbers
        k=2#number of desert(s)
    colors = []   
    for i in xrange(len(color)):
        for j in xrange(color_num[i]):
             colors.append(color[i])
                
    number=[7,2,3,4,5,6,8,9,10,11,12]
    numbers = []
    for i in xrange(len(number)):
        for j in xrange(number_num[i]):
            numbers.append(number[i])
    
    info = np_zeros((len(numbers),2))
    info[0:k,0]=colors[:k]
    info[0:k,1]=numbers[:k]
    info[k:,0]=sample(colors[k:],len(colors[k:]))
    info[k:,1]=sample(numbers[k:],len(colors[k:]))
    p=range(len(colors))
    p=sample(p,len(colors))
    points_new = np_zeros((len(colors),6))
    points_new[:,:2]=points
    points_new[:,2:-1]=r_c
    points_new[:,-1]= range(len(colors))
    points_new = points_new[p,:]
    find_68 = np_isin(info[:,1],[7,6,8])
    info2=info.copy()
    info2[:red+k,:]=info[find_68,:]
    info2[red+k:]=info[(1-find_68)==1,:]
    final_points = random_info(info2,deny,points_new,k,red)
    final_points=final_points.astype('uint32')
    return final_points[:,:-1]
#color_number2 eplaced color_number for its higher efficiency
def color_number2(p,catan,r_c):
    """
    Input: (center points of polygon tiles in pixels, CATAN version, center points of polygon tiles in reletive pose(not used))
    Output: A numpy matrix including random colors, random positions and random assigned numbers at the center of tiles
            "Red numbers are not adjacet"
    """
    color=[150235235,30110240,190160080,20110180,50250240,80255080]
    if catan == "CATAN":
        length = 19
        numbers = [6,6,8,8,7,2,3,3,4,4,5,5,9,9,10,10,11,11,12]
        l = 4;ll=1
        col = [1,3,3,4,4,4]
        deny = {1:[1,2,4,5],2:[1,2,3,5,6],3:[2,3,6,7],4:[1,4,5,8,9],5:[1,2,4,5,6,9,10],6:[2,3,5,6,7,10,11],
       7:[3,6,7,11,12],8:[4,8,9,13],9:[4,5,8,9,10,13,14],10:[5,6,9,10,11,14,15],11:[6,7,10,11,12,15,16],
       12:[7,11,12,16],13:[8,9,13,14,17],14:[9,10,13,14,15,17,18],15:[10,11,14,15,16,18,19],
       16:[11,12,15,16,19],17:[13,14,17,18],18:[14,15,17,18,19],19:[15,16,18,19]}
    else:
        length = 30
        numbers = [6,6,6,8,8,8,7,7,2,2,3,3,3,4,4,4,5,5,5,9,9,9,10,10,10,11,11,11,12,12]
        l = 6;ll=2
        col = [2,5,5,6,6,6]
        deny = {1:[1,2,4,5],2:[1,2,3,5,6],3:[2,3,6,7],4:[1,4,5,8,9],5:[1,2,4,5,6,9,10],6:[2,3,5,6,7,10,11],
           7:[3,6,7,11,12],8:[4,8,9,13,14],9:[4,5,8,9,10,14,15],10:[5,6,9,10,11,15,16],11:[6,7,10,11,12,16,17],
           12:[7,11,12,17,18],13:[8,13,14,19],14:[8,9,13,14,15,19,20],15:[9,10,14,15,16,20,21],
           16:[10,11,15,16,17,21,22],17:[11,12,16,17,18,22,23],18:[12,17,18,23],19:[13,14,19,20,24],
               20:[14,15,19,20,21,24,25],21:[15,16,20,21,22,25,26],22:[16,17,21,22,23,26,27],
               23:[17,18,22,23,27],24:[19,20,24,25,28],25:[20,21,24,25,26,28,29],26:[21,22,25,26,27,29,30],
               27:[22,23,26,27,30],28:[24,25,28,29],29:[25,26,28,29,30],30:[26,27,29,30]}
    num = range(length)
    num2 = list(num)
    points = np_zeros((len(num),2))
    for i in xrange(l):
        j = sample(num,1)[0]
        points[i+ll,:]=[numbers[i],j+1]
        k = deny[j+1]
        for ik in k:
            try:
                num.remove(ik-1)
            except:
                pass
        num2.remove(j)
            
    for i in xrange(ll):
        j = sample(num2,1)[0]
        points[i,:] = [7,j+1]
        num2.remove(j)

    points[ll+l:,0] = sample(numbers[ll+l:],len(numbers[ll+l:]))
    points[ll+l:,1] = sample(num2,len(num2))
    points[ll+l:,1] +=1
    points[:,1] -=1
    points = points.astype('uint8')
    colors = []
    for i in xrange(len(color)):
        for j in xrange(col[i]):
            colors.append(color[i])
    final_points = np_zeros((len(colors),4))
    final_points[:,:2] = p[points[:,1],:]
    final_points[:,3] = points[:,0]
    final_points[:ll,2] = colors[:ll]
    final_points[ll:,2] = sample(colors[ll:],len(colors[ll:]))
    final_points = final_points.astype('uint32')
    return final_points

    
def folder(directory):
    """
    Input: Directory to make folder
    Output: Folder created if already doesn't exist
    """
    try:
        if not os_path.exists(directory):
            os_makedirs(directory)
    except OSError:
        print "Error Creating "+directory
    return 0  
#Two CATAN versions are supported:
catan = ['CATAN','CATAN_ext'] 
#---------------------------------
#Choose the required version here:
CATAN = catan[0]
#---------------------------------
if CATAN == 'CATAN':
    direct = ""
else:
    direct = "_extension"
#Dimension of the pictures
dim = 700
dim_x = int(dim*1.3)
#Uncomment the line below and others containing "out" if you need to save results as a video
#out = cv2_VideoWriter('CATAN.avi',1, 10, (dim_x,dim))
side = 11*dim/21
edges = 6
name = 0
#Choose the directory to save picture of samples
D_main = "\Users\Hesam\Project Tests\CATAN\CATAN-5000K"
n_k = ""
#t=[]
#Decide the number of samples you want to create here
numbers_to_generate = 500000
while name < numbers_to_generate:
    #t1 = time()
    name+=1
    ground = np_ones((dim,dim_x,3))*255
    ground = ground.astype('uint8')
    c = [int(dim_x/2.0+0.5+side/11.0),int(dim/2.0+0.5)]
    ground,small_side = polygon(ground,c,side,edges,0,int(side*0.67+0.5),color=[250,80,30])
    ground,ss = polygon(ground,c,small_side,edges,0,0,color=[160,200,200])
    #print side,small_side
    points,r_c = centers(c,small_side*2,edges,CATAN)
    points = points.astype('uint16')
    #data = color_number(points,CATAN,r_c)
    data = color_number2(points,CATAN,r_c)

    if catan[0]==CATAN:
        i_y = 55
    elif catan[1]==CATAN:
        i_y = 44
    for p in xrange(np_shape(data)[0]):
        if data[p,3] >= 10:
            radius = 15
        else: 
            radius = 8
        col = [int((data[p,2]/1000000)%1000),int((data[p,2]/1000)%1000),int(data[p,2]%1000)]
        if data[p,3] != 7:
            factor = 0.3
        else:
            factor = 0
        ground,small_side = polygon(ground,data[p,:2],i_y,edges,1/2.0,int(i_y*factor+0.5),color=col)
        if data[p,3] != 7:
            cv2_circle(ground,(data[p,0],data[p,1]),7,(255,215,255),14)
            if data[p,3] ==8 or data[p,3] == 6:
                color = [0,0,200]
            else:
                color = [50,50,50]
            cv2_putText(ground,str(data[p,3]),(data[p,0]-radius,data[p,1]+7),cv2_FONT_HERSHEY_SIMPLEX,0.7,color, 2)
        cv2_putText(ground,str("#"+str(name)),(10,int(dim-30)),cv2_FONT_HERSHEY_SIMPLEX,0.7,[0,0,0], 1)
        cv2_putText(ground,str(6),(int(dim_x/2-4.5*side/11+30+0.5),int(55+side/20+0.5)),cv2_FONT_HERSHEY_SIMPLEX,0.7,[250,250,250], 2)
        cv2_putText(ground,str(6),(int(dim_x/2-4.5*side/11+0.5),int(80+side/20+0.5)),cv2_FONT_HERSHEY_SIMPLEX,0.7,[250,250,250], 2)
        cv2_putText(ground,str(1),(int(dim_x/2-4.5*side/11+side*0.93-30),int(55+side/20+0.5)),cv2_FONT_HERSHEY_SIMPLEX,0.7,[250,250,250], 2)
        cv2_putText(ground,str(1),(int(dim_x/2-4.5*side/11+side*0.93),int(80+side/20+0.5)),cv2_FONT_HERSHEY_SIMPLEX,0.7,[250,250,250], 2)
        #color=[150235235,30110240,190160080,20110180,50250240,80255080]
        cv2_circle(ground,(15,30),5,(150,235,235),9)
        cv2_putText(ground,"Desert",(30,37),cv2_FONT_HERSHEY_SIMPLEX,0.7,[0,0,0], 2)
        cv2_circle(ground,(15,60),5,(30,110,240),9)
        cv2_putText(ground,"Hill",(30,67),cv2_FONT_HERSHEY_SIMPLEX,0.7,[0,0,0], 2)
        cv2_circle(ground,(15,90),5,(190,160,80),9)
        cv2_putText(ground,"Mountain",(30,97),cv2_FONT_HERSHEY_SIMPLEX,0.7,[0,0,0], 2)
        cv2_circle(ground,(15,120),5,(20,110,180),9)
        cv2_putText(ground,"Forrest",(30,127),cv2_FONT_HERSHEY_SIMPLEX,0.7,[0,0,0], 2)
        cv2_circle(ground,(15,150),5,(50,250,240),9)
        cv2_putText(ground,"Field",(30,157),cv2_FONT_HERSHEY_SIMPLEX,0.7,[0,0,0], 2)
        cv2_circle(ground,(15,180),5,(80,255,80),9)
        cv2_putText(ground,"Pasture",(30,187),cv2_FONT_HERSHEY_SIMPLEX,0.7,[0,0,0], 2)
    if name%100==0:
        cv2_imshow('CATAN',ground)
    if name%100000 ==1:
        d_sub = D_main+"\\"+str((name/100000)*100)+str(n_k)+'-'+str((1+name/100000)*100)+'K'
        #folder(d_sub)
    if name%10000 ==1:
        d_sub_1 = d_sub+"\\"+str((name/10000)*10)+str(n_k)+'-'+str((1+name/10000)*10)+'K'
        #folder(d_sub_1)
    if name%1000 ==1:    
        d_sub_2 = d_sub_1+"\\"+str(name/1000)+str(n_k)+'-'+str(1+name/1000)+'K'+direct
        n_k = "K"
        folder(d_sub_2)
    cv2_imwrite(os_path.join(d_sub_2,CATAN+'_'+str(name)+'.PNG'), ground)
    #out.write(ground)
    key = cv2_waitKey(1) & 0xFF
    if key == 27:
        break
    elif key == ord('p'):
        k = cv2_waitKey(0) & 0xFF
        if k == 27:
            break
    
    #t.append(time()-t1)
#print sum(t)/len(t)
cv2_destroyAllWindows()
#out.release()
