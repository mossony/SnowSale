from Corbetts import Corbetts
from Rudeboys import Rudeboys
from Comor import Comor
from Oberson import Oberson


options = {'Corbetts': False, 'Rudeboys': False, 'Comor': False, 'Oberson': True}


if options['Corbetts']:
    Corbetts_Obj = Corbetts()
    Corbetts_Obj.get_corbetts()
if options['Rudeboys']:
    Rudeboys_Obj = Rudeboys()
    Rudeboys_Obj.get_rudeboys()
if options['Comor']:
    Comor_Obj = Comor()
    Comor_Obj.get_comor()
if options['Oberson']:
    Oberson_Obj = Oberson()
    Oberson_Obj.get_oberson()
