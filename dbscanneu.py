import numpy as np
from PIL import Image


########################################
#
#  Distanzberechnung im L2 Raum
#
########################################

def getSimpleDistance(dimensions, dataValue, data, i_neu):
    dist_vector = np.zeros(dimensions) #erzeuge 1D-Array
    for j in range (0,dimensions): #berechne Distanzen
        dist_vector[j] = dataValue[j] - data[i_neu, j]
    
    dist_vector = np.power(dist_vector,2) #fuer Raum L2
    return np.sum(dist_vector)
    


###############################################
#
#   Kernobjekt prueft, ob besuchter Pixel an Position i,j in data (siehe Main-Funktion) ein Kernobjekt ist
#   cluster gibt zu pruefenden Cluster an
#   seeds sind alle zu pruefenden Pixel
#   seedCount ist die Position des letzten Nachbarn (der Array wird nicht dynamisch erweitert)
#
###############################################

def Kernobjekt (i, dataValue, cluster, seeds, seedCount):
    dataPoints = data.shape[0]
    dimensions = data.shape[1] - 1 #letzte Dimension ist Clusterindex, und demnach keine
    neighbours = 0 #gefundene nachbarn
    seedRelCount = 0 #neue zu besuchende Punkte
    #pruefe auf Kernobjekt (k Nachbarn in e anliegenden Pixeln)        
    for i_neu in range(0,dataPoints):        
        if (data[i_neu,dimensions] == cluster):#Pixel im selben cluster
            neighbours += 1
        if (data[i_neu,dimensions] > 1): #Pixel bereits zugeordnet und nicht Rauschen
            continue #Pixel muss nicht geprueft werden
        
        # Distanzberechnung
        dist = getSimpleDistance(dimensions, dataValue, data, i_neu) #Distanzberechnung im L2 Raum
        maxdist = pow(d,2) #Epsilon Umgebung in L2 Raum
        
        ###################
        #
        # Nachbar?
        #
        ###################     
        
        if (dist < maxdist): #Punkt ist benachbart
            if((i_neu == i)): #wir haben uns selbst gefunden
                continue
            neighbours += 1
            seeds[seedCount] = np.array([i_neu]) #merken fuer zu besuchend
            seedCount += 1
            seedRelCount += 1
    if (neighbours >= k): #Objekt ist Kernobjekt
        data[i,dimensions]=cluster #ordne Objekt Cluster zu
        seeds[0] = seedRelCount #speichere Anzahl neuer Punkte in 0. Zeile
        #print(i,"ist Kernobjekt mit ", neighbours, "Nachbarn")
        return seeds
    else:
        data[i,dimensions]=1 #Markiere Pixel als Rauschen
        seeds[0] = 0 #keine neuen Punkte
        #print(i,"ist kein Kernobjekt, nur", neighbours, "Nachbarn")
        return seeds 

###############################################
#
#   Bild umwandeln in Datenstrom
#   Datenstrom besteht aus Index und Dimensionen + Clusterindex
#
###############################################

def Picture2Data (img):
    x = img.shape[0]
    y = img.shape[1]
    resolution = x*y
    dimension =  img.shape[2]
    dataTemp = img.reshape(resolution, dimension)
    #Wert fuer Cluster einfuegen
    data = np.insert(dataTemp, dimension, 0, axis = 1) #Clusterindex zu Dimensionen hinzufuegen
    print(x*y, "Datenpunkte mit", dimension, "Dimensionen.")
    return data

###############################################
#
#   speichert Bild ab
#
###############################################
def save():
    data2Image() #zum einfachem Austauschen der save()-Funktion
    
