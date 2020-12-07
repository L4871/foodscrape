

from bs4 import BeautifulSoup
import requests
import lxml
import re

#nimi joka tallennetaan tietokantaan
name = ""
def getSource():
    #raaka-aineen foodie URL
    url = ""
    reg = requests.get(url)
    data = reg.text
    soup = BeautifulSoup(data, "lxml")
    return soup

def getNutriens():
    soup = getSource()
    nutrion = soup.find(id="nutritions")
    stats = nutrion.find_all('td')
    return stats

#return price and weight

def getPrice():
    soup = getSource()
    info = soup.findAll('script', type='text/javascript')
    info = info[len(info) - 1]
    info = re.search(r"comp_price(.*?(?=\,))",str(info))
    try:
        price = info.group(1)
        price = price.strip("\"")
        price = price.strip(":")
        price = price.strip("'")
    except AttributeError:
        price = 0
        print('could not find price')
    return price




#deletes extra data from list
def getData():
    stats = getNutriens()
    for inx, item in enumerate(stats):
        try:
            if stats[inx]['class'][1] == 'value':
                del stats[inx]
        except IndexError:
            pass
    return stats

def nutrientConcent():
    stats = getData()
    nutriens = {}
    for index in range(0, len(stats), +2):
        if 'µ' not in stats[index+1].contents[0] and 'g' in stats[index+1].contents[0]:
            nutriens[stats[index].contents[0]] = stats[index + 1].contents[0]
    return nutriens

# Removes units and changes , to . returns how many nutrients per gram as dictionary
def getMacros():
    #removes kJ
    nutrients = nutrientConcent()
    try:
        for i in nutrients:
            nutrients[i] = nutrients[i].replace(",", ".")
            nutrients[i] = re.sub("[a-z]", "", nutrients[i])
            #Calculates how many nutrients per gram
            nutrients[i] = round(float(nutrients[i]) / 100, 5)
        return nutrients
    except KeyError:
        print("KeyError in getMacros could not find key")
        pass
    except IndexError:
        print("IndexError in getMacros")
        pass

# funktio joka vaihtaa esim rasva josta tyydyttyneitä johonkin tiettyyn jokainen pitää olla varmasti samalla nimellä

# hae hinta ja lisää se dictiin


def getInfo():
    price = getPrice()
    price = float(price) / 1000
    price = round(price, 6)
    makrot = getMacros()
    lista = []
    lista.append(price)
    lista.append(makrot['Rasvaa'])
    # voi olla "Hiilihydraatti" tai "Hiilihydraattia"
    try:
        lista.append(makrot['Hiilihydraattia'])
    except KeyError:
        lista.append(makrot['Hiilihydraatti'])
        pass
    lista.append(makrot['Proteiinia'])
    return lista

def djangoCommands():
    data = getInfo()
    command ="{} = Ingredient.objects.create(ingredient=\"{}\",price={},fats={},carbs={},protein={})".format(name.replace(" ",""),name ,data[0],data[1],data[2],data[3])
    file = open('djangocommands.txt', 'a')
    file.write(command + "\n")
    file.close()
    print(command)


getInfo()
getPrice()
djangoCommands()
