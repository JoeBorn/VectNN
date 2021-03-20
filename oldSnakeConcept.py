#mids_image = Image.new("L",(28,28)) 
#mids_image.putdata(midsImageList)

#print(midsList)
#mids_image.save('C:/Users/joebo_000/Downloads/VNN/4_9_mids.png')
#mids_image.show()

#returns a list of (segLength) length vector angles 
# + starting and ending point coordinates, and number of segments
#TODO: resolve conflict between one end and start with potentially 
#multiple segments

def getSnake(mids_image,image, segLength=1):
    #start at beginning of midsList 
    # (smallest x (smallest y within that if more than one x))
    #check x+1 and x+2
    #if no left, the mark as start and go right
    # if left, keep going until no more left (recursion base case)
    #if no right, mark end and return segment

    return snake,startPoint,endPoint,segments