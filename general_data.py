"""
Storage location for infromation about apartment info
"""

def invert_dict(d):
    inverted_dict = {}
    for key, value in d.items():
        inverted_dict.setdefault(value, []).append(key)
    return inverted_dict

#Molukken 411 t/m 545
#Sumatrastraat 217A t/m 223D
#Tidorestraat 58 t/m 98

MOLUKKEN_GEBOUW = [
    "Molukkenstraat 411",
    "Molukkenstraat 413",
    "Molukkenstraat 415",
    "Molukkenstraat 417",
    "Molukkenstraat 419",
    "Molukkenstraat 421",
    "Molukkenstraat 423",
    "Molukkenstraat 425",
    "Molukkenstraat 427",
    "Molukkenstraat 429",
    "Molukkenstraat 431",
    "Molukkenstraat 433",
    "Molukkenstraat 435",
    "Molukkenstraat 437",
    "Molukkenstraat 439",
    "Molukkenstraat 441",
    "Molukkenstraat 443",
    "Molukkenstraat 445",
    "Molukkenstraat 447",
    "Molukkenstraat 449",
    "Molukkenstraat 451",
    "Molukkenstraat 453",
    "Molukkenstraat 455",
    "Molukkenstraat 457",
    "Molukkenstraat 459",
    "Molukkenstraat 461",
    "Molukkenstraat 463-A/B/C",
    "Molukkenstraat 465",
    "Molukkenstraat 467",
    "Molukkenstraat 469",
    "Molukkenstraat 471-A/B/C",
    "Molukkenstraat 473",
    "Molukkenstraat 475",
    "Molukkenstraat 477",
    "Molukkenstraat 479",
    "Molukkenstraat 481",
    "Molukkenstraat 483",
    "Molukkenstraat 485",
    "Molukkenstraat 487",
    "Molukkenstraat 489",
    "Molukkenstraat 491",
    "Molukkenstraat 493",
    "Molukkenstraat 495",
    "Molukkenstraat 497",
    "Molukkenstraat 499",
    "Molukkenstraat 501",
    "Molukkenstraat 505",
    "Molukkenstraat 503",
    "Molukkenstraat 507",
    "Molukkenstraat 509",
    "Molukkenstraat 511",
    "Molukkenstraat 513",
    "Molukkenstraat 515",
    "Molukkenstraat 517",
    "Molukkenstraat 519",
    "Molukkenstraat 521",
    "Molukkenstraat 523",
    "Molukkenstraat 525",
    "Molukkenstraat 527",
    "Molukkenstraat 529",
    "Molukkenstraat 531",
    "Molukkenstraat 533",
    "Molukkenstraat 535",
    "Molukkenstraat 537",
    "Molukkenstraat 539",
    "Molukkenstraat 541",
    "Molukkenstraat 543",
    "Molukkenstraat 545",
    "Sumatrastraat 217-A",
    "Sumatrastraat 217-B",
    "Sumatrastraat 217-C",
    "Sumatrastraat 217-D",
    "Sumatrastraat 217-E",
    "Sumatrastraat 219-A",
    "Sumatrastraat 219-B",
    "Sumatrastraat 219-C",
    "Sumatrastraat 219-D",
    "Sumatrastraat 219-E",
    "Sumatrastraat 221-A",
    "Sumatrastraat 221-B",
    "Sumatrastraat 221-C",
    "Sumatrastraat 221-D",
    "Sumatrastraat 221-E",
    "Sumatrastraat 223-A",
    "Sumatrastraat 223-B",
    "Sumatrastraat 223-C",
    "Sumatrastraat 223-D",
    "Tidorestraat 58",
    "Tidorestraat 60",
    "Tidorestraat 62",
    "Tidorestraat 64",
    "Tidorestraat 66",
    "Tidorestraat 68",
    "Tidorestraat 70",
    "Tidorestraat 72",
    "Tidorestraat 74",
    "Tidorestraat 76",
    "Tidorestraat 78",
    "Tidorestraat 80",
    "Tidorestraat 82",
    "Tidorestraat 84",
    "Tidorestraat 86",
    "Tidorestraat 88-A/B",
    "Tidorestraat 90",
    "Tidorestraat 92",
    "Tidorestraat 94",
    "Tidorestraat 96",
    "Tidorestraat 98",
]

