#!/usr/bin/python
import sys, getopt, os, subprocess

global sourcefolder
global destfolder
global finaldicttomove
global dicttomove
global listtomove
global filesplitter

def init():
    global filesplitter
    global  dicttomove
    global  listtomove
    global finaldicttomove
    filesplitter = '/'
    finaldicttomove = {}
    dicttomove = {}
    listtomove = []


def movefiles(dict):
    for key in dict:
        listcommand = ["rsync","-arv",key, dict[key]]
        try:
            subprocess.check_call(listcommand)
        except subprocess.CalledProcessError:
            print("There was a problem moving this file skipping: from: "+key+" to: "+dict[key])
            continue
        print("Confirming file is at new location...: "+dict[key])
        if (os.path.isfile(dict[key])):
            isitfile = key
            listfile = isitfile.split(filesplitter)
            lastfileorfolder = listfile[len(listfile)-2]
            print("lastfileorfolder: "+lastfileorfolder)
            listsrcfolder = sourcefolder.split(filesplitter)
            srclast = listsrcfolder[len(listsrcfolder)-1]        
            print("srclast: "+srclast)
            if(srclast != lastfileorfolder):
               dumdelpath = os.path.join(*listfile[:len(listfile)-1])
               delpath = filesplitter+dumdelpath
               print("deleting this folder and its contents: "+delpath) 
               listdelcommand = ["rm","-rf",delpath]
               try:
                   subprocess.check_call(listdelcommand)               
               except subprocess.CalledProcessError:
                   print("folder did not delete continuing to next")
                   continue
            else:
                print("delete the file: "+str(key))
                listdelfile = ["rm","-f",key]
                try:
                    subprocess.check_call(listdelfile)
                except subprocess.CalledProcessError:
                    print("file did not delete continuing to next")
                    continue
        
        else:
            print("Deleting original file after succesfully moved to destination: "+lastfileorfolder)
            continue


def buildsrcfiles():
    """
    Function: takes src directory and builds a dict of all files of type .avi, .mp4, etc
    dicttomove is key: src file path val: dest file path
    """
    global dicttomove, listtomove
    global sourcefolder
    try:
        for fname in os.listdir(sourcefolder):
            if not fname.startswith('.'):
                sourcepath = os.path.join(sourcefolder, fname)
                dicttomove[sourcepath] = ""
                listtomove.append(sourcepath)
                print("adding: "+sourcepath)
    except NameError:
        print('Folder NO GOOD!! USE ABSOLUTE PATHS!: mediamover.py -s <sourcefolder> -d <destfolder>')
        sys.exit(2)


def addName(src):
    """
    Display old name Prompt User to input new name
    :param src: the source directory path
    :return: Break out of adding names: True or False
    """
    global dicttomove
    global finaldicttomove
    global listtomove
    global filesplitter
    listp = src.split(filesplitter)
    oldName = listp[len(listp)-1]

    #request a name change
    extlist = oldName.split('.')
    ext = extlist[len(extlist)-1]
    print("type 'x' to skip moving this file")
    print("type 'xall' to skip all future files and move whatever you renamed so far")
    print("type 'q' to quit and move nothing")
    print("NO SPACES ALLOWED IN NAME PROVIDED")
    finalName = input("curr name: "+oldName+"  <typeName>."+ext+" :")
    if(finalName == 'x'):
        i = -1
        for p in range(0, len(listtomove)-1):
            if(listtomove[p] == src):
                i = p
        listtomove.pop(i)
    elif(finalName == 'q'):
        sys.exit(2)
    elif(finalName == "xall"):
        print("Skipping the rest of the source files ....")
        return True
    else:
        finalName = finalName+'.'+ext
        i = -1
        for p in range(0, len(listtomove)-1):
            if(listtomove[p] == src):
                i = p
        finaldicttomove[src] = os.path.join(destfolder,finalName)
    return False

def inputloop():
    """
    Function: takes each key from dicttomove and asks user to input final file name with extension and that is added to the value in the dicttomove.
    All destination files are <destinationfolder>/filename.ext no folders are allowed in the destination
    """
    global destfolder
    i = 0
    done = False
    while(not done and (i < len(listtomove)-1)):
        if os.path.isdir(listtomove[i]):
             for fname in os.listdir(listtomove[i]):
                if not os.path.isdir(os.path.join(listtomove[i],fname)) and (fname.endswith('.avi') or fname.endswith('.mpg') or fname.endswith('.vob') or fname.endswith('.mp4') or fname.endswith('.mov') or fname.endswith('.mkv')):
                    if(addName(os.path.join(listtomove[i], fname))):
                        done = True
                        break
        elif listtomove[i].endswith('.avi') or listtomove[i].endswith('.mpg') or listtomove[i].endswith('.vob') or listtomove[i].endswith('.mp4') or listtomove[i].endswith('.mov') or listtomove[i].endswith('.mkv'):
            if(addName(listtomove[i])):
                done = True
                break
        i += 1
    for k in finaldicttomove:
        print("file: "+k+" is moving to: "+finaldicttomove[k])

    while(True):
        confirm = input("hit 'y' to continue or 'q' to quit and do nothing: ")
        if(confirm == 'y'):
            movefiles(finaldicttomove)
            break
        elif(confirm == 'q'):
            sys.exit(2)

def main(argv):
    global sourcefolder
    global destfolder
    try:
        opts, args = getopt.getopt(argv, "hs:d:",["source=","dest="])
    except getopt.GetoptError:
        print('USE FULLPATHS!: mediamover.py -s <sourcefolder> -d <destfolder>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('media mover: uses rsync to move movies from the sourcefolder by looking thru all movies up to two directories deep')
            print('use absolute paths only for your source and destination folders')
            print('must use python3')
            print('mediamover.py -s <sourcefolder> -d <destfolder>')
            sys.exit(2)
        elif opt in ('-s'):
            sourcefolder = arg
        elif opt in ('-d'):
            destfolder = arg

    print("source folder: "+sourcefolder)
    print("destination folder: "+destfolder)
    init()
    buildsrcfiles()
    inputloop()

if __name__ == "__main__":
    main(sys.argv[1:])
