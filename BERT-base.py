# Bert-base NER - recognising entity input (location - LOC, organisations - ORG, person - PER, miscellaneous - MISC)

from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
 

tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
 

nlp = pipeline("ner", model=model, tokenizer=tokenizer)
# example = "My name is Wolfgang"
 
# ner_results = nlp(example)
# print(ner_results)

# class NER:
#     def __init__(self, ner_results):

input1 = str(input("Enter a string: "))

ner_results = nlp(input1)

sub = "B-PER"
for text in ner_results:
    if sub in text:
        print("It's a person")
# elif text == ["B-ORG"]:
#     print("It's an organisation")

    print(ner_results)

if ner_results == []: 
    print("Enter an input with location, person or organisation")