# Tidorestraat 88-A/B, Molukkenstraat 463-A/B/C, Molukkenstraat 471-A/B/C
# are not real adresses according to kadaster or BAG. 

#NOTE Molukkenstraat 463-A/B/C is just Molukkenstraat 463 on kadaster
#NOTE Molukkenstraat 471-A/B/C is just Molukkenstraat 471 on kadaster
#NOTE Tidorestraat 88-A/B is just Tidorestraat 88 on kadaster


#Sumatraplantsoen 20A t/m 38D
#Sumatrastraat 225A t/m 321D
#Tidorestraat 100 t/m 128

SUMATRAPLANTSOEN_GEBOUW =[
    "Sumatraplantsoen 20-A",
    "Sumatraplantsoen 20-B",
    "Sumatraplantsoen 20-C",
    "Sumatraplantsoen 20-D",
    "Sumatraplantsoen 22-A",
    "Sumatraplantsoen 22-B",
    "Sumatraplantsoen 22-C",
    "Sumatraplantsoen 22-D",
    "Sumatraplantsoen 24-A",
    "Sumatraplantsoen 24-B",
    "Sumatraplantsoen 24-C",
    "Sumatraplantsoen 24-D",
    "Sumatraplantsoen 26-A",
    "Sumatraplantsoen 26-B",
    "Sumatraplantsoen 26-C",
    "Sumatraplantsoen 26-D",
    "Sumatraplantsoen 28-A",
    "Sumatraplantsoen 28-B",
    "Sumatraplantsoen 28-C",
    "Sumatraplantsoen 28-D",
    "Sumatraplantsoen 30-A",
    "Sumatraplantsoen 30-B",
    "Sumatraplantsoen 30-C",
    "Sumatraplantsoen 32-A",
    "Sumatraplantsoen 32-B",
    "Sumatraplantsoen 32-C",
    "Sumatraplantsoen 32-D",
    "Sumatraplantsoen 34-A",
    "Sumatraplantsoen 34-B",
    "Sumatraplantsoen 34-C",
    "Sumatraplantsoen 34-D",
    "Sumatraplantsoen 36-A",
    "Sumatraplantsoen 36-B",
    "Sumatraplantsoen 36-C",
    "Sumatraplantsoen 36-D",
    "Sumatraplantsoen 38-A",
    "Sumatraplantsoen 38-B",
    "Sumatraplantsoen 38-C",
    "Sumatraplantsoen 38-D",
    "Sumatrastraat 225-A",
    "Sumatrastraat 225-B",
    "Sumatrastraat 225-C",
    "Sumatrastraat 225-D",
    "Sumatrastraat 227-A",
    "Sumatrastraat 227-B",
    "Sumatrastraat 227-C",
    "Sumatrastraat 229-A",
    "Sumatrastraat 229-B",
    "Sumatrastraat 229-C",
    "Sumatrastraat 229-D",
    "Sumatrastraat 231-A",
    "Sumatrastraat 231-B",
    "Sumatrastraat 231-C",
    "Sumatrastraat 231-D",
    "Tidorestraat 100",
    "Tidorestraat 102",
    "Tidorestraat 104",
    "Tidorestraat 106",
    "Tidorestraat 108",
    "Tidorestraat 110",
    "Tidorestraat 112",
    "Tidorestraat 114",
    "Tidorestraat 116",
    "Tidorestraat 118",
    "Tidorestraat 120",
    "Tidorestraat 122",
    "Tidorestraat 124",
    "Tidorestraat 126",
    "Tidorestraat 128", ]