def data2Image():
    x = img.shape[0]
    y = img.shape[1]
    dimension =  3 #Farbdimension muss drei sein
    tempData = np.delete(data,dimension,axis=1)
    newData = np.reshape(tempData, (x,y,dimension))
    clusterfarben = np.array([[0,0,0,0]]) #clusterfarben speichert alle Cluster mit entsprechender Farbe
    for i in range(0,x*y): #gehe durch alle Werte
            my_cluster = data[i,dimension]
            if (my_cluster>=2):
                #lese farbwert aus clusterfarben
                farbe = clusterfarben[(clusterfarben[:,dimension]==my_cluster)] 
                if (farbe.shape[0]==0): #wenn noch keine Farbe zugewiesen
                    clusterfarben = np.vstack((clusterfarben,data[i])) #fuege aktuelle Farbe zum Cluster hinzu
                    continue 
                rot = (farbe[0,0])%256
                gruen = (farbe[0,1])%256
                blau = (farbe[0,2])%256
                
                xi = int(i/y) 
                yi = i%y
                
                newData[xi,yi] = [rot,gruen,blau]
    out = Image.fromarray(newData, 'RGB')
    out.save(savePicture)
    #out.show()

###############################################
#
#   Eigentlicher Algorithmus, der gefundene Kernobjekte zu Clustern zusammenfasst
#
###############################################

def DBScan(data):
    cluster = 2 #1=Rauschen => erster cluster = 2
    dataPoints = data.shape[0]
    dimensions = data.shape[1] - 1 #letzte Dimension gibt Cluster an, und ist demnach keine
    seeds = np.zeros((dataPoints,1))
    clusterobj = seeds
    for i_abs in range(0,dataPoints):
        i = i_abs #i,j wird zwischengespeichert, damit nachher Schleife mit richtigen i_abs weitermacht
        old_s = 0
        seedCount = 1
        if (data[i,dimensions] >= 2): #Cluster zugeordnet, nicht rauschen
            continue            #nicht weiter suchen
        is_Kernobjekt = False
        while(seedCount > 0): #nicht alle Nachbarn abgearbeitet
            dataValue = data[i,0:(dimensions)]
            clusterobj = Kernobjekt(i, dataValue, cluster, seeds, seedCount)
            seedRel = int(clusterobj[0])
            if(seedRel != 0): #wenn neue Nachbarn vorhanden)
                for z in range (seedCount,seedCount+seedRel): #gehe durch alle Nachbarn
                    i_z = int(clusterobj[z])
                    data[i_z,dimensions] = cluster #Ordne alle Nachbarn dem Cluster zu
                
                seedCount += seedRel #lese SeedCount aus clusterobj            
                seeds = clusterobj
                is_Kernobjekt = True
            seedCount -= 1 #'entferne' letzten Pixel
            s = seedCount
            if(s>1):
                i = int(seeds[seedCount,0]) #lese letzten Pixel aus to_visit
              
            if(s>old_s): #Ausgabe, wenn sich Anzahl der neuen Nachbarn in groesseren Massstab aendert
                print(s,"Punkte zu verarbeiten in Cluster #",cluster - 1)
                save()
                old_s = s
            elif (s<old_s-100): #Ausgabe, wenn Anzahl der Nachbarn verringert wird
                print("Nur noch", s,"Punkte zu verarbeiten in Cluster #",cluster - 1)
                old_s = s
        if (is_Kernobjekt): #Cluster gefunden
            cluster += 1
            save()
            print("Cluster",cluster-2,"fertiggestellt.")
        else: #Wenn Punkt kein Kernobjekt und keinem Cluster angehoert
            data[i,dimensions] = 1  #Punkt als Rauschen markieren

###############################################
#
#   User Input
#
###############################################

openPicture = input("Bitte geben Sie den Pfad zur Bilddatei an: ")
k =int(input("Bitte geben Sie die Anzahl der Nachbarn (MinPoints) an: "))
e = float(input("Bitte geben Sie die Groesse der Epsilon-Umgebung an (zwischen 0.0 und 1.0): "))
savePicture = 'Bild.png' #Output fuer data2Image()

d = e*255   #Farb-Distanz


#Bild einlesen
img = Image.open(openPicture)
img = np.array(img)
data = Picture2Data(img)
DBScan(data)

                


        
                
                
                
