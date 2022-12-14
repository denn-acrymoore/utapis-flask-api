import nltk
import test_preprocessing_func as tpf

test = """Dia pergi ke taman
Toni tidur di lapangan! Drs. Moh. hatta."""

print(nltk.tokenize.sent_tokenize(test))
print(tpf.preprocess_separate_sentences(test))