# %%
#Portieken data

PORTIEKEN = {
    "Tidorestraat 58": "Mol_411_435",
    "Molukkenstraat 411": "Mol_411_435",
    "Molukkenstraat 413": "Mol_411_435",
    "Molukkenstraat 415": "Mol_411_435",
    "Molukkenstraat 417": "Mol_411_435",
    "Molukkenstraat 419": "Mol_411_435",
    "Molukkenstraat 421": "Mol_411_435",
    "Molukkenstraat 423": "Mol_411_435",
    "Molukkenstraat 425": "Mol_411_435",
    "Molukkenstraat 427": "Mol_411_435",
    "Molukkenstraat 429": "Mol_411_435",
    "Molukkenstraat 431": "Mol_411_435",
    "Molukkenstraat 433": "Mol_411_435",
    "Molukkenstraat 435": "Mol_411_435",
    "Molukkenstraat 437": "Mol_437_455",
    "Molukkenstraat 439": "Mol_437_455",
    "Molukkenstraat 441": "Mol_437_455",
    "Molukkenstraat 443": "Mol_437_455",
    "Molukkenstraat 445": "Mol_437_455",
    "Molukkenstraat 447": "Mol_437_455",
    "Molukkenstraat 449": "Mol_437_455",
    "Molukkenstraat 451": "Mol_437_455",
    "Molukkenstraat 453": "Mol_437_455",
    "Molukkenstraat 455": "Mol_437_455",
    "Molukkenstraat 457": "Mol_457_471",
    "Molukkenstraat 459": "Mol_457_471",
    "Molukkenstraat 461": "Mol_457_471",
    "Molukkenstraat 463-A/B/C": "Mol_457_471",
    "Molukkenstraat 465": "Mol_457_471",
    "Molukkenstraat 467": "Mol_457_471",
    "Molukkenstraat 469": "Mol_457_471",
    "Molukkenstraat 471-A/B/C": "Mol_457_471",
    "Molukkenstraat 473": "Mol_473_491",
    "Molukkenstraat 475": "Mol_473_491",
    "Molukkenstraat 477": "Mol_473_491",
    "Molukkenstraat 479": "Mol_473_491",
    "Molukkenstraat 481": "Mol_473_491",
    "Molukkenstraat 483": "Mol_473_491",
    "Molukkenstraat 485": "Mol_473_491",
    "Molukkenstraat 487": "Mol_473_491",
    "Molukkenstraat 489": "Mol_473_491",
    "Molukkenstraat 491": "Mol_473_491",
    "Molukkenstraat 493": "Mol_493_545",
    "Molukkenstraat 495": "Mol_493_545",
    "Molukkenstraat 497": "Mol_493_545",
    "Molukkenstraat 499": "Mol_493_545",
    "Molukkenstraat 501": "Mol_493_545",
    "Molukkenstraat 505": "Mol_493_545",
    "Molukkenstraat 503": "Mol_493_545",
    "Molukkenstraat 507": "Mol_493_545",
    "Molukkenstraat 509": "Mol_493_545",
    "Molukkenstraat 511": "Mol_493_545",
    "Molukkenstraat 513": "Mol_493_545",
    "Molukkenstraat 515": "Mol_493_545",
    "Molukkenstraat 517": "Mol_493_545",
    "Molukkenstraat 519": "Mol_493_545",
    "Molukkenstraat 521": "Mol_493_545",
    "Molukkenstraat 523": "Mol_493_545",
    "Molukkenstraat 525": "Mol_493_545",
    "Molukkenstraat 527": "Mol_493_545",
    "Molukkenstraat 529": "Mol_493_545",
    "Molukkenstraat 531": "Mol_493_545",
    "Molukkenstraat 533": "Mol_493_545",
    "Molukkenstraat 535": "Mol_493_545",
    "Molukkenstraat 537": "Mol_493_545",
    "Molukkenstraat 539": "Mol_493_545",
    "Molukkenstraat 541": "Mol_493_545",
    "Molukkenstraat 543": "Mol_493_545",
    "Molukkenstraat 545": "Mol_493_545",
    "Sumatrastraat 217-A": "Sum_217_219",
    "Sumatrastraat 217-B": "Sum_217_219",
    "Sumatrastraat 217-C": "Sum_217_219",
    "Sumatrastraat 217-D": "Sum_217_219",
    "Sumatrastraat 217-E": "Sum_217_219",
    "Sumatrastraat 219-A": "Sum_217_219",
    "Sumatrastraat 219-B": "Sum_217_219",
    "Sumatrastraat 219-C": "Sum_217_219",
    "Sumatrastraat 219-D": "Sum_217_219",
    "Sumatrastraat 219-E": "Sum_217_219",
    "Sumatrastraat 221-A": "Sum_221_223",
    "Sumatrastraat 221-B": "Sum_221_223",
    "Sumatrastraat 221-C": "Sum_221_223",
    "Sumatrastraat 221-D": "Sum_221_223",
    "Sumatrastraat 221-E": "Sum_221_223",
    "Sumatrastraat 223-A": "Sum_221_223",
    "Sumatrastraat 223-B": "Sum_221_223",
    "Sumatrastraat 223-C": "Sum_221_223",
    "Sumatrastraat 223-D": "Sum_221_223",
    "Tidorestraat 60": "Tid_60_78",
    "Tidorestraat 62": "Tid_60_78",
    "Tidorestraat 64": "Tid_60_78",
    "Tidorestraat 66": "Tid_60_78",
    "Tidorestraat 68": "Tid_60_78",
    "Tidorestraat 70": "Tid_60_78",
    "Tidorestraat 72": "Tid_60_78",
    "Tidorestraat 74": "Tid_60_78",
    "Tidorestraat 76": "Tid_60_78",
    "Tidorestraat 78": "Tid_60_78",
    "Tidorestraat 80": "Tid_80_98",
    "Tidorestraat 82": "Tid_80_98",
    "Tidorestraat 84": "Tid_80_98",
    "Tidorestraat 86": "Tid_80_98",
    "Tidorestraat 88-A/B": "Tid_80_98",
    "Tidorestraat 90": "Tid_80_98",
    "Tidorestraat 92": "Tid_80_98",
    "Tidorestraat 94": "Tid_80_98",
    "Tidorestraat 96": "Tid_80_98",
    "Tidorestraat 98": "Tid_80_98",
    "Sumatraplantsoen 20-A": "Plant_20_22",
    "Sumatraplantsoen 20-B": "Plant_20_22",
    "Sumatraplantsoen 20-C": "Plant_20_22",
    "Sumatraplantsoen 20-D": "Plant_20_22",
    "Sumatraplantsoen 22-A": "Plant_20_22",
    "Sumatraplantsoen 22-B": "Plant_20_22",
    "Sumatraplantsoen 22-C": "Plant_20_22",
    "Sumatraplantsoen 22-D": "Plant_20_22",
    "Sumatraplantsoen 24-A": "Plant_24_26",
    "Sumatraplantsoen 24-B": "Plant_24_26",
    "Sumatraplantsoen 24-C": "Plant_24_26",
    "Sumatraplantsoen 24-D": "Plant_24_26",
    "Sumatraplantsoen 26-A": "Plant_24_26",
    "Sumatraplantsoen 26-B": "Plant_24_26",
    "Sumatraplantsoen 26-C": "Plant_24_26",
    "Sumatraplantsoen 26-D": "Plant_24_26",
    "Sumatraplantsoen 28-A": "Plant_28_30",
    "Sumatraplantsoen 28-B": "Plant_28_30",
    "Sumatraplantsoen 28-C": "Plant_28_30",
    "Sumatraplantsoen 28-D": "Plant_28_30",
    "Sumatraplantsoen 30-A": "Plant_28_30",
    "Sumatraplantsoen 30-B": "Plant_28_30",
    "Sumatraplantsoen 30-C": "Plant_28_30",
    "Sumatraplantsoen 32-A": "Plant_32_34",
    "Sumatraplantsoen 32-B": "Plant_32_34",
    "Sumatraplantsoen 32-C": "Plant_32_34",
    "Sumatraplantsoen 32-D": "Plant_32_34",
    "Sumatraplantsoen 34-A": "Plant_32_34",
    "Sumatraplantsoen 34-B": "Plant_32_34",
    "Sumatraplantsoen 34-C": "Plant_32_34",
    "Sumatraplantsoen 34-D": "Plant_32_34",
    "Sumatraplantsoen 36-A": "Plant_36_38",
    "Sumatraplantsoen 36-B": "Plant_36_38",
    "Sumatraplantsoen 36-C": "Plant_36_38",
    "Sumatraplantsoen 36-D": "Plant_36_38",
    "Sumatraplantsoen 38-A": "Plant_36_38",
    "Sumatraplantsoen 38-B": "Plant_36_38",
    "Sumatraplantsoen 38-C": "Plant_36_38",
    "Sumatraplantsoen 38-D": "Plant_36_38",
    "Sumatrastraat 225-A": "Sum_225_227",
    "Sumatrastraat 225-B": "Sum_225_227",
    "Sumatrastraat 225-C": "Sum_225_227",
    "Sumatrastraat 225-D": "Sum_225_227",
    "Sumatrastraat 227-A": "Sum_225_227",
    "Sumatrastraat 227-B": "Sum_225_227",
    "Sumatrastraat 227-C": "Sum_225_227",
    "Sumatrastraat 229-A": "Sum_229_231",
    "Sumatrastraat 229-B": "Sum_229_231",
    "Sumatrastraat 229-C": "Sum_229_231",
    "Sumatrastraat 229-D": "Sum_229_231",
    "Sumatrastraat 231-A": "Sum_229_231",
    "Sumatrastraat 231-B": "Sum_229_231",
    "Sumatrastraat 231-C": "Sum_229_231",
    "Sumatrastraat 231-D": "Sum_229_231",
    "Tidorestraat 100": "Tid_100_112",
    "Tidorestraat 102": "Tid_100_112",
    "Tidorestraat 104": "Tid_100_112",
    "Tidorestraat 106": "Tid_100_112",
    "Tidorestraat 108": "Tid_100_112",
    "Tidorestraat 110": "Tid_100_112",
    "Tidorestraat 112": "Tid_100_112",
    "Tidorestraat 114": "Tid_114_128",
    "Tidorestraat 116": "Tid_114_128",
    "Tidorestraat 118": "Tid_114_128",
    "Tidorestraat 120": "Tid_114_128",
    "Tidorestraat 122": "Tid_114_128",
    "Tidorestraat 124": "Tid_114_128",
    "Tidorestraat 126": "Tid_114_128",
    "Tidorestraat 128": "Tid_114_128",
}


# Dakaanbouw. Data gathered manually from google sattelite on 2024-04-23

DAKAANBOUW = [
            "Molukkenstraat 431",
            "Molukkenstraat 433",
            "Molukkenstraat 515",
            "Molukkenstraat 519",
            "Molukkenstraat 523",
            "Molukkenstraat 541",
            "Molukkenstraat 541",
            "Molukkenstraat 545",
            "Tidorestraat 78",
            "Tidorestraat 88",
            "Tidorestraat 112",
            "Tidorestraat 126",
            "Sumatraplaantsoen 22-D",
            "Sumatraplaantsoen 30-C",
            "Sumatraplaantsoen 34-D",
            "Sumatrasstraat 229-D",]

TUINDAANBOUW = []


