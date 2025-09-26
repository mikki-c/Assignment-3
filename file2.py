# Impira Layout LM for Visual Question Answering
from transformers import pipeline

nlp = pipeline(
    "document-question-answering",
    model="impira/layoutlm-document-qa",
)

a= nlp(
    # "https://templates.invoicehome.com/invoice-template-us-neat-750px.png",
    # "What is the invoice number?"
    "C:/Users/S381332/Python/invoice.png",
    "What is the invoice number?"
)
print(a)
# {'score': 0.9943977, 'answer': 'us-001', 'start': 15, 'end': 15}

