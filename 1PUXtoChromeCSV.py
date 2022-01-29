import json, csv, sys, getopt
from zipfile import ZipFile

class line:
    def __init__(self, name, url, username, password):
        self.name = name
        self.url = url
        self.username = username
        self.password = password
    def __str__(self):
        return 'name:%s, url:%s, username:%s, password:%s' % (self.name, self.url, self.username, self.password)

def readFile(ifile):
    with ZipFile(ifile) as file:
        with file.open("export.data") as dfile:
            json_file = dfile.read()
    return readJSON(json_file)

def readJSON(file_data: str):
    data = json.loads(file_data)

    list = []

    accountData = data["accounts"]
    for a in accountData:
        vaultData = a["vaults"]

        for d in vaultData:
            items = d["items"]
            
            for ic in items:
                username = ""
                password = ""
                url = ""
                title = None
                
                i = ic["item"]
                overview = i["overview"]
                
                type = ''
                category = str(i["categoryUuid"])

                match category:
                    case "005":
                        type = "password"
                    case "001":
                        type = "login"
                    case _:
                        type = "other"

                if type == "password":
                    details = i["details"]
                    password = details["password"]

                    title = overview["title"]
                    url = overview["url"]
                elif type == "login":
                    title = overview["title"]
                    url = overview["url"]

                    details = i["details"]
                    loginfields = details["loginFields"]
                    
                    for f in loginfields:
                        if "designation" in f:
                            if f["designation"] == "username":
                                username = f["value"]
                            elif f["designation"] == "password":
                                password = f["value"]

                if title != None:
                    list.append(line(title, url, username, password))
    
    return list

def writeCSV(lst, file):
    out_file = open(file, "w", newline='')
    csv_writer = csv.writer(out_file)
    count = 0

    for line in lst:
        if count == 0:
            header = line.__dict__.keys()
            csv_writer.writerow(header)
        csv_writer.writerow(line.__dict__.values())
        count += 1
    
    out_file.close()

    return count


def main(argv):
    inputfile = ''
    outputfile = ''
    verbose = False

    try:
        acount = len(argv)
        if acount < 4:
            raise getopt.GetoptError("invalid arguments")
        opts, args = getopt.getopt(argv, "i:o:v", ["ifile", "ofile", "verbose"])
    except getopt.GetoptError:
        print("1PUXtoChromeCSV -i <inputfile> -o <outputfile> [-v]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-v", "--verbose"):
            verbose = True
    
    if verbose == True:
        print("Reading %s" % (inputfile))

    inputdata = readFile(inputfile)

    if verbose == True:
        for line in inputdata:
            print(line)

    print("%i records imported" % (len(inputdata)))

    if verbose == True:
        print("Writing %s" % (outputfile))

    output_count = writeCSV(inputdata, outputfile)

    print ("%i records saved" % output_count)
    

if __name__ == "__main__":
    main(sys.argv[1:])
